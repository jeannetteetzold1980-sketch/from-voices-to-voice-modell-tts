import os
import sys
from pydub import AudioSegment

from audio_processing import is_supported, convert_to_wav, get_audio_quality, segment_audio, transcribe_segment, save_results_csv

def batch_convert(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if os.path.isfile(input_path) and is_supported(filename):
            print(f"Verarbeite: {filename}")
            output_filename = os.path.splitext(filename)[0] + ".wav"
            file_output_dir = os.path.join(output_dir, os.path.splitext(filename)[0])
            os.makedirs(file_output_dir, exist_ok=True)
            output_path = os.path.join(file_output_dir, output_filename)
            try:
                convert_to_wav(input_path, output_path)
                print(f"Konvertiert: {output_filename}")
                # Qualitätsprüfung
                qual = get_audio_quality(output_path)
                if qual['error']:
                    print(f"Qualitätsfehler: {qual['error']}")
                # Segmentierung
                segments = segment_audio(output_path)
                segments_info = []
                for seg in segments:
                    # Segment speichern
                    seg_filename = f"segment_{seg['segment_number']:02d}.wav"
                    seg_path = os.path.join(file_output_dir, seg_filename)
                    # Exportiere Segment als WAV
                    audio = AudioSegment.from_wav(output_path)
                    start_ms = int(seg['start_time'] * 1000)
                    end_ms = int(seg['end_time'] * 1000)
                    segment_audio_data = audio[start_ms:end_ms]
                    segment_audio_data.export(seg_path, format="wav")
                    # Transkription
                    transcript = transcribe_segment(seg_path)
                    seg_info = {
                        "original_filename": filename,
                        "segment_number": seg['segment_number'],
                        "audio_file": seg_filename,
                        "transcript": transcript,
                        "start_time": seg['start_time'],
                        "end_time": seg['end_time'],
                        "duration": seg['duration'],
                        "error": qual['error']
                    }
                    segments_info.append(seg_info)
                # CSV speichern
                save_results_csv(file_output_dir, os.path.splitext(filename)[0], segments_info)
            except Exception as e:
                print(f"Fehler bei {filename}: {e}")
        else:
            print(f"Übersprungen (nicht unterstützt oder kein File): {filename}")

def main(argv):
    print("WhatsApp Voice Processing gestartet.")
    if len(argv) < 3:
        print("Nutzung: python main.py <input_dir> <output_dir>")
        sys.exit(1)
        return
    input_dir = argv[1]
    output_dir = argv[2]
    batch_convert(input_dir, output_dir)

if __name__ == "__main__":
    main(sys.argv)
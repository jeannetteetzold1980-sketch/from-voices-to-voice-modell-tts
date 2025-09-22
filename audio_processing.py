import csv

def save_results_csv(output_dir, original_filename, segments_info):
    """
    Speichert die Segmentinformationen als CSV im Ergebnisordner.
    segments_info: Liste von Dicts mit allen Infos pro Segment
    """
    csv_path = os.path.join(output_dir, f"{original_filename}_results.csv")
    header = [
        "original_filename",
        "segment_number",
        "audio_file",
        "transcript",
        "start_time",
        "end_time",
        "duration",
        "error"
    ]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for seg in segments_info:
            writer.writerow(seg)
    return csv_path
def transcribe_segment(segment_path, model_name="base"):
    """
    Transkribiert ein einzelnes Audiosegment mit OpenAI Whisper.
    Gibt den transkribierten Text zurück.
    """
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(segment_path)
    return result.get('text', '')
from pydub import AudioSegment, silence

def segment_audio(wav_path, min_silence_len=500, silence_thresh=-40):
    """
    Segmentiert eine WAV-Datei anhand von Sprachpausen.
    Gibt eine Liste von Segmenten mit Startzeit, Endzeit, Dauer und Segmentnummer zurück.
    """
    audio = AudioSegment.from_wav(wav_path)
    segments = []
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    current_time = 0.0
    for i, chunk in enumerate(chunks):
        duration = len(chunk) / 1000.0  # Dauer in Sekunden
        segment = {
            'segment_number': i + 1,
            'start_time': current_time,
            'end_time': current_time + duration,
            'duration': duration
        }
        segments.append(segment)
        current_time += duration
    return segments

import os
import ffmpeg
from pydub import AudioSegment
import numpy as np
import librosa
import scipy

SUPPORTED_FORMATS = ['.opus', '.mp3', '.wav', '.m4a', '.aac', '.flac']


def is_supported(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_FORMATS


def convert_to_wav(input_path, output_path):
    """
    Konvertiert eine Audiodatei ins WAV-Format.
    """
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    return output_path


def get_audio_quality(wav_path):
    result = {
        'snr': None,
        'clipping': False,
        'dynamik': None,
        'frequenzanalyse': None,
        'stille': False,
        'error': ''
    }

    try:
        y, sr = librosa.load(wav_path, sr=None)
    except Exception as e:
        result['error'] = f'Fehler beim Laden der Audiodatei: {e}'
        return result

    # --- SNR-Berechnung ---
    try:
        signal_power = np.mean(y ** 2)
        noise_power = np.var(y - np.mean(y))
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
            result['snr'] = round(snr, 2)
            if snr < 20:
                result['error'] += 'SNR zu niedrig; '
        else:
            result['snr'] = None
            result['error'] += 'SNR nicht berechenbar; '
    except Exception as e:
        result['error'] += f'SNR-Fehler: {e}; '

    # --- Clipping-Erkennung ---
    try:
        max_val = np.max(np.abs(y))
        result['clipping'] = max_val >= 0.99
        if result['clipping']:
            result['error'] += 'Clipping erkannt; '
    except Exception as e:
        result['error'] += f'Clipping-Fehler: {e}; '

    # --- Dynamikbereich ---
    try:
        min_val = np.min(np.abs(y[np.nonzero(y)])) if np.any(y) else 0.0
        if min_val > 0:
            max_val = np.max(np.abs(y))
            dynamic_range = 20 * np.log10(max_val / min_val)
            result['dynamik'] = round(dynamic_range, 2)
            if dynamic_range < 10:
                result['error'] += 'Dynamikbereich kritisch; '
        else:
            result['dynamik'] = None
            result['error'] += 'Dynamik nicht berechenbar; '
    except Exception as e:
        result['error'] += f'Dynamik-Fehler: {e}; '

    # --- Frequenzanalyse ---
    try:
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        spectrum = np.mean(S, axis=1)
        low_freq_power = np.mean(spectrum[freqs < 300]) if np.any(freqs < 300) else 0
        high_freq_power = np.mean(spectrum[freqs > 4000]) if np.any(freqs > 4000) else 0
        result['frequenzanalyse'] = {
            'low_freq_power': round(float(low_freq_power), 2),
            'high_freq_power': round(float(high_freq_power), 2)
        }
        if low_freq_power < 0.01 or high_freq_power < 0.01:
            result['error'] += 'Frequenzverluste/-verzerrungen; '
    except Exception as e:
        result['error'] += f'Frequenzanalyse-Fehler: {e}; '

    # --- Stille-Erkennung ---
    try:
        silence_ratio = np.sum(np.abs(y) < 0.001) / len(y)
        result['stille'] = silence_ratio > 0.5
        if result['stille']:
            result['error'] += 'Stille erkannt; '
    except Exception as e:
        result['error'] += f'Stille-Fehler: {e}; '

    return result
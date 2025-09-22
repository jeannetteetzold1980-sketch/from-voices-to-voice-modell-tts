
from flask import Flask, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from audio_processing import is_supported, convert_to_wav, get_audio_quality, segment_audio, transcribe_segment, save_results_csv

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'.opus', '.mp3', '.wav', '.m4a', '.aac', '.flac'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files')
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)
        # Verarbeitung nach Upload
        results = []
        for filename in saved_files:
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_dir = os.path.join(app.config['RESULT_FOLDER'], os.path.splitext(filename)[0])
            os.makedirs(output_dir, exist_ok=True)
            output_wav = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')
            convert_to_wav(input_path, output_wav)
            qual = get_audio_quality(output_wav)
            segments = segment_audio(output_wav)
            segments_info = []
            for seg in segments:
                seg_filename = f"segment_{seg['segment_number']:02d}.wav"
                seg_path = os.path.join(output_dir, seg_filename)
                # Segment speichern
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(output_wav)
                start_ms = int(seg['start_time'] * 1000)
                end_ms = int(seg['end_time'] * 1000)
                segment_audio_data = audio[start_ms:end_ms]
                segment_audio_data.export(seg_path, format="wav")
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
            save_results_csv(output_dir, os.path.splitext(filename)[0], segments_info)
            results.append({"filename": filename, "segments": segments_info, "error": qual['error']})
        return f'<h3>Verarbeitung abgeschlossen!</h3><pre>{results}</pre>'
    return '''
    <h2>WhatsApp Voice Batch-Upload</h2>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="files" multiple>
      <input type="submit" value="Hochladen">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)

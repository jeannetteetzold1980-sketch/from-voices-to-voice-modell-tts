from flask import send_from_directory

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
# Download-Route für Ergebnisdateien
@app.route('/results/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)

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

        # Professionelle Ergebnisdarstellung
        html = '''
                <!DOCTYPE html>
                <html lang="de">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Ergebnisse - WhatsApp Voice Batch</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" rel="stylesheet">
                    <link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&display=swap" rel="stylesheet">
                    <style>
                        body {
                            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
                            min-height: 100vh;
                        }
                        .container {
                            max-width: 900px;
                            margin-top: 40px;
                        }
                        .wow {
                            animation: tada 1.2s;
                        }
                        .table thead th {
                            background: #007bff;
                            color: #fff;
                            font-weight: 500;
                            letter-spacing: 0.05em;
                        }
                        .accordion-button {
                            background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%);
                            color: #fff;
                            font-size: 1.1rem;
                            font-weight: 500;
                            box-shadow: 0 2px 8px rgba(33,147,176,0.08);
                            transition: background 0.3s;
                        }
                        .accordion-button:not(.collapsed) {
                            background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
                            color: #fff;
                        }
                        .accordion-item {
                            border-radius: 12px;
                            margin-bottom: 18px;
                            box-shadow: 0 4px 16px rgba(33,147,176,0.10);
                            border: none;
                            overflow: hidden;
                        }
                        .table {
                            background: #fff;
                            border-radius: 8px;
                            box-shadow: 0 2px 8px rgba(33,147,176,0.07);
                            overflow: hidden;
                        }
                        .badge-success {
                            background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%);
                            color: #fff;
                            font-size: 0.95em;
                        }
                        .badge-danger {
                            background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);
                            color: #fff;
                            font-size: 0.95em;
                        }
                        .transcript-cell {
                            font-family: 'Fira Mono', 'Consolas', monospace;
                            font-size: 1em;
                            color: #2193b0;
                            background: #f0f7fa;
                            border-radius: 4px;
                            padding: 4px 8px;
                            transition: box-shadow 0.3s;
                            position: relative;
                        }
                        .transcript-cell:hover {
                            box-shadow: 0 0 8px #6dd5ed;
                        }
                        .copy-btn {
                            position: absolute;
                            top: 4px;
                            right: 4px;
                            background: #6dd5ed;
                            color: #fff;
                            border: none;
                            border-radius: 4px;
                            font-size: 0.9em;
                            padding: 2px 6px;
                            cursor: pointer;
                            transition: background 0.2s;
                        }
                        .copy-btn:hover {
                            background: #2193b0;
                        }
                        .audio-player {
                            width: 120px;
                            margin-right: 8px;
                        }
                        .download-btn {
                            background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
                            color: #fff;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 10px;
                            font-size: 0.95em;
                            margin-right: 4px;
                            transition: background 0.2s;
                        }
                        .download-btn:hover {
                            background: #007bff;
                        }
                        #confetti-canvas {
                            position: fixed;
                            top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999;
                        }
                    </style>
                </head>
                <body>
                    <canvas id="confetti-canvas"></canvas>
                    <div class="container animate__animated animate__fadeIn wow">
                        <h2 class="mb-4 text-center animate__animated animate__zoomIn">🎉 Verarbeitung abgeschlossen! 🎉</h2>
                        <div class="accordion animate__animated animate__fadeInUp" id="resultsAccordion">
                '''
        for idx, file_result in enumerate(results):
            html += f'''
                        <div class="accordion-item animate__animated animate__fadeInUp">
                            <h2 class="accordion-header" id="heading{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{idx}" aria-expanded="false" aria-controls="collapse{idx}">
                                    <span class="me-2">📄</span> <strong>{file_result['filename']}</strong>
                                </button>
                            </h2>
                            <div id="collapse{idx}" class="accordion-collapse collapse" aria-labelledby="heading{idx}" data-bs-parent="#resultsAccordion">
                                <div class="accordion-body">
                                    <table class="table table-bordered table-sm align-middle animate__animated animate__fadeIn">
                                        <thead>
                                            <tr>
                                                <th>Segment</th>
                                                <th>Start</th>
                                                <th>Ende</th>
                                                <th>Dauer</th>
                                                <th>Transkript</th>
                                                <th>Fehler</th>
                                                <th>Audio</th>
                                                <th>Download</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        '''
            for seg in file_result['segments']:
                error_badge = f'<span class="badge badge-danger" title="Fehler">{seg["error"]}</span>' if seg['error'] else f'<span class="badge badge-success" title="Alles OK">OK</span>'
                audio_file_url = f"/results/{file_result['filename'].split('.')[0]}/{seg['audio_file']}"
                transcript_id = f"transcript_{file_result['filename']}_{seg['segment_number']}"
                html += f'''
                    <tr class="animate__animated animate__fadeIn">
                        <td><span class="badge bg-info">{seg['segment_number']}</span></td>
                        <td>{seg['start_time']:.2f}s</td>
                        <td>{seg['end_time']:.2f}s</td>
                        <td>{seg['duration']:.2f}s</td>
                        <td class="transcript-cell" id="{transcript_id}">{seg['transcript']}<button class="copy-btn" onclick="copyToClipboard('{transcript_id}')" title="Transkript kopieren">📋</button></td>
                        <td>{error_badge}</td>
                        <td><audio class="audio-player" controls src="{audio_file_url}"></audio></td>
                        <td><a class="download-btn" href="{audio_file_url}" download>⬇️ Download</a></td>
                    </tr>
                '''
        html += '''
        </tbody>
        </table>
        </div>
        </div>
        </div>
        </div>
        <div class="text-center mt-4">
            <a href="/" class="btn btn-lg btn-gradient animate__animated animate__pulse animate__infinite" style="background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%); color: #fff; border: none;">⬅️ Zurück zum Upload</a>
            <a class="btn btn-lg download-btn ms-2" href="/results.zip" download>📦 Alle Ergebnisse als ZIP herunterladen</a>
        </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Copy-to-Clipboard Funktion
            function copyToClipboard(id) {
                var el = document.getElementById(id);
                var text = el.innerText.replace('📋','').trim();
                navigator.clipboard.writeText(text);
                el.style.boxShadow = '0 0 12px #56ab2f';
                setTimeout(function(){ el.style.boxShadow = ''; }, 800);
            }
            // Konfetti-Effekt
            function confetti() {
                var canvas = document.getElementById('confetti-canvas');
                var ctx = canvas.getContext('2d');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                var pieces = [];
                for (var i=0; i<120; i++) {
                    pieces.push({
                        x: Math.random()*canvas.width,
                        y: Math.random()*canvas.height,
                        r: Math.random()*8+4,
                        c: 'hsl('+(Math.random()*360)+',80%,60%)',
                        vx: Math.random()*2-1,
                        vy: Math.random()*2+1
                    });
                }
                var frame = 0;
                function draw() {
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    for (var i=0; i<pieces.length; i++) {
                        var p = pieces[i];
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.r, 0, 2*Math.PI);
                        ctx.fillStyle = p.c;
                        ctx.fill();
                        p.x += p.vx;
                        p.y += p.vy;
                        if (p.y > canvas.height) p.y = 0;
                        if (p.x > canvas.width) p.x = 0;
                        if (p.x < 0) p.x = canvas.width;
                    }
                    frame++;
                    if (frame < 120) requestAnimationFrame(draw);
                }
                draw();
            }
            window.onload = confetti;
        </script>
        </body>
        </html>
        '''
        return html
    else:
        return '''
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>WhatsApp Voice Batch-Upload</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background: #f8f9fa; }
                .container { max-width: 600px; margin-top: 60px; }
                .card { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="card-body">
                        <h2 class="card-title text-center mb-4">WhatsApp Voice Batch-Upload</h2>
                        <form method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="files" class="form-label">Audiodateien auswählen</label>
                                <input class="form-control" type="file" id="files" name="files" multiple required accept=".opus,.mp3,.wav,.m4a,.aac,.flac">
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Hochladen & Verarbeiten</button>
                        </form>
                    </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=True)

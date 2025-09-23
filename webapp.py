from flask import send_from_directory
irect, url_for, send_from_directory
from flask import Flask, request, redirect, url_forimport os
import os
from werkzeug.utils import secure_filenameo_processing import is_supported, convert_to_wav, get_audio_quality, segment_audio, transcribe_segment, save_results_csv
from audio_processing import is_supported, convert_to_wav, get_audio_quality, segment_audio, transcribe_segment, save_results_csv

UPLOAD_FOLDER = 'uploads'RESULT_FOLDER = 'results'
RESULT_FOLDER = 'results'pus', '.mp3', '.wav', '.m4a', '.aac', '.flac'}
ALLOWED_EXTENSIONS = {'.opus', '.mp3', '.wav', '.m4a', '.aac', '.flac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Download-Route für Segmentdateien aus Unterordnern
@app.route('/results/<filefolder>/<filename>')
def download_file(filefolder, filename):
    import logging, os
    full_path = os.path.join(app.config['RESULT_FOLDER'], filefolder, filename)
    logging.warning(f"Download-Request: {full_path} exists: {os.path.exists(full_path)}")
    return send_from_directory(os.path.join(app.config['RESULT_FOLDER'], filefolder), filename, as_attachment=True)

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
    full_path = os.path.join(app.config['RESULT_FOLDER'], filefolder, filename)
    logging.warning(f"Download-Request: {full_path} exists: {os.path.exists(full_path)}")    if request.method == 'POST':
    return send_from_directory(os.path.join(app.config['RESULT_FOLDER'], filefolder), filename, as_attachment=True)iles')
 = []

name):
def allowed_file(filename): = secure_filename(file.filename)
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONSos.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files')            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        saved_files = []ir = os.path.join(app.config['RESULT_FOLDER'], os.path.splitext(filename)[0])
        for file in files:exist_ok=True)
            if file and allowed_file(file.filename):[0] + '.wav')
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)

        results = []
        for filename in saved_files:egment_number']:02d}.wav"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)path.join(output_dir, seg_filename)
            output_dir = os.path.join(app.config['RESULT_FOLDER'], os.path.splitext(filename)[0])t AudioSegment
            os.makedirs(output_dir, exist_ok=True)
            output_wav = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')
            convert_to_wav(input_path, output_wav) 1000)
            qual = get_audio_quality(output_wav)s]
            segments = segment_audio(output_wav)at="wav")
            segments_info = []path)
            for seg in segments:
                seg_filename = f"segment_{seg['segment_number']:02d}.wav"
                seg_path = os.path.join(output_dir, seg_filename)'],
                from pydub import AudioSegmentile": seg_filename,
                audio = AudioSegment.from_wav(output_wav)
                start_ms = int(seg['start_time'] * 1000)
                end_ms = int(seg['end_time'] * 1000),
                segment_audio_data = audio[start_ms:end_ms]'],
                segment_audio_data.export(seg_path, format="wav")
                transcript = transcribe_segment(seg_path)
                seg_info = {
                    "original_filename": filename,s.path.splitext(filename)[0], segments_info)
                    "segment_number": seg['segment_number'],ts.append({"filename": filename, "segments": segments_info, "error": qual['error']})
                    "audio_file": seg_filename,
                    "transcript": transcript,
                    "start_time": seg['start_time'],
                    "end_time": seg['end_time'],                <!DOCTYPE html>
                    "duration": seg['duration'],
                    "error": qual['error']ead>
                }et="UTF-8">
                segments_info.append(seg_info)viewport" content="width=device-width, initial-scale=1">
            save_results_csv(output_dir, os.path.splitext(filename)[0], segments_info)itle>Ergebnisse - WhatsApp Voice Batch</title>
            results.append({"filename": filename, "segments": segments_info, "error": qual['error']})n.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
/animate.min.css" rel="stylesheet">
        # Professionelle Ergebnisdarstellungmily=Fira+Mono:wght@400;700&display=swap" rel="stylesheet">
        html = '''
                <!DOCTYPE html>
                <html lang="de">
                <head> min-height: 100vh;
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Ergebnisse - WhatsApp Voice Batch</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">   margin-top: 40px;
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" rel="stylesheet">
                    <link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&display=swap" rel="stylesheet">
                    <style>.2s;
                        body {
                            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); thead th {
                            min-height: 100vh;
                        }   color: #fff;
                        .container {500;
                            max-width: 900px;em;
                            margin-top: 40px;
                        }
                        .wow {ient(90deg, #6dd5ed 0%, #2193b0 100%);
                            animation: tada 1.2s;   color: #fff;
                        }em;
                        .table thead th {
                            background: #007bff;0 2px 8px rgba(33,147,176,0.08);
                            color: #fff;ound 0.3s;
                            font-weight: 500;
                            letter-spacing: 0.05em;
                        }90deg, #2193b0 0%, #6dd5ed 100%);
                        .accordion-button {   color: #fff;
                            background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%);
                            color: #fff;
                            font-size: 1.1rem;s: 12px;
                            font-weight: 500;   margin-bottom: 18px;
                            box-shadow: 0 2px 8px rgba(33,147,176,0.08); 4px 16px rgba(33,147,176,0.10);
                            transition: background 0.3s;
                        }
                        .accordion-button:not(.collapsed) {
                            background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
                            color: #fff;
                        }   border-radius: 8px;
                        .accordion-item {shadow: 0 2px 8px rgba(33,147,176,0.07);
                            border-radius: 12px;
                            margin-bottom: 18px;
                            box-shadow: 0 4px 16px rgba(33,147,176,0.10);
                            border: none;r-gradient(90deg, #56ab2f 0%, #a8e063 100%);
                            overflow: hidden;   color: #fff;
                        }.95em;
                        .table {
                            background: #fff;
                            border-radius: 8px;-gradient(90deg, #e52d27 0%, #b31217 100%);
                            box-shadow: 0 2px 8px rgba(33,147,176,0.07);   color: #fff;
                            overflow: hidden;0.95em;
                        }
                        .badge-success { {
                            background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%); Mono', 'Consolas', monospace;
                            color: #fff;   font-size: 1em;
                            font-size: 0.95em;;
                        }
                        .badge-danger {4px;
                            background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);x;
                            color: #fff;ow 0.3s;
                            font-size: 0.95em;
                        }
                        .transcript-cell {
                            font-family: 'Fira Mono', 'Consolas', monospace; #6dd5ed;
                            font-size: 1em;
                            color: #2193b0;
                            background: #f0f7fa;
                            border-radius: 4px;   top: 4px;
                            padding: 4px 8px;4px;
                            transition: box-shadow 0.3s;;
                            position: relative;ff;
                        }e;
                        .transcript-cell:hover {
                            box-shadow: 0 0 8px #6dd5ed;.9em;
                        }6px;
                        .copy-btn {
                            position: absolute;round 0.2s;
                            top: 4px;
                            right: 4px;
                            background: #6dd5ed;
                            color: #fff;
                            border: none;
                            border-radius: 4px;
                            font-size: 0.9em;   margin-right: 8px;
                            padding: 2px 6px;
                            cursor: pointer;
                            transition: background 0.2s;-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
                        }   color: #fff;
                        .copy-btn:hover {e;
                            background: #2193b0;
                        } 10px;
                        .audio-player {95em;
                            width: 120px;
                            margin-right: 8px;ound 0.2s;
                        }
                        .download-btn {
                            background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%);
                            color: #fff;
                            border: none;
                            border-radius: 4px;
                            padding: 4px 10px;   top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999;
                            font-size: 0.95em;
                            margin-right: 4px;
                            transition: background 0.2s;
                        }
                        .download-btn:hover {id="confetti-canvas"></canvas>
                            background: #007bff;v class="container animate__animated animate__fadeIn wow">
                        }  <h2 class="mb-4 text-center animate__animated animate__zoomIn">🎉 Verarbeitung abgeschlossen! 🎉</h2>
                        #confetti-canvas {mated animate__fadeInUp" id="resultsAccordion">
                            position: fixed;
                            top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999;
                        }
                    </style>     <div class="accordion-item animate__animated animate__fadeInUp">
                </head>ader" id="heading{idx}">
                <body>        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{idx}" aria-expanded="false" aria-controls="collapse{idx}">
                    <canvas id="confetti-canvas"></canvas>ilename']}</strong>
                    <div class="container animate__animated animate__fadeIn wow">
                        <h2 class="mb-4 text-center animate__animated animate__zoomIn">🎉 Verarbeitung abgeschlossen! 🎉</h2>
                        <div class="accordion animate__animated animate__fadeInUp" id="resultsAccordion">ading{idx}" data-bs-parent="#resultsAccordion">
                '''s="accordion-body">
        for idx, file_result in enumerate(results):   <table class="table table-bordered table-sm align-middle animate__animated animate__fadeIn">
            html += f'''
                        <div class="accordion-item animate__animated animate__fadeInUp">
                            <h2 class="accordion-header" id="heading{idx}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{idx}" aria-expanded="false" aria-controls="collapse{idx}"> <th>Start</th>
                                    <span class="me-2">📄</span> <strong>{file_result['filename']}</strong><th>Ende</th>
                                </button>
                            </h2></th>
                            <div id="collapse{idx}" class="accordion-collapse collapse" aria-labelledby="heading{idx}" data-bs-parent="#resultsAccordion">h>
                                <div class="accordion-body">
                                    <table class="table table-bordered table-sm align-middle animate__animated animate__fadeIn">
                                        <thead>
                                            <tr>
                                                <th>Segment</th>
                                                <th>Start</th>
                                                <th>Ende</th>
                                                <th>Dauer</th>dge badge-danger" title="Fehler">{seg["error"]}</span>' if seg['error'] else f'<span class="badge badge-success" title="Alles OK">OK</span>'
                                                <th>Transkript</th>url = f"/results/{file_result['filename'].split('.')[0]}/{seg['audio_file']}"
                                                <th>Fehler</th>ile_result['filename']}_{seg['segment_number']}"
                                                <th>Audio</th>
                                                <th>Download</th>
                                            </tr>
                                        </thead>{seg['start_time']:.2f}s</td>
                                        <tbody>
                        '''
            for seg in file_result['segments']:transcript_id}">{seg['transcript']}<button class="copy-btn" onclick="copyToClipboard('{transcript_id}')" title="Transkript kopieren">📋</button></td>
                error_badge = f'<span class="badge badge-danger" title="Fehler">{seg["error"]}</span>' if seg['error'] else f'<span class="badge badge-success" title="Alles OK">OK</span>'
                audio_file_url = f"/results/{file_result['filename'].split('.')[0]}/{seg['audio_file']}" controls src="{audio_file_url}"></audio></td>
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
                        <td><a class="download-btn" href="{audio_file_url}" download>⬇️ Download</a></td>lass="text-center mt-4">
                    </tr> href="/" class="btn btn-lg btn-gradient animate__animated animate__pulse animate__infinite" style="background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%); color: #fff; border: none;">⬅️ Zurück zum Upload</a>
                ''' class="btn btn-lg download-btn ms-2" href="/results.zip" download>📦 Alle Ergebnisse als ZIP herunterladen</a>
        html += '''
        </tbody>
        </table>
        </div>t>
        </div> Copy-to-Clipboard Funktion
        </div>
        </div>var el = document.getElementById(id);
        <div class="text-center mt-4">eplace('📋','').trim();
            <a href="/" class="btn btn-lg btn-gradient animate__animated animate__pulse animate__infinite" style="background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 100%); color: #fff; border: none;">⬅️ Zurück zum Upload</a>ext(text);
            <a class="btn btn-lg download-btn ms-2" href="/results.zip" download>📦 Alle Ergebnisse als ZIP herunterladen</a>f';
        </div>}, 800);
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Copy-to-Clipboard Funktion   var canvas = document.getElementById('confetti-canvas');
            function copyToClipboard(id) {as.getContext('2d');
                var el = document.getElementById(id);ndow.innerWidth;
                var text = el.innerText.replace('📋','').trim();
                navigator.clipboard.writeText(text);
                el.style.boxShadow = '0 0 12px #56ab2f';
                setTimeout(function(){ el.style.boxShadow = ''; }, 800);
            }random()*canvas.width,
            // Konfetti-Effektnvas.height,
            function confetti() {andom()*8+4,
                var canvas = document.getElementById('confetti-canvas');',80%,60%)',
                var ctx = canvas.getContext('2d');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                var pieces = [];
                for (var i=0; i<120; i++) {
                    pieces.push({n draw() {
                        x: Math.random()*canvas.width,   ctx.clearRect(0,0,canvas.width,canvas.height);
                        y: Math.random()*canvas.height,=0; i<pieces.length; i++) {
                        r: Math.random()*8+4,ieces[i];
                        c: 'hsl('+(Math.random()*360)+',80%,60%)',
                        vx: Math.random()*2-1,PI);
                        vy: Math.random()*2+1c;
                    });
                }
                var frame = 0;
                function draw() {anvas.height) p.y = 0;
                    ctx.clearRect(0,0,canvas.width,canvas.height);nvas.width) p.x = 0;
                    for (var i=0; i<pieces.length; i++) { p.x = canvas.width;
                        var p = pieces[i];
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.r, 0, 2*Math.PI);me(draw);
                        ctx.fillStyle = p.c;
                        ctx.fill();
                        p.x += p.vx;
                        p.y += p.vy;w.onload = confetti;
                        if (p.y > canvas.height) p.y = 0;
                        if (p.x > canvas.width) p.x = 0;y>
                        if (p.x < 0) p.x = canvas.width;
                    }
                    frame++;html
                    if (frame < 120) requestAnimationFrame(draw);
                }urn '''
                draw();tml>
            }html lang="de">
            window.onload = confetti;
        </script>et="UTF-8">
        </body>viewport" content="width=device-width, initial-scale=1">
        </html>itle>WhatsApp Voice Batch-Upload</title>
        '''n.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        return html
    else:
        return '''
        <!DOCTYPE html>rd { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">ss="container">
            <title>WhatsApp Voice Batch-Upload</title> <div class="card">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">      <div class="card-body">
            <style>card-title text-center mb-4">WhatsApp Voice Batch-Upload</h2>
                body { background: #f8f9fa; }od="post" enctype="multipart/form-data">
                .container { max-width: 600px; margin-top: 60px; }3">
                .card { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }bel>
            </style>="files" name="files" multiple required accept=".opus,.mp3,.wav,.m4a,.aac,.flac">
        </head>
        <body>ten</button>
            <div class="container">
                <div class="card">
                    <div class="card-body">
                        <h2 class="card-title text-center mb-4">WhatsApp Voice Batch-Upload</h2>
                        <form method="post" enctype="multipart/form-data">ttps://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
                            <div class="mb-3">
                                <label for="files" class="form-label">Audiodateien auswählen</label>
                                <input class="form-control" type="file" id="files" name="files" multiple required accept=".opus,.mp3,.wav,.m4a,.aac,.flac">
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Hochladen & Verarbeiten</button>'__main__':
                        </form>(debug=True)
                    </div>                </div>            </div>            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=True)

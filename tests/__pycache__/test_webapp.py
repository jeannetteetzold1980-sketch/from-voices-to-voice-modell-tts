import os
import tempfile
from flask.testing import FlaskClient
import pytest
from webapp import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['RESULT_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        yield client

def test_upload_and_download(client: FlaskClient):
    # Test: Upload einer echten kleinen WAV-Datei und Download-Link
    import wave
    import numpy as np
    dummy_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    framerate = 8000
    duration = 2.0  # Sekunden
    t = np.linspace(0, duration, int(framerate*duration), endpoint=False)
    data = (np.sin(2*np.pi*440*t) * 32767).astype(np.int16)
    with wave.open(dummy_audio.name, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(data.tobytes())
    with open(dummy_audio.name, 'rb') as f:
        data = {'files': (f, 'test.wav')}
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'Download' in response.data
    # Test: Download-Link funktioniert
    result_dir = os.path.join(app.config['RESULT_FOLDER'], 'test')
    # Suche nach erzeugten Segmentdateien
    segment_files = [f for f in os.listdir(result_dir) if f.startswith('segment_') and f.endswith('.wav')]
    assert segment_files, "Es wurden keine Segmentdateien erzeugt!"
    # Teste Download für die erste gefundene Segmentdatei
    download_url = f'/results/test/{segment_files[0]}'
    response = client.get(download_url)
    assert response.status_code == 200
    assert response.data.startswith(b'RIFF')
    os.unlink(dummy_audio.name)

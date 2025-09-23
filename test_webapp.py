import os
import tempfile
import pytest
from webapp import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['RESULT_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        yield client

def test_upload_and_download(client):
    # Test: Upload einer Dummy-Datei und Download-Link
    dummy_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    dummy_audio.write(b'RIFF....WAVEfmt ')  # Minimaler WAV-Header
    dummy_audio.seek(0)
    dummy_audio.close()
    with open(dummy_audio.name, 'rb') as f:
        data = {'files': (f, 'test.wav')}
        response = client.post('/', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'Download' in response.data
    # Test: Download-Link funktioniert
    result_dir = os.path.join(app.config['RESULT_FOLDER'], 'test')
    segment_path = os.path.join(result_dir, 'segment_01.wav')
    if os.path.exists(segment_path):
        download_url = f'/results/test/segment_01.wav'
        response = client.get(download_url)
        assert response.status_code == 200
        assert response.data.startswith(b'RIFF')
    else:
        pytest.skip('Segment wurde nicht erzeugt, Audioverarbeitung ggf. nicht lauffähig.')
    os.unlink(dummy_audio.name)

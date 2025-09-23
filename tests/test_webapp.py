import pytest
from unittest.mock import patch, MagicMock
import os

# Import the Flask app from webapp.py
from webapp import app, allowed_file, UPLOAD_FOLDER, RESULT_FOLDER

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_files_get(client):
    """
    Test the GET request for the upload_files route.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"WhatsApp Voice Batch-Upload" in response.data

@patch('webapp.secure_filename', side_effect=lambda x: x)
@patch('webapp.os.makedirs')
@patch('webapp.convert_to_wav')
@patch('webapp.get_audio_quality')
@patch('webapp.segment_audio')
@patch('webapp.transcribe_segment')
@patch('webapp.save_results_csv')
@patch('webapp.AudioSegment')
def test_upload_files_post_single_file(mock_audio_segment, mock_save_results_csv, mock_transcribe_segment, mock_segment_audio, mock_get_audio_quality, mock_convert_to_wav, mock_makedirs, mock_secure_filename, client):
    """
    Test the POST request for the upload_files route with a single supported file.
    """
    mock_get_audio_quality.return_value = {'error': ''}
    mock_segment_audio.return_value = [{'segment_number': 1, 'start_time': 0.0, 'end_time': 1.0, 'duration': 1.0}]
    mock_transcribe_segment.return_value = "test transcript"
    mock_audio_segment.from_wav.return_value = MagicMock()

    data = {
        'files': [(BytesIO(b"dummy audio data"), 'test.mp3')]
    }
    response = client.post('/', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b"Verarbeitung abgeschlossen!" in response.data
    mock_secure_filename.assert_called_once_with('test.mp3')
    mock_makedirs.assert_called()
    mock_convert_to_wav.assert_called_once()
    mock_get_audio_quality.assert_called_once()
    mock_segment_audio.assert_called_once()
    mock_transcribe_segment.assert_called_once()
    mock_save_results_csv.assert_called_once()

@patch('webapp.send_from_directory')
def test_serve_results_file(mock_send_from_directory, client):
    """
    Test the route for serving processed audio files.
    """
    mock_send_from_directory.return_value = "file content"
    response = client.get('/results/testfile/segment_01.wav')
    assert response.status_code == 200
    mock_send_from_directory.assert_called_once_with(os.path.join(app.config['RESULT_FOLDER'], 'testfile'), 'segment_01.wav')


from io import BytesIO

def test_allowed_file():
    assert allowed_file("test.mp3") == True
    assert allowed_file("test.wav") == True
    assert allowed_file("test.txt") == False
    assert allowed_file("image.jpg") == False

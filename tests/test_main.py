import os
import pytest
from unittest.mock import patch, call, MagicMock
from main import batch_convert

@patch('main.save_results_csv')
@patch('main.transcribe_segment')
@patch('main.segment_audio')
@patch('main.get_audio_quality')
@patch('main.convert_to_wav')
@patch('main.is_supported')
@patch('os.path.isfile')
@patch('os.listdir')
@patch('os.makedirs')
@patch('os.path.exists')
@patch('main.AudioSegment.from_wav')
def test_batch_convert_success_path(mock_from_wav, mock_exists, mock_makedirs, mock_listdir, mock_isfile, mock_is_supported, mock_convert_to_wav, mock_get_audio_quality, mock_segment_audio, mock_transcribe_segment, mock_save_results_csv):
    # Arrange
    input_dir = 'input'
    output_dir = 'output'
    filename = 'test.wav'
    
    mock_exists.return_value = False
    mock_listdir.return_value = [filename]
    mock_isfile.return_value = True
    mock_is_supported.return_value = True
    mock_get_audio_quality.return_value = {'error': ''}
    mock_segment_audio.return_value = [{'segment_number': 1, 'start_time': 0, 'end_time': 1, 'duration': 1}]
    mock_transcribe_segment.return_value = 'transcript'
    mock_audio = MagicMock()
    mock_from_wav.return_value = mock_audio

    # Act
    batch_convert(input_dir, output_dir)

    # Assert
    mock_exists.assert_called_once_with(output_dir)
    mock_makedirs.assert_any_call(output_dir)
    mock_listdir.assert_called_once_with(input_dir)
    mock_isfile.assert_called_once_with(os.path.join(input_dir, filename))
    mock_is_supported.assert_called_once_with(filename)
    mock_convert_to_wav.assert_called_once()
    mock_get_audio_quality.assert_called_once()
    mock_segment_audio.assert_called_once()
    mock_transcribe_segment.assert_called_once()
    mock_save_results_csv.assert_called_once()
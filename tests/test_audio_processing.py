import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pydub import AudioSegment
from audio_processing import is_supported, convert_to_wav, get_audio_quality, segment_audio, transcribe_segment, save_results_csv

def test_is_supported():
    assert is_supported("test.wav") == True
    assert is_supported("test.mp3") == True
    assert is_supported("test.txt") == False
    assert is_supported("test.opus") == True

@patch('audio_processing.AudioSegment')
def test_convert_to_wav(mock_audio_segment):
    mock_audio = MagicMock()
    mock_audio_segment.from_file.return_value = mock_audio
    
    input_path = "dummy_input.mp3"
    output_path = "dummy_output.wav"
    
    result = convert_to_wav(input_path, output_path)
    
    mock_audio_segment.from_file.assert_called_once_with(input_path)
    mock_audio.export.assert_called_once_with(output_path, format="wav")
    assert result == output_path

@pytest.fixture
def dummy_wav_file(tmp_path):
    file_path = tmp_path / "dummy.wav"
    AudioSegment.silent(duration=1000).export(file_path, format="wav")
    return file_path

def test_get_audio_quality(dummy_wav_file):
    quality = get_audio_quality(str(dummy_wav_file))
    assert "snr" in quality
    assert "clipping" in quality
    assert "dynamik" in quality
    assert "frequenzanalyse" in quality
    assert "stille" in quality
    assert "error" in quality

@patch('whisper.load_model')
def test_transcribe_segment(mock_load_model, dummy_wav_file):
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_model.transcribe.return_value = {'text': 'hello world'}
    transcript = transcribe_segment(str(dummy_wav_file))
    assert transcript == 'hello world'

@patch('audio_processing.AudioSegment.from_wav')
@patch('pydub.silence.split_on_silence')
def test_segment_audio(mock_split, mock_from_wav, dummy_wav_file):
    mock_audio = MagicMock()
    mock_from_wav.return_value = mock_audio
    chunks = [AudioSegment.silent(duration=1000), AudioSegment.silent(duration=2000)]
    mock_split.return_value = chunks
    segments = segment_audio(str(dummy_wav_file))
    assert len(segments) == 2
    assert segments[0]['duration'] == 1.0
    assert segments[1]['duration'] == 2.0

@patch('builtins.open')
@patch('csv.DictWriter')
def test_save_results_csv(mock_csv_writer, mock_open):
    segments_info = [{'test': 'data'}]
    save_results_csv('output', 'test', segments_info)
    mock_open.assert_called_once_with(os.path.join('output', 'test_results.csv'), mode='w', newline='', encoding='utf-8')
    mock_csv_writer.assert_called_once()
    mock_csv_writer.return_value.writeheader.assert_called_once()
    mock_csv_writer.return_value.writerow.assert_called_once_with(segments_info[0])
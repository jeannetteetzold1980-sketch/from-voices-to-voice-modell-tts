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

@patch('audio_processing.librosa.load')
def test_get_audio_quality_librosa_load_error(mock_librosa_load, dummy_wav_file):
    mock_librosa_load.side_effect = Exception("Test load error")
    quality = get_audio_quality(str(dummy_wav_file))
    assert "Fehler beim Laden der Audiodatei: Test load error" in quality['error']

@patch('audio_processing.librosa.load')
@patch('audio_processing.np.mean')
@patch('audio_processing.np.var')
def test_get_audio_quality_low_snr_and_silent_audio(mock_np_var, mock_np_mean, mock_librosa_load, dummy_wav_file):
    # Simulate a silent audio file
    mock_librosa_load.return_value = (np.zeros(44100), 22050) # Longer silent audio
    mock_np_mean.return_value = 0.0
    mock_np_var.return_value = 0.0 # This will cause noise_power to be 0

    quality = get_audio_quality(str(dummy_wav_file))
    assert "SNR nicht berechenbar" in quality['error']
    assert "Dynamik nicht berechenbar" in quality['error']
    assert quality['snr'] is None
    assert quality['dynamik'] is None

@patch('audio_processing.librosa.load')
def test_get_audio_quality_low_snr(mock_librosa_load, dummy_wav_file):
    # Simulate audio with low SNR (e.g., signal_power / noise_power < 1)
    y = np.random.rand(44100) * 0.1 # Low signal
    noise = np.random.rand(44100) * 0.5 # High noise
    mock_librosa_load.return_value = (y + noise, 22050)
    quality = get_audio_quality(str(dummy_wav_file))
    assert "SNR zu niedrig" in quality['error']

@patch('audio_processing.librosa.load')
def test_get_audio_quality_clipping(mock_librosa_load, dummy_wav_file):
    # Simulate audio with clipping
    y = np.array([0.5, 0.99, 1.0, 0.8]) # Max value >= 0.99
    mock_librosa_load.return_value = (y, 22050)
    quality = get_audio_quality(str(dummy_wav_file))
    assert quality['clipping'] == True
    assert "Clipping erkannt" in quality['error']

@patch('audio_processing.librosa.load')
def test_get_audio_quality_low_dynamic_range(mock_librosa_load, dummy_wav_file):
    # Simulate audio with low dynamic range (e.g., highly compressed)
    y = np.linspace(0.1, 0.2, 44100) # Small difference between min and max
    mock_librosa_load.return_value = (y, 22050)
    quality = get_audio_quality(str(dummy_wav_file))
    assert "Dynamikbereich kritisch" in quality['error']

@patch('audio_processing.librosa.load')
@patch('audio_processing.librosa.stft')
@patch('audio_processing.librosa.fft_frequencies')
def test_get_audio_quality_frequency_issues(mock_fft_frequencies, mock_stft, mock_librosa_load, dummy_wav_file):
    # Simulate audio with frequency losses (e.g., only low frequencies)
    sr = 44100
    y = np.sin(2 * np.pi * 100 * np.arange(sr * 5) / sr) # 5 seconds of 100 Hz sine wave
    mock_librosa_load.return_value = (y, sr)
    
    # Mock STFT to return a spectrum where high frequencies have very low power
    n_fft = 2048 # Default for librosa.stft
    freqs_mock = np.linspace(0, sr / 2, n_fft // 2 + 1)
    mock_fft_frequencies.return_value = freqs_mock

    # Create a mock STFT output where high frequencies are near zero
    S_mock = np.zeros((n_fft // 2 + 1, 100)) # 100 frames
    # Set low frequencies to have some power
    S_mock[freqs_mock < 300, :] = 1.0
    mock_stft.return_value = S_mock
    
    quality = get_audio_quality(str(dummy_wav_file))
    assert "Frequenzverluste/-verzerrungen" in quality['error']

@patch('audio_processing.librosa.load')
def test_get_audio_quality_high_silence_ratio(mock_librosa_load, dummy_wav_file):
    # Simulate audio with high silence ratio
    y = np.zeros(44100) # 1 second of silence
    y[100:110] = 0.5 # A small burst of sound
    mock_librosa_load.return_value = (y, 22050)
    quality = get_audio_quality(str(dummy_wav_file))
    assert quality['stille'] == True
    assert "Stille erkannt" in quality['error']

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
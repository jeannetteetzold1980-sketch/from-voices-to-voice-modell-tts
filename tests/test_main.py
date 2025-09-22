
import os
import pytest
from unittest.mock import patch, call
from main import batch_convert

@patch('main.convert_to_wav')
@patch('main.is_supported')
@patch('os.path.isfile')
@patch('os.listdir')
@patch('os.makedirs')
def test_batch_convert_output_dir_does_not_exist(mock_makedirs, mock_listdir, mock_isfile, mock_is_supported, mock_convert_to_wav):
    # Setup mocks
    mock_listdir.return_value = ['file1.wav', 'file2.txt', 'file3.mp3']
    mock_isfile.return_value = True
    mock_is_supported.side_effect = lambda x: x.endswith('.wav') or x.endswith('.mp3')
    
    input_dir = "input"
    output_dir = "output"

    # Run the function
    batch_convert(input_dir, output_dir)

    # Assertions
    mock_makedirs.assert_called_once_with(output_dir)
    
    assert mock_listdir.call_count == 1
    assert mock_isfile.call_count == 3
    assert mock_is_supported.call_count == 3
    
    expected_convert_calls = [
        call(os.path.join(input_dir, 'file1.wav'), os.path.join(output_dir, 'file1.wav')),
        call(os.path.join(input_dir, 'file3.mp3'), os.path.join(output_dir, 'file3.wav'))
    ]
    mock_convert_to_wav.assert_has_calls(expected_convert_calls, any_order=True)

@patch('main.convert_to_wav')
@patch('main.is_supported')
@patch('os.path.isfile')
@patch('os.listdir')
@patch('os.path.exists', return_value=True)
@patch('os.makedirs')
def test_batch_convert_output_dir_exists(mock_makedirs, mock_path_exists, mock_listdir, mock_isfile, mock_is_supported, mock_convert_to_wav):
    # Setup mocks
    mock_listdir.return_value = ['file1.wav']
    mock_isfile.return_value = True
    mock_is_supported.return_value = True

    input_dir = "input"
    output_dir = "output"

    # Run the function
    batch_convert(input_dir, output_dir)

    # Assertions
    mock_makedirs.assert_not_called()
    mock_convert_to_wav.assert_called_once()

@patch('builtins.print')
@patch('main.convert_to_wav')
@patch('main.is_supported', return_value=False)
@patch('os.path.isfile', return_value=True)
@patch('os.listdir', return_value=['file.txt'])
@patch('os.makedirs')
def test_batch_convert_skip_unsupported_file(mock_makedirs, mock_listdir, mock_isfile, mock_is_supported, mock_convert_to_wav, mock_print):
    input_dir = "input"
    output_dir = "output"

    batch_convert(input_dir, output_dir)

    mock_convert_to_wav.assert_not_called()
    mock_print.assert_any_call('Übersprungen (nicht unterstützt oder kein File): file.txt')

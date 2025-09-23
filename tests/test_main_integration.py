import pytest
from unittest.mock import patch
import sys

from main import main

def test_main_no_arguments(capsys):
    """
    Test that main exits with an error message when no arguments are provided.
    """
    with patch('sys.argv', ['main.py']):
        with pytest.raises(SystemExit) as excinfo:
            main(sys.argv)
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "Nutzung: python main.py <input_dir> <output_dir>" in captured.out

def test_main_with_arguments_and_batch_convert_mocked():
    """
    Test that main calls batch_convert with the correct arguments when provided.
    """
    mock_input_dir = "/fake/input"
    mock_output_dir = "/fake/output"
    with patch('sys.argv', ['main.py', mock_input_dir, mock_output_dir]):
        with patch('main.batch_convert') as mock_batch_convert:
            main(sys.argv)
            mock_batch_convert.assert_called_once_with(mock_input_dir, mock_output_dir)

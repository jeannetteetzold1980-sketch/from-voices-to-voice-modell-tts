
import pytest
from unittest.mock import patch
from io import StringIO
import sys

from main import main

@patch('main.batch_convert')
def test_main_with_args(mock_batch_convert):
    argv = ['main.py', 'input_dir', 'output_dir']
    
    # Redirect stdout to capture print statements
    captured_output = StringIO()
    sys.stdout = captured_output

    main(argv)

    # Restore stdout
    sys.stdout = sys.__stdout__

    mock_batch_convert.assert_called_once_with('input_dir', 'output_dir')
    assert "WhatsApp Voice Processing gestartet." in captured_output.getvalue()

@patch('sys.exit')
def test_main_without_args(mock_sys_exit):
    argv = ['main.py']

    # Redirect stdout to capture print statements
    captured_output = StringIO()
    sys.stdout = captured_output

    with pytest.raises(SystemExit) as e:
        main(argv)

    # Restore stdout
    sys.stdout = sys.__stdout__

    assert e.type == SystemExit
    assert e.value.code == 1
    mock_sys_exit.assert_called_once_with(1)
    assert "Nutzung: python main.py <input_dir> <output_dir>" in captured_output.getvalue()

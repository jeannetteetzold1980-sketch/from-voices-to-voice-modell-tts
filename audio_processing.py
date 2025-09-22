import os
import ffmpeg
from pydub import AudioSegment

SUPPORTED_FORMATS = ['.opus', '.mp3', '.wav', '.m4a', '.aac', '.flac']


def is_supported(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_FORMATS


def convert_to_wav(input_path, output_path):
    """
    Konvertiert eine Audiodatei ins WAV-Format.
    """
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    return output_path


def get_audio_quality(wav_path):
    """
    Platzhalter für Qualitätsprüfung (SNR, Clipping, Dynamik, etc.)
    """
    # TODO: Implementierung der Audioanalyse
    return {
        'snr': None,
        'clipping': False,
        'dynamik': None,
        'error': ''
    }

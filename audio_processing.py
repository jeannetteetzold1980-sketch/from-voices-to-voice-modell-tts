
import os
import ffmpeg
from pydub import AudioSegment
import numpy as np
import librosa
import scipy

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
    # --- Frequenzanalyse ---
    try:
        # Berechne das Frequenzspektrum
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        spectrum = np.mean(S, axis=1)
        # Prüfe auf auffällige Frequenzverluste (z.B. < 300 Hz oder > 4000 Hz)
        low_freq_power = np.mean(spectrum[freqs < 300]) if np.any(freqs < 300) else 0
        high_freq_power = np.mean(spectrum[freqs > 4000]) if np.any(freqs > 4000) else 0
        result['frequenzanalyse'] = {
            'low_freq_power': round(float(low_freq_power), 2),
            'high_freq_power': round(float(high_freq_power), 2)
        }
        if low_freq_power < 0.01 or high_freq_power < 0.01:
            result['error'] += 'Frequenzverluste/-verzerrungen; '
    except Exception as e:
        result['error'] += f'Frequenzanalyse-Fehler: {e}; '

    # --- Stille-Erkennung ---
    try:
        # Stille: Anteil der Samples mit sehr geringer Amplitude (<0.001)
        silence_ratio = np.sum(np.abs(y) < 0.001) / len(y)
        result['stille'] = silence_ratio > 0.5
        if result['stille']:
            result['error'] += 'Stille erkannt; '
    except Exception as e:
        result['error'] += f'Stille-Fehler: {e}; '
    """
    Platzhalter für Qualitätsprüfung (SNR, Clipping, Dynamik, etc.)
    """
    # Beispielhafte Struktur für die Qualitätsprüfung
    result = {
        'snr': None,
        'clipping': False,
        'dynamik': None,
        'frequenzanalyse': None,
        'stille': False,
        'error': ''
    }

    # --- SNR-Berechnung ---
    try:
        y, sr = librosa.load(wav_path, sr=None)
        # SNR: Verhältnis von Signal zu Rauschen (grob: mittlere Leistung / Varianz)
        signal_power = np.mean(y ** 2)
        noise_power = np.var(y - np.mean(y))
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
            result['snr'] = round(snr, 2)
            if snr < 20:
                result['error'] += 'SNR zu niedrig; '
        else:
            result['snr'] = None
            result['error'] += 'SNR nicht berechenbar; '
    except Exception as e:
        result['error'] += f'SNR-Fehler: {e}; '

    # --- Clipping-Erkennung ---
    try:
        max_val = np.max(np.abs(y))
        # WAV: typischer Maximalwert ist 1.0 (float)
        result['clipping'] = max_val >= 0.99
        if result['clipping']:
            result['error'] += 'Clipping erkannt; '
    except Exception as e:
        result['error'] += f'Clipping-Fehler: {e}; '

    # --- Dynamikbereich ---
    try:
        # Dynamikbereich: Differenz zwischen lautestem und leisestem Wert (in dB)
        min_val = np.min(np.abs(y[np.nonzero(y)])) if np.any(y) else 0.0
        if min_val > 0:
            dynamic_range = 20 * np.log10(max_val / min_val)
            result['dynamik'] = round(dynamic_range, 2)
            if dynamic_range < 10:
                result['error'] += 'Dynamikbereich kritisch; '
        else:
            result['dynamik'] = None
            result['error'] += 'Dynamik nicht berechenbar; '
    except Exception as e:
        result['error'] += f'Dynamik-Fehler: {e}; '
    #     result['error'] += 'Stille erkannt; '

    return result

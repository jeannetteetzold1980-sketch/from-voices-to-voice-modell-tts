import os
import sys


from audio_processing import is_supported, convert_to_wav

def batch_convert(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if os.path.isfile(input_path) and is_supported(filename):
            print(f"Verarbeite: {filename}")
            output_filename = os.path.splitext(filename)[0] + ".wav"
            output_path = os.path.join(output_dir, output_filename)
            try:
                convert_to_wav(input_path, output_path)
                print(f"Konvertiert: {output_filename}")
            except Exception as e:
                print(f"Fehler bei {filename}: {e}")
        else:
            print(f"Übersprungen (nicht unterstützt oder kein File): {filename}")

if __name__ == "__main__":
    print("WhatsApp Voice Processing gestartet.")
    if len(sys.argv) < 3:
        print("Nutzung: python main.py <input_dir> <output_dir>")
        sys.exit(1)
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    batch_convert(input_dir, output_dir)

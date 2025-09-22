Developer: Developer: Developer: # Schritt-für-Schritt-Anleitung zur Entwicklung einer kostenfreien Software zur Verarbeitung von WhatsApp-Voice-Nachrichten

Diese Anleitung ist so gestaltet, dass auch Laien sie umsetzen können. Jeder Schritt ist klar und verständlich formuliert.

## 1. Konzept-Checkliste der Hauptaufgaben
1. Festlegen, welche Audioformate unterstützt werden sollen (.opus, .mp3, .wav, .m4a, .aac, .flac)
2. Planung der Benutzeroberfläche (UI), die übersichtlich und professionell gestaltet sein soll
3. Bestimmen der einzelnen Verarbeitungsschritte: Qualitätsprüfung, Segmentierung und Transkription
4. Festlegen, wie die Ausgaben für jede Datei strukturiert und gespeichert werden sollen (Ordner, Benennung, CSV-Format)
5. Überlegen, wie Fehler eindeutig dokumentiert werden (z.B. Spalte `error` in der CSV)
6. Anlegen einer Batch-Upload-Funktion für die gleichzeitige Verarbeitung mehrerer Dateien
7. Prüfen und Validieren der Zwischenergebnisse nach jedem Hauptschritt

## 2. Schritt-für-Schritt Umsetzung

### Schritt 1: Voraussetzungen schaffen
- Installiere eine geeignete Entwicklungsumgebung (z.B. Python, JavaScript oder eine andere Sprache deiner Wahl)
- Sorge für die benötigten Bibliotheken (z.B. für Audioverarbeitung `pydub`, `ffmpeg`, für Transkription `whisper`/Speech-to-Text-Dienste oder ähnliche)

### Schritt 2: Benutzeroberfläche planen und erstellen
- Entwerfe eine übersichtliche Oberfläche, auf der mehrere Dateien per „Dateien auswählen“-Button hochgeladen werden können
- Zeige den Fortschritt der Verarbeitung für jede Datei sichtbar an
- Benutze einfache Designs und klare Beschriftungen für alle Funktionen

### Schritt 3: Unterstützte Audioformate festlegen und konvertieren
- Akzeptiere alle genannten Formate beim Upload: .opus, .mp3, .wav, .m4a, .aac, .flac
- Konvertiere alle Dateien nach dem Upload automatisch ins .wav-Format (dafür ein Konvertierungstool wie `ffmpeg` benutzen)

### Schritt 4: Erweiterte Qualitätsprüfung implementieren
- Miss die Qualität jeder Datei, z.B. das Signal-Rausch-Verhältnis (SNR)
- Führe Clipping-Erkennung durch, um übersteuertes Audio zu identifizieren, und dokumentiere dies gegebenenfalls in der `error`-Spalte
- Führe eine spektrale Qualitätsbewertung (Frequenzanalyse) durch, um auffällige Frequenzverluste oder -verzerrungen zu erkennen
- Ermittle den Dynamikbereich der Aufnahme und prüfe auf unnatürlich geringe Dynamik (z.B. Werte < 10dB als kritisch markieren)
- Führe eine Stille-Detektion durch, um leere oder nahezu leere Segmente zu erkennen; diese sollten ebenfalls entsprechend dokumentiert werden
- Lege Schwellenwerte an (mind. 20dB für Transkription, 30dB für Voice Cloning)
- Wenn die Datei die Mindestqualität nicht erfüllt oder einer der erweiterten Qualitätsprüfungen negativ ausfällt, dokumentiere dies in der `error`-Spalte und brich die Verarbeitung ab

### Schritt 5: Audio segmentieren
- Teile jede Datei anhand von Sprachpausen in Segmente
- Speichere für jedes Segment: Startzeit, Endzeit, Dauer, Segmentnummer

### Schritt 6: Jedes Segment transkribieren
- Transkribiere automatisch jedes Segment
- Schreibe den transkribierten Text und die Zeitstempel in das endgültige Transkript

### Schritt 7: Ergebnisse organisieren und speichern
- Lege für jede Eingabedatei einen separaten Ordner an, benannt nach dem Dateinamen ohne Endung
- Speichere in jedem Ordner:
  - Die einzelnen Audiosegmente als `segment_01.wav`, `segment_02.wav`, …
  - Eine CSV-Datei mit allen Informationen für jedes Segment:
    - original_filename, segment_number, audio_file, transcript, start_time, end_time, duration, error (siehe unten Beispiel)

#### Beispielhafter CSV-Kopf:
```csv
original_filename,segment_number,audio_file,transcript,start_time,end_time,duration,error
voice_001,1,segment_01.wav,"Dies ist ein Beispiel.",0.0,3.2,3.2,
voice_001,2,segment_02.wav,"Noch ein Segment.",3.2,7.1,3.9,
```

- Prüfe, dass alle Dateien und Daten korrekt angelegt und die Benennungen konsistent sind
- Alle Fehler während der Verarbeitung werden in der `error`-Spalte dokumentiert (sonst bleibt sie leer)

### Schritt 8: Dokumentation und finale Validierung
- Überprüfe das Ergebnis nach jedem Hauptschritt (Audio, Segmentierung, Transkript) und halte eventuelle Fehler/Abweichungen schriftlich fest
- Passe bei geringen Fehlern die Ausgabe nach Möglichkeit automatisch an

### Schritt 9: Ausgabe für den Nutzer
- Packe alle Ergebnis-Ordner als .zip-Datei zusammen für den Download
- Weisen den Nutzer in der Oberfläche auf Fehler und auf den Speicherort der Ergebnisdateien hin

### Schritt 10: Docker-Container zur plattformunabhängigen Ausführung erstellen
- Erstelle ein Dockerfile, das alle notwendigen Abhängigkeiten (z.B. Python, ffmpeg, benötigte Python-Bibliotheken) installiert
- Füge alle notwendige Quellcodes, Modelle und Konfigurationsdateien in das Image ein
- Stelle sicher, dass das Starten der Anwendung über einen einheitlichen Befehl (z.B. `CMD ["python", "main.py"]`) möglich ist
- Beschreibe im README, wie das Image gebaut (`docker build -t whatsapp-voice-app .`) und gestartet (`docker run -v /lokaler/pfad:/app/results whatsapp-voice-app`) wird
- Damit gewährleisten Sie, dass die Software plattformunabhängig auf jedem System mit Docker lauffähig ist

**Hinweis zum Whisper-Modell:**
Das Whisper-Modell ("base") wird beim Docker-Build automatisch heruntergeladen und in das Image integriert. Dadurch ist beim ersten Start des Containers keine Internetverbindung mehr nötig und die Transkription funktioniert direkt offline.

**Docker-Build und Nutzung:**
1. Image bauen:
  ```bash
  docker build -t whatsapp-voice-app .
  ```
2. Container starten (mit Ergebnis-Ordner als Volume):
  ```bash
  docker run -v /lokaler/pfad:/app/results whatsapp-voice-app /app/input /app/results
  ```
  `/app/input` sollte die Audiodateien enthalten, `/app/results` ist der Ausgabeordner.

Mit dieser Anleitung sollten auch technisch wenig versierte Anwender die beschriebene Software Schritt für Schritt umsetzen können.

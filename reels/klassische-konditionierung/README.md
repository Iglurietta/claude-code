# Reel: Klassische Konditionierung (Motion Graphics, Erklärstil)

Hochformat 1080×1920, 30 fps, 54 s, mit Musikbett und Sound-Effekten.

| Zeit | Szene |
|---|---|
| 0–5,5 s | Hook: „Warum läuft dir das Wasser im Mund zusammen … wenn du nur die Chipstüte hörst?“ |
| 5,5–10,5 s | Titel: Klassische Konditionierung · Iwan Pawlow |
| 10,5–20 s | Schritt 1 – Vor dem Lernen: Futter (UCS) → Speichel (UCR), Glocke (NS) → nichts |
| 20–29,5 s | Schritt 2 – Während des Lernens: Glocke + Futter, Wiederholungszähler |
| 29,5–37 s | Schritt 3 – Nach dem Lernen: Glocke (CS) → Speichel (CR) |
| 37–43 s | Kurz gesagt: Formeln |
| 43–49,5 s | Alltagsbeispiele: Handy-Ton, Chipstüte, Song von früher |
| 49,5–54 s | Abschluss + Call-to-Action |

## Dateien

- `reel.html` – die ganze Animation. Im Browser öffnen = Live-Vorschau; `reel.html?t=25` springt zu Sekunde 25.
  Texte, Farben (`:root`) und Einblendzeiten (`data-in`) lassen sich direkt dort ändern.
- `render.js` – rendert jedes Bild mit Playwright und baut daraus ein stummes MP4.
- `audio.py` – erzeugt die Tonspur synchron zu den Animations-Events.
- `out/klassische-konditionierung.mp4` – das fertige Reel.

## Neu rendern

```bash
node render.js            # -> out/video_noaudio.mp4 + out/sfx.json
python3 audio.py          # -> out/audio.wav
ffmpeg -y -i out/video_noaudio.mp4 -i out/audio.wav -c:v copy -c:a aac -b:a 192k -shortest out/klassische-konditionierung.mp4
```

Hinweis: Das Reel hat keine Sprecherstimme. Für Instagram/TikTok kannst du in der App
ein Voiceover aufnehmen oder den Text-to-Speech-Effekt nutzen; die Einblendzeiten oben helfen beim Timing.

# The Empathy Engine: Giving AI a Human Voice

## Overview

The **Empathy Engine** is a small Python service that turns plain text into emotionally aware speech.  
It detects the sentiment of the input text and dynamically modulates the voice characteristics of the
Text-to-Speech (TTS) output to better match the underlying emotion.

This project is designed for the Darwix AI assignment and demonstrates:

- **Emotion Detection**: Positive, Negative, and Neutral classification with intensity scaling.
- **Vocal Parameter Modulation**: Programmatic control of **rate** and **volume** based on emotion.
- **Emotion-to-Voice Mapping**: A clear mapping from sentiment scores to TTS parameters.
- **Audio Output**: Speech is rendered to a playable `.wav` file.
- **Interfaces**:
  - A **CLI** tool for quick testing.
  - A minimal **web UI** (FastAPI) with a text area and embedded audio playback.

## Architecture

- `empathy_engine.py`
  - `EmotionDetector`: Uses VADER sentiment analysis to classify input text as **positive**, **negative**, or **neutral** and computes an **intensity** score in \[0, 1\].
  - `EmpathyEngine`: Core orchestration class. It:
    - Analyzes emotion.
    - Maps emotion + intensity to a `VoiceProfile` (rate, volume).
    - Configures a local `pyttsx3` TTS engine and saves synthesized speech to disk.

- `cli.py`
  - Simple command-line interface that accepts text and outputs a `.wav` file while printing out the detected emotion and applied voice parameters.

- `web_app.py`
  - A lightweight **FastAPI** app that:
    - Serves a single-page HTML UI.
    - Accepts text via an HTML form.
    - Uses `EmpathyEngine` to generate audio.
    - Exposes an `/audio` endpoint that the page uses for playback.

## Emotion Detection & Mapping Logic

### 1. Emotion Detection

The engine uses **VADER** (`vaderSentiment`) to compute sentiment scores:

- VADER returns a **compound score** in \[-1.0, 1.0\].
- Classification thresholds:
  - `compound >= 0.2` → **POSITIVE**
  - `compound <= -0.2` → **NEGATIVE**
  - otherwise → **NEUTRAL**
- **Intensity** is defined as `abs(compound)` (clamped to \[0, 1\]), which captures how strong the emotion is.

This yields:

- At least **three primary emotions**: Positive, Negative, Neutral.
- **Intensity scaling** for more nuanced modulation (e.g., mildly positive vs. extremely positive).

### 2. Emotion-to-Voice Mapping

The `EmpathyEngine` starts from the default `pyttsx3` baseline:

- `base_rate` – default speech rate (words per minute).
- `base_volume` – default volume (0.0–1.0).

Then it applies the following mapping:

- **POSITIVE**
  - Rate: up to **+25% faster** as intensity approaches 1.0.
  - Volume: up to **+0.15** louder (capped at 1.0).
  - Effect: more energetic and enthusiastic for strongly positive text.

- **NEGATIVE**
  - Rate: up to **25% slower** as intensity grows.
  - Volume: up to **0.2** quieter (with a floor around 0.3 to stay audible).
  - Effect: slower and softer tone for strongly negative/frustrated content.

- **NEUTRAL**
  - Rate and volume remain at the baseline values.

This mapping provides:

- At least **two distinct vocal parameters** being modulated (**rate** and **volume**).
- **Intensity scaling** that makes, for example, “This is good” sound less excited than “This is the best news ever!”.

## Setup Instructions

### 1. Create and Activate a Virtual Environment (Recommended)

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows (PowerShell / CMD)
# source .venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `pyttsx3` – offline TTS engine.
- `vaderSentiment` – sentiment analysis for emotion detection.
- `fastapi`, `uvicorn` – for the optional web UI.

> Note: On some systems, `pyttsx3` may require additional audio libraries or voices to be installed.  
> On Windows, it generally works out of the box using the system speech APIs.

## Usage

### 1. CLI: Quick Test

Run the CLI tool from the project root:

```bash
python cli.py "I am absolutely thrilled with this result!"
```

Or interactively:

```bash
python cli.py
# You will be prompted to enter the text.
```

By default, the output file is:

- `output/empathy_output.wav`

You can choose a different path:

```bash
python cli.py "This is the best news ever!" -o output/happy.wav
```

The CLI prints:

- Detected **emotion** (positive / negative / neutral).
- **Intensity** and raw VADER compound score.
- Applied **rate** and **volume**.
- The absolute path to the generated audio file.

### 2. Web UI (FastAPI)

Start the FastAPI server:

```bash
uvicorn web_app:app --reload
```

Then open your browser at:

- `http://127.0.0.1:8000/`

From there:

- Type your message into the text area.
- Click **“Generate Emotional Voice”**.
- The page will:
  - Display the detected emotion and intensity.
  - Show the rate and volume used.
  - Embed an HTML audio player to listen to the generated `.wav` output.

The audio file is served from the `/audio` endpoint and stored on disk at:

- `output/empathy_output.wav`

## Design Choices & Notes

- **Python & Local TTS**:
  - Chosen to meet the “offline-friendly” suggestion and avoid external API dependencies.
  - `pyttsx3` provides programmatic control over rate and volume and can save to audio files.

- **VADER for Emotion**:
  - Lightweight, well-suited to short social-style messages.
  - No external APIs or large model downloads needed.
  - Compound score directly maps to an interpretable \[-1, 1\] sentiment scale.

- **Intensity Scaling**:
  - Intensity is derived from `abs(compound)` and used as a multiplier for rate/volume deltas.
  - This enables more nuanced control: subtle vs. strong emotions.

- **Extensibility**:
  - You can plug in more granular emotion classifiers (e.g., Hugging Face emotion models) by replacing `EmotionDetector`.
  - You can also extend `VoiceProfile` and `EmpathyEngine` to control pitch, pauses, or even external TTS APIs for higher fidelity voices.

## How to Turn This Into a GitHub Submission

1. Initialize a git repo in the project directory:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Empathy Engine"
   ```
2. Create a new repository on GitHub.
3. Add the remote and push:
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

You can then submit your GitHub repository URL as required by the assignment.


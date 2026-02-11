# The Empathy Engine: Giving AI a Human Voice

## Overview

The **Empathy Engine** is a service that dynamically modulates Text-to-Speech (TTS) vocal characteristics based on the detected emotion of the input text. It bridges the gap between robotic TTS and expressive human communication.

## Features

- **Emotion Detection**: Analyzes text to determine:
  - Base: Positive, Negative, Neutral.
  - Granular: Surprised, Inquisitive, Concerned.
- **Dynamic Voice Modulation**: Adjusts speech Rate and Volume to create distinct emotional personas.
  - **Positive**: Fast, Energetic.
  - **Negative**: Very Slow, Soft.
  - **Surprised**: Rapid, Loud.
  - **Concerned**: Slow, Soft, Worried.
  - **Inquisitive**: Slightly faster, engaging.
- **Smart Voice Selection**: Automatically attempts to select a female voice (e.g., "Zira" on Windows) for a more empathetic tone.
- **Web Interface**: A clean, modern UI to test the engine with granular feedback.
- **CLI**: A command-line tool for quick testing.

## Prerequisites

- Python 3.8+
- Windows (Recommended for pyttsx3 default drivers & "Zira" voice), macOS, or Linux.

## Setup

### 1. Clone/Navigate to the directory:

```bash
cd EmpathyEngine_DarwixAi
```

### 2. Create and Activate Virtual Environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies:

```bash
pip install -r requirements.txt
```
This installs:

pyttsx3 – offline TTS engine.
vaderSentiment – sentiment analysis for emotion detection.
fastapi, uvicorn – for the optional web UI.

## Usage

### Web Interface (Recommended)

1. CLI: Quick Test
Run the CLI tool from the project root:

python cli.py "I am absolutely thrilled with this result!"
Or interactively:

python cli.py
# You will be prompted to enter the text.
By default, the output file is:

output/empathy_output.wav
You can choose a different path:

python cli.py "This is the best news ever!" -o output/happy.wav
The CLI prints:

Detected emotion (positive / negative / neutral).
Intensity and raw VADER compound score.
Applied rate and volume.

2. Web UI (FastAPI)
Start the FastAPI server:

uvicorn web_app:app --reload
Then open your browser at:

http://127.0.0.1:8000/
From there:

Type your message into the text area.
Click “Generate Emotional Voice”.
The page will:
Display the detected emotion and intensity.
Show the rate and volume used.
Embed an HTML audio player to listen to the generated .wav output.
The audio file is served from the /audio endpoint and stored on disk at:

output/empathy_output.wav

## Design Choices

- **Emotion Analysis**: Combined vaderSentiment (for base polarity) with Heuristics (punctuation, keywords) to detect nuanced states like Surprise and Concern.
- **TTS Engine**: pyttsx3 was chosen for offline capabilities. Implemented a Rate/Volume Modulation system instead of unstable SSML tags to ensure reliable playback on all systems.
- **Modulation Logic**:
  - **Rate**: Effectively conveys energy (fast) or sadness/concern (slow).
  - **Volume**: Adds emphasis (loud) or intimacy/worry (soft).

## Troubleshooting

- **No Audio**: Ensure your system volume is up.
- **Module Not Found**: Ensure you are running commands from the empathy_engine directory and the virtual environment is active.

## Examples

Try these phrases to get started:

- "I’m honestly feeling very anxious about how this is going to turn out."
- "Seriously? I didn’t expect that at all!"
- "Oh my god! That is amazing!"


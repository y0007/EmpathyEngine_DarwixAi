from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse

from empathy_engine import EmpathyEngine, get_default_output_path


app = FastAPI(title="The Empathy Engine")
engine = EmpathyEngine()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>The Empathy Engine</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; background: #0f172a; color: #e5e7eb; }
    .card { max-width: 720px; margin: 0 auto; background: #020617; border-radius: 1rem; padding: 2rem 2.5rem; box-shadow: 0 24px 60px rgba(15,23,42,0.7); border: 1px solid #1f2937; }
    h1 { font-size: 2rem; margin-bottom: 0.5rem; color: #f9fafb; }
    p { color: #9ca3af; }
    textarea { width: 100%; min-height: 140px; margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 0.75rem; border: 1px solid #374151; background: #020617; color: #f9fafb; font-size: 0.95rem; resize: vertical; box-sizing: border-box; }
    textarea:focus { outline: none; border-color: #60a5fa; box-shadow: 0 0 0 1px #1d4ed8; }
    button { margin-top: 1rem; padding: 0.75rem 1.5rem; border-radius: 999px; border: none; background: linear-gradient(135deg, #4f46e5, #ec4899); color: white; font-weight: 600; cursor: pointer; font-size: 0.95rem; box-shadow: 0 10px 30px rgba(79,70,229,0.6); }
    button:hover { filter: brightness(1.05); transform: translateY(-1px); }
    button:active { transform: translateY(0); box-shadow: 0 5px 18px rgba(79,70,229,0.5); }
    .meta { margin-top: 1.5rem; font-size: 0.85rem; color: #9ca3af; }
    .pill { display: inline-flex; align-items: center; padding: 0.15rem 0.7rem; border-radius: 999px; font-size: 0.75rem; margin-right: 0.4rem; background: rgba(55,65,81,0.6); color: #e5e7eb; }
    audio { margin-top: 1rem; width: 100%; }
    .badge { font-size: 0.7rem; text-transform: uppercase; letter-spacing: .1em; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">Prototype</div>
    <h1>The Empathy Engine</h1>
    <p>Type a message and hear how the AI adapts its voice based on the detected emotion.</p>
    <form method="post">
      <textarea name="text" placeholder="Try: I am absolutely thrilled with this result!">{{ text }}</textarea>
      <button type="submit">Generate Emotional Voice</button>
    </form>

    {% if audio_url %}
      <div class="meta">
        <div><span class="pill">Emotion: {{ emotion }}</span>
             <span class="pill">Intensity: {{ intensity }}</span></div>
        <div>Rate: {{ rate }} • Volume: {{ volume }}</div>
      </div>
      <audio controls>
        <source src="{{ audio_url }}" type="audio/wav" />
        Your browser does not support the audio element.
      </audio>
    {% endif %}
  </div>
</body>
</html>
"""


def render_html(
    text: str = "",
    audio_url: str | None = None,
    emotion: str | None = None,
    intensity: float | None = None,
    rate: int | None = None,
    volume: float | None = None,
) -> HTMLResponse:
    # Very small, manual string "templating" to avoid bringing in Jinja.
    html = HTML_TEMPLATE
    replacements = {
        "{{ text }}": (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
        "{{ audio_url }}": audio_url or "",
        "{{ emotion }}": emotion or "",
        "{{ intensity }}": f"{intensity:.2f}" if intensity is not None else "",
        "{{ rate }}": str(rate) if rate is not None else "",
        "{{ volume }}": f"{volume:.2f}" if volume is not None else "",
    }
    for key, value in replacements.items():
        html = html.replace(key, value)

    if audio_url:
        html = html.replace("{% if audio_url %}", "")
        html = html.replace("{% endif %}", "")
    else:
        # Remove the conditional block entirely when no audio is available.
        start = html.find("{% if audio_url %}")
        end = html.find("{% endif %}") + len("{% endif %}")
        if start != -1 and end != -1:
            html = html[:start] + html[end:]

    return HTMLResponse(content=html)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return render_html()


@app.post("/", response_class=HTMLResponse)
async def generate(text: str = Form(...)) -> HTMLResponse:
    output_path = get_default_output_path()
    emotion_result, voice_profile, _ = engine.synthesize_to_file(text, output_path)
    audio_url = "/audio"

    return render_html(
        text=text,
        audio_url=audio_url,
        emotion=emotion_result.emotion.value.title(),
        intensity=emotion_result.intensity,
        rate=voice_profile.rate,
        volume=voice_profile.volume,
    )


@app.get("/audio")
async def get_audio() -> FileResponse:
    path = get_default_output_path()
    if not Path(path).exists():
        # No audio yet; return 404.
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="No audio generated yet.")
    return FileResponse(path, media_type="audio/wav")


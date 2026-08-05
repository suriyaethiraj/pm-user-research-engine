from __future__ import annotations
import io
import os
import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple


# ── Audio → Text via Whisper ──────────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str, api_key: str = "") -> Tuple[str, str]:
    """
    Transcribe audio using OpenAI Whisper API.
    Falls back to a clear error message if key not set.
    Returns (transcript_text, source_label).
    """
    try:
        from openai import OpenAI
    except ImportError:
        return ("[openai package not installed — run: pip install openai]", "audio_error")

    if not api_key:
        return ("[OpenAI API key required for audio transcription]", "audio_error")

    client = OpenAI(api_key=api_key)

    suffix = Path(filename).suffix or ".mp3"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )
        return (str(result), "audio_whisper")
    except Exception as e:
        return (f"[Whisper transcription failed: {e}]", "audio_error")
    finally:
        os.unlink(tmp_path)


# ── PDF → Text ────────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages[:30]]
            return "\n".join(pages)
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages[:30])
    except Exception as e:
        return f"[PDF extraction failed: {e}]"


# ── DOCX → Text ───────────────────────────────────────────────────────────────

def extract_docx_text(docx_bytes: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(docx_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        pass
    try:
        # Fallback: mammoth
        import mammoth
        result = mammoth.extract_raw_text(io.BytesIO(docx_bytes))
        return result.value
    except Exception as e:
        return f"[DOCX extraction failed: {e}]"


# ── Transcript cleaner ────────────────────────────────────────────────────────

def clean_transcript(text: str) -> str:
    """Remove excessive whitespace and common transcript artifacts."""
    text = re.sub(r"\[inaudible\]|\[crosstalk\]|\[unclear\]", "[...]", text, flags=re.I)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def estimate_duration(text: str) -> Optional[int]:
    """Rough estimate: average speaking pace ~130 words/minute."""
    words = len(text.split())
    return round(words / 130) if words > 100 else None

import streamlit as st
from datetime import datetime   # ← keep or add this line
import re
st.set_page_config(page_title="🐎 Racing Predictor", page_icon="🐎")
st.title("🐎 Racing Predictor – Step 1")
st.write("Upload a racing document (PDF, TXT, CSV).")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is not None:
    from pypdf import PdfReader
    import io, re

    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        st.error("No readable text found in PDF – try an OCR’d or text-based PDF.")
        st.stop()

    st.success(f"Extracted {len(text)} chars from {len(reader.pages)} page(s)")

    # ultra-simple horse grab: lines that start with “H” + digit(s) + “a”
        # grab post-position + horse name from any line that has
    #   number(s)  name-with-spaces  more-numbers
    # catch EVERY horse line:  post-position  name  weight/odds/numbers
    seen = set()
    horses = []
    # ---------- helper ----------
def _looks_like_jockey(name: str) -> bool:
    """Return True if the token sequence screams ‘jockey’."""
    tokens = name.split()
    if not tokens:
        return True

    # --- 1. single token ≤ 8 and ALL-CAPS → jockey ---
    if len(tokens) == 1 and len(tokens[0]) <= 8 and tokens[0].isupper():
        return True

    # --- 2. two tokens, both ≤ 6 and Capitalised → jockey ---
    if (len(tokens) == 2 and
        len(tokens[0]) <= 6 and len(tokens[1]) <= 6 and
        tokens[0][0].isupper() and tokens[1][0].isupper()):
        return True

    # --- 3. last token is lowercase → surname ---
    if tokens[-1].islower():
        return True

    # --- 4. last token in known-surname list ---
    common_surnames = {
        "sánchez", "rodríguez", "garcía", "uzcátegui", "palencia", "petit",
        "quevedo", "gonzález", "villamizar", "capriles", "rive", "gonzalez",
        "gómez", "márquez", "alejandra"
    }
    if tokens[-1].lower() in common_surnames:
        return True

    return False
# ----------------------------

for line in text.splitlines():
        m = re.search(
            r'(?:^|\s)(1?\d)\s+([A-Z][A-Z0-9ÁÉÍÓÚÜÑáéíóúüñ\ \(\)\-]{4,}?(?:\s+[A-Z][a-z]*){0,2})(?=\s+[A-Z][a-z]+\s+[A-Z][a-z]|\s+\d)',
            line, re.I)
        if not m:
            continue

        post, name = m.groups()
        post = int(post)
        name = name.strip()

        if not (1 <= post <= 20) or name.lower() in seen:
            continue

        # ---- fast jockey reject ----
        def _looks_like_jockey(n: str) -> bool:
            tokens = n.split()
            if not tokens:
                return True
            if len(tokens) == 1 and len(tokens[0]) <= 8 and tokens[0].isupper():
                return True
            if (len(tokens) == 2 and
                len(tokens[0]) <= 6 and len(tokens[1]) <= 6 and
                tokens[0][0].isupper() and tokens[1][0].isupper()):
                return True
            if tokens[-1].islower():
                return True
            common_surnames = {
                "sánchez", "rodríguez", "garcía", "uzcátegui", "palencia", "petit",
                "quevedo", "gonzález", "villamizar", "capriles", "rive", "gonzalez",
                "gómez", "márquez", "alejandra"
            }
            if tokens[-1].lower() in common_surnames:
                return True
            return False

        if _looks_like_jockey(name):
            continue

        seen.add(name.lower())
        horses.append({"post": post, "name": name})

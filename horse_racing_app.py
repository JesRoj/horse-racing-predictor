import streamlit as st
from datetime import datetime
import re, io
from pypdf import PdfReader

st.set_page_config(page_title="🐎 Racing Predictor", page_icon="🐎")
st.title("🐎 Racing Predictor – Step 1")
st.write("Upload a racing document (PDF, TXT, CSV).")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is None:
    st.stop()                       # ← nothing to do yet

# ------------------------------------------------------------------
# 1.  ALWAYS extract text  (PDF branch shown; TXT/CSV left as exercise)
# ------------------------------------------------------------------
# ---- 5-line OCR drop-in ----
try:
    from pytesseract import image_to_string
    from pdf2image import convert_from_bytes
    images = convert_from_bytes(uploaded_file.read())
    text = "\n".join(image_to_string(img, lang='spa') for img in images)
except Exception as e:
    st.error("OCR failed → " + str(e))
    st.stop()

if not text.strip():
    st.error("No readable text found – be sure the PDF contains selectable text.")
    st.stop()

st.success(f"Extracted {len(text)} characters from PDF.")

# ------------------------------------------------------------------
# 2.  Horse parsing starts  →  text is **guaranteed** to exist
# ------------------------------------------------------------------
seen = set()
horses = []
for line in text.splitlines():          #  line 63  –  ‘text’ is now defined
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
    "gómez", "márquez", "alejandra", "trujillo", "correia"
}
        if tokens[-1].lower() in common_surnames:
            return True
        return False

    if _looks_like_jockey(name):
        continue

    seen.add(name.lower())
    horses.append({"post": post, "name": name})

horses.sort(key=lambda x: x["post"])

# ------------------------------------------------------------------
# 3.  Top-5 win-probability horses + short analysis
# ------------------------------------------------------------------
if st.button("🔮 Predict race", type="primary"):
    # ---- build stats ----
    for line in text.splitlines():
        for h in horses:
            if h["name"] not in line:
                continue
            finishes = [int(n) for n in re.findall(r'\b([1-9]|1\d|20)\b', line)]
            h["avg_finish"] = sum(finishes[:3]) / 3 if finishes else 5.0
            h["win%"] = round(max(0, 100 - h["avg_finish"] * 5), 1)
            h["runs"] = len(finishes)
            h["wins"] = finishes.count(1)
            break

    # ---- top-5 only ----
    top5 = sorted([h for h in horses if "win%" in h],
              key=lambda x: x["win%"], reverse=True)[:5]

    st.markdown("### 🏆 Top 5 win probabilities")
    for i, h in enumerate(top5, 1):
        bar = "█" * int(h["win%"] / 2) + "░" * (25 - int(h["win%"] / 2))
        st.write(f"{i}. **{h['name']}**  "
                 f"`avg finish {h['avg_finish']:.1f}`  "
                 f"`{h['win%']}%`  \n{bar}")

    st.markdown("### 📊 Quick analysis")
    for i, h in enumerate(top5, 1):
        cons = "very consistent" if h["avg_finish"] <= 3.5 else "steady"
        if h["wins"]:
            note = f"has already won {h['wins']} of last {h['runs']} starts"
        else:
            note = f"no wins recently but finishes close (avg {h['avg_finish']:.1f})"
        st.write(f"{i}. **{h['name']}** – {cons}, {note}.")

    # ---- CSV (full list) ----
    csv_lines = ["Rank,Horse,Post,Win%"]
    for i, h in enumerate(sorted(horses, key=lambda x: x["win%"], reverse=True), 1):
        csv_lines.append(f"{i},{h['name']},{h['post']},{h['win%']}")
    csv_str = "\n".join(csv_lines)
    st.download_button(
        label="📥 Download full CSV",
        data=csv_str,
        file_name=f"race_pred_{datetime.now():%Y%m%d_%H%M%S}.csv",
        mime="text/csv"
    )




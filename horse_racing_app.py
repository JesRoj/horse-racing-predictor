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

    # >>>>>>>  NEW FAST REJECT  <<<<<<<
    if _looks_like_jockey(name):
        continue
    # >>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<

    seen.add(name.lower())
    horses.append({"post": post, "name": name})
                    continue
                # rule 3: last word lowercase → surname
                if words and words[-1].islower():
                    continue
                # ------------------------------------

                seen.add(name.lower())
                horses.append({"post": post, "name": name})
    horses.sort(key=lambda x: x["post"])

    if st.button("🔮 Predict race", type="primary", key="predict"):
            # --- real form from same line only ---
            for line in text.splitlines():
                for h in horses:
                    if h["name"] not in line:
                        continue
                    # pick up every 1-20 number on that line
                    finishes = [int(n) for n in re.findall(r'\b([1-9]|[1-1]\d|20)\b', line)]
                    h["avg_finish"] = sum(finishes[:3]) / 3 if finishes else 5.0
                    h["win%"] = round(max(0, 100 - h["avg_finish"] * 5), 1)
                    break          # done for this horse

            horses.sort(key=lambda x: x["win%"], reverse=True)
            # ------------------------------------
            st.markdown("### 🏆 Real-form prediction")
            for i, h in enumerate(horses, 1):
                bar = "█" * int(h["win%"] / 2) + "░" * (25 - int(h["win%"] / 2))
                st.write(f"{i}. **{h['name']}**  `avg finish {h['avg_finish']:.1f}`  `{h['win%']}%`  \n{bar}")
            # ---- CSV export ----
            csv_lines = ["Rank,Horse,Post,Win%"]
            for i, h in enumerate(horses, 1):
                csv_lines.append(f"{i},{h['name']},{h['post']},{h['win%']}")
            csv_str = "\n".join(csv_lines)

            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name=f"race_pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
















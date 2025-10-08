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
    for line in text.splitlines():
        m = re.search(
                    r'(?:^|\s)(1?\d)\s+([A-Z][A-Z0-9ÁÉÍÓÚÜÑáéíóúüñ\ \(\)\-]{4,}?(?:\s+[A-Z][a-z]*){0,2})(?=\s+[A-Z][a-z]+\s+[A-Z][a-z]|\s+\d)',
                    line,
                    re.I,
                )
        if m:
            post, name = m.groups()
            post = int(post)
            name = name.strip()

            # 1-20 only, no duplicates
            if 1 <= post <= 20 and name.lower() not in seen:
                # ---- stricter automatic filters ----
                # ---- final automatic filters ----
                # ---- final filters ----
                words = name.split()
                # 1) single short word → garbage
                if len(words) == 1 and len(name) <= 8:
                    continue
                # 2) second word is a known surname → jockey
                common_surnames = {
                    "sánchez", "rodríguez", "garcía", "uzcátegui", "palencia", "petit",
                    "quevedo", "gonzález", "villamizar", "capriles", "rive", "gonzalez"
                }
                if len(words) == 2 and words[-1].lower() in common_surnames:
                    continue
                # 3) lowercase tail → surname
                if words and words[-1].islower():
                    continue
                # 4) deduplicate
                if name.lower() in seen:
                    continue
                # -----------------------
                # 4) last word lowercase → surname
                if words and words[-1].islower():
                    continue
                # ---------------------------------
                # rule 2: two short capitalised words → jockey  (both ≤ 6)
                if (len(words) == 2 and
                    len(words[0]) <= 6 and len(words[1]) <= 6 and
                    words[0][0].isupper() and words[1][0].isupper()):
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















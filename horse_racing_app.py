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
    horses = []
    for line in text.splitlines():
        # look for:  (1-2 digits)  (capitalised name)  (decimal or integer)
        m = re.search(r'(?:^|\s)(\d{1,2})\s+([A-Z][A-Z0-9 ]+?)\s+\d+(?:\.\d+)?', line)
        if m:
            post, name = m.groups()
            name = name.strip()
            if len(name) > 3 and name not in {"PRINCESA"}:   # avoid duplicates
                horses.append({"post": int(post), "name": name})
    if horses:
        st.subheader(f"🐎 Found {len(horses)} horses")
        for h in horses:
            st.write(f"Post {h['post']:2} – {h['name']}")

    if st.button("🔮 Predict race", type="primary"):
            import random
            for h in horses:
                h["win%"] = round(random.uniform(5, 30), 1)
            horses.sort(key=lambda x: x["win%"], reverse=True)

            st.markdown("### 🏆 Quick prediction")
            for i, h in enumerate(horses, 1):
                bar = "█" * int(h["win%"] / 2) + "░" * (25 - int(h["win%"] / 2))
                st.write(f"{i}. **{h['name']}**  `{h['win%']}%`  \n{bar}")
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


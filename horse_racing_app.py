import streamlit as st

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
    horses = []
    for line in text.splitlines():
        m = re.match(r'^\s*H\d+a\s+(\d+)\s+([A-Z][A-Z0-9 ]+)\b', line, re.I)
        if m:
            post, name = m.groups()
            horses.append({"post": int(post), "name": name.strip()})

    if horses:
        st.subheader(f"🐎 Found {len(horses)} horses")
        for h in horses:
            st.write(f"Post {h['post']:2} – {h['name']}")
    else:
        st.warning("No horse lines matched – showing raw first 1000 chars")
        with st.expander("Raw text"):
            st.text(text[:1000])

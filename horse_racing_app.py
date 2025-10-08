import streamlit as st

st.set_page_config(page_title="🐎 Racing Predictor", page_icon="🐎")
st.title("🐎 Racing Predictor – Step 1")
st.write("Upload a racing document (PDF, TXT, CSV).")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is not None:
    from pypdf import PdfReader
    import io

    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        st.error("No readable text found in PDF – try an OCR’d or text-based PDF.")
    else:
        st.success(f"Extracted {len(text)} chars from {len(reader.pages)} page(s)")
        with st.expander("👀 Text preview"):
            st.text(text[:1000])

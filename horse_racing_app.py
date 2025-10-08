import streamlit as st

st.set_page_config(page_title="🐎 Racing Predictor", page_icon="🐎")
st.title("🐎 Racing Predictor – Step 1")
st.write("Upload a racing document (PDF, TXT, CSV).")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is not None:
    raw = uploaded_file.read()
    st.success(f"Loaded {uploaded_file.name}  –  {len(raw)} bytes")
    st.text(raw[:300])          # show first 300 chars
else:
    st.info("Waiting for file …")

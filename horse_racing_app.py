import streamlit as st

st.set_page_config(page_title="🐎 Racing Predictor", page_icon="🐎")
st.title("🐎 Racing Predictor – Step 1")
st.write("Upload a racing document (PDF, TXT, CSV).")

uploaded_file = st.file_uploader("📁 Choose file", type=["pdf", "txt", "csv"])

if uploaded_file is not None:
    raw = uploaded_file.read()

    # try a few encodings
    text = None
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        st.error("Could not decode file – try a plain-text or CSV version.")
    else:
        st.success(f"Loaded {uploaded_file.name} – {len(text)} chars")
        with st.expander("👀 Text preview (first 500 chars)"):
            st.text(text[:500])

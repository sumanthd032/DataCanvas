import streamlit as st

st.set_page_config(
    page_title="DataCanvas: Smart SQLite Visualizer",
    layout="wide"
)


st.title("DataCanvas 🎨: Smart SQLite Visualizer")

st.markdown("""
Welcome to DataCanvas! 

To get started, please upload your SQLite database file (`.db` or `.sqlite`).
""")

uploaded_file = st.file_uploader(
    "Choose a SQLite database file",
    type=["sqlite", "db"]
)

if uploaded_file is not None:
    st.success(f"✅ Successfully uploaded '{uploaded_file.name}'!")
    st.write("File Details:")
    st.write(f"- **File size:** {round(uploaded_file.size / 1024, 2)} KB")

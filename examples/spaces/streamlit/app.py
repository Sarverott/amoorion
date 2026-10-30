"""amoorion in Streamlit: `streamlit run app.py`, or as a Hugging Face Space."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[1]))  # in a Space, panel.py lies beside this file
from panel import post

st.title("amoorion")
text = st.text_input("Post")
st.table([{"id": row[0], "text": row[1]} for row in post(text)])

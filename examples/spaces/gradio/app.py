"""amoorion in Gradio: `python app.py`, or as a Hugging Face Space."""

import sys
from pathlib import Path

import gradio as gr

# panel.py is one directory up, and shared by both apps.
sys.path.insert(
    0,
    str(Path(__file__).parents[1]),
)  # in a Space, panel.py lies beside this file
from panel import post

# Gradio makes the page from the function: a text box in, a table out.
demo = gr.Interface(
    fn=post,
    inputs=gr.Textbox(label="Post"),
    outputs=gr.Dataframe(
        headers=[
            "id",
            "text",
        ]
    ),
    title="amoorion",
)

if __name__ == "__main__":
    demo.launch()

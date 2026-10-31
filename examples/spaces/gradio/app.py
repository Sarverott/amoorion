"""amoorion in Gradio: `python app.py`, or as a Hugging Face Space."""

import sys
from pathlib import Path

import gradio as gr

sys.path.insert(
    0,
    str(Path(__file__).parents[1]),
)  # in a Space, panel.py lies beside this file
from panel import post

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

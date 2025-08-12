from IPython.display import display, Markdown

def show_md(md_text: str):
    """Display Markdown text in Jupyter or Streamlit-friendly format."""
    display(Markdown(md_text))

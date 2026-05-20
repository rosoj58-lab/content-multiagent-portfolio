"""Streamlit entrypoint for the SEO Content Pipeline."""

import streamlit as st


def main() -> None:
    """Render the initial scaffold screen."""
    st.set_page_config(page_title="SEO Content Pipeline", layout="wide")
    st.title("SEO Content Pipeline")
    st.write("Project scaffold is ready. Workflow stages will be added in later stories.")


if __name__ == "__main__":
    main()

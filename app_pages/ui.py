"""Shared presentation helpers for the Data-Pilot Streamlit pages."""

import streamlit as st


WORKFLOW_STEPS = (
    "Load your data",
    "Check data quality",
    "Review recommendations",
    "Clean your dataset",
    "Validate and export",
)


def render_page_header(title: str, description: str, step: int | None = None) -> None:
    """Render a consistent page heading and, when relevant, workflow progress."""
    if step is not None:
        total_steps = len(WORKFLOW_STEPS)
        label = WORKFLOW_STEPS[step - 1]
        st.caption(f"DATA-PILOT WORKFLOW  ·  STEP {step} OF {total_steps}")

    st.title(title)
    st.write(description)

    if step is not None:
        st.progress(step / len(WORKFLOW_STEPS), text=label)
        st.divider()

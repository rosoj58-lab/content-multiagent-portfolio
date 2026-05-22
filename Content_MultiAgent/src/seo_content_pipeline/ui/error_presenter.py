"""Controlled Streamlit error presentation."""

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class ControlledErrorMessage:
    """User-facing error details without traceback noise."""

    title: str
    detail: str
    action: str


def build_controlled_error(error: Exception, *, action: str) -> ControlledErrorMessage:
    """Convert an exception into a controlled user-facing message."""
    return ControlledErrorMessage(
        title="Action needed" if isinstance(error, ValueError) else "Something needs attention",
        detail=str(error),
        action=action,
    )


def render_controlled_error(message: ControlledErrorMessage) -> None:
    """Render controlled error state and next action."""
    st.error(message.title)
    st.write(message.detail)
    st.info(message.action)

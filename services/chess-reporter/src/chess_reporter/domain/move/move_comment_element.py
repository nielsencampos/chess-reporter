"""
Chess domain: Move comment element module
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .move_comment_title import MoveCommentTitle


class MoveCommentElement(BaseModel):
    """
    Move Comment Element
    """

    title: MoveCommentTitle = Field(description="Title of the comment")
    content: str = Field(description="Content of the comment", min_length=1)

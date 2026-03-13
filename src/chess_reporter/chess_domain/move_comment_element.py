"""
Chess domain: Move comment element
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from chess_reporter.chess_domain.move_comment_title_type import MoveCommentTitleType


class MoveCommentElement(BaseModel):
    """
    Data class representing a comment element associated with a chess move.
    """

    title: MoveCommentTitleType = Field(description="Title of the comment")
    content: str = Field(description="Content of the comment", min_length=1)

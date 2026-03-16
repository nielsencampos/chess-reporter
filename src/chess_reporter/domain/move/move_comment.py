"""
Chess domain: Move comment module
"""

from __future__ import annotations

from re import Pattern, compile
from typing import Any

from pydantic import RootModel, model_serializer, model_validator

from .move_comment_element import MoveCommentElement
from .move_comment_title import MoveCommentTitle

COMMENT_PATTERN: Pattern[str] = compile(r"\[%(\w+)\s+([^\]]+)\]")


class MoveComment(RootModel[list[MoveCommentElement]]):
    """
    Move Comment
    """

    @model_serializer(mode="plain")
    def serialize_model(self) -> str:
        """
        Serializes the move comment model into a string representation.
        """

        if not self.root:
            return ""

        elements_serialized: str = " ".join(
            f"[%{element.title.value} {element.content}]" for element in self.root
        )

        return f"{{{elements_serialized}}}"

    @model_validator(mode="before")
    @classmethod
    def deserialize_model(cls, value: Any) -> Any:
        """
        Parses PGN structured comments into MoveComment elements.
        """

        if isinstance(value, str):
            matches: list[tuple[str, str]] = COMMENT_PATTERN.findall(value)

            return [
                MoveCommentElement(
                    title=MoveCommentTitle(tag),
                    content=content.strip(),
                )
                for tag, content in matches
            ]

        return value

    @model_validator(mode="after")
    def validate_unique_titles(self) -> MoveComment:
        """
        Validates that comment titles are unique within the move comment.
        """

        titles: list[MoveCommentTitle] = [element.title for element in self.root]

        if len(titles) != len(set(titles)):
            raise ValueError("Move comment cannot contain duplicated titles.")

        return self

    def has(self, title: MoveCommentTitle) -> bool:
        """
        Checks if a comment element exists.
        """

        return any(element.title == title for element in self.root)

    def get(self, title: MoveCommentTitle) -> str | None:
        """
        Retrieves the content of a comment element.
        """

        for element in self.root:
            if element.title == title:
                return element.content

        return None

    def add(self, title: MoveCommentTitle, content: str) -> None:
        """
        Adds a new comment element.
        """

        if self.has(title):
            raise ValueError(f"Comment element '{title.value}' already exists.")

        self.root.append(MoveCommentElement(title=title, content=str(content)))

    def set(self, title: MoveCommentTitle, content: str) -> None:
        """
        Sets the content of a comment element.
        """

        for element in self.root:
            if element.title == title:
                element.content = str(content)
                return

        self.root.append(MoveCommentElement(title=title, content=str(content)))

    def remove(self, title: MoveCommentTitle) -> None:
        """
        Removes a comment element by title.
        """

        self.root = [element for element in self.root if element.title != title]

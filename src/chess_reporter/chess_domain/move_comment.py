"""
Chess domain: Move comment
"""

from __future__ import annotations

from re import Pattern, compile
from typing import Any, List, Optional, Tuple

from pydantic import RootModel, model_serializer, model_validator

from chess_reporter.chess_domain.move_comment_element import MoveCommentElement
from chess_reporter.chess_domain.move_comment_title_type import MoveCommentTitleType

COMMENT_PATTERN: Pattern[str] = compile(r"\[%(\w+)\s+([^\]]+)\]")


class MoveComment(RootModel[List[MoveCommentElement]]):
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
    def deserialize_model(cls, value: Any) -> MoveComment:
        """
        Parses PGN structured comments into MoveComment elements.
        """

        if isinstance(value, str):
            matches: List[Tuple[str, str]] = COMMENT_PATTERN.findall(value)
            elements: List[MoveCommentElement] = [
                MoveCommentElement(
                    title=MoveCommentTitleType(tag),
                    content=content.strip(),
                )
                for tag, content in matches
            ]

            return cls(root=elements)

        return cls(root=value)

    @model_validator(mode="after")
    def validate_unique_titles(self) -> MoveComment:
        """
        Validates that comment titles are unique within the move comment.
        """

        titles: List[MoveCommentTitleType] = [element.title for element in self.root]

        if len(titles) != len(set(titles)):
            raise ValueError("Move comment cannot contain duplicated titles.")

        return self

    def has(self, title: MoveCommentTitleType) -> bool:
        """
        Checks if a comment element exists.
        """

        return any(element.title == title for element in self.root)

    def get(self, title: MoveCommentTitleType) -> Optional[str]:
        """
        Retrieves the content of a comment element.
        """

        for element in self.root:
            if element.title == title:
                return element.content

        return None

    def add(self, title: MoveCommentTitleType, content: str) -> None:
        """
        Adds a new comment element.

        Raises an error if the title already exists.
        """

        if self.has(title):
            raise ValueError(f"Comment element '{title.value}' already exists.")

        self.root.append(MoveCommentElement(title=title, content=str(content)))

    def set(self, title: MoveCommentTitleType, content: str) -> None:
        """
        Sets the content of a comment element.
        Creates the element if it does not exist.
        """

        for element in self.root:
            if element.title == title:
                element.content = str(content)
                return

        self.root.append(MoveCommentElement(title=title, content=str(content)))

    def remove(self, title: MoveCommentTitleType) -> None:
        """
        Removes a comment element by title.
        """

        self.root = [element for element in self.root if element.title != title]

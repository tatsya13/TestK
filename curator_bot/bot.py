"""Rule-based chat bot for a master's degree group curator."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_WORD_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)
_DEFAULT_KNOWLEDGE_PATH = Path(__file__).with_name("knowledge_base.json")
_HELP_COMMANDS = {"help", "помощь", "темы", "меню", "старт", "start"}


@dataclass(frozen=True)
class KnowledgeItem:
    """Single knowledge base entry used to answer student questions."""

    id: str
    title: str
    keywords: tuple[str, ...]
    answer: str

    @classmethod
    def from_dict(cls, raw_item: dict[str, object]) -> "KnowledgeItem":
        """Create a validated knowledge item from a JSON dictionary."""
        required_fields = {"id", "title", "keywords", "answer"}
        missing_fields = required_fields.difference(raw_item)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Knowledge item is missing required fields: {missing}")

        keywords = raw_item["keywords"]
        if not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords):
            raise ValueError("Knowledge item field 'keywords' must be a list of strings")

        return cls(
            id=str(raw_item["id"]),
            title=str(raw_item["title"]),
            keywords=tuple(keyword.strip().lower() for keyword in keywords if keyword.strip()),
            answer=str(raw_item["answer"]),
        )


class CuratorBot:
    """Simple Russian-language assistant for master's students."""

    greeting = (
        "Здравствуйте! Я бот-куратор группы магистратуры. "
        "Спросите про расписание, дедлайны, документы, практику, контакты или мероприятия."
    )
    fallback = (
        "Пока не нашёл точный ответ. Попробуйте переформулировать вопрос или напишите куратору: "
        "anna.ivanova@example.edu. Для списка тем введите «помощь»."
    )

    def __init__(self, knowledge_items: Iterable[KnowledgeItem]) -> None:
        self.knowledge_items = tuple(knowledge_items)
        if not self.knowledge_items:
            raise ValueError("CuratorBot requires at least one knowledge item")

    def reply(self, message: str) -> str:
        """Return a helpful answer for the student's message."""
        normalized_message = message.strip().lower()
        if not normalized_message:
            return self.greeting

        if normalized_message in _HELP_COMMANDS:
            return self.help_message()

        best_item = self._find_best_item(normalized_message)
        if best_item is None:
            return self.fallback
        return best_item.answer

    def help_message(self) -> str:
        """Return available knowledge base topics."""
        topics = "\n".join(f"— {item.title}" for item in self.knowledge_items)
        return f"Я могу подсказать по темам:\n{topics}\n\nЗадайте вопрос обычным текстом."

    def _find_best_item(self, message: str) -> KnowledgeItem | None:
        message_tokens = set(_tokenize(message))
        scored_items: list[tuple[int, KnowledgeItem]] = []

        for item in self.knowledge_items:
            score = 0
            for keyword in item.keywords:
                keyword_tokens = set(_tokenize(keyword))
                if keyword in message:
                    score += 3
                score += len(message_tokens.intersection(keyword_tokens))
            if score > 0:
                scored_items.append((score, item))

        if not scored_items:
            return None

        scored_items.sort(key=lambda scored_item: scored_item[0], reverse=True)
        return scored_items[0][1]


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _WORD_RE.finditer(text)]


def load_knowledge_base(path: Path = _DEFAULT_KNOWLEDGE_PATH) -> tuple[KnowledgeItem, ...]:
    """Load and validate knowledge base items from a JSON file."""
    with path.open(encoding="utf-8") as knowledge_file:
        raw_items = json.load(knowledge_file)

    if not isinstance(raw_items, list):
        raise ValueError("Knowledge base must contain a list of items")

    return tuple(KnowledgeItem.from_dict(raw_item) for raw_item in raw_items)


def load_default_bot() -> CuratorBot:
    """Create a bot with the bundled knowledge base."""
    return CuratorBot(load_knowledge_base())

import unittest

from curator_bot import CuratorBot, KnowledgeItem, load_default_bot


class CuratorBotTest(unittest.TestCase):
    def test_reply_returns_schedule_answer_by_keyword(self):
        bot = load_default_bot()

        answer = bot.reply("Подскажите расписание консультации на сегодня")

        self.assertIn("Консультация куратора", answer)

    def test_reply_returns_deadline_answer_by_phrase(self):
        bot = load_default_bot()

        answer = bot.reply("Когда сдавать индивидуальный план?")

        self.assertIn("индивидуальный план", answer.lower())

    def test_reply_returns_help_for_help_command(self):
        bot = load_default_bot()

        answer = bot.reply("помощь")

        self.assertIn("Я могу подсказать", answer)
        self.assertIn("Документы", answer)

    def test_reply_returns_fallback_for_unknown_question(self):
        bot = load_default_bot()

        answer = bot.reply("Где купить кофе рядом с корпусом?")

        self.assertIn("не нашёл точный ответ", answer)

    def test_empty_knowledge_base_is_rejected(self):
        with self.assertRaises(ValueError):
            CuratorBot([])

    def test_invalid_keywords_are_rejected(self):
        with self.assertRaises(ValueError):
            KnowledgeItem.from_dict(
                {
                    "id": "bad",
                    "title": "Bad",
                    "keywords": "not-a-list",
                    "answer": "Bad answer",
                }
            )


if __name__ == "__main__":
    unittest.main()

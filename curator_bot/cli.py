"""Command-line interface for the master's group curator bot."""

from __future__ import annotations

from .bot import load_default_bot

_EXIT_COMMANDS = {"выход", "exit", "quit", "q"}


def main() -> None:
    """Run an interactive curator bot chat in the terminal."""
    bot = load_default_bot()
    print(bot.greeting)
    print("Введите «помощь» для списка тем или «выход» для завершения.")

    while True:
        try:
            message = input("Студент: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nБот: До встречи! Удачной учёбы.")
            break

        if message.lower() in _EXIT_COMMANDS:
            print("Бот: До встречи! Удачной учёбы.")
            break

        print(f"Бот: {bot.reply(message)}")


if __name__ == "__main__":
    main()

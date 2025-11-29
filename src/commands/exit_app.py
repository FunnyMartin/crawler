# src/commands/exit_app.py
# Autor: Martin Šilar
# Ukončení aplikace přes Command pattern

from .base import Command


class ExitAppCommand(Command):
    def execute(self):
        print("\nUkončuji aplikaci...\n")
        exit(0)

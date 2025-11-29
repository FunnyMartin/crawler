# src/commands/base.py
# Autor: Martin Šilar
# Základ Command Pattern třída

from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

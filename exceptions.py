from typing import Optional

class NektoMeException(Exception):
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

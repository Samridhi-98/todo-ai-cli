from dataclasses import dataclass
from datetime import date

@dataclass
class Todo:
    id: int
    task: str
    priority: str
    due_date: date
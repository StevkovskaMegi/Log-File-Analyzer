from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class LogEntry:
    timestamp: Optional[datetime]
    level: str
    message: str
    raw: str
    source: str = ""

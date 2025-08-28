from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Iterable

@dataclass
class FilterCriteria:
    keyword: Optional[str] = None
    level: Optional[str] = None  # INFO|ERROR|WARNING|DEBUG|UNKNOWN
    start: Optional[datetime] = None
    end: Optional[datetime] = None

    def match(self, entry) -> bool:
        if self.level and entry.level.upper() != self.level.upper():
            return False
        if self.keyword and (self.keyword.lower() not in entry.message.lower() and self.keyword.lower() not in entry.raw.lower()):
            return False
        if self.start and entry.timestamp and entry.timestamp < self.start:
            return False
        if self.end and entry.timestamp and entry.timestamp > self.end:
            return False
        return True

    def filter(self, entries: Iterable) -> Iterable:
        for e in entries:
            if self.match(e):
                yield e

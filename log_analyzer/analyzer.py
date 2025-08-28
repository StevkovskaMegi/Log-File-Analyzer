from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Dict, List, Optional, Iterator
from .models import LogEntry
from .filters import FilterCriteria

class LogAnalyzer:
    def __init__(self, entries: Iterable[LogEntry] = ()):
        self._entries = list(entries)

    def ingest(self, entries: Iterable[LogEntry]):
        self._entries.extend(entries)

    @property
    def entries(self) -> List[LogEntry]:
        return self._entries

    def filter(self, criteria: FilterCriteria) -> List[LogEntry]:
        return list(criteria.filter(self._entries))

    def counts_by_level(self, entries: Optional[Iterable[LogEntry]] = None) -> Dict[str, int]:
        entries = entries if entries is not None else self._entries
        c = Counter(e.level for e in entries)
        # Ensure consistent keys
        for k in ["INFO","WARNING","ERROR","DEBUG","UNKNOWN"]:
            c.setdefault(k, 0)
        return dict(c)

    def summary(self, entries: Optional[Iterable[LogEntry]] = None) -> Dict:
        entries = list(entries) if entries is not None else self._entries
        total = len(entries)
        first = min((e.timestamp for e in entries if e.timestamp), default=None)
        last = max((e.timestamp for e in entries if e.timestamp), default=None)
        # Most common error messages
        error_msgs = Counter(e.message for e in entries if e.level == 'ERROR')
        common_errors = error_msgs.most_common(5)
        return {
            "total_entries": total,
            "first_log": first.isoformat() if first else None,
            "last_log": last.isoformat() if last else None,
            "counts": self.counts_by_level(entries),
            "common_errors": common_errors,
        }

    def timeline(self, bucket: str = "hour", entries: Optional[Iterable[LogEntry]] = None):
        """Return a {timestamp_bucket: count} mapping for all entries with a timestamp.
        bucket: 'minute' | 'hour' | 'day'
        """
        entries = entries if entries is not None else self._entries
        buckets = Counter()
        for e in entries:
            if not e.timestamp:
                continue
            if bucket == 'minute':
                key = e.timestamp.replace(second=0, microsecond=0)
            elif bucket == 'day':
                key = e.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                key = e.timestamp.replace(minute=0, second=0, microsecond=0)
            buckets[key] += 1
        return dict(sorted(buckets.items(), key=lambda kv: kv[0]))

import re
from datetime import datetime
from typing import Iterable, Iterator, Optional
from .models import LogEntry

class LogParser:
    """Robust log parser supporting multiple common formats.

    Supported levels: INFO, WARNING, ERROR, DEBUG (others will be 'UNKNOWN').
    Timestamp parsing tries several common formats. Malformed lines are returned
    with level='UNKNOWN' and timestamp=None so you can still inspect them.
    """

    # Regex patterns for common log formats
    # Example: 2025-08-28 12:34:56,789 INFO Module - Message
    PATTERN_ISO = re.compile(
        r"""
        ^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[\.,]\d{1,6})?)\s*
        (?:(?:-|:)?\s*)?
        (?:\[?(?P<level>INFO|ERROR|WARNING|DEBUG)\]?)
        [\s:\-]*
        (?P<msg>.*)$
        """,
        re.VERBOSE
    )

    # Example syslog-ish: Aug 28 10:00:01 host app[123]: ERROR Something broke
    PATTERN_SYSLOG = re.compile(
        r"""
        ^(?P<mon>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+
        (?P<day>\d{1,2})\s+
        (?P<time>\d{2}:\d{2}:\d{2}).*?
        (?P<level>INFO|ERROR|WARNING|DEBUG)[:\- ]\s*
        (?P<msg>.*)$
        """,
        re.VERBOSE
    )

    # Example: 2025-08-28T12:34:56Z [ERROR] Message
    PATTERN_ISO_Z = re.compile(
        r"""
        ^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*\[?(?P<level>INFO|ERROR|WARNING|DEBUG)\]?\s*[:\-]?\s*(?P<msg>.*)$
        """
    )

    MONTHS = {m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], start=1)}

    TS_FORMATS = [
        "%Y-%m-%d %H:%M:%S,%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    def __init__(self, default_year: Optional[int] = None):
        self.default_year = default_year or datetime.now().year
        self.malformed_lines = 0

    def _parse_ts(self, ts_str: str) -> Optional[datetime]:
        ts_str = ts_str.replace(',', '.')
        for fmt in self.TS_FORMATS:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        return None

    def parse_line(self, line: str, source: str = "") -> LogEntry:
        line = line.rstrip('\n')
        m = self.PATTERN_ISO.match(line) or self.PATTERN_ISO_Z.match(line)
        if m:
            ts = self._parse_ts(m.group('ts'))
            level = (m.group('level') or 'UNKNOWN').upper()
            msg = m.group('msg') or ''
            return LogEntry(timestamp=ts, level=level, message=msg, raw=line, source=source)

        m = self.PATTERN_SYSLOG.match(line)
        if m:
            month = self.MONTHS[m.group('mon')]
            day = int(m.group('day'))
            time_str = m.group('time')
            ts = None
            try:
                ts = datetime.strptime(f"{self.default_year}-{month:02d}-{day:02d} {time_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                ts = None
            level = (m.group('level') or 'UNKNOWN').upper()
            msg = m.group('msg') or ''
            return LogEntry(timestamp=ts, level=level, message=msg, raw=line, source=source)

        # Fallback: try to find a bare level and take rest as message
        level_match = re.search(r"\b(INFO|ERROR|WARNING|DEBUG)\b", line, re.IGNORECASE)
        level = level_match.group(1).upper() if level_match else 'UNKNOWN'
        if level == 'UNKNOWN':
            self.malformed_lines += 1
        return LogEntry(timestamp=None, level=level, message=line, raw=line, source=source)

    def parse_file(self, path: str) -> Iterator[LogEntry]:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                yield self.parse_line(line, source=path)

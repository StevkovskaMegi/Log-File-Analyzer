import json
from typing import Dict, Any

class JSONExporter:
    @staticmethod
    def save(data: Dict[str, Any], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

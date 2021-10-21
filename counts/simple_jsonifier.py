"""
Helpers for turning rows from excel, csv, sharepoint, whatever into json
that can be uploaded to the database.
"""

from typing import List, Dict
import json
from pathlib import Path


def make_json(records_list: List[Dict], table_name: str) -> List[Dict]:
    return [{'model': table_name, 
     'pk': i,
     'fields': fields} for i, fields in enumerate(records_list)]


def dump_json(records: List[Dict], filename=Path) -> None:
    with open(filename, 'w') as f:
        f.write(json.dumps(records))

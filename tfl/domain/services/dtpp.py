import pathlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, NamedTuple, Optional

import xmltodict

from tfl.domain.facilities import DTPPHeader
from xml.etree import ElementTree as ET
DTPP_DATE_PATTERN = re.compile(r'(\d{4})Z\s+(\d+\/\d+\/\d+)')

def convert_dtpp_date(date_string: str) -> datetime:
    groups = re.search(DTPP_DATE_PATTERN, date_string).groups()
    formatted_string = f"{groups[0]} {groups[1]}"
    return datetime.strptime(formatted_string, '%H%M %m/%d/%y').replace(tzinfo=timezone.utc)

def get_dtpp_header(path: pathlib.Path) -> Optional[DTPPHeader]:
    try:
        for _, elem in ET.iterparse(path, events=("start", "end")):
            if elem.tag == 'digital_tpp':
                return DTPPHeader(
                    cycle=elem.attrib['cycle'],
                    valid_from=convert_dtpp_date(elem.attrib['from_edate']),
                    valid_to=convert_dtpp_date(elem.attrib['to_edate']),
                )
    except FileNotFoundError:
        return

def load_raw_plate_data(path: pathlib.Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        data = xmltodict.parse(f.read())
        return data


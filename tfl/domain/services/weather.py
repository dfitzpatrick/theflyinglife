from __future__ import annotations

import re
from decimal import Decimal, ROUND_UP
from typing import List, Dict, Tuple

from fuzzywuzzy import process, fuzz

from tfl.domain.core import HeadAndTailString
from tfl.domain.weather_translations import *


def string_to_decimal_rounded(unit: str, precision='0.1', strategy=ROUND_UP) -> Decimal:
    return Decimal(unit).quantize(Decimal(precision), strategy)


def translate_sky_condition_abbr_to_text(abbr: str) -> str:
    return wx_sky_conditions.get(abbr, 'Unknown Abbreviation')


def translate_flight_rule_abbr_to_text(abbr: str) -> str:
    return wx_flight_rules.get(abbr, 'Unknown Abbreviation')


def head_and_tail(line: str, n: int) -> HeadAndTailString:
    head, tail = line[:n], line[n:]
    return HeadAndTailString(head=head, tail=tail)


def merge_forecasts(child, parent):
    """
    Child is assumed to be the most recent forecast. In TAFs, they may omit
    data that is from their parent. This will carry down those forecasts.
    :param child:
    :param parent:
    :return:
    """
    schema = child.schema()
    fields = schema['properties'].keys()

    kwargs = {}
    for attr in fields:
        v = getattr(child, attr)
        if parent is not None:

            if v is None or v == []:
                v = getattr(parent, attr)
        kwargs[attr] = v

    return type(child)(
        **kwargs
    )


def get_string_ratios(input: str, comparable: Tuple[str]) -> List[Tuple[str, int]]:
    return process.extract(input, comparable, scorer=fuzz.partial_ratio)


def get_best_plates(text: str, comparables: str | List[str]) -> List[str]:
    def sanitize_plate_name(name: str):
        # To help with matching, remove stuff out of the name as much as possible
        pattern = r"\s(runway|rwy|or)\s"
        name = str(re.sub(pattern, ' ', name))
        return name
    comparable_mapping: Dict[str, str] = {sanitize_plate_name(name):name for name in comparables}
    ratios = get_string_ratios(sanitize_plate_name(text), tuple(comparable_mapping.keys()))
    print(f"Input is: {text}")
    print(f"Comparing to {' | '.join(comparable_mapping.keys())}")
    print("Ratios are")
    print(ratios)
    highest_ratio = ratios[0][1]
    threshold = 7
    return [comparable_mapping[r[0]] for r in ratios if highest_ratio - r[1] < threshold]


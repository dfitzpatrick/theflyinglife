from __future__ import annotations
from decimal import Decimal, ROUND_UP
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

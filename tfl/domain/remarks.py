from .weather import Remark
import re
from typing import Optional, Pattern, List
from decimal import Decimal

from .weather_translations import wx_phenomenon

WIND_PATTERN = re.compile(r"PK WND (\d+)/(\d+)")
WIND_SHIFT = re.compile(r"WSHFT (\d+)")
TWR_SFC_VIS = re.compile(r"(TWR|SFC) VIS (\d/\d+|\d+)")
MAXIUMUM_TEMP = re.compile(r"1(0|1)(\d{3})")
MINIMUM_TEMP = re.compile(r"2(0|1)(\d{3})")
THREE_HOUR_PRECIP = re.compile(r"3(\d{4}|/{4})")
TWENTY_FOUR_HOUR_TEMP = re.compile(r"4(0|1)(\d{3})(0|1)(\d{3})")
SNOW_DEPTH = re.compile(r"4/(\d{3})")
WEATHER_BEGINNING = re.compile(r"([A-Z]{2})B(\d+)E?(\d+)?")
CEILING_VARIABLE = re.compile(r"CIG (\d{2})V(\d{2})")
HOURLY_TEMP = re.compile(r"T(0|1)(\d{3})(0|1)(\d{3})")
SEA_LEVEL_PRESSURE = re.compile(r"SLP(\d{3})")

def wind_pattern(text: str) -> Optional[Remark]:
    match = re.search(WIND_PATTERN, text)
    if match is None:
        return
    wind, wind_time = match.groups()
    wind_dir, gust = wind[:3], wind[3:]
    if len(wind_time) > 2:
        wind_time += "Z"
    else:
        wind_time += " minutes past the hour"
    text = f"Peak Wind of {gust} kts from {wind_dir} degrees that occurred at {wind_time}"
    return Remark(code=match.group(), text=text)


def ao2(text: str) -> Optional[Remark]:
    words = text.split()
    if any('AO2' == w.upper() for w in words):
        return Remark(code='AO2', text='Automated station with precipitation discriminator')


def wind_shift(text: str) -> Optional[Remark]:
    match = re.search(WIND_SHIFT, text)
    if match is None:
        return
    shift_time = match.groups()[0]
    fmt = f"{shift_time[:2]}:{shift_time[2:]}"
    return Remark(code=match.group(), text=f"Wind shift at {fmt}Z")


def surface_visibility(text: str) -> Optional[Remark]:
    match = re.search(TWR_SFC_VIS, text)
    if match is None:
        return
    source, visibility = match.groups()
    source = "Tower" if source == "TWR" else "ASOS"
    return Remark(code=match.group(), text=f"{source} reports {visibility}sm visibility")


def _hour_base(text: str, min=True, prefix_str='') -> Optional[Remark]:
    words = text.split()
    for w in words:
        match = re.match(MINIMUM_TEMP if min else MAXIUMUM_TEMP, w)
        if match is not None:
            mod, degrees = match.groups()
            mod = "" if mod == "0" else "-"
            threshold = "Minimum" if min else "Maximum"
            degrees = Decimal(degrees) * Decimal('0.1')
            txt = f"{prefix_str} {threshold} Temp of {mod}{degrees}C"
            return Remark(code=match.group(), text=txt.strip())


def six_hour_max(text: str) -> Optional[Remark]:
    return _hour_base(text, min=False, prefix_str='Six Hour')


def six_hour_min(text: str) -> Optional[Remark]:
    return _hour_base(text, min=True, prefix_str='Six Hour')



def three_hour_precip(text: str) -> Optional[Remark]:
    words = text.split()
    for w in words:
        match = re.match(THREE_HOUR_PRECIP, w)
        if match is None:
            continue
        measure = match.groups()[0]
        if measure == "0000":
            amount = "a trace of precipitation"
        elif measure == "////":
            amount = "a indeterminable amount of precipitation"
        else:
            amount = Decimal(measure) * Decimal("0.1")
            amount = f"{amount} inches of precipitation"
        return Remark(code=match.group(), text=f"Three Hour Precipitation measure with {amount}")


def _split_and_find_match(text: str, pattern: Pattern[str]) -> Optional[re.Match]:
    for w in text.split():
        match = re.match(pattern, w)
        if match is not None:
            return match


def twenty_four_hour_min_max(text: str) -> Optional[Remark]:
    match = _split_and_find_match(text, TWENTY_FOUR_HOUR_TEMP)
    if match is None:
        return
    max_mod, max_temp, min_mod, min_temp = match.groups()
    fmt_max = f"1{max_mod}{max_temp}"
    fmt_min = f"2{min_mod}{min_temp}"
    max_remark = _hour_base(fmt_max, min=False)
    min_remark = _hour_base(fmt_min, min=True)
    txt = f"24-hour {max_remark.text} and {min_remark.text}"
    return Remark(code=match.group(), text=txt)


def snow_depth(text: str) -> Optional[Remark]:
    match = _split_and_find_match(text, SNOW_DEPTH)
    if match is None:
        return
    depth = match.groups()[0]
    depth = int(depth)
    return Remark(code=match.group(), text=f"Snow depth of {depth} inches")


def weather_beginning(text: str) -> Optional[Remark]:
    match = re.search(WEATHER_BEGINNING, text)
    if match is None:
        return
    try:
        phenomenon, begin, end = match.groups()
    except ValueError:
        phenomenon, begin, end = match.groups() + (None,)
    # TS for parser is not considered a phenom but instead a descriptor
    # But it acts as a phenom here
    ph_map = {**wx_phenomenon, **{"TS": "Thunderstorm"}}
    phenomenon = ph_map.get(phenomenon.upper(), phenomenon.upper())
    begin_fmt = f"{begin} min after the hour" if len(begin) < 4 else f"{begin[:2]}:{begin[2:]}Z"
    txt = f"{phenomenon} began {begin_fmt}"
    if end is not None:
        end_fmt = f"{end} min after the hour" if len(end) < 4 else f"{end[:2]}:{end[2:]}Z"
        txt = f"{txt}, ended at {end_fmt}"
    return Remark(code=match.group(), text=txt)

def virga(text: str) -> Optional[Remark]:
    if any('VIRGA' == w.upper() for w in text.split()):
        return Remark(code="VIRGA", text="Precipitation not reaching the ground")

def hourly_temp_dew(text: str) -> Optional[Remark]:
    match = _split_and_find_match(text, HOURLY_TEMP)
    is_neg = lambda s: s == "1"
    tenths = Decimal('0.1')
    if match is None:
        return
    temp_mod, temp, dew_mod, dew_temp = match.groups()
    temp = Decimal(temp) * tenths
    dew_temp = Decimal(dew_temp) * tenths
    temp_mod = f"-" if is_neg(temp_mod) else ""
    dew_mod = f"-" if is_neg(dew_mod) else ""
    txt = f"Hourly Temp {temp_mod}{temp}C and Dewpoint {dew_mod}{dew_temp}C"
    return Remark(code=match.group(), text=txt)

def sea_level_pressure(text: str) -> Optional[Remark]:
    match = _split_and_find_match(text, SEA_LEVEL_PRESSURE)
    if match is None:
        return
    pressure = match.groups()[0]
    first_digit = pressure[0]
    pressure = Decimal(pressure) * Decimal('0.1')
    pressure = Decimal('900') + pressure if first_digit == '9' else Decimal('1000') + pressure
    txt = f"Sea Level Pressure {pressure} hPa"
    return Remark(code=match.group(), text=txt)


def parse_literals(text: str) -> List[Remark]:
    literals = {
        'PRESFR': 'Pressure falling rapidly',
        'PRESRR': 'Pressure rising rapidly',
        '$': 'Maintenance needed on system',
        'AO2': 'Automated station with precipitation discriminator',
        'RVRNO': 'RVR missing',
        'PWINO': 'Precipitation identifier information not available',
        'PNO': 'Precipitation amount not available',
        'FZRANO': 'Freezing rain information not available',
        'TSNO': 'Thunderstorm information not available'
    }
    container = []
    for w in text.split():
        w = w.upper()
        if w in literals.keys():
            txt = literals[w]
            container.append(Remark(code=w, text=txt))
    return container

remarks_pipeline = [
    parse_literals,
    wind_pattern,
    wind_shift,
    surface_visibility,
    six_hour_max,
    six_hour_min,
    three_hour_precip,
    twenty_four_hour_min_max,
    snow_depth,
    weather_beginning,
    hourly_temp_dew,
    virga,
    sea_level_pressure
]
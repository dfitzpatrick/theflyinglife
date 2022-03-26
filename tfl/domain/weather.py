from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from tfl.domain.core import ValueObject, Aggregate, Form
from tfl.domain.services.weather import translate_sky_condition_abbr_to_text, translate_flight_rule_abbr_to_text
from decimal import Decimal, ROUND_UP

class Wind(ValueObject):
    dir: int = 0
    at: int = 0
    gusting: int = 0

    @property
    def text(self):
        if self.dir == 0 and self.at == 0:
            s = "Calm"
        elif self.dir == 0 and self.at > 0:
            s = f"Variable @ {self.at}kts"
        else:
            s = f"{self.dir} @ {self.at}kts"
        if self.gusting > 0:
            s += f" gusting {self.gusting}kts"
        return s


class Visibility(ValueObject):
    sm: Decimal

    @property
    def km(self):
        kms = self.sm * Decimal('1.60934')
        return kms.quantize(Decimal('0.1'), ROUND_UP)

    @property
    def text(self):
        return "{} sm ({} km)".format(self.sm, self.km)


class SkyCondition(ValueObject):
    coverage: str
    bases: Optional[int]
    text: str

    @property
    def text(self):
        s = translate_sky_condition_abbr_to_text(self.coverage)
        if self.bases:
            s += f" @ {self.bases} ft AGL"
        return s


class Temperature(ValueObject):
    celsius: Decimal

    @property
    def fahrenheit(self):
        c = self.celsius * 9 / 5 + 32
        return c.quantize(Decimal('0.1'), ROUND_UP)

    @property
    def text(self):
        return f"{self.celsius}°C ({self.fahrenheit}°F)"


class Dewpoint(Temperature):
    pass



class Point(Aggregate):
    latitude: Decimal
    longitude: Decimal


class AltimeterSetting(ValueObject):
    inhg: Decimal

    @property
    def hPa(self) -> Decimal:
        inhg = self.inhg * Decimal('33.86')
        return inhg.quantize(Decimal('0.1'), ROUND_UP)

    @property
    def text(self):
        return f"{self.inhg} inHg ({self.hPa} hPa)"
class FlightRule(ValueObject):
    code: str

    @property
    def text(self):
        return translate_flight_rule_abbr_to_text(self.code)


class WxCodeSymbol(ValueObject):
    symbol: str
    text: str


class WxIntensity(WxCodeSymbol):
    pass


class WxDescriptor(WxCodeSymbol):
    pass


class WxPhenomenon(WxCodeSymbol):
    pass


class WxProximity(WxCodeSymbol):
    pass


class WeatherChange(WxCodeSymbol):
    pass


class WxCode(ValueObject):
    raw: Optional[str]
    text: str
    intensity: Optional[WxCodeSymbol]
    has_proximity: bool
    descriptor: Optional[WxDescriptor]
    phenomenons: List[WxPhenomenon]


class Remark(ValueObject):
    code: str
    text: str


class TAFForecast(Aggregate):
    valid_from: datetime
    valid_to: datetime
    sky_condition: List[SkyCondition]
    wind: Wind
    visibility: Optional[Visibility]


    @property
    def ceilings(self) -> List[int]:
        ceiling_sky_conditions = ['BKN', 'OVC', 'OVX']
        cs = [
            c.bases
            for c in self.sky_condition
            if c.coverage in ceiling_sky_conditions and c.bases is not None
        ]
        return cs

    @property
    def flight_rules(self) -> Optional[str]:

        if self.sky_condition == [] or self.visibility is None:
            return
        if any(c < 500 for c in self.ceilings) or self.visibility.sm < 1:
            return "LIFR"
        if any(500 <= c < 1000 for c in self.ceilings) or 1 < self.visibility.sm < 3:
            return "IFR"
        if any(1000 <= c <= 3000 for c in self.ceilings) or 3 < self.visibility.sm < 5:
            return "MVFR"
        return "VFR"

    @property
    def text(self):
        mask = "%b %d %H:%MZ"
        frm = self.valid_from.strftime(mask)
        to = self.valid_to.strftime(mask)
        return f"{frm} thru {to}"


class TAF(Aggregate):
    valid_from: datetime
    valid_to: datetime
    raw_text: str
    station_id: str
    issue_time: datetime
    bulletin_time: datetime
    location: Optional[Point]
    forecasts: List[TAFForecast]


class PROB(TAFForecast):
    probability: int

    @property
    def text(self):
        base = super().text
        s = f"PROBABILITY ({self.probability}%) {base}"
        return s


class BECMG(TAFForecast):
    time_becoming: datetime

    @property
    def text(self):
        mask = "%b %d %H:%MZ"
        becoming = self.time_becoming.strftime(mask)
        base = super().text
        s = f"BECOMING ({becoming}) {base}"
        return s


class TEMPO(TAFForecast):

    @property
    def text(self):
        base = super().text
        s = f"TEMPORARILY {base}"
        return s


class FM(TAFForecast):
    @property
    def text(self):
        base = super().text
        s = f"FROM {base}"
        return s


class Metar(Aggregate):
    time: datetime
    raw_text: str
    station_id: str
    location: Optional[Point]
    wind: Optional[Wind]

    temperature: Optional[Temperature]
    dewpoint: Optional[Dewpoint]
    wind: Optional[Wind]
    visibility: Optional[Visibility]
    altimeter: Optional[AltimeterSetting]
    sky_condition: List[SkyCondition]
    flight_rule: Optional[FlightRule]
    wx_codes: List[WxCode]
    remarks: List[Remark]



class ICAO(str):

    def __init__(self, value):
        str.__init__(value)


class ICAOSearchForm(Form):
    icao: ICAO


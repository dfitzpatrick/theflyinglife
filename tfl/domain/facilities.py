from typing import Optional, List
from decimal import Decimal
from tfl.domain.core import Aggregate, ValueObject


class Runway(ValueObject):
    bearing1: Optional[Decimal]
    bearing2: Optional[Decimal]
    ident1: str
    ident2: str
    length_ft: int
    lights: bool
    surface: str
    width_ft: int

    @property
    def text(self):
        light_mod = "" if self.lights else "No "
        return f"{0}/{1} {3}x{4}' {5} -- {6}".format(
            self.ident1,
            self.ident2,
            self.length_ft,
            self.width_ft,
            self.surface,
            light_mod + "Lighting"
        )


class Airport(Aggregate):
    city: str
    country: str
    elevation_ft: int
    elevation_m: int
    iata: Optional[str]
    icao: Optional[str]
    latitude: Decimal
    longitude: Decimal
    name: str
    note: Optional[str]
    reporting: bool
    runways: Optional[List[Runway]]
    state: str
    type: str
    website: Optional[str]
    wiki: Optional[str]


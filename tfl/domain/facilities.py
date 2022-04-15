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
    surface: Optional[str]
    width_ft: int

    @property
    def text(self):
        light_mod = "" if self.lights else "No "
        return "{0}/{1} {2}x{3}' {4} -- {5}".format(
            self.ident1,
            self.ident2,
            self.length_ft,
            self.width_ft,
            self.surface,
            light_mod + "Lighting"
        )





class FAAPlate(ValueObject):
    tpp_cycle: int
    icao: str
    code: str
    name: str
    pdf_name: str

    @property
    def plate_url(self):
        return f"https://aeronav.faa.gov/d-tpp/{self.tpp_cycle}/{self.pdf_name}"


class Airport(Aggregate):
    city: Optional[str]
    country: str
    elevation_ft: Optional[int]
    elevation_m: Optional[int]
    iata: Optional[str]
    icao: str
    latitude: Decimal
    longitude: Decimal
    name: str
    note: Optional[str]
    reporting: bool
    runways: Optional[List[Runway]]
    state: Optional[str]
    type: str
    website: Optional[str]
    wiki: Optional[str]
    plates: List[FAAPlate] = []
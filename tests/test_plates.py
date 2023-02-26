import json

import pytest
import pathlib

from tfl.domain.facilities import FAAPlate
from tfl.domain.services.weather import get_string_ratios, get_best_plates
from tfl.infrastructure.airport import parse_raw_plate_data
from tfl.domain.services.dtpp import load_raw_plate_data

path = str(pathlib.Path(__file__).parents[1].resolve() / "data/d-tpp_Metafile.xml")
data = json.loads("""[
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "MIN",
    "name": "TAKEOFF MINIMUMS",
    "pdf_name": "SW3TO.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/SW3TO.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "MIN",
    "name": "DIVERSE VECTOR AREA",
    "pdf_name": "SW3TO.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/SW3TO.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "MIN",
    "name": "ALTERNATE MINIMUMS",
    "pdf_name": "SW3ALT.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/SW3ALT.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "LAH",
    "name": "LAHSO",
    "pdf_name": "SW3LAHSO.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/SW3LAHSO.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "HOT",
    "name": "HOT SPOT",
    "pdf_name": "SW3HOTSPOT.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/SW3HOTSPOT.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "BAUBB TWO (RNAV)",
    "pdf_name": "00236BAUBB.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236BAUBB.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "DSNEE FIVE (RNAV)",
    "pdf_name": "00236DSNEE.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236DSNEE.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "DSNEE FIVE (RNAV), CONT.1",
    "pdf_name": "00236DSNEE_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236DSNEE_C.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "KAYOH EIGHT",
    "pdf_name": "00236KAYOH.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236KAYOH.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "PCIFC TWO (RNAV)",
    "pdf_name": "00236PCIFC.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236PCIFC.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "PCIFC TWO (RNAV), CONT.1",
    "pdf_name": "00236PCIFC_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236PCIFC_C.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "ROOBY THREE (RNAV)",
    "pdf_name": "00236ROOBY.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ROOBY.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "ROOBY THREE (RNAV), CONT.1",
    "pdf_name": "00236ROOBY_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ROOBY_C.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "STAR",
    "name": "TANDY FIVE",
    "pdf_name": "00236TANDY.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236TANDY.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "ILS OR LOC RWY 30",
    "pdf_name": "00236IL30.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236IL30.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "RNAV (RNP) RWY 12",
    "pdf_name": "00236RR12.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236RR12.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "RNAV (RNP) RWY 26R",
    "pdf_name": "00236RR26R.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236RR26R.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "RNAV (RNP) Y RWY 30",
    "pdf_name": "00236RRY30.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236RRY30.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "RNAV (GPS) Z RWY 30",
    "pdf_name": "00236RZ30.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236RZ30.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "VOR OR TACAN RWY 30",
    "pdf_name": "00236VT30.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236VT30.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "ARSENAL VISUAL RWY 30",
    "pdf_name": "00236ARSENAL_VIS30.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ARSENAL_VIS30.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "IAP",
    "name": "LA RIVER VISUAL RWY 12",
    "pdf_name": "00236LARIVER_VIS12.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236LARIVER_VIS12.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "APD",
    "name": "AIRPORT DIAGRAM",
    "pdf_name": "00236AD.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236AD.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "ANAHEIM ONE",
    "pdf_name": "00236ANAHEIM.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ANAHEIM.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "ANAHEIM ONE, CONT.1",
    "pdf_name": "00236ANAHEIM_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ANAHEIM_C.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "FRITR THREE (RNAV)",
    "pdf_name": "00236FRITR.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236FRITR.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "HAWWC THREE (RNAV)",
    "pdf_name": "00236HAWWC.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236HAWWC.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "TOPMM FOUR (RNAV)",
    "pdf_name": "00236TOPMM.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236TOPMM.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "TOPMM FOUR (RNAV), CONT.1",
    "pdf_name": "00236TOPMM_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236TOPMM_C.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "ZOOMM THREE (RNAV)",
    "pdf_name": "00236ZOOMM.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ZOOMM.PDF"
  },
  {
    "tpp_cycle": 2205,
    "icao": "KLGB",
    "code": "DP",
    "name": "ZOOMM THREE (RNAV), CONT.1",
    "pdf_name": "00236ZOOMM_C.PDF",
    "plate_url": "https://aeronav.faa.gov/d-tpp/2205/00236ZOOMM_C.PDF"
  }
]""")
data = [FAAPlate(**p) for p in data]

def test_load_raw_plate_data():

    data = load_raw_plate_data(path)
    assert data is not None


def test_parse_raw_plate_data():
    data = parse_raw_plate_data(path)
    a = 1 + 1
    assert True


def test_string_ratios():
    test_string = "ils 30"
    comparables = ["VOR OR TACAN RWY 30", "ILS OR LOC RWY 30", "ILS OR LOC RWY 26"]
    comparables = list(map(str.lower, comparables))

    levenshtein_ratios = get_string_ratios(test_string, comparables)
    assert len(levenshtein_ratios) == 3
    assert comparables[0] in levenshtein_ratios.keys()
    assert comparables[1] in levenshtein_ratios.keys()
    assert False

def test_plate_ratios():
    test_string = "vor"
    comparables = ["VOR OR TACAN RWY 30", "ILS OR LOC RWY 30", "ILS OR LOC RWY 26"]
    comparables = list(map(str.lower, [d.name.lower() for d in data]))
    ratios = get_best_plates(test_string, comparables)
    assert False
import pytest
import pathlib
from tfl.infrastructure.airport import load_raw_plate_data, parse_raw_plate_data

path = str(pathlib.Path(__file__).parents[1].resolve() / "data/d-tpp_Metafile.xml")

def test_load_raw_plate_data():

    data = load_raw_plate_data(path)
    assert data is not None


def test_parse_raw_plate_data():
    data = parse_raw_plate_data(path)
    a = 1 + 1
    assert True

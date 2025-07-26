from datetime import date
from pathlib import Path

from tfl.application_services.dcs import (
    Airport,
    _edition_path,
    _ingest_xml,
    get_schedule,
    editions_available
)

sample_xml = """<?xml version="1.0" encoding="iso-8859-1"?>
<?xml-stylesheet type="text/xsl" href="test.xsl"?>
<airports from_edate="0901Z 06/12/25" to_edate="0901Z 08/07/25">
  <location state="CALIFORNIA">
    <airport>
      <aptname>LONG BEACH (DAUGHERTY FLD)</aptname>
      <aptcity>LONG BEACH</aptcity>
      <aptid>LGB</aptid>
      <navidname></navidname>
      <pages>
        <pdf>sw_195_12JUN2025.pdf</pdf>
        <pdf>sw_LGB_notices_12JUN2025.pdf</pdf>
      </pages>
    </airport>
    </location>
    </airports>"""

def test_edition_path():
    edition_date = date(2025, 2, 20)
    expected_path = Path('/foo/DCS_20250220')
    assert _edition_path(edition_date, base_path=Path('/foo')) == expected_path

def test_get_schedule():
    query_date = date(2025, 4, 19)
    expected_date = date(2025, 4, 17)
    assert get_schedule(query_date) == expected_date

    next_date = date(2025, 6, 12)
    assert get_schedule(query_date, offset=1) == next_date

    prior_date = date(2025, 2, 20)
    assert get_schedule(query_date, offset=-1) == prior_date

def test_ingest_xml():
    expected_airports = {
        'LGB': Airport(
            name='LONG BEACH (DAUGHERTY FLD)',
            city='LONG BEACH',
            navid_name=None,
            files=['sw_195_12JUN2025.pdf', 'sw_LGB_notices_12JUN2025.pdf']
        )
    }
    airports = _ingest_xml(sample_xml)
    assert airports == expected_airports
    assert isinstance(airports, dict)
    assert 'LGB' in airports
    assert airports['LGB'].name == 'LONG BEACH (DAUGHERTY FLD)'
    assert len(airports['LGB'].files) == 2

def test_editions_available():
    path = Path('/foo')
    query_date = date(2025, 2, 21)
    editions = list(editions_available(path, query_date))
    assert len(editions) == 1
    assert editions[0] == date(2025, 2, 20)
    
    query_date = date(2025, 5, 30)
    editions = list(editions_available(path, query_date))
    assert len(editions) == 2
    assert editions[0] == date(2025, 4, 17)
    assert editions[1] == date(2025, 6, 12)
    
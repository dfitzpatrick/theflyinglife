
from __future__ import annotations
from datetime import date, timedelta
import asyncio
import pathlib
import aiohttp
import io
import logging
from functools import partial
from zipfile import ZipFile
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Generator
import os
from tfl import pdf

log = logging.getLogger(__name__)
_start_date = date(2025, 2, 20)
_folder_fmt="DCS_{edition_date}"
_payload_format = "https://aeronav.faa.gov/Upload_313-d/supplements/DCS_{edition_date}.zip"
_download_mapping = {k:_payload_format.format(edition_date=k.strftime("%Y%m%d")) for k in
            (_start_date + timedelta(days=56 * i) for i in range(0,163))}
_current_ingested: date | None = None

@dataclass(frozen=True)
class Airport:
    name: str
    city: str
    navid_name: str | None
    files: list[str]

def _edition_path(edition_date: date, base_path = './') -> pathlib.Path:
    return base_path / _folder_fmt.format(edition_date=date_to_string(edition_date))

def date_to_string(edition_date: date):
    return edition_date.strftime("%Y%m%d")

def get_schedule(query_date: date, offset = 0) -> date:
    days_since_start = (query_date - _start_date).days
    cycle = days_since_start // 56 + offset
    key_date = _start_date + timedelta(days=56 * cycle)
    return key_date

async def download_dcs(edition_date: date) -> io.BytesIO:
    url = _download_mapping[edition_date]
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            data = await response.read()
            return io.BytesIO(data)


def catalogue_dcs(base_dir: pathlib.Path, dcs_data: io.BytesIO):
    # FAA is random with filename case for each file. Standardize
    with ZipFile(dcs_data) as z:
        for member in z.namelist():
            target_path = base_dir / member.lower()
            # Ensure parent directories exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member) as source, open(target_path, "wb") as target:
                shutil.copyfileobj(source, target)

def editions_available(path, query_date: date = date.today()) -> Generator[date, None, None]:
    cycle_publish_days = 20
    edition_path = partial(_edition_path, base_path=path)
    current = get_schedule(query_date)
    next = get_schedule(query_date, offset=1)
    # check to see if the current edition is missing
    if not edition_path(current).exists():
        yield current

    if not edition_path(next).exists() and next - timedelta(days=cycle_publish_days) <= query_date:
        yield next
    
async def _poll(path: pathlib.Path):
    query = date.today()
    prior_path = _edition_path(get_schedule(query, offset=-1), path)
    for edition_date in editions_available(path):
        zip_data = await download_dcs(edition_date)
        _subfolder = _folder_fmt.format(edition_date=date_to_string(edition_date))
        catalogue_dcs(path / _subfolder, zip_data)

    if prior_path.exists():
        shutil.rmtree(prior_path)

    
def _dcs_task_done(task: asyncio.Task):
    try:
        task.result()
    except Exception as e:
        log.error(f"DCS polling task failed: {e}")
    else:
        log.info("DCS polling task completed successfully.")

def start_polling_dcs(edition_path: pathlib.Path) -> asyncio.Task:
    task = asyncio.create_task(_poll(edition_path))
    task.add_done_callback(_dcs_task_done)
    return task


def _ingest_xml(xml: str) -> dict[str, Airport]:
    root = ET.fromstring(xml) 
    airports = {}
    for location in root.findall('location'):
        for airport in location.findall('airport'):
            aptid = airport.find('aptid').text
            airports[aptid] = Airport(
                name=airport.find('aptname').text,
                city=airport.find('aptcity').text,
                navid_name=airport.find('navidname').text if airport.find('navidname') is not None else None,
                files=[pdf.text for pdf in airport.find('pages').findall('pdf')]
            )
    return airports

def get_supplement_bytes(file_path) -> io.BytesIO:
    with open(file_path, 'rb') as f:
        return io.BytesIO(f.read())

class NoChartSupplementError(Exception):
    pass

class ChartSupplementService:
    def __init__(self, path: pathlib.Path):
        query = date.today()
        self.path = path
        self._current = get_schedule(query)
        self._data: dict[str, Airport] = {}
        self._data = self._ingest()

    
    def _ingest(self) -> dict[str, Airport]:
        try:
            with open(self.afd_xml_path, 'r') as f:
                return _ingest_xml(f.read())
        except FileNotFoundError:
            return {}

    
    @property
    def edition_path(self):
        return _edition_path(self._current, self.path)
    
    @property
    def afd_xml_path(self):
        _fn = 'afd_{edition}.xml'
        edition = self._current.strftime('%d%b%Y').lower()
        return self.edition_path / _fn.format(edition=edition)
    
    @property
    def data(self):
        current = get_schedule(date.today())
        if current != self._current or not self._data:
            # New edition in place
            self._current = current 
            self._data = self._ingest()
        return self._data

    def get(self, icao: str) -> list[io.BytesIO]:
        icao = icao.upper()
        if icao not in self.data.keys():
            raise NoChartSupplementError
        bytes = []
        airport = self.data[icao.upper()]
        for fn in airport.files:
            path = self.edition_path / fn.lower()
            pdf_bytes = get_supplement_bytes(path)
            # Split each page into its own file
            for page in pdf.split_pdf_pages(pdf_bytes):
                bytes.append(page)
        return bytes
     
    def get_as_zip(self, icao: str) -> io.BytesIO[ZipFile]:
        files = self.get(icao)
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zf:
            for idx, f in enumerate(files):
                name = f"file_{idx+1}.pdf"
                f.seek(0)
                zf.writestr(name, f.read())
        return zip_buffer

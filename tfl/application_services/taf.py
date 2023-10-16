from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.interfaces.weather import ITAFRepository
from gzip import GzipFile
import aiohttp
import xmltodict
import io
from tfl.domain.weather import *
from tfl.domain.factories.weather import WeatherFactory
from typing import Any, Optional, Dict

from dateutil.parser import parse
from tfl.application_services.adds import ADDSPolling, PollingFile
import logging

log = logging.getLogger(__name__)

class BadResponseError(Exception):
    pass


class TafService:

    def __init__(self, repo: ITAFRepository):
        self._repo = repo
        self.poller = ADDSPolling()
        self.poller.add_file('tafs.cache.xml.gz', self.file_updated)

    async def file_updated(self, polling_file: PollingFile):
        log.debug("In taf update callback")
        gz = await self._fetch_taf(polling_file.filename)
        await self._parse_taf_gzip(gz)

    async def _fetch_taf(self, url) -> GzipFile:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            data = io.BytesIO(await response.read())
            return GzipFile(fileobj=data)

    async def _parse_taf_gzip(self, gz_metar: GzipFile):
        data = xmltodict.parse(gz_metar.read())
        try:
            data = data['response']['data']['TAF']
        except KeyError:
            raise BadResponseError("Invalid Response from aviationweather.gov")
        for t in data:
            taf = self._parse_taf(t)
            try:
                await self._repo.create(taf)
            except EntityExistsError:
                await self._repo.update(taf)


    def _parse_taf(self, t: Dict[str, Any]) -> TAF:
        location = None
        forecasts = []
        raw_text = t['raw_text']
        station_id = t['station_id']
        issue_time = parse(t['issue_time'])
        
        bulletin_time = parse(t['bulletin_time'])
        valid_from = parse(t['valid_time_from'])
        valid_to = parse(t['valid_time_to'])
        latitude = t.get('latitude')
        longitude = t.get('longitude')
        
        if latitude is not None and longitude is not None:
            location = Point(latitude=latitude, longitude=longitude)

        
        forecasts = WeatherFactory.forecasts(t)
        taf = TAF(
            raw_text=raw_text,
            station_id=station_id,
            issue_time=issue_time,
            valid_from=valid_from,
            valid_to=valid_to,
            bulletin_time=bulletin_time,
            location=location,
            forecasts=forecasts,
            last_polling_succeeded=self.poller.last_polling_succeeded
        )
        return taf

    async def taf(self, icao) -> Optional[TAF]:
        try:
            return await self._repo.find(icao)
        except EntityNotFoundError:
            return

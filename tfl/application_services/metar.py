import io
from gzip import GzipFile

import aiohttp
import xmltodict
from dateutil.parser import parse

from tfl.application_services.adds import ADDSPolling, PollingFile
from tfl.domain.exceptions import EntityExistsError, EntityNotFoundError
from tfl.domain.factories.weather import WeatherFactory
from tfl.domain.interfaces.weather import IMetarRepository
from tfl.domain.services.weather import string_to_decimal_rounded
from tfl.domain.weather import *
from tfl.domain.weather_translations import *
from tfl.infrastructure.metar import MetarRepository


class BadResponseError(Exception):
    pass


class MetarService:
    """
    Service for METAR Functionality and updating of the repository.
    """

    def __init__(self, repo: IMetarRepository):
        self._repo = repo
        self.poller = ADDSPolling()
        self.poller.add_file('metars.cache.xml.gz', self._file_updated)

    async def metar(self, icao) -> t.Optional[Metar]:
        """
        Return a new Metar from the given icao.
        Parameters
        ----------
        icao
            The string identifier of the airport.
        Returns
        -------
            Metar

        Raises
        -------

        """
        try:
            return await self._repo.find(icao)
        except EntityNotFoundError:
            return

    async def _file_updated(self, polling_file: PollingFile):
        gz = await self._fetch_metar(polling_file.filename)
        await self._parse_metar_gzip(gz)

    async def _fetch_metar(self, url) -> GzipFile:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            data = io.BytesIO(await response.read())
            return GzipFile(fileobj=data)

    async def _parse_metar_gzip(self, gz_metar: GzipFile):
        data = xmltodict.parse(gz_metar.read())
        try:
            data = data['response']['data']['METAR']
        except KeyError:
            raise BadResponseError("Invalid Response from aviationweather.gov")

        for m in data:
            metar = self._parse_metar(m)
            try:
                await self._repo.create(metar)
            except EntityExistsError:
                await self._repo.update(metar)

    def _parse_metar(self, m: t.Dict[str, t.Any]) -> Metar:
        latitude = m.get('latitude')
        longitude = m.get('longitude')
        altimeter = m.get('altim_in_hg')
        wx_string = m.get('wx_string', "")
        wx_codes = WeatherFactory.wx_codes(wx_string)
        flight_rule = m.get('flight_category')
        sky_condition = WeatherFactory.sky_condition(m)
        visibility = WeatherFactory.visibility(m)
        wind = WeatherFactory.wind(m)
        temp = WeatherFactory.temperature(m)
        dewpoint = WeatherFactory.dewpoint(m)
        if flight_rule is not None:
            flight_rule = FlightRule(code=flight_rule, text=wx_flight_rules[flight_rule])

        location = None
        if latitude is not None and longitude is not None:
            location = Point(latitude=latitude, longitude=longitude)
        if altimeter is not None:
            inhg = string_to_decimal_rounded(altimeter, precision='0.01')
            altimeter = AltimeterSetting(inhg=inhg)

        metar = Metar(
            raw_text=m['raw_text'],
            station_id=m['station_id'],
            time=parse(m['observation_time']),
            location=location,
            temperature=temp,
            visibility=visibility,
            wind=wind,
            altimeter=altimeter,
            dewpoint=dewpoint,
            wx_codes=wx_codes,
            sky_condition=sky_condition,
            flight_rule=flight_rule,

        )
        return metar



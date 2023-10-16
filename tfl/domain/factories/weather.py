import typing as t

from dateutil.parser import parse
from tfl.domain.services.weather import head_and_tail, merge_forecasts, string_to_decimal_rounded

from tfl.domain.weather import *
from tfl.domain.weather_translations import *
import logging

log = logging.getLogger(__name__)

WIND_DIRECTION = 'wind_dir_degrees'
WIND_SPEED = 'wind_speed_kt'
WIND_GUST = 'wind_gust_kt'
SKY_CONDITION = 'sky_condition'
SKY_COVER = '@sky_cover'
CLOUD_BASES = '@cloud_base_ft_agl'
VISIBILITY = 'visibility_statute_mi'
TEMPERATURE = 'temp_c'
DEWPOINT = 'dewpoint_c'
WEATHER_CHANGE = 'change_indicator'


def _get_symbol(abbreviation: str) -> t.Optional[WxCodeSymbol]:
    if abbreviation in wx_intensities.keys():
        return WxIntensity(
            symbol=abbreviation,
            text=wx_intensities[abbreviation]
        )
    if abbreviation in wx_descriptors.keys():
        return WxDescriptor(
            symbol=abbreviation,
            text=wx_descriptors[abbreviation]
        )
    if abbreviation in wx_phenomenon.keys():
        return WxPhenomenon(
            symbol=abbreviation,
            text=wx_phenomenon[abbreviation]
        )
    if abbreviation in wx_proximities.keys():
        return WxProximity(
            symbol=abbreviation,
            text=wx_proximities[abbreviation]
        )


class WeatherFactory:

    @staticmethod
    def wind(data: t.Dict[str, t.Any]) -> Wind:
        dir = data.get(WIND_DIRECTION, 0)
        if dir == "VRB":
            dir = 0
        at = data.get(WIND_SPEED, 0)
        gust = data.get(WIND_GUST, 0)
        wind = Wind(
            dir=dir,
            at=at,
            gusting=gust,
        )
        return wind

    @staticmethod
    def sky_condition(data: t.Dict[str, t.Any]) -> t.List[SkyCondition]:
        def _create(s: t.Dict[str, t.Any]) -> SkyCondition:
            coverage = s[SKY_COVER]
            bases = s.get(CLOUD_BASES)

            return SkyCondition(
                    coverage=coverage,
                    bases=bases,
            )

        container = []
        skc = data.get(SKY_CONDITION, [])
        if isinstance(skc, list):
            for cond in skc:
                container.append(_create(cond))
        if isinstance(skc, dict):
            container.append(_create(skc))
        return container

    @staticmethod
    def visibility(data: t.Dict[str, t.Any]) -> t.Optional[Visibility]:
        vis = data.get(VISIBILITY)
        if vis is None:
            return
        # Fix for visibility to allow +
        if vis[-1] == "+":
            vis = vis[0:-1]
        sm = string_to_decimal_rounded(vis)
        return Visibility(sm=sm)

    @staticmethod
    def temperature(data: t.Dict[str, t.Any], key=None) -> t.Optional[Temperature]:
        key = TEMPERATURE if key is None else key
        temp = data.get(key)
        if temp is None:
            return
        c = string_to_decimal_rounded(temp)
        return Temperature(celsius=c)

    @staticmethod
    def dewpoint(data: t.Dict[str, t.Any]) -> t.Optional[Dewpoint]:
        return WeatherFactory.temperature(data, key=DEWPOINT)

    @staticmethod
    def change_type(data: t.Dict[str, t.Any]) -> t.Optional[WeatherChange]:
        change = data.get(WEATHER_CHANGE)
        if change is None:
            return
        return WeatherChange(
            code=change,
            text=wx_taf_changes[change]
        )

    @staticmethod
    def forecasts(data: t.Dict[str, t.Any], parent: TAFForecast = None) -> t.List[t.Union[TAFForecast, BECMG, TEMPO]]:
        def _make(f: t.Dict[str, t.Any], parent=None) -> t.Union[TAFForecast, BECMG, TEMPO]:
            change = f.get('change_indicator')
            fc_from = parse(f['fcst_time_from'])
            fc_to = parse(f['fcst_time_to'])
            wind = WeatherFactory.wind(f)
            sky_condition = WeatherFactory.sky_condition(f)
            visibility = WeatherFactory.visibility(f)
            prob = f.get('probability', 0)
            time_becoming = f.get('time_becoming')
            wx_codes = WeatherFactory.wx_codes(f.get('wx_string', ''))
        
            # New Site update that drops time_becoming. Quick fix to verify schema change.
            if time_becoming is None:
                time_becoming = fc_from
            temp = {
                None: FM,
                'PROB': PROB,
                'FM': FM,
                'TEMPO': TEMPO,
                'BECMG': BECMG
            }[change](
                probability=prob,
                time_becoming=parse(time_becoming) if isinstance(time_becoming, str) else time_becoming,
                valid_from=fc_from,
                valid_to=fc_to,
                wind=wind,
                visibility=visibility,
                wx_codes=wx_codes,
                sky_condition=sky_condition,
            )
            return merge_forecasts(temp, parent)

        forecasts = data.get('forecast', [])
       
        container = []
        if isinstance(forecasts, list):
            parent = None
            for fc in forecasts:
               
                obj = _make(fc, parent)
                container.append(obj)
                parent = obj
        if isinstance(forecasts, dict):
            container.append(_make(forecasts))
      
        return container


    @staticmethod
    def wx_codes(codes) -> t.List[WxCode]:
        container = []
        codes = codes.split()
        for code in codes:
            item = WeatherFactory.parse_wx_code(code)
            container.append(item)
        return container


    @staticmethod
    def parse_wx_code(code: str) -> WxCode:
        raw = code
        intensity = None
        descriptor = None
        has_proximity = False
        phenomenons = []

        # Intensity is always one character and leads the code.
        symbol = _get_symbol(code[:1])
        if isinstance(symbol, WxIntensity):
            intensity = symbol
            code = code[1:]

        # All remaining symbols are now groups of two characters.
        while len(code) >= 2:
            symbol, code = head_and_tail(code, 2)

            wx = _get_symbol(symbol)
            if isinstance(wx, WxDescriptor):
                # There should only be one descriptor
                descriptor = wx
            if isinstance(wx, WxProximity):
                has_proximity = True
            if isinstance(wx, WxPhenomenon):
                phenomenons.append(wx)

        intensity_text = intensity.text if intensity else ""
        descriptor_text = descriptor.text if descriptor else ""
        phs = phenomenons
        if descriptor and descriptor.symbol != "TS":
            if descriptor.symbol == "SH":
                phs = [f"{ph.text} {descriptor.text}" for ph in phs]
            else:
                phs = [f"{descriptor.text} {ph.text}" for ph in phs]
        else:
            phs = [ph.text for ph in phs]
        if intensity:
            ph_text = " and ".join(f"{intensity_text} {ph}" for ph in phs)
        else:
            ph_text = " and ".join(f"{ph}" for ph in phs)

        # Weird english rules
        ds_text = ""
        if descriptor and len(ph_text) > 0:
            if descriptor.symbol == "TS":
                ph_text += " associated with thunderstorms"
        elif descriptor:
            # Standalone as a phenomenon
            ph_text = descriptor.text
        if has_proximity:
            ph_text += " in the vicinity"

        return WxCode(
            raw=raw,
            text=ph_text,
            intensity=intensity,
            descriptor=descriptor,
            has_proximity=has_proximity,
            phenomenons=phenomenons

        )
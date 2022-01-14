import typing as t
wx_intensities = {
    "-": "Light",
    "+": "Heavy",

}
wx_proximity_allowed_abbreviations = [
    "TS", "FG", "FC", "SH", "PO", "BLDU", "BLSA", "BLSN"
]
wx_descriptors = {
    "MI": "Shallow",
    "PR": "Partial",
    "TS": "Thunderstorm",
    "BC": "Patches",
    "DR": "Low Drifting",
    "BL": "Blowing",
    "SH": "Showers",
    "FZ": "Freezing",

}
wx_proximities = {
    "VC": "in the vicinity"
}
wx_phenomenon = {
    "RA": "Rain",
    "DZ": "Drizzle",
    "SN": "Snow",
    "SG": "Snow Grains",
    "IC": "Ice Crystals",
    "PL": "Ice Pellets",
    "GR": "Hail",
    "GS": "Small Hail",
    "UP": "Unknown Precipitation",
    "FG": "Fog",
    "BR": "Mist",
    "HZ": "Haze",
    "VA": "Volcanic Ash",
    "DU": "Widespread Dust",
    "FU": "Smoke",
    "SA": "Sand",
    "PY": "Spray"
}

wx_sky_conditions = {
    'SKC': 'Clear Skies',
    'CLR': 'No clouds below 12,000 ft',
    'CAVOK': 'No clouds below 5000 ft',
    'FEW': 'Few Clouds',
    'SCT': 'Scattered Clouds',
    'BKN': 'Broken Layer',
    'OVC': 'Overcast Layer',
    'OVX': 'Sky Obscured',
    'NSC': '?????????'
}
wx_flight_rules = {
    'VFR': 'Visual Flight Rules',
    'MVFR': 'Marginal Visual Flight Rules',
    'IFR': 'Instrument Flight Rules',
    'LIFR': 'Low Instrument Flight Rules'
}

wx_taf_changes = {
    'TEMPO': 'Temporarily',
    'BECMG': 'Becoming',
    'FM': 'From',
    'PROB': 'Probability',
}
from typing import Dict, Optional
from tfl.domain.exceptions import EntityExistsError
from tfl.domain.facilities import Airport
from tfl.domain.interfaces.facility import IAirportRepository
import json

class AirportService:

    def __init__(self, path: str, repo: IAirportRepository):
        self._repo = repo
        with open(path, 'r') as fh:
            data: Dict[str, Airport] = json.load(fh)

        for airport in data.values():
            try:
                self._repo.create(airport)
            except EntityExistsError:
                self._repo.update(airport)

    def get_airport(self, icao) -> Optional[Airport]:
        return self._repo.find(icao)







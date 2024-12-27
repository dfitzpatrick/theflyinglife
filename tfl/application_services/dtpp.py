import asyncio
import os
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Union, Optional

import dateutil.relativedelta
import aiohttp

from tfl.domain.facilities import DTPPHeader
from tfl.domain.services.dtpp import get_dtpp_header
import logging

log = logging.getLogger(__name__)

class DTPPVersionFile:
    def __init__(self, cached_files_path: pathlib.Path, from_date = datetime.utcnow(), override_version: Optional[int] = None):
        self._cached_files_path = cached_files_path
        self._from_date = from_date
        self._remote_path = "https://aeronav.faa.gov/d-tpp/{version_date}/xml_data/d-tpp_Metafile.xml"
        if override_version:
            self.value = override_version
        else:
            self.value = int(self._from_date.strftime("%y%m"))
        self.file_path = self._cached_files_path / f"DTPP_{self.value}.xml"
        self.file_exists = self.file_path.exists()
        self.month_value = int(str(self.value)[2:])
        self.year_value = int(str(self.value)[:2])


    @property
    def previous(self) -> 'DTPPVersionFile':
        return self.__class__(
            cached_files_path=self._cached_files_path,
            from_date=self._from_date + dateutil.relativedelta.relativedelta(months=-1)
        )

    @property
    def next(self) -> 'DTPPVersionFile':
        return self.__class__(
            cached_files_path=self._cached_files_path,
            from_date=self._from_date + dateutil.relativedelta.relativedelta(months=1)
        )
    def override_version(self, number: int) -> 'DTPPVersionFile':
        return self.__class__(
            cached_files_path=self._cached_files_path,
            override_version=number
        )
    def read_header(self) -> Optional[DTPPHeader]:
        return get_dtpp_header(self.file_path)




    @property
    def is_valid(self):
        header = get_dtpp_header(self.file_path)
        return header and header.is_valid

    def get(self):
        with self.file_path.open(mode='r') as f:
            return f.read()

    async def fetch_and_save(self, force_remote: bool = False) -> str:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(self._remote_path.format(version_date=self.value)) as resp:
                data = await resp.text()
                with self.file_path.open(mode='w') as f:
                    f.write(data)
                return data

    def remove_cached_file(self):
        self.file_path.unlink(missing_ok=True)


class DTPPService:

    def __init__(self, cached_files_path: pathlib.Path):
        self.cached_files_path = cached_files_path
        self._callbacks = []
        self._task: Optional[asyncio.Task] = None
        self.path = "https://aeronav.faa.gov/d-tpp/{version_date}/xml_data/d-tpp_Metafile.xml"
        self.current_valid_header: Optional[DTPPHeader] = None
        self.clean_cache()

    def _task_callback(self, task: asyncio.Future):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"DTPP Task exception {e}")
            raise e

    def cached_filepath(self, version: int) -> pathlib.Path:
        return self.cached_files_path / f"{version}.xml"

    def register_callback(self, func):
        self._callbacks.append(func)

    def save_xml(self, version: int, data: str):
        with self.cached_filepath(version).open(mode='w') as f:
            f.write(data)

    @property
    def version(self):
        return DTPPVersionFile(cached_files_path=self.cached_files_path)

    def get_version(self, version: Union[int, str]) -> DTPPVersionFile:
        try:
            dt = datetime.strptime(str(version), "%y%m")
            version_file = DTPPVersionFile(cached_files_path=self.cached_files_path, from_date=dt)
        except ValueError:
            # Unstandard 13 period
            version_file = DTPPVersionFile(cached_files_path=self.cached_files_path, override_version=int(version))
        return version_file


    @property
    def cached_versions(self):
        return [self.get_version(fn.name.split('_')[1][:-4]) for fn in self.cached_files_path.glob("DTPP_*.xml")]

    def clean_cache(self):
        for version_cache in [cv for cv in self.cached_versions if not cv.is_valid]:
                version_cache.remove_cached_file()

    def valid_version_from_file(self) -> Optional[DTPPVersionFile]:
        for version in self.cached_versions:
            if version.is_valid:
                return version

    async def _notify(self, header: DTPPHeader, version: DTPPVersionFile):
        log.info("Notifying observers of DTPP update")
        for cb in self._callbacks:
            await cb(header, version)

    async def _poll(self) -> (DTPPHeader, DTPPVersionFile):
        log.info("Polling for DTPP Updates")
        # Pull possibly the next months and have it ready
        if not self.version.file_exists:
            await self.version.fetch_and_save()

        # Find the current
        version = await self.seek_valid_version()
        header = version.read_header()
        return header, version

    async def _polling_task(self):
        while True:
            header, version = await self._poll()
            if header != self.current_valid_header:
                self.current_valid_header = header
                await self._notify(header, version)
            now = datetime.now(timezone.utc)
            next_polling_seconds = (header.valid_to - now).total_seconds() + 10
            await asyncio.sleep(next_polling_seconds)

    def header_is_valid(self, version: DTPPVersionFile):
        header = version.read_header()
        return header and header.is_valid
    
    async def seek_valid_version(self):
        version = self.version
        for i in range(2):
            if not version.file_exists:
                await version.fetch_and_save()
            if self.header_is_valid(version):
                return version
            else:
                now = datetime.now(timezone.utc)
                header = version.read_header()
                version = version.next if now > header.valid_to else version.previous
                log.debug(f"Else version is: {version.file_path}")
                if self.header_is_valid(version):
                    log.debug("shows as valid")
                    return version
                elif version.previous.month_value == 12:
                    # Some times it may go off a 13 month year. Test for this before raising an error
                    override_version = int(f"{version.previous.year_value}13")
                    version = version.override_version(override_version)
                    log.debug(f"trying {version.file_path}")
                    try:
                        await version.fetch_and_save()
                        if self.header_is_valid(version):
                            return version
                    except aiohttp.ClientResponseError:
                        continue              
        raise RuntimeError("No Valid version found")

    def start(self):
        if self._task:
            return
        self._task = asyncio.create_task(self._polling_task())
        self._task.add_done_callback(self._task_callback)

    def stop(self):
        if self._task:
            self._task.cancel()







from typing import Callable, Optional, List, Dict

import asyncio
from datetime import datetime
import logging
import time
from dataclasses import dataclass

import htmllistparse

log = logging.getLogger(__name__)

DEFAULT_ADDS_PATH = 'https://aviationweather.gov/adds/dataserver_current/current/'


@dataclass
class PollingFile:
    path: str
    name: str
    callback: Callable
    last_polled: Optional[datetime] = None

    @property
    def filename(self):
        return self.path + self.name


class ADDSPolling:
    """
    Handles functionality to automatically poll and fetch files from the
    Aviation Weather ADDS server.
    """

    def __init__(self, path=None, delay=5*60, loop=None):
        """

        Parameters
        ----------
        path
            The path to the directory listing. This relies on Apache style
            directory listings.
        delay
            The delay in seconds between polling.
        loop
            The event loop
        """
        self.path = path or DEFAULT_ADDS_PATH
        self.loop: asyncio.AbstractEventLoop = loop if loop is not None else asyncio.get_event_loop()
        self.task: Optional[asyncio.Task] = None
        self.delay = delay
        self._polling_files: List[PollingFile] = []
        self.last_polling_succeeded = True

    def add_file(self, name: str, callback: Callable):
        """
        Adds a file to the 'watch' list for the poller
        Parameters
        ----------
        name
            The filename (without a path) to add
        callback
            A callback function that takes a PolledFile argument which will be
            called once a new file is available.

        Returns
        -------
        None


        """
        o = PollingFile(
            path=self.path,
            name=name,
            callback=callback
        )
        self._polling_files.append(o)

    def _file_entry(self, file_entry: htmllistparse.FileEntry):
        """
        We use a third-party library to help parse the directory structure of
        a Apache server. The default implementation uses a time.struct_time.
        This function converts it to a datetime that is more prevalent in our code.
        Parameters
        ----------
        file_entry
            The named tuple htmllistparse.FileEntry
        Returns
        -------
            htmllistparse.FileEntry

        """
        modified = datetime.fromtimestamp(time.mktime(file_entry.modified))
        return htmllistparse.FileEntry(
            name=file_entry.name,
            modified=modified,
            size=file_entry.size,
            description=file_entry.description
        )

    def _index_listing_results(self, listings: List[htmllistparse.FileEntry]) -> Dict[str, htmllistparse.FileEntry]:
        """
        Helper function that transforms the htmllistingparse.FileEntry object to use
        datetimes and also creates a mapping by the filename.
        Parameters
        ----------
        listings
            A Listing of htmllistparse.FileEntry
        Returns
        -------
        Dict[str, htmllistparse.FileEntry]

        """
        return {fe.name:fe for fe in map(self._file_entry, listings)}

    async def _poll(self, **kwargs):
        """
        Fires on each polling cycle to check for modified files.
        Parameters
        ----------
        kwargs
            Optional arguments to pass
        Returns
        -------
        None
        """
        try:
            log.debug(f"Fetching listing for {self.path}")
            cwd, files = htmllistparse.fetch_listing(self.path)
            files = self._index_listing_results(files)
            for polling_file in self._polling_files:
                file_entry = files.get(polling_file.name)
                if file_entry is None:
                    continue
                if polling_file.last_polled is None or file_entry.modified > polling_file.last_polled:
                    # call back
                    await polling_file.callback(polling_file, **kwargs)
        except:
            self.last_polling_succeeded = False
            await asyncio.sleep(60)
            await self._poll(**kwargs)
        else:
            self.last_polling_succeeded = True

    def _task_finished(self, future: asyncio.Future):
        """
        Task callback when the task completes or encounters an error.
        Parameters
        ----------
        future
            The future object of the finished task
        Returns
        -------
        None
        """
        if future.exception():
            log.error(str(future.exception()))
            raise future.exception()
        log.info("ADDS Task has finished and is now stopped.")

    async def _task_loop(self, **kwargs):
        """
        Main loop that continuously polls with a given delay.
        Parameters
        ----------
        kwargs
            Optional Parameters
        Returns
        -------
        None
        """

        while True:
            log.debug(f"ADDS Polling {kwargs}")
            await self._poll(**kwargs)
            await asyncio.sleep(self.delay)

    async def start(self, **kwargs):
        """
        Starts the polling service.
        Parameters
        ----------
        kwargs
            Optional parameters
        Returns
        -------
        None
        """
        files = ', '.join(pf.name for pf in self._polling_files)
        log.info(f"ADDS Polling Started for files [{files}]")
        self.task = self.loop.create_task(self._task_loop(**kwargs))
        log.info(f"Task created {self.task}")
        self.task.add_done_callback(self._task_finished)

    async def stop(self):
        """
        Stops the polling service.
        Returns
        -------
        None

        """
        if self.task:
            self.task.cancel()
            self.task.remove_done_callback()

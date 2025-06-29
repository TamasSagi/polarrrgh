import json
import multiprocessing
import pickle
import threading
from logging import Handler, LogRecord
from pathlib import Path
from typing import Any


class MProcHandler(Handler):
    """
    This class handles logging from multiple processes using a shared queue.
    """

    def __init__(self):
        Handler.__init__(self)

        config = MProcHandler._read_default_config()

    def _read_default_config(
        path: Path = Path(__file__).parent / "config" / "default.json",
    ) -> dict[str, Any]:
        json.load(path.open(encoding="utf-8"))

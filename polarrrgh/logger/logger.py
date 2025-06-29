import logging
import sys
import traceback
from io import StringIO
from types import TracebackType
from typing import Type

from polarrrgh.logger.config import LoggerConfig
from polarrrgh.logger.handler import Handler
from polarrrgh.logger.mproc_handler import MProcHandler


class LogCtx:
    def __init__(self, config: LoggerConfig | None = None, mproc: bool = False):
        self.config = config if config else LoggerConfig.default()
        self.handler = MProcHandler(self.config) if mproc else Handler(self.config)

        logger = logging.getLogger(self.config.name)
        logger.setLevel(logging.DEBUG)

        # TODO: it should be restricted to add the same handler twice
        logger.addHandler(self.handler)

        sys.excepthook = lambda *args: None

    def __enter__(self):
        return logging.getLogger(self.config.name)

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType,
    ):
        if exc_tb:
            sio = StringIO()
            traceback.print_exception(exc_type, exc_value, exc_tb, limit=None, file=sio)
            s = sio.getvalue()
            sio.close()
            if s[-1:] == "\n":
                s = s[:-1]

            tb_info = traceback.extract_tb(exc_tb, 1)[0]
            record = logging.LogRecord(
                tb_info.name,
                logging.ERROR,
                tb_info.filename,
                tb_info.lineno,
                s,
                [],
                None,
            )

            self.handler.emit(record)

        self.handler.close()

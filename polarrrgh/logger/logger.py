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

        # Redirect system hook to "do nothing"
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
            record = LogCtx._exc_to_logrecord(exc_type, exc_value, exc_tb)
            self.handler.emit(record)

        self.handler.close()

    @staticmethod
    def _exc_to_logrecord(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType,
    ) -> logging.LogRecord:
        sio = StringIO()
        traceback.print_exception(exc_type, exc_value, exc_tb, limit=None, file=sio)
        exc_str = sio.getvalue()
        sio.close()

        if exc_str[-1:] == "\n":
            exc_str = exc_str[:-1]

        tb_info = traceback.extract_tb(exc_tb, 1)[0]

        return logging.LogRecord(
            name=tb_info.name,
            level=logging.ERROR,
            pathname=tb_info.filename,
            lineno=tb_info.lineno,
            msg=exc_str,
            args=[],
            exc_info=None,
        )

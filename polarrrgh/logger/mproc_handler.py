import logging
import multiprocessing
import queue
import threading

from polarrrgh.logger.config import LoggerConfig
from polarrrgh.logger.handler import Handler


class MProcHandler(Handler):
    """
    Handles logging from multiple processes using a shared queue.
    """

    SENTINEL = "BYE"

    def __init__(self, config: LoggerConfig):
        super().__init__(config)

        self.manager = multiprocessing.Manager()
        self.queue = self.manager.Queue()

        self.receiver = threading.Thread(target=self.receive, daemon=False)
        self.receiver.start()

    @staticmethod
    def _format_record(record: logging.LogRecord) -> logging.LogRecord:
        record.msg = record.msg % record.args
        record.args = None
        record.exc_info = None

        return record

    def receive(self) -> None:
        while True:
            try:
                record: logging.LogRecord = self.queue.get()

                if record == MProcHandler.SENTINEL:
                    break

                for handler in self.handlers:
                    if handler.level <= record.levelno:
                        handler.emit(record)

            except (EOFError, KeyboardInterrupt):
                break

    def emit(self, record: logging.LogRecord) -> None:
        try:
            record = MProcHandler._format_record(record)
            self.queue.put_nowait(record)
        except (ValueError, RuntimeError, queue.Full):
            self.handleError(record)

    def close(self):
        self.queue.put(MProcHandler.SENTINEL)
        self.receiver.join()

        for handler in self.handlers:
            try:
                handler.acquire()
                handler.flush()
                handler.close()

            except (OSError, ValueError):
                pass

            finally:
                handler.release()

        self.manager.shutdown()
        self.handlers.clear()

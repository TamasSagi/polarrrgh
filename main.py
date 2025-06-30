import time
from itertools import repeat
from multiprocessing import Pool

from polarrrgh.logger.log_ctx import LogCtx, MProcLogCtx, init_queue_handler


def test_simple():
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")


def test_unhandled_exc():
    logger.debug("debug")
    logger.info("info")
    x = 10 / 0
    logger.warning("warning")


def _mproc_func(name: str, queue, iter_cnt=5):
    logger = init_queue_handler(queue)

    for i in range(iter_cnt):
        logger.warning(f"{name} - {i}")
        time.sleep(0.8)


def test_multiple_processes():
    with Pool(5) as p:
        p.starmap(
            _mproc_func,
            zip(["proc#1", "proc#2", "proc#3", "proc#4", "proc#5"], repeat(queue)),
        )


if __name__ == "__main__":
    with MProcLogCtx() as (logger, queue):
        test_simple()
        # test_unhandled_exc()
        test_multiple_processes()

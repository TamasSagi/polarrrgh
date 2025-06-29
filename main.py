from polarrrgh.logger.logger import LogCtx


def main():
    logger.debug("debug")
    logger.info("info")

    x = 8 / 0
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")


if __name__ == "__main__":
    with LogCtx(mproc=True) as logger:
        main()

from core.logger import log


def handle_live_event(status: bool):

    if status:
        log.info("Live status OK")

    else:
        log.warning("Live status FAIL")
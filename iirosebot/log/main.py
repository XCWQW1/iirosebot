import sys
from loguru import logger

from iirosebot.API.api_get_config import get_log_color


def log(log_level):
    logger.remove()
    if get_log_color():
        logger.add(sys.stderr,
                   format="<w>{time:YYYY-MM-DD HH:mm:ss}</w><c>|</c><level>{level: <8}</level><c>|</c><level>{message}</level> <w>({file})</w>",
                   level=log_level, colorize=True)
    else:
        logger.add(sys.stderr,
                   format="<w>{time:YYYY-MM-DD HH:mm:ss}</w><c>|</c><level>{level: <8}</level><c>|</c><level>{message}</level> <w>({file})</w>",
                   level=log_level, colorize=False)
    logger.add("logs/{time:YYYY-MM-DD-HH-mm-ss}.log",
               format="<w>{time:YYYY-MM-DD HH:mm:ss}</w><c>|</c><level>{level: <8}</level><c>|</c><level>{message}</level> <w>({file})</w>",
               level=log_level, colorize=False)

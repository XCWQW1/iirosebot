import sys
from loguru import logger


def log(log_level):
    logger.remove()
    logger.add(sys.stderr,
               format="<w>{time:YYYY-MM-DD HH:mm:ss}</w><c>|</c><level>{level: <8}</level><c>|</c><level>{message}</level> <w>({file})</w>",
               level='INFO', colorize=True)
    logger.add("logs/{time:YYYY-MM-DD-HH-mm-ss}.log",
               format="<w>{time:YYYY-MM-DD HH:mm:ss}</w><c>|</c><level>{level: <8}</level><c>|</c><level>{message}</level> <w>({file})</w>",
               level='INFO', colorize=False)

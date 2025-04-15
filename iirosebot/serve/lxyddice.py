"""
This code belongs to you forever, lxyddice.
https://xc.null.red:8043/XCimg/img/lxyddice.png
"""

import datetime

from loguru import logger


async def lxyddice():
    life = True
    while life:
        today = datetime.date.today()
        if today.month == 10 and today.day == 5:
            logger.warning("lxyddice left the game")
        break

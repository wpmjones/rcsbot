from coc import utils
from datetime import datetime, date


def get_season_start() -> date:
    return utils.get_season_start().date()


def get_season_end() -> date:
    return utils.get_season_end().date()


def get_days_left():
    now = datetime.now()
    delta = utils.get_season_end() - now
    return delta.days + 1


def get_days_since():
    now = datetime.now()
    delta = now - utils.get_season_start()
    return delta.days


def get_season_length():
    delta = utils.get_season_end() - utils.get_season_start()
    return delta.days

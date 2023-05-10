import requests

from visualization.backend import db
from visualization.config import FINMIND_API_TOKEN
from visualization.utility.date import get_tomorrow


def get_start_date(dataset: str, start_date: str) -> str:
    sql = f"""
        select max(date) from {dataset}
    """
    result = db.query(sql)
    max_date = result[0][0]
    start_date = get_tomorrow(max_date) if max_date else start_date
    return start_date


def crontab_run(now_hour: int, crontab_hour: str):
    if crontab_hour == "*":
        return True
    elif "-" in crontab_hour:
        start_crontab_hour, end_crontab_hour = crontab_hour.split("-")
        if now_hour >= int(start_crontab_hour) and now_hour <= int(end_crontab_hour):
            return True
        else:
            return False
    else:
        if now_hour == int(crontab_hour):
            return True
        else:
            return False


def get_user_level() -> int:
    url = "https://api.web.finmindtrade.com/v2/user_info"
    parload = {
        "token": FINMIND_API_TOKEN,
    }
    resp = requests.get(url, params=parload)
    user_level = resp.json().get("level", 0)
    return user_level


def is_update_with_data_id(update_with_data_id: int) -> bool:
    user_level = get_user_level()
    if user_level < 2:
        return True
    else:
        return bool(update_with_data_id)

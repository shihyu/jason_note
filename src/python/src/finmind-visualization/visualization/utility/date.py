import datetime
import typing


def get_now() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8)


def get_today(string: bool = True) -> datetime.date:
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()
    if string:
        today = today.strftime("%Y-%m-%d")
    return today


def get_tomorrow(date: typing.Union[str, datetime.date]) -> str:
    date = (
        datetime.datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    )
    tomorrow = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    return tomorrow


def create_date(
    start_date: str,
    end_date: str = "",
    today: bool = False,
    include_start: bool = True,
    include_weekday: bool = False,
    descending: bool = True,
) -> typing.List[str]:
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    if not include_start:
        start_date = start_date + datetime.timedelta(days=1)
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = datetime.date.today()
    day_len = (
        (end_date - start_date).days + 1 if today else (end_date - start_date).days
    )
    date = [start_date + datetime.timedelta(days=day) for day in range(day_len)]
    if include_weekday:
        date = [str(d) for d in date]
    else:
        date = [str(d) for d in date if d.weekday() < 5]
    if descending:
        date = date[::-1]
    return date

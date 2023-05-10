import typing
import time

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from visualization.backend import db
from visualization.tasks.task import update_all_data_task
from visualization.utility.common import (
    crontab_run,
    get_start_date,
    is_update_with_data_id,
)
from visualization.utility.date import get_now


def get_scheduler_info_list() -> typing.List[typing.Dict[str, typing.Union[str, int]]]:
    sql = """
        SELECT
            dataset,
            update_with_data_id,
            start_date,
            crontab_hour
        FROM
            `scheduler`
        WHERE
            is_scheduler = TRUE
    """
    scheduler_info_list = [
        dict(
            dataset=data[0],
            update_with_data_id=data[1],
            start_date=data[2].strftime("%Y-%m-%d"),
            crontab_hour=data[3],
        )
        for data in db.query(sql)
    ]
    return scheduler_info_list


def run_scheduler():
    logger.info("run_scheduler")
    now = get_now()
    scheduler_info_list = get_scheduler_info_list()
    for scheduler_info in scheduler_info_list:
        if crontab_run(now_hour=now.hour, crontab_hour=scheduler_info["crontab_hour"]):
            start_date = get_start_date(
                dataset=scheduler_info["dataset"],
                start_date=scheduler_info["start_date"],
            )
            update_all_data_task(
                dataset=scheduler_info["dataset"],
                start_date=start_date,
                update_with_data_id=is_update_with_data_id(
                    update_with_data_id=scheduler_info["update_with_data_id"]
                ),
            )
            logger.info(
                f"""
                sent task
                dataset: {scheduler_info['dataset']},
                start_date: {start_date},
            """
            )


def add_job(scheduler: BackgroundScheduler) -> BackgroundScheduler:
    scheduler.add_job(
        run_scheduler, "cron", day_of_week="*", hour="*", minute="0",
    )
    return scheduler


def main():
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    scheduler = add_job(scheduler)
    scheduler.start()
    logger.info("scheduler start")


if __name__ == "__main__":
    main()
    while True:
        time.sleep(600)

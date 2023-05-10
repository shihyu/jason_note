import pandas as pd
from loguru import logger
from tqdm import tqdm

from visualization.backend import db, finmind_api
from visualization.tasks.worker import app
from visualization.utility.date import create_date


def convert_data(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) > 0:
        df = df.reset_index()
        df.columns = [
            "id",
            "securities_trader",
            "price",
            "buy",
            "sell",
            "securities_trader_id",
            "stock_id",
            "date",
        ]
    return df


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def update_data_task(
    dataset: str, start_date: str = "", end_date: str = "", data_id: str = "",
):
    logger.info(
        f"""
    dataset: {dataset},
    start_date: {start_date},
    end_date: {end_date},
    data_id: {data_id},
    """
    )
    try:
        df = finmind_api.get_data(
            dataset=dataset, data_id=data_id, start_date=start_date, end_date=end_date,
        )
        if dataset in ["TaiwanStockTradingDailyReport"]:
            df = convert_data(df)
        db.df_update2mysql(df=df, table=dataset)
    except Exception as e:
        logger.info(e)
        raise Exception(str(e))


def update_data(
    dataset: str, data_id: str = "", start_date: str = "", end_date: str = ""
):
    update_data_task.s(
        dataset=dataset, data_id=data_id, start_date=start_date, end_date=end_date,
    ).apply_async(queue="finmind")


def update_all_data_task_with_data_id(dataset: str, start_date: str, end_date: str):
    for data_id in tqdm(finmind_api.taiwan_stock_id_list):
        update_data_task.s(
            dataset=dataset, data_id=data_id, start_date=start_date, end_date=end_date,
        ).apply_async(queue="finmind")


def update_all_data_task_without_data_id(dataset: str, start_date: str, end_date: str):
    date_list = create_date(start_date=start_date, end_date=end_date, today=True)
    for start_date in tqdm(date_list):
        update_data_task.s(dataset=dataset, start_date=start_date,).apply_async(
            queue="finmind"
        )


@app.task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 5})
def update_all_data_task(
    dataset: str, start_date: str, end_date: str = "", update_with_data_id: bool = True,
):
    if dataset == "TaiwanStockInfo":
        update_data_task.s(dataset=dataset,).apply_async(queue="finmind")
    elif update_with_data_id:
        update_all_data_task_with_data_id(
            dataset=dataset, start_date=start_date, end_date=end_date
        )
    else:
        update_all_data_task_without_data_id(
            dataset=dataset, start_date=start_date, end_date=end_date
        )


def update_all_data(
    dataset: str, start_date: str, end_date: str, update_with_data_id: bool
):
    update_all_data_task.s(
        dataset=dataset,
        start_date=start_date,
        end_date=end_date,
        update_with_data_id=update_with_data_id,
    ).apply_async(queue="finmind")

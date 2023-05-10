from fastapi import APIRouter, Form
from starlette.requests import Request
from starlette.responses import UJSONResponse

from visualization.schema.input import DataSetInput
from visualization.backend import db
from visualization.tasks.task import update_all_data_task


router = APIRouter()


def get_start_date(dataset: str):
    sql = f"""
        SELECT
            start_date
        FROM
            `scheduler`
        WHERE
            dataset = '{dataset}'
    """
    temp = db.query(sql)
    start_date = temp[0][0].strftime("%Y-%m-%d") if temp[0][0] else ""
    return start_date


@router.post("/sync_history_data")
async def sync_history_data(
    request: Request, dataset: DataSetInput = Form(DataSetInput.TaiwanStockPrice),
):
    update_all_data_task(
        dataset=dataset, start_date=get_start_date(dataset), update_with_data_id=True,
    )
    return UJSONResponse(
        {"msg": "", "status": 200}, headers={"Access-Control-Allow-Origin": "*"},
    )

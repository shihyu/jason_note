from fastapi import APIRouter, Form
from starlette.requests import Request
from starlette.responses import UJSONResponse

from visualization.schema.input import DataSetInput
from visualization.tasks import task

router = APIRouter()


@router.post("/update_data")
async def update_data(
    request: Request,
    dataset: DataSetInput = Form(DataSetInput.TaiwanStockPrice),
    data_id: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
):
    task.update_data(
        dataset=dataset, data_id=data_id, start_date=start_date, end_date=end_date,
    )
    return UJSONResponse(
        {"msg": "", "status": 200}, headers={"Access-Control-Allow-Origin": "*"},
    )


@router.post("/update_all_data")
async def update_all_data(
    request: Request,
    dataset: DataSetInput = Form(DataSetInput.TaiwanStockPrice),
    start_date: str = Form(""),
    end_date: str = Form(""),
    update_with_data_id: bool = Form(True),
):
    task.update_all_data(
        dataset=dataset,
        start_date=start_date,
        end_date=end_date,
        update_with_data_id=update_with_data_id,
    )
    return UJSONResponse(
        {"msg": "", "status": 200}, headers={"Access-Control-Allow-Origin": "*"},
    )

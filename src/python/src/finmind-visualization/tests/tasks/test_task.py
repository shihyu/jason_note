from visualization.tasks import task
from visualization.backend import db


def test_update_data():
    # clear table
    sql = """
    delete FROM `TaiwanStockPrice` WHERE 1
    """
    db.query(sql)
    task.update_data(
        dataset="TaiwanStockPrice",
        data_id="2330",
        start_date="2022-01-01",
        end_date="2022-05-01",
    )
    sql = """
    select count(*) FROM `TaiwanStockPrice`
    """
    count = db.query(sql)[0][0]
    assert count > 0

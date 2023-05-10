import typing

import pandas as pd
import pymysql
from loguru import logger
from tqdm import tqdm

from visualization.backend.router import Router


class DB:
    def __init__(self):
        self.router = Router()

    def _build_update_sql(
        self,
        colname: typing.List[str],
        value: typing.List[typing.Union[str, int, float]],
    ):
        update_sql = ",".join(
            [
                ' `{}` = "{}" '.format(
                    colname[i], pymysql.converters.escape_string(str(value[i]))
                )
                for i in range(len(colname))
                if str(value[i])
            ]
        )
        return update_sql

    def _build_df_update_sql(self, table: str, df: pd.DataFrame) -> typing.List[str]:
        logger.info("build_df_update_sql")
        df_columns = list(df.columns)
        sql_list = []
        for i in range(len(df)):
            temp = list(df.iloc[i])
            value = [pymysql.converters.escape_string(str(v)) for v in temp]
            sub_df_columns = [df_columns[j] for j in range(len(temp))]
            update_sql = self._build_update_sql(sub_df_columns, value)
            sql = """INSERT INTO `{}`({})VALUES ({}) ON DUPLICATE KEY UPDATE {}
                """.format(
                table,
                "`{}`".format("`,`".join(sub_df_columns)),
                '"{}"'.format('","'.join(value)),
                update_sql,
            )
            sql_list.append(sql)
        return sql_list

    def upload_data_by_pandas(self, df: pd.DataFrame, table: str):
        df.to_sql(
            con=self.router.mysql_redash_conn,
            name=table,
            if_exists="append",
            index=False,
        )
        logger.info(f"upload_data_by_pandas {len(df)}")

    def df_update2mysql(self, df: pd.DataFrame, table: str):
        try:
            self.upload_data_by_pandas(df, table)
        except Exception as e:
            logger.info(e)
            sql = self._build_df_update_sql(table, df)
            self.commit(sql=sql)

    def commit(
        self, sql: str,
    ):
        try:
            trans = self.router.mysql_redash_conn.begin()
            if isinstance(sql, list):
                for s in tqdm(sql):
                    try:
                        self.router.mysql_redash_conn.execution_options(
                            autocommit=False
                        ).execute(s)
                    except Exception as e:
                        logger.info(e)
                        logger.info(s)

            elif isinstance(sql, str):
                self.router.mysql_redash_conn.execution_options(
                    autocommit=False
                ).execute(sql)
            trans.commit()
        except Exception as e:
            trans.rollback()
            logger.info(e)

    def query(self, sql: str):
        data = self.router.mysql_redash_conn.execute(sql)
        return data.fetchall()

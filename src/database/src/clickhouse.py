from clickhouse_driver import Client

# host为ip地址，port为端口号，database为数据库名
client = Client(host="", port="", database="")
import re


def read_ck(sql, client):
    data, columns = client.execute(sql, columnar=True, with_column_types=True)
    df = pd.DataFrame({re.sub(r"\W", "_", col[0]): d for d, col in zip(data, columns)})
    return df


def to_clickhouse(data, client, table="", orderby="", partitionby="", rksj=0):
    """
    :param data: 需要存入ck的dataframe
    :param client: 建立连接的基本参数
    :param table: 存入ck中的表的表名
    :param orderby: 排序字段
    :param partitionby:
    :param rksj:
    :return:
    """
    orderby = data.dtypes.index[0] if orderby == "" else orderby
    #  partition是建立分区
    partitionbysql = "PARTITION BY %s" % partitionby if partitionby != "" else ""
    rksjsql = ",\n rksj DateTime DEFAULT now()" if rksj == 1 else ""

    def table_exist():
        return read_ch(
            """
                select * from system.parts
                where table =  '%s'
                """
            % (table),
            client,
        ).size

    def to_sqldatatype(data):
        def datatype_map(value):
            if isinstance(value, int) or isinstance(value, np.int64):
                datatype = "Int32"
            elif isinstance(value, float) or isinstance(value, np.float64):
                datatype = "Float32"
            elif isinstance(value, np.datetime64) or isinstance(value, datetime):
                datatype = "Datetime64"
            elif isinstance(value, list) or isinstance(value, np.ndarray):
                datatype = "Array(String)"
            else:
                datatype = "String"
            return datatype

        data = data.copy()
        temp = data.iloc[0]
        datatypesql = ""
        for i, j in zip(temp.index, temp.values):
            datatype = datatype_map(j)
            datatypesql = (
                datatypesql + i + " " + datatype
                if datatypesql == ""
                else datatypesql + ",\n" + i + " " + datatype
            )
            if (
                isinstance(j, int)
                or isinstance(j, np.int64)
                or isinstance(j, float)
                or isinstance(j, np.float64)
            ):
                data[i] = data[i].fillna(np.nan).copy()
            else:
                data[i] = data[i].fillna("")
        return datatypesql

    if table_exist() == 0:
        datatypesql = to_sqldatatype(data)

        read_ck(
            """
                CREATE TABLE IF NOT EXISTS %s 
                    (
                        %s
                        %s
                    )ENGINE = MergeTree()
                    ORDER BY %s
                    %s
                    --PRIMARY KEY id;
                """
            % (table, datatypesql, rksjsql, orderby, partitionbysql),
            client,
        )

    col = ",".join(data.columns.tolist())
    client.execute(
        "INSERT INTO %s (%s) VALUES" % (table, col),
        data.fillna("").values.tolist(),
        types_check=True,
    )

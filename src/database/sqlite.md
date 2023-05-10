## 把Sqlite當嵌入式KV資料庫用

https://zhuanlan.zhihu.com/p/93969678

市面上已經有很優秀的嵌入式KV資料庫了，如Berkeley DB。為什麼還需要把Sqlite當KV資料庫用呢？原因若干。

1，可能是為了好玩或者純屬無聊

2，可結合關係型資料庫與KV資料庫的優點

3，可利用一些sqlite特性做其他KV資料庫不好做的事情

4，事務管理更方便

5，sqlite更可靠，更流行

**實現思路**

使用json（或pickle）dump資料，並將資料寫入有KEY（主鍵）和VALUE兩個欄位的SQLITE庫表中。參照kv資料庫呼叫辦法實現外部介面。

**主要功能**

1，put：寫入key/value資料

2，get：獲取某個key的value

3，put_many：批次寫入key/value資料

4，keys：獲取所有key的列表

5，value：獲取所有value的列表

6，limit：利用SQL語句中limit關鍵字，獲取資料庫中“前”N條KV資料

7，random：利用SQL語句中random關鍵字，從資料庫中隨即獲取N條KV資料

8，has_key：某個key是否存在

9，cursor_execute：執行sql自訂語句

10，其他：items，pop，filter，count等

```py
import os
import json
import sqlite3
import sys
from threading import Lock

PY3 = sys.version_info >= (3,)
if PY3:
    ifilter = filter
else:
    from itertools import ifilter

DUMPS = lambda d: json.dumps(d)
LOADS = lambda d: json.loads(d)


class SDB(object):
    _DEFAULT_TABLE = "__KVS_DEFAULT_TABLE__"
    _MEMORY_DB = ":memory:"

    def __init__(self, filename):
        if filename is None or len(filename) < 1 or filename.lower() == self._MEMORY_DB:
            self.filename = self._MEMORY_DB
        else:
            self.filename = filename
        self._lock = Lock()
        self._db_init()

    def _row_factory(self, cursor, row):
        result = []
        for idx, col in enumerate(cursor.description):
            if col[0].lower() in ("k", "v"):
                result.append(LOADS(row[idx]))
            else:
                result.append(row[idx])
        return result

    def _db_init(self):
        _new_table = "CREATE TABLE IF NOT EXISTS {0} ( k PRIMARY KEY,v)".format(
            self._DEFAULT_TABLE
        )
        db = sqlite3.connect(self.filename, timeout=60, check_same_thread=False)
        db.row_factory = self._row_factory
        db.execute(_new_table)
        self._cursor = db.cursor()
        self._db = db

    def _statement_init(self):
        table = self._DEFAULT_TABLE
        return dict(
            insert="insert or replace into {0}(k,v) values(:1,:2)".format(table),
            delete="delete from {0} where k=:1".format(table),
            update="update {0} set v=:1 where k=:2".format(table),
            clear="delete from {0}".format(table),
            get="select v from {0} where k=:1".format(table),
            has_key="select count(1) from {0} where k=:1".format(table),
            keys="select k from {0}".format(table),
            values="select v from {0}".format(table),
            items="select k,v from {0}".format(table),
            count="select count(*) from {0}".format(table),
            random="select * from {0} order BY RANDOM() limit :1".format(table),
            limit="select * from {0} limit :1 offset :2".format(table),
        )

    _statements = property(_statement_init)
    del _statement_init

    def _commit(self):
        self._db.commit()

    def _rollback(self):
        self._db.rollback()

    def _insert(self, key, value):
        try:
            self._lock.acquire(True)
            self._cursor.execute(
                self._statements.get("insert"), (DUMPS(key), DUMPS(value))
            )
        finally:
            self._lock.release()

    def _update(self, key, value):
        try:
            self._lock.acquire(True)
            self._cursor.execute(
                self._statements.get("update"), (DUMPS(value), DUMPS(key))
            )
        finally:
            self._lock.release()

    def _delete(self, key):
        try:
            self._lock.acquire(True)
            self._cursor.execute(self._statements.get("delete"), (DUMPS(key),))
        finally:
            self._lock.release()

    def _query(self, method, *args):
        try:
            self._lock.acquire(True)
            return self._cursor.execute(self._statements.get(method), args)
        finally:
            self._lock.release()

    def _clear(self):
        """
        刪除所有數據,需要調用_commit方法確認刪除
        :return:
        """
        try:
            self._lock.acquire(True)
            self._cursor.execute(self._statements.get("clear"))
        except Exception as e:
            self._rollback()
            raise e
        finally:
            self._lock.release()

    def keys(self, sort=False, sort_key=None, reverse=False):
        if sort:
            return sorted(self.iterkeys(), key=sort_key, reverse=reverse)
        return list(self.iterkeys())

    def values(self, sort=False, sort_key=None, reverse=False):
        if sort:
            return sorted(self.itervalues(), key=sort_key, reverse=reverse)
        return list(self.itervalues())

    def iterkeys(self):
        for k in self._query("keys"):
            yield k[0]

    def itervalues(self):
        for k in self._query("values"):
            yield k[0]

    def items(self, sort=False, key=None, reverse=False):
        if sort:
            return sorted(self.iteritems(), key=key, reverse=reverse)
        return list(self.iteritems())

    def iteritems(self):
        for k, v in self._query("items"):
            yield k, v

    def count(self):
        return self._query("count").fetchone()[0]

    def has_key(self, key):
        return self._query("has_key", DUMPS(key)).fetchone()[0] > 0

    def get(self, key):
        data = self._query("get", DUMPS(key)).fetchone()
        if data:
            return data[0]

    def put(self, key, value):
        try:
            self._insert(key, value)
            self._commit()
        except Exception as e:
            self._rollback()
            raise e

    def pop(self, key):
        try:
            value = self.get(key)
            self._delete(key)
            self._commit()
            return value
        except Exception as e:
            self._rollback()
            raise e

    def put_many(self, rows):
        try:
            self._lock.acquire(True)
            if rows and len(rows) > 0:
                self._cursor.executemany(
                    self._statements.get("insert"),
                    [(DUMPS(k), DUMPS(v)) for k, v in rows],
                )
                self._commit()
        except Exception as e:
            self._rollback()
            raise e
        finally:
            if self._lock.locked():
                self._lock.release()

    def limit(self, limit=1, offset=0):
        rows = self._query("limit", limit, offset)
        if limit == 1:
            return rows.fetchone()
        return rows.fetchall()

    def random(self, limit=1):
        rows = self._query("random", limit)
        if limit == 1:
            return rows.fetchone()
        return rows.fetchall()

    def filter(self, func):
        return list(ifilter(func, self.items()))

    def ifilter(self, func):
        return ifilter(func, self.iteritems())

    def cursor_execute(self, sql, parameters=None):
        """
        執行SQL語句，如:SELECT K,V FROM __KVS_DEFAULT_TABLE__ WHERE K LIKE 'ABC%'
        """
        try:
            self._lock.acquire(True)
            return self._cursor.execute(sql=sql, parameters=parameters)
        finally:
            self._lock.release()

    def close(self):
        try:
            self._rollback()
            self._cursor.close()
            self._db.close()
        except:
            pass


if __name__ == "__main__":
    # 打開資料庫
    db = SDB("test.sqlite")
    # 寫入單條資料
    db.put("first", "第一條資料")
    db.put("second", dict(a=1, b=2, c=[2, 3, 4]))
    # 獲取資料
    db.get("first")
    # 寫入多條資料
    db.put_many([[1, 2], [3, 4], ["A", "abc"]])
    # 獲取key的列表
    db.keys()
```


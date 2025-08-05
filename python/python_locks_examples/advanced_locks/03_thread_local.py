#!/usr/bin/env python3
"""
threading.local (執行緒本地儲存) 使用範例
每個執行緒都有獨立的變數副本，避免鎖競爭
"""

import threading
import time
import random
from contextlib import contextmanager


# 全域執行緒本地儲存
thread_local_data = threading.local()


class DatabaseConnection:
    """模擬資料庫連線"""
    
    def __init__(self, connection_id, database_name="TestDB"):
        self.connection_id = connection_id
        self.database_name = database_name
        self.queries_count = 0
        self.connection_time = time.time()
        self.is_active = True
    
    def execute_query(self, query):
        """執行查詢"""
        if not self.is_active:
            raise RuntimeError("連線已關閉")
        
        self.queries_count += 1
        # 模擬查詢時間
        query_time = random.uniform(0.1, 0.3)
        time.sleep(query_time)
        
        result = {
            'connection_id': self.connection_id,
            'query_number': self.queries_count,
            'query': query,
            'execution_time': query_time,
            'timestamp': time.time()
        }
        
        return result
    
    def close(self):
        """關閉連線"""
        self.is_active = False
        active_time = time.time() - self.connection_time
        print(f"🔒 關閉連線 {self.connection_id} (活躍時間: {active_time:.2f}s, 執行了 {self.queries_count} 次查詢)")


class ConnectionPool:
    """使用執行緒本地儲存的連線池"""
    
    def __init__(self, database_name="MainDB"):
        self.database_name = database_name
        self.total_connections_created = 0
        self._stats_lock = threading.Lock()
        self.connection_stats = {}
    
    def get_connection(self):
        """獲取執行緒本地連線"""
        # 檢查當前執行緒是否已有連線
        if not hasattr(thread_local_data, 'db_connection'):
            # 為當前執行緒建立新連線
            thread_name = threading.current_thread().name
            
            with self._stats_lock:
                self.total_connections_created += 1
                connection_id = f"conn-{thread_name}-{self.total_connections_created}"
            
            thread_local_data.db_connection = DatabaseConnection(connection_id, self.database_name)
            print(f"🔗 為執行緒 {thread_name} 建立連線: {connection_id}")
        
        return thread_local_data.db_connection
    
    def close_connection(self):
        """關閉當前執行緒的連線"""
        if hasattr(thread_local_data, 'db_connection'):
            conn = thread_local_data.db_connection
            thread_name = threading.current_thread().name
            
            # 記錄連線統計
            with self._stats_lock:
                self.connection_stats[conn.connection_id] = {
                    'thread': thread_name,
                    'queries_executed': conn.queries_count,
                    'active_time': time.time() - conn.connection_time
                }
            
            conn.close()
            del thread_local_data.db_connection
    
    def get_stats(self):
        """獲取連線池統計"""
        with self._stats_lock:
            return {
                'total_connections_created': self.total_connections_created,
                'connection_details': self.connection_stats.copy()
            }


class UserSession:
    """模擬用戶會話"""
    
    def __init__(self):
        self.user_id = None
        self.session_id = None
        self.login_time = None
        self.request_count = 0
        self.data = {}
    
    def login(self, user_id):
        """用戶登入"""
        self.user_id = user_id
        self.session_id = f"session-{user_id}-{int(time.time())}"
        self.login_time = time.time()
        print(f"👤 用戶 {user_id} 登入，會話ID: {self.session_id}")
    
    def make_request(self, request_type):
        """處理請求"""
        if not self.user_id:
            raise RuntimeError("用戶未登入")
        
        self.request_count += 1
        thread_name = threading.current_thread().name
        
        # 模擬請求處理時間
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        request_info = {
            'request_number': self.request_count,
            'request_type': request_type,
            'processing_time': processing_time,
            'thread': thread_name,
            'timestamp': time.time()
        }
        
        print(f"📝 {thread_name}: 用戶 {self.user_id} 的第 {self.request_count} 個請求 ({request_type}) - {processing_time:.2f}s")
        return request_info
    
    def logout(self):
        """用戶登出"""
        if self.login_time:
            session_duration = time.time() - self.login_time
            print(f"👋 用戶 {self.user_id} 登出 (會話時間: {session_duration:.2f}s, 請求數: {self.request_count})")


# 全域會話儲存
user_sessions = threading.local()


def get_current_session():
    """獲取當前執行緒的用戶會話"""
    if not hasattr(user_sessions, 'session'):
        user_sessions.session = UserSession()
    return user_sessions.session


class WebRequestHandler:
    """Web 請求處理器"""
    
    def __init__(self):
        self.total_requests = 0
        self.request_stats = {}
        self._stats_lock = threading.Lock()
    
    def handle_request(self, request_id, user_id, request_type):
        """處理 Web 請求"""
        thread_name = threading.current_thread().name
        
        try:
            # 設定用戶會話
            session = get_current_session()
            if not session.user_id:
                session.login(user_id)
            
            print(f"🌐 {thread_name}: 處理請求 {request_id}")
            
            # 模擬請求處理的各個階段
            self._authenticate_user(session)
            self._fetch_user_data(session)
            result = self._process_business_logic(session, request_type)
            
            with self._stats_lock:
                self.total_requests += 1
                self.request_stats[request_id] = {
                    'user_id': user_id,
                    'thread': thread_name,
                    'request_type': request_type,
                    'processing_time': result['processing_time'],
                    'session_requests': session.request_count
                }
            
            print(f"✅ {thread_name}: 請求 {request_id} 處理完成")
            
        except Exception as e:
            print(f"❌ {thread_name}: 請求 {request_id} 處理失敗: {e}")
    
    def _authenticate_user(self, session):
        """模擬用戶認證"""
        print(f"🔐 認證用戶 {session.user_id}")
        time.sleep(random.uniform(0.05, 0.15))
    
    def _fetch_user_data(self, session):
        """模擬獲取用戶資料"""
        print(f"📋 獲取用戶 {session.user_id} 的資料")
        session.data['user_profile'] = f"profile_of_{session.user_id}"
        time.sleep(random.uniform(0.1, 0.3))
    
    def _process_business_logic(self, session, request_type):
        """模擬業務邏輯處理"""
        print(f"⚙️  處理用戶 {session.user_id} 的業務邏輯 ({request_type})")
        return session.make_request(request_type)
    
    def cleanup_session(self):
        """清理當前執行緒的會話"""
        if hasattr(user_sessions, 'session'):
            user_sessions.session.logout()
            del user_sessions.session
    
    def get_stats(self):
        """獲取統計資訊"""
        with self._stats_lock:
            return {
                'total_requests': self.total_requests,
                'request_details': self.request_stats.copy()
            }


@contextmanager
def database_transaction(connection_pool):
    """資料庫事務上下文管理器"""
    conn = connection_pool.get_connection()
    transaction_id = f"txn-{int(time.time())}-{random.randint(1000, 9999)}"
    
    try:
        print(f"🔄 開始事務 {transaction_id}")
        yield conn, transaction_id
        print(f"✅ 提交事務 {transaction_id}")
    except Exception as e:
        print(f"🔙 回滾事務 {transaction_id}: {e}")
        raise
    finally:
        print(f"🏁 結束事務 {transaction_id}")


def database_worker(pool, worker_id, num_queries=3):
    """資料庫工作者"""
    thread_name = threading.current_thread().name
    print(f"👷 工作者 {worker_id} ({thread_name}) 開始工作")
    
    try:
        with database_transaction(pool) as (conn, txn_id):
            for i in range(num_queries):
                query = f"SELECT * FROM table_{worker_id} WHERE id = {i}"
                result = conn.execute_query(query)
                print(f"📊 工作者 {worker_id}: 查詢 {i+1} 完成，耗時 {result['execution_time']:.3f}s")
                time.sleep(random.uniform(0.1, 0.3))
    
    except Exception as e:
        print(f"❌ 工作者 {worker_id} 發生錯誤: {e}")
    
    finally:
        # 清理連線
        pool.close_connection()


def web_request_worker(handler, requests):
    """Web 請求工作者"""
    try:
        for request_id, user_id, request_type in requests:
            handler.handle_request(request_id, user_id, request_type)
            time.sleep(random.uniform(0.1, 0.3))
    finally:
        handler.cleanup_session()


def test_database_connections():
    """測試資料庫連線池"""
    print("🧪 測試執行緒本地儲存 - 資料庫連線")
    print("=" * 50)
    
    pool = ConnectionPool("TestDatabase")
    threads = []
    num_workers = 4
    queries_per_worker = 3
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(
            target=database_worker, 
            args=(pool, i, queries_per_worker),
            name=f"DBWorker-{i}"
        )
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示統計
    stats = pool.get_stats()
    print(f"\n📊 資料庫連線統計:")
    print(f"   建立連線數: {stats['total_connections_created']}")
    print(f"   連線詳情:")
    
    total_queries = 0
    for conn_id, details in stats['connection_details'].items():
        print(f"     {conn_id}: {details['queries_executed']} 次查詢，活躍 {details['active_time']:.2f}s ({details['thread']})")
        total_queries += details['queries_executed']
    
    expected_queries = num_workers * queries_per_worker
    print(f"   總查詢數: {total_queries} (預期: {expected_queries})")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_web_requests():
    """測試 Web 請求處理"""
    print("\n🧪 測試執行緒本地儲存 - Web 請求")
    print("=" * 50)
    
    handler = WebRequestHandler()
    threads = []
    
    # 定義請求
    request_sets = [
        [("req-001", "alice", "login"), ("req-002", "alice", "profile"), ("req-003", "alice", "logout")],
        [("req-004", "bob", "login"), ("req-005", "bob", "search"), ("req-006", "bob", "logout")],
        [("req-007", "charlie", "login"), ("req-008", "charlie", "purchase"), ("req-009", "charlie", "logout")],
    ]
    
    start_time = time.time()
    
    # 建立請求處理執行緒
    for i, requests in enumerate(request_sets):
        t = threading.Thread(
            target=web_request_worker,
            args=(handler, requests),
            name=f"WebWorker-{i}"
        )
        threads.append(t)
        t.start()
        time.sleep(0.1)  # 稍微錯開請求時間
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # 顯示統計
    stats = handler.get_stats()
    print(f"\n📊 Web 請求統計:")
    print(f"   總請求數: {stats['total_requests']}")
    print(f"   請求詳情:")
    
    for req_id, details in stats['request_details'].items():
        print(f"     {req_id}: 用戶 {details['user_id']} ({details['request_type']}) - "
              f"{details['processing_time']:.2f}s ({details['thread']})")
    
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_thread_local_isolation():
    """測試執行緒本地儲存的隔離性"""
    print("\n🧪 測試執行緒本地儲存隔離性")
    print("=" * 50)
    
    results = {}
    results_lock = threading.Lock()
    
    def isolation_worker(worker_id):
        # 設定執行緒本地變數
        thread_local_data.worker_id = worker_id
        thread_local_data.counter = 0
        thread_local_data.data = []
        
        # 每個執行緒獨立操作
        for i in range(5):
            thread_local_data.counter += 1
            thread_local_data.data.append(f"item-{worker_id}-{i}")
            time.sleep(0.1)
        
        # 收集結果
        with results_lock:
            results[worker_id] = {
                'worker_id': thread_local_data.worker_id,
                'counter': thread_local_data.counter,
                'data_count': len(thread_local_data.data),
                'first_item': thread_local_data.data[0] if thread_local_data.data else None,
                'last_item': thread_local_data.data[-1] if thread_local_data.data else None
            }
        
        print(f"🔍 工作者 {worker_id}: 計數器={thread_local_data.counter}, "
              f"資料項目={len(thread_local_data.data)}")
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=isolation_worker, args=(i,), name=f"IsolationWorker-{i}")
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\n📊 隔離性測試結果:")
    for worker_id, result in results.items():
        print(f"   工作者 {worker_id}: 計數器={result['counter']}, "
              f"資料數量={result['data_count']}")
        print(f"      第一項: {result['first_item']}")
        print(f"      最後項: {result['last_item']}")


if __name__ == "__main__":
    test_database_connections()
    test_web_requests()
    test_thread_local_isolation()
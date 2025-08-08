# Django 網站效能診斷完整指南

## 🔍 快速診斷檢查清單

先進行這些基本檢查，快速定位問題所在：

### ⚡ 1分鐘快速檢查

```bash
# 1. 檢查伺服器資源使用率
htop
# 或
top

# 2. 檢查磁碟空間
df -h

# 3. 檢查記憶體使用
free -h

# 4. 檢查網路連線
ping google.com
curl -w "@curl-format.txt" -o /dev/null -s "http://your-site.com"
```

**curl-format.txt 內容：**
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

---

## 🌐 網路和連線測試

### 在線測試工具
```bash
# 1. GTmetrix (推薦)
# https://gtmetrix.com
# 提供詳細的效能分析和建議

# 2. Google PageSpeed Insights
# https://pagespeed.web.dev
# Google 官方工具，移動端和桌面端分析

# 3. WebPageTest
# https://www.webpagetest.org
# 可選擇不同地區測試

# 4. Pingdom
# https://tools.pingdom.com
```

### 命令列測試
```bash
# 測試網站回應時間
curl -w "Connect: %{time_connect} TTFB: %{time_starttransfer} Total: %{time_total}\n" -o /dev/null -s http://your-site.com

# 測試 DNS 解析時間
dig your-domain.com

# 測試從不同地點的連線速度
# 使用 mtr 追蹤路由
mtr your-domain.com
```

---

## 🖥️ 伺服器端效能檢查

### 系統資源監控

```bash
# 1. CPU 使用率監控
# 高 CPU 使用率可能表示程式碼效率問題
watch -n 1 'cat /proc/loadavg'

# 2. 記憶體使用監控
# 記憶體不足會導致 swap，大幅降低效能
watch -n 1 'free -h'

# 3. 磁碟 I/O 監控
# 高磁碟使用率會拖慢資料庫查詢
iostat -x 1

# 4. 網路使用監控
iftop
# 或
nethogs
```

### 資料庫效能檢查

```bash
# PostgreSQL 檢查
sudo -u postgres psql -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# MySQL 檢查
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW STATUS LIKE 'Slow_queries';"

# 檢查慢查詢日誌
tail -f /var/log/mysql/slow.log
# 或
tail -f /var/log/postgresql/postgresql.log
```

---

## 🐍 Django 應用效能診斷

### 1. Django Debug Toolbar（開發環境）

```python
# settings.py（僅開發環境）
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # Debug Toolbar 設定
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }
    
    # 內部 IP 設定（如果是遠端伺服器）
    INTERNAL_IPS = ['127.0.0.1', 'YOUR_EXTERNAL_IP']
```

**安裝指令：**
```bash
pip install django-debug-toolbar
```

### 2. Django 效能分析工具

```python
# 在 views.py 中加入效能測量
import time
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

logger = logging.getLogger(__name__)

def performance_monitor(view_func):
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # 轉換為毫秒
        logger.info(f"View {view_func.__name__} took {duration:.2f}ms")
        
        return response
    return wrapper

# 使用裝飾器
@performance_monitor
def my_view(request):
    # 你的 view 邏輯
    pass
```

### 3. 資料庫查詢優化檢查

```python
# 在 Django shell 中檢查查詢
python manage.py shell

# 檢查 N+1 查詢問題
from django.db import connection
from django.conf import settings

# 開啟查詢記錄
settings.DEBUG = True

# 執行你的查詢
from myapp.models import MyModel
queryset = MyModel.objects.all()
for obj in queryset:
    print(obj.related_field.name)  # 這可能造成 N+1 問題

# 查看執行的 SQL
print(len(connection.queries))
for query in connection.queries:
    print(query['sql'])
```

**優化方案：**
```python
# 使用 select_related（一對一、多對一）
queryset = MyModel.objects.select_related('foreign_key_field')

# 使用 prefetch_related（一對多、多對多）
queryset = MyModel.objects.prefetch_related('many_to_many_field')

# 組合使用
queryset = MyModel.objects.select_related('user').prefetch_related('tags')

# 只選擇需要的欄位
queryset = MyModel.objects.only('id', 'name', 'created_at')

# 或排除不需要的欄位
queryset = MyModel.objects.defer('large_text_field')
```

---

## 📊 效能監控腳本

### 自動化監控腳本

```bash
#!/bin/bash
# Django 效能監控腳本
# 儲存為 monitor_performance.sh

LOG_FILE="/var/log/django_performance.log"
SITE_URL="https://your-site.com"

echo "$(date): 開始效能檢查" >> "$LOG_FILE"

# 1. 檢查網站回應時間
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s "$SITE_URL")
echo "$(date): 網站回應時間: ${RESPONSE_TIME}s" >> "$LOG_FILE"

# 2. 檢查伺服器資源
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f"), $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')

echo "$(date): CPU使用率: ${CPU_USAGE}%" >> "$LOG_FILE"
echo "$(date): 記憶體使用率: ${MEMORY_USAGE}%" >> "$LOG_FILE"
echo "$(date): 磁碟使用率: ${DISK_USAGE}" >> "$LOG_FILE"

# 3. 檢查 Gunicorn 程序
GUNICORN_PROCESSES=$(pgrep -c gunicorn)
echo "$(date): Gunicorn 程序數: ${GUNICORN_PROCESSES}" >> "$LOG_FILE"

# 4. 如果回應時間超過 3 秒，發送警告
if (( $(echo "$RESPONSE_TIME > 3.0" | bc -l) )); then
    echo "$(date): 警告! 網站回應時間過慢: ${RESPONSE_TIME}s" >> "$LOG_FILE"
    # 可以在這裡加入發送通知的邏輯
fi

echo "$(date): 效能檢查完成" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
```

**設定定期執行：**
```bash
# 給予執行權限
chmod +x monitor_performance.sh

# 加入 crontab（每10分鐘執行一次）
crontab -e
# 加入這行：
*/10 * * * * /path/to/monitor_performance.sh
```

---

## 🚀 Django 效能優化建議

### 1. 快取策略

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,  # 5分鐘
    }
}

# 快取用法
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# View 層快取
@cache_page(60 * 5)  # 快取5分鐘
def my_view(request):
    # 你的邏輯
    pass

# Template 快取
{% load cache %}
{% cache 300 sidebar %}
    <!-- 耗時的模板內容 -->
{% endcache %}

# 低階快取
def expensive_function():
    result = cache.get('expensive_result')
    if result is None:
        # 執行昂貴的計算
        result = perform_expensive_calculation()
        cache.set('expensive_result', result, 300)
    return result
```

### 2. 資料庫優化

```python
# models.py - 添加資料庫索引
class MyModel(models.Model):
    name = models.CharField(max_length=100, db_index=True)  # 單一索引
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'created_at']),  # 複合索引
            models.Index(fields=['-created_at']),  # 降序索引
        ]

# 資料庫連線池
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,  # 最大連線數
        },
        'CONN_MAX_AGE': 600,  # 連線重用時間（秒）
    }
}
```

### 3. 靜態檔案優化

```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 壓縮靜態檔案
INSTALLED_APPS += ['compressor']
STATICFILES_FINDERS += ['compressor.finders.CompressorFinder']

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True  # 預先壓縮
```

**Nginx 靜態檔案配置：**
```nginx
# /etc/nginx/sites-available/your-site
server {
    # ... 其他配置

    # 靜態檔案直接由 Nginx 服務
    location /static/ {
        alias /path/to/your/static/files/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # 啟用 gzip 壓縮
        gzip on;
        gzip_types text/css application/javascript image/svg+xml;
    }
    
    location /media/ {
        alias /path/to/your/media/files/;
        expires 7d;
    }
}
```

---

## 🔧 進階診斷工具

### 1. APM 工具（生產環境推薦）

```python
# 安裝 New Relic（免費版可用）
pip install newrelic

# settings.py
if not DEBUG:
    import newrelic.agent
    newrelic.agent.initialize('/path/to/newrelic.ini')

# 或使用 Sentry 效能監控
pip install sentry-sdk

SENTRY_DSN = "your-sentry-dsn"
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,  # 效能監控採樣率
    profiles_sample_rate=1.0,  # 效能分析採樣率
)
```

### 2. 程式碼分析工具

```bash
# 安裝分析工具
pip install django-silk
pip install py-spy

# 使用 py-spy 分析執行中的 Python 程序
sudo py-spy record -o profile.svg --pid $(pgrep -f gunicorn)

# 使用 cProfile 分析特定功能
python -m cProfile -o profile.stats manage.py runserver
```

### 3. 記憶體分析

```python
# 記憶體使用分析
import tracemalloc
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        tracemalloc.start()
        
        # 執行你的邏輯
        # ...
        
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
        print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
        tracemalloc.stop()
```

---

## 📈 效能基準測試

### 建立效能基準

```bash
# 使用 Apache Bench 進行壓力測試
ab -n 100 -c 10 http://your-site.com/

# 使用 wrk 進行更詳細的測試
wrk -t12 -c400 -d30s http://your-site.com/

# 測試特定頁面的載入時間
for i in {1..10}; do
    curl -w "Try $i: %{time_total}s\n" -o /dev/null -s http://your-site.com/
done
```

### 效能目標設定

**良好的效能指標：**
- **首次內容繪製 (FCP)**：< 1.8 秒
- **最大內容繪製 (LCP)**：< 2.5 秒
- **累積版面配置偏移 (CLS)**：< 0.1
- **首次輸入延遲 (FID)**：< 100 毫秒
- **伺服器回應時間 (TTFB)**：< 600 毫秒

---

## ✅ 快速修復檢查清單

### 立即可做的優化

- [ ] **啟用 Gzip 壓縮**（Nginx 層級）
- [ ] **設定靜態檔案快取**（30天過期）
- [ ] **優化圖片大小**（WebP 格式，適當尺寸）
- [ ] **移除未使用的 CSS/JS**
- [ ] **啟用資料庫連線池**
- [ ] **加入關鍵查詢的資料庫索引**
- [ ] **實作基本快取策略**

### 中期優化

- [ ] **設定 Redis 快取**
- [ ] **優化資料庫查詢**（解決 N+1 問題）
- [ ] **實作 CDN**（Cloudflare 免費版）
- [ ] **程式碼分析和重構**
- [ ] **升級伺服器硬體**（如需要）

### 長期優化

- [ ] **微服務架構**（如適用）
- [ ] **資料庫讀寫分離**
- [ ] **搜尋引擎**（Elasticsearch）
- [ ] **訊息佇列**（Celery + Redis）
- [ ] **效能監控系統**

使用這個指南，你應該能夠找出網站速度慢的根本原因並針對性地進行優化！
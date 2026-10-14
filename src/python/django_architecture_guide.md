# Django 架構與專案結構完整指南

> 本指南以白話方式介紹 Django 的系統架構與專案結構，幫助初學者快速掌握 Django 的運作原理和開發實務。

## 🏗️ Django 系統架構總覽

Django 採用 MTV (Model-Template-View) 架構模式，實際上是 MVC 模式的變體：

```
┌─────────────────────────────────────────┐
│             Web Browser                 │  ← 使用者介面
│  • HTML/CSS/JavaScript                  │
│  • HTTP Request/Response                │
└─────────────────────────────────────────┘
                     ↕️
┌─────────────────────────────────────────┐
│            Web Server                   │  ← 網頁伺服器層
│  • Apache/Nginx/Gunicorn                │
│  • Static File Serving                  │
│  • Load Balancing                       │
└─────────────────────────────────────────┘
                     ↕️
┌─────────────────────────────────────────┐
│           Django Framework              │  ← Django 框架層
│  ┌────────────────────────────────────┐ │
│  │        URL Dispatcher              │ │  ← URLs 路由
│  └────────────────────────────────────┘ │
│                     ↓                   │
│  ┌────────────────────────────────────┐ │
│  │           Views                    │ │  ← 控制邏輯
│  │  • Function-based Views            │ │
│  │  • Class-based Views               │ │
│  │  • Business Logic                  │ │
│  └────────────────────────────────────┘ │
│           ↙️                    ↘️      │
│  ┌──────────────┐  ┌────────────────┐   │
│  │     Models   │  │    Templates   │   │
│  │  • ORM       │  │  • HTML + DTL  │   │  ← 資料層 & 呈現層
│  │  • Database  │  │  • Jinja2      │   │
│  │  • Validation│  │  • Static Files│   │
│  └──────────────┘  └────────────────┘   │
└─────────────────────────────────────────┘
                     ↕️
┌─────────────────────────────────────────┐
│              Database                   │  ← 資料庫層
│  • PostgreSQL/MySQL/SQLite              │
│  • Redis (快取/Session)                 │
│  • Elasticsearch (搜尋)                 │
└─────────────────────────────────────────┘
```

### MTV 架構詳解

| 層級 | 全名 | 職責 | 對應 MVC | 開發者接觸度 |
|------|------|------|----------|-------------|
| **Model** | 資料模型 | 資料結構定義、ORM、驗證 | Model | ⭐⭐⭐⭐⭐ 高頻使用 |
| **Template** | 模板系統 | HTML 生成、資料呈現 | View | ⭐⭐⭐⭐ 經常使用 |
| **View** | 視圖邏輯 | 業務邏輯、請求處理 | Controller | ⭐⭐⭐⭐⭐ 高頻使用 |
| **URL** | 路由配置 | URL 映射、請求分發 | Router | ⭐⭐⭐ 常用 |

## 📁 Django 專案結構深度解析

### 標準專案目錄結構

```
my_django_project/
├── 🚀 manage.py                    # Django 管理指令入口
├── 📁 my_django_project/           # 主專案設定資料夾
│   ├── __init__.py
│   ├── 🔧 settings.py              # 專案設定檔
│   │   ├── base.py                 # 基礎設定
│   │   ├── development.py          # 開發環境設定
│   │   ├── production.py           # 正式環境設定
│   │   └── testing.py              # 測試環境設定
│   ├── 🌐 urls.py                  # 主 URL 配置
│   ├── 📡 wsgi.py                  # WSGI 部署設定
│   └── ⚡ asgi.py                  # ASGI 部署設定 (非同步)
├── 📱 apps/                        # Django 應用程式資料夾
│   ├── accounts/                   # 使用者帳戶模組
│   │   ├── __init__.py
│   │   ├── 🏷️ models.py            # 資料模型
│   │   ├── 👀 views.py             # 視圖邏輯
│   │   ├── 🎨 templates/           # HTML 模板
│   │   │   └── accounts/
│   │   │       ├── login.html
│   │   │       └── profile.html
│   │   ├── 📝 forms.py             # 表單定義
│   │   ├── 🔗 urls.py              # URL 路由
│   │   ├── 👑 admin.py             # 後臺管理
│   │   ├── 📱 apps.py              # App 配置
│   │   ├── 🧪 tests.py             # 測試程式
│   │   ├── 🔧 utils.py             # 工具函數
│   │   ├── 🎯 serializers.py       # API 序列化 (DRF)
│   │   └── 📊 migrations/          # 資料庫遷移檔
│   ├── blog/                       # 部落格模組
│   ├── products/                   # 商品模組
│   └── orders/                     # 訂單模組
├── 🎨 static/                      # 靜態檔案
│   ├── css/
│   │   ├── base.css
│   │   └── app.css
│   ├── js/
│   │   ├── main.js
│   │   └── utils.js
│   ├── images/
│   └── fonts/
├── 📂 media/                       # 使用者上傳檔案
│   ├── uploads/
│   └── avatars/
├── 🧪 tests/                       # 專案層級測試
│   ├── __init__.py
│   ├── test_settings.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── 📚 docs/                        # 專案文件
│   ├── README.md
│   ├── API.md
│   └── deployment.md
├── 🔧 requirements/                # 依賴套件管理
│   ├── base.txt                    # 基礎套件
│   ├── development.txt             # 開發環境套件
│   ├── production.txt              # 正式環境套件
│   └── testing.txt                 # 測試環境套件
├── 🐳 docker/                      # Docker 相關檔案
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── 📋 .env                         # 環境變數 (不可提交)
├── 📋 .env.example                 # 環境變數範例
├── 🚫 .gitignore                   # Git 忽略檔案
└── 📄 README.md                    # 專案說明文件
```

### 核心檔案與資料夾說明

#### 🔧 `settings.py` - 專案配置核心
```python
# settings/base.py - 基礎設定
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 安全性設定
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = []

# Django 應用程式
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_extensions',
    'crispy_forms',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.blog',
    'apps.products',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 資料庫設定
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# 國際化
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True
```

#### 📱 Django App 結構詳解
```python
# models.py - 資料模型
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

# views.py - 視圖邏輯
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    context = {'title': '首頁'}
    return render(request, 'home.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        # 處理表單提交
        pass
    return render(request, 'accounts/profile.html')

# urls.py - URL 路由
from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
]
```

## 🚀 開發工作流程

### 1. 專案建立與設定
```bash
# 安裝 Django
pip install django

# 建立專案
django-admin startproject my_project
cd my_project

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements/development.txt
```

### 2. 建立 Django App
```bash
# 建立新的應用程式
python manage.py startapp blog

# 或建立在 apps 資料夾中
mkdir apps
python manage.py startapp blog apps/blog
```

### 3. 資料庫操作
```bash
# 建立遷移檔
python manage.py makemigrations

# 檢視 SQL 語句
python manage.py sqlmigrate blog 0001

# 執行遷移
python manage.py migrate

# 建立超級使用者
python manage.py createsuperuser
```

### 4. 開發除錯
```bash
# 啟動開發伺服器
python manage.py runserver

# 指定 IP 和 Port
python manage.py runserver 0.0.0.0:8000

# Django Shell
python manage.py shell

# 收集靜態檔案
python manage.py collectstatic
```

### 5. 測試與品質檢查
```bash
# 執行測試
python manage.py test

# 執行特定 App 測試
python manage.py test apps.blog

# 程式碼覆蓋率
coverage run --source='.' manage.py test
coverage report
coverage html

# 程式碼風格檢查
flake8 .
black .
isort .
```

## 🔄 Django 請求處理流程

```
瀏覽器發送 HTTP 請求
         ↓
    Web Server (Nginx/Apache)
         ↓
    WSGI Server (Gunicorn/uWSGI)
         ↓
┌──── Django Framework ────┐
│                          │
│  1. URL Dispatcher       │ ← urls.py 路由匹配
│         ↓                │
│  2. Middleware           │ ← 請求預處理
│         ↓                │
│  3. View Function        │ ← views.py 處理邏輯
│    ↙️        ↘️          │
│ Model      Template      │ ← 資料處理 & 渲染
│    ↘️        ↙️          │
│  4. HTTP Response        │ ← 回應生成
│         ↓                │
│  5. Middleware           │ ← 回應後處理
└──────────────────────────┘
         ↓
    回傳給瀏覽器
```

### 請求處理詳解

| 階段 | 處理內容 | 涉及檔案 | 說明 |
|------|----------|----------|------|
| **URL 路由** | 解析 URL 路徑 | `urls.py` | 將 URL 映射到對應的 View |
| **中介軟體** | 請求預處理 | `settings.py` | 認證、CORS、快取等 |
| **視圖處理** | 業務邏輯執行 | `views.py` | 處理請求資料、調用 Model |
| **模型操作** | 資料庫互動 | `models.py` | ORM 查詢、資料驗證 |
| **模板渲染** | 生成 HTML | `templates/` | 結合資料與樣板 |
| **回應生成** | 建立 HTTP 回應 | `views.py` | JSON、HTML、檔案下載等 |

## 🎯 Django 核心組件深入

### 1. ORM (Object-Relational Mapping)
```python
# 模型定義
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
        ]

# 查詢操作
# 基本查詢
posts = Post.objects.all()
post = Post.objects.get(id=1)
posts = Post.objects.filter(author__username='john')

# 複雜查詢
from django.db.models import Q, F, Count
posts = Post.objects.filter(
    Q(title__icontains='django') | Q(content__icontains='django')
).annotate(
    comment_count=Count('comments')
).select_related('author').prefetch_related('tags')
```

### 2. Django Admin 客製化
```python
# admin.py
from django.contrib import admin
from .models import Post, Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_published']
    list_filter = ['created_at', 'author', 'tags']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author')
        }),
        ('進階選項', {
            'classes': ('collapse',),
            'fields': ('tags', 'is_published'),
        }),
    )
```

### 3. Django REST Framework
```python
# serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author_name', 'created_at']

# views.py (API)
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        # 點讚邏輯
        return Response({'status': 'success'})
```

## 🔧 開發最佳實務

### 專案結構組織
- **應用程式模組化**：按功能領域分割 App
- **設定檔分環境**：開發、測試、正式環境分離
- **敏感資料外部化**：使用環境變數
- **遵循 Django 命名慣例**：models.py、views.py 等

### 效能最佳化
```python
# 資料庫查詢最佳化
# ❌ N+1 查詢問題
for post in Post.objects.all():
    print(post.author.username)  # 每次都查詢資料庫

# ✅ 使用 select_related
for post in Post.objects.select_related('author'):
    print(post.author.username)  # 一次查詢完成

# ✅ 使用 prefetch_related (多對多)
posts = Post.objects.prefetch_related('tags').all()

# 快取使用
from django.core.cache import cache
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 分鐘快取
def expensive_view(request):
    # 耗時操作
    data = cache.get('expensive_data')
    if not data:
        data = expensive_calculation()
        cache.set('expensive_data', data, 3600)
    return render(request, 'template.html', {'data': data})
```

### 安全性考量
```python
# settings.py 安全設定
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# 防範 SQL 注入 - 使用 ORM
# ❌ 危險做法
User.objects.extra(where=[f"username = '{username}'"])

# ✅ 安全做法
User.objects.filter(username=username)

# 防範 XSS - 模板自動跳脫
<!-- Django 模板會自動跳脫 -->
<p>{{ user_input }}</p>

<!-- 如需原始 HTML -->
<p>{{ user_input|safe }}</p>
```

## 🛠️ 開發工具與生態系

### 必備套件
```txt
# requirements/base.txt
Django>=4.2,<5.0
psycopg2-binary>=2.9.0  # PostgreSQL
Pillow>=9.0.0           # 圖片處理
django-environ>=0.9.0   # 環境變數管理

# requirements/development.txt
-r base.txt
django-debug-toolbar>=4.0
django-extensions>=3.2
ipython>=8.0
black>=22.0
flake8>=5.0
pytest-django>=4.5
factory-boy>=3.2        # 測試資料生成
```

### 推薦工具
| 工具 | 用途 | 安裝指令 |
|------|------|----------|
| **Django Debug Toolbar** | 開發除錯 | `pip install django-debug-toolbar` |
| **Django Extensions** | 管理指令擴充 | `pip install django-extensions` |
| **Celery** | 非同步任務 | `pip install celery redis` |
| **Django REST Framework** | API 開發 | `pip install djangorestframework` |
| **Django Crispy Forms** | 表單美化 | `pip install django-crispy-forms` |
| **Whitenoise** | 靜態檔案服務 | `pip install whitenoise` |
| **Sentry** | 錯誤監控 | `pip install sentry-sdk` |

### IDE 與編輯器
- **PyCharm Professional** (Django 專案支援完整)
- **VS Code** + Python 擴充套件
- **Sublime Text** + Anaconda 套件

## 🚀 部署與維運

### 部署流程
```bash
# 1. 準備正式環境
pip install -r requirements/production.txt

# 2. 環境變數設定
export DJANGO_SETTINGS_MODULE=my_project.settings.production
export SECRET_KEY="your-secret-key"
export DEBUG=False

# 3. 資料庫遷移
python manage.py migrate

# 4. 收集靜態檔案
python manage.py collectstatic --noinput

# 5. 啟動 Gunicorn
gunicorn --bind 0.0.0.0:8000 my_project.wsgi:application
```

### Docker 部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/production.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "my_project.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

## 📚 延伸學習資源

### 官方資源
- [Django 官方文件](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Packages](https://djangopackages.org/) - 套件搜尋

### 社群資源
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) - 最佳實務書籍
- [Django 中文社群](https://django-chinese-doc.readthedocs.io/)

### 進階主題
- **Django Channels** - WebSocket 支援
- **Django Q** - 分散式任務佇列
- **Django CMS** - 內容管理系統
- **Django GraphQL** - GraphQL API
- **Django Ninja** - 快速 API 開發

---

🎉 **恭喜！** 你現在對 Django 的架構和開發流程有了完整的理解。開始建構你的 Web 應用程式吧！
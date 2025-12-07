# PyMuPDF4LLM 安裝與使用指南

## 簡介

PyMuPDF4LLM 是一個基於 PyMuPDF 的工具，專門用於將 PDF 文件轉換為適合 LLM (Large Language Models) 使用的 Markdown 格式。

## 安裝步驟

### 1. 系統需求

- Python 3.8 或更高版本
- pip 套件管理工具

### 2. 安裝 PyMuPDF4LLM

```bash
pip3 install pymupdf4llm
```

或使用 Makefile：

```bash
make install
```

### 3. 驗證安裝

```bash
python3 -c "import pymupdf4llm; print(pymupdf4llm.__version__)"
```

## 使用方法

### 基本用法

#### 方法一：Python 腳本

```python
import pymupdf4llm

# 轉換 PDF 為 Markdown
pdf_path = 'input.pdf'
md_text = pymupdf4llm.to_markdown(pdf_path)

# 儲存為檔案
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(md_text)
```

#### 方法二：命令列

```bash
python3 -c "
import pymupdf4llm

pdf_path = 'input.pdf'
output_path = 'output.md'

md_text = pymupdf4llm.to_markdown(pdf_path)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(md_text)

print(f'轉換完成: {output_path}')
"
```

#### 方法三：使用 Makefile

```bash
# 轉換單一檔案（預設：上市股票行情規格書.pdf）
make convert

# 轉換指定檔案
make convert PDF=your_file.pdf
```

### 進階選項

```python
import pymupdf4llm

# 指定頁面範圍
md_text = pymupdf4llm.to_markdown(
    'input.pdf',
    pages=[0, 1, 2]  # 只轉換前三頁
)

# 自定義輸出選項
md_text = pymupdf4llm.to_markdown(
    'input.pdf',
    write_images=True,  # 提取圖片
    image_path='images'  # 圖片儲存路徑
)
```

## 功能特點

1. **保留文件結構**
   - 自動識別標題層級
   - 保留列表格式
   - 正確轉換表格

2. **中文支援**
   - 完整支援繁體中文
   - 正確處理中文字符編碼

3. **格式化輸出**
   - 生成標準 Markdown 格式
   - 適合 LLM 訓練和處理

4. **高效能**
   - 快速轉換大型 PDF
   - 低記憶體佔用

## 常見問題

### Q1: 轉換後表格格式錯亂？

**A**: PyMuPDF4LLM 會盡力保留表格格式，但複雜表格可能需要手動調整。建議使用 Markdown 表格語法檢查工具。

### Q2: 圖片無法顯示？

**A**: 使用 `write_images=True` 參數並指定 `image_path`：

```python
md_text = pymupdf4llm.to_markdown(
    'input.pdf',
    write_images=True,
    image_path='./images'
)
```

### Q3: 特殊字符亂碼？

**A**: 確保使用 UTF-8 編碼儲存：

```python
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(md_text)
```

### Q4: 記憶體不足？

**A**: 分頁處理大型 PDF：

```python
import pymupdf

doc = pymupdf.open('large.pdf')
total_pages = len(doc)

for i in range(0, total_pages, 10):  # 每次處理 10 頁
    pages = list(range(i, min(i+10, total_pages)))
    md_text = pymupdf4llm.to_markdown('large.pdf', pages=pages)
    # 處理或儲存 md_text
```

## 實際範例

### 範例 1: 批次轉換多個 PDF

```python
import pymupdf4llm
import os
from pathlib import Path

def batch_convert(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for pdf_file in input_path.glob('*.pdf'):
        print(f'正在轉換: {pdf_file.name}')

        md_text = pymupdf4llm.to_markdown(str(pdf_file))

        output_file = output_path / f'{pdf_file.stem}.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_text)

        print(f'完成: {output_file}')

# 使用範例
batch_convert('./pdfs', './markdown')
```

### 範例 2: 加入進度顯示

```python
import pymupdf4llm
import pymupdf
from tqdm import tqdm

def convert_with_progress(pdf_path, output_path):
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)

    print(f'總頁數: {total_pages}')

    md_text = pymupdf4llm.to_markdown(pdf_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_text)

    print(f'轉換完成: {output_path}')
    print(f'檔案大小: {len(md_text)} 字元')

# 使用範例
convert_with_progress('input.pdf', 'output.md')
```

### 範例 3: 提取特定頁面

```python
import pymupdf4llm

def extract_pages(pdf_path, start_page, end_page, output_path):
    """
    提取 PDF 指定頁面範圍並轉換為 Markdown

    Args:
        pdf_path: PDF 檔案路徑
        start_page: 起始頁（從 0 開始）
        end_page: 結束頁（不含）
        output_path: 輸出檔案路徑
    """
    pages = list(range(start_page, end_page))
    md_text = pymupdf4llm.to_markdown(pdf_path, pages=pages)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_text)

    print(f'已提取第 {start_page+1} 到 {end_page} 頁')
    print(f'輸出: {output_path}')

# 使用範例：提取第 1-10 頁
extract_pages('input.pdf', 0, 10, 'output_pages_1-10.md')
```

## 與其他工具比較

| 工具 | 優點 | 缺點 |
|------|------|------|
| **PyMuPDF4LLM** | 快速、輕量、中文支援佳 | 表格複雜度有限 |
| MinerU | 表格識別強、支援 OCR | 需要下載模型、較慢 |
| pdfplumber | 表格處理優秀 | 不直接輸出 Markdown |
| pdf2md | 簡單易用 | 格式保留較差 |

## 參考資源

- [PyMuPDF4LLM GitHub](https://github.com/pymupdf/PyMuPDF4LLM)
- [PyMuPDF 官方文檔](https://pymupdf.readthedocs.io/)
- [Markdown 語法指南](https://www.markdownguide.org/)

## 授權

PyMuPDF4LLM 使用 AGPL-3.0 授權。

## 更新日誌

- **v0.2.6** (2024): 改進表格識別
- **v0.2.0** (2024): 支援圖片提取
- **v0.1.0** (2023): 首次發布

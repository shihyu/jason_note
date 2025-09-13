# PaddleOCR 安裝指南與使用範例

## 系統需求
- Python 3.7+ (建議使用 3.8-3.11)
- pip 套件管理工具

## 安裝步驟

### 1. 安裝 PaddlePaddle 核心框架
```bash
# CPU 版本
pip install paddlepaddle

# GPU 版本 (需要 CUDA 11.2)
pip install paddlepaddle-gpu
```

### 2. 安裝 PaddleOCR
```bash
pip install paddleocr
```

### 3. 安裝額外依賴（選用）
```bash
# 如需處理 PDF
pip install pypdf2

# 如需更好的圖片處理
pip install pillow opencv-python
```

## 使用範例

### 基本 OCR 識別
```python
from paddleocr import PaddleOCR

# 初始化 PaddleOCR
ocr = PaddleOCR(
    use_angle_cls=True,  # 使用角度分類
    lang='ch'            # 語言：'ch'(中文), 'en'(英文), 'japan'(日文)
)

# 執行 OCR
result = ocr.ocr('your_image.jpg')

# 顯示結果
for line in result[0]:
    print(f"文字: {line[1][0]}, 信心度: {line[1][1]:.2f}")
```

### 進階設定範例
```python
from paddleocr import PaddleOCR

# 進階配置
ocr = PaddleOCR(
    use_angle_cls=True,           # 使用文字角度分類
    lang='ch',                     # 語言設定
    det_model_dir='./det_model',   # 自訂偵測模型路徑
    rec_model_dir='./rec_model',   # 自訂識別模型路徑
    use_gpu=False,                 # 是否使用 GPU
    show_log=False                 # 是否顯示日誌
)

# 批次處理多張圖片
image_list = ['image1.jpg', 'image2.jpg', 'image3.jpg']
for img_path in image_list:
    result = ocr.ocr(img_path)
    print(f"\n{img_path} 的識別結果:")
    for line in result[0]:
        print(f"  {line[1][0]}")
```

### 網路圖片 OCR
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# 使用網路圖片
url = "https://example.com/image.png"
result = ocr.predict(input=url)

# 儲存結果
for res in result:
    res.print()                    # 印出結果
    res.save_to_img("output")      # 儲存視覺化圖片
    res.save_to_json("output")     # 儲存 JSON 格式結果
```

### 表格識別
```python
from paddleocr import PPStructure

# 初始化表格識別
table_engine = PPStructure(show_log=False)

# 識別表格
result = table_engine('table_image.jpg')

# 處理結果
for line in result:
    if line['type'] == 'table':
        # 表格內容在 line['res'] 中
        print("找到表格")
        print(line['res'])
```

## 常見問題

### 1. ModuleNotFoundError: No module named 'paddle'
**解決方案**: 先安裝 paddlepaddle
```bash
pip install paddlepaddle
```

### 2. 模型自動下載失敗
**解決方案**: 手動下載模型並指定路徑
```python
ocr = PaddleOCR(
    det_model_dir='./models/det',
    rec_model_dir='./models/rec'
)
```

### 3. GPU 相關錯誤
**解決方案**: 改用 CPU 模式
```python
ocr = PaddleOCR(use_gpu=False)
```

### 4. 記憶體不足
**解決方案**: 降低圖片解析度或分批處理
```python
ocr = PaddleOCR(
    det_limit_side_len=960,  # 限制圖片最大邊長
    det_limit_type='max'
)
```

## 支援的語言

| 語言代碼 | 語言 | 說明 |
|---------|------|------|
| ch | 中文簡繁體 | 預設，支援簡體和繁體 |
| en | 英文 | 純英文文檔 |
| japan | 日文 | 日文文檔 |
| korean | 韓文 | 韓文文檔 |
| french | 法文 | 法文文檔 |
| german | 德文 | 德文文檔 |
| latin | 拉丁文 | 支援拉丁字母的多種語言 |

## 輸出格式說明

### OCR 結果格式
```python
[
    [
        [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 文字框座標
        ('識別的文字', 0.95)                         # 文字內容和信心度
    ],
    ...
]
```

### JSON 輸出格式
```json
{
    "res": {
        "rec_texts": ["文字1", "文字2"],
        "rec_scores": [0.98, 0.97],
        "dt_polys": [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],
        "rec_boxes": [[x_min, y_min, x_max, y_max], ...]
    }
}
```

## 效能優化建議

1. **批次處理**: 一次處理多張圖片比逐張處理更有效率
2. **調整圖片大小**: 過大的圖片會影響處理速度
3. **使用 GPU**: 如有 NVIDIA GPU，使用 GPU 版本可大幅提升速度
4. **關閉不需要的功能**: 如不需要角度分類，設定 `use_angle_cls=False`
5. **模型選擇**:
   - 快速版: `PP-OCRv4_mobile`
   - 精確版: `PP-OCRv4_server`

## 參考連結
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [官方文檔](https://paddlepaddle.github.io/PaddleOCR/)
- [模型庫](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md)
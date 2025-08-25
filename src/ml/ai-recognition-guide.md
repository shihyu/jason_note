# AI 語音與影像辨識技術指南

## 📋 目錄
- [語音辨識技術](#語音辨識技術)
- [影像辨識技術](#影像辨識技術)
- [多模態應用](#多模態應用)
- [安裝指南](#安裝指南)
- [實際應用案例](#實際應用案例)

---

## 🎤 語音辨識技術

### 1. OpenAI Whisper（推薦）

**特點：**
- 離線運行，保護隱私
- 支援 99 種語言
- 準確度極高
- 免費開源

**安裝：**
```bash
pip install openai-whisper
```

**基本使用：**
```python
import whisper

# 載入模型 (tiny, base, small, medium, large)
model = whisper.load_model("base")

# 辨識音檔
result = model.transcribe("audio.mp3")
print(result["text"])

# 支援中文
result = model.transcribe("chinese_audio.mp3", language="zh")
print(result["text"])

# 取得時間戳記
result = model.transcribe("audio.mp3", verbose=True)
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

### 2. Google Speech-to-Text

**特點：**
- 雲端服務，準確度高
- 支援即時串流
- 自動標點符號

**安裝：**
```bash
pip install google-cloud-speech
```

**使用範例：**
```python
from google.cloud import speech
import io

def transcribe_file(speech_file):
    """轉錄本地音檔"""
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="zh-TW",  # 繁體中文
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)
    
    for result in response.results:
        print(f"轉錄結果: {result.alternatives[0].transcript}")
        print(f"信心分數: {result.alternatives[0].confidence}")
```

### 3. 即時語音辨識

**安裝：**
```bash
pip install SpeechRecognition pyaudio
```

**即時麥克風辨識：**
```python
import speech_recognition as sr

def live_speech_recognition():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print("調整環境噪音...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    print("開始說話...")
    
    while True:
        try:
            with mic as source:
                # 設定超時時間
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
            # 使用 Google API（免費）
            text = recognizer.recognize_google(audio, language="zh-TW")
            print(f"你說: {text}")
            
            # 也可以使用 Whisper
            # text = recognizer.recognize_whisper(audio, language="chinese")
            
        except sr.UnknownValueError:
            pass  # 無法辨識
        except sr.RequestError as e:
            print(f"錯誤: {e}")
        except KeyboardInterrupt:
            print("\n停止辨識")
            break

if __name__ == "__main__":
    live_speech_recognition()
```

---

## 📷 影像辨識技術

### 1. YOLO v8（物件偵測）

**特點：**
- 即時偵測
- 高準確度
- 支援影片串流

**安裝：**
```bash
pip install ultralytics
```

**使用範例：**
```python
from ultralytics import YOLO
import cv2

# 載入預訓練模型
model = YOLO('yolov8n.pt')  # n=nano, s=small, m=medium, l=large, x=extra large

# 圖片偵測
def detect_image(image_path):
    results = model(image_path)
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # 取得座標
            x1, y1, x2, y2 = box.xyxy[0]
            # 取得類別和信心分數
            conf = box.conf[0]
            cls = box.cls[0]
            print(f"偵測到: {model.names[int(cls)]} (信心度: {conf:.2f})")
    
    # 儲存結果
    results[0].save(filename='result.jpg')

# 影片即時偵測
def detect_video(video_path):
    cap = cv2.VideoCapture(video_path)  # 或使用 0 為攝影機
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        results = model(frame)
        annotated_frame = results[0].plot()
        
        cv2.imshow('YOLOv8 偵測', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

### 2. Transformers 影像分類

**安裝：**
```bash
pip install transformers torch pillow
```

**使用範例：**
```python
from transformers import pipeline
from PIL import Image

# 建立分類器
classifier = pipeline("image-classification", 
                     model="google/vit-base-patch16-224")

def classify_image(image_path):
    image = Image.open(image_path)
    results = classifier(image)
    
    print("影像分類結果:")
    for item in results[:5]:  # 顯示前5個結果
        print(f"  {item['label']}: {item['score']:.3f}")
    
    return results

# 物件偵測
detector = pipeline("object-detection", 
                   model="facebook/detr-resnet-50")

def detect_objects(image_path):
    image = Image.open(image_path)
    results = detector(image)
    
    print("偵測到的物件:")
    for item in results:
        print(f"  {item['label']}: {item['score']:.2f}")
        print(f"    位置: {item['box']}")
    
    return results
```

### 3. 臉部辨識

**安裝：**
```bash
pip install face-recognition opencv-python
```

**使用範例：**
```python
import face_recognition
import cv2
import numpy as np

def face_detection_and_recognition():
    # 載入已知人臉
    known_image = face_recognition.load_image_file("person1.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]
    
    known_face_encodings = [known_encoding]
    known_face_names = ["Person 1"]
    
    # 開啟攝影機
    video_capture = cv2.VideoCapture(0)
    
    while True:
        ret, frame = video_capture.read()
        
        # 轉換 BGR (OpenCV) 到 RGB (face_recognition)
        rgb_frame = frame[:, :, ::-1]
        
        # 找出所有臉部位置和編碼
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # 比對臉部
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            
            # 計算距離找出最佳匹配
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            
            # 畫框和標籤
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        
        cv2.imshow('Video', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()
```

---

## 🔄 多模態應用

### 1. CLIP - 圖文匹配

**安裝：**
```bash
pip install transformers torch pillow
```

**使用範例：**
```python
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def image_text_similarity(image_path, text_descriptions):
    """計算圖片與文字描述的相似度"""
    image = Image.open(image_path)
    
    # 處理輸入
    inputs = processor(
        text=text_descriptions, 
        images=image, 
        return_tensors="pt", 
        padding=True
    )
    
    # 計算相似度
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    
    # 顯示結果
    for i, (desc, prob) in enumerate(zip(text_descriptions, probs[0])):
        print(f"{desc}: {prob:.2%}")
    
    # 回傳最可能的描述
    max_idx = probs.argmax()
    return text_descriptions[max_idx]

# 使用範例
descriptions = [
    "一隻貓在睡覺",
    "一隻狗在玩球",
    "一個人在跑步",
    "一輛車在路上"
]

best_match = image_text_similarity("test_image.jpg", descriptions)
print(f"\n最佳匹配: {best_match}")
```

### 2. 影片理解（結合語音和視覺）

```python
import whisper
import cv2
from ultralytics import YOLO
import numpy as np

class VideoAnalyzer:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.yolo_model = YOLO('yolov8n.pt')
    
    def analyze_video(self, video_path):
        """完整分析影片內容"""
        # 提取音訊並轉錄
        audio_text = self.transcribe_audio(video_path)
        
        # 分析視覺內容
        visual_summary = self.analyze_visual(video_path)
        
        return {
            "audio_transcript": audio_text,
            "visual_summary": visual_summary
        }
    
    def transcribe_audio(self, video_path):
        """提取並轉錄音訊"""
        # 使用 ffmpeg 提取音訊（需要先安裝 ffmpeg）
        import subprocess
        audio_path = "temp_audio.wav"
        subprocess.run([
            "ffmpeg", "-i", video_path, 
            "-vn", "-acodec", "pcm_s16le", 
            "-ar", "16000", "-ac", "1", 
            audio_path, "-y"
        ])
        
        result = self.whisper_model.transcribe(audio_path)
        return result["text"]
    
    def analyze_visual(self, video_path, sample_rate=30):
        """分析視覺內容"""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        detected_objects = {}
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每 sample_rate 幀分析一次
            if frame_count % sample_rate == 0:
                results = self.yolo_model(frame)
                
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        label = self.yolo_model.names[cls]
                        
                        if label not in detected_objects:
                            detected_objects[label] = 0
                        detected_objects[label] += 1
            
            frame_count += 1
        
        cap.release()
        return detected_objects

# 使用範例
analyzer = VideoAnalyzer()
results = analyzer.analyze_video("sample_video.mp4")
print("語音內容:", results["audio_transcript"])
print("視覺內容:", results["visual_summary"])
```

---

## 📦 安裝指南

### 基礎環境設定

```bash
# 建立虛擬環境
python -m venv ai_recognition_env
source ai_recognition_env/bin/activate  # Linux/Mac
# 或
ai_recognition_env\Scripts\activate  # Windows

# 升級 pip
pip install --upgrade pip
```

### 完整安裝套件

```bash
# 語音辨識套件
pip install openai-whisper
pip install SpeechRecognition
pip install pyaudio  # 可能需要額外安裝 portaudio

# 影像辨識套件
pip install ultralytics  # YOLO
pip install transformers  # Hugging Face models
pip install torch torchvision  # PyTorch
pip install opencv-python  # OpenCV
pip install face-recognition  # 臉部辨識

# 工具套件
pip install pillow  # 圖片處理
pip install numpy  # 數值運算
pip install matplotlib  # 視覺化
```

### Docker 容器設定

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

---

## 💡 實際應用案例

### 1. 智慧會議系統

**功能：**
- 即時語音轉文字紀錄
- 發言者識別
- 重點摘要生成

```python
class SmartMeetingSystem:
    def __init__(self):
        self.whisper_model = whisper.load_model("medium")
        self.speakers = {}
    
    def process_meeting(self, audio_file):
        # 轉錄會議內容
        result = self.whisper_model.transcribe(
            audio_file,
            language="zh",
            verbose=True
        )
        
        # 產生時間戳記的逐字稿
        transcript = []
        for segment in result["segments"]:
            transcript.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"],
                "speaker": self.identify_speaker(segment)  # 需實作
            })
        
        return transcript
```

### 2. 智慧安防系統

**功能：**
- 人臉識別門禁
- 異常行為偵測
- 即時警報通知

```python
class SecuritySystem:
    def __init__(self):
        self.yolo_model = YOLO('yolov8x.pt')
        self.known_faces = self.load_known_faces()
        self.alert_actions = ['fighting', 'falling', 'running']
    
    def monitor_camera(self, camera_id):
        cap = cv2.VideoCapture(camera_id)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # 物件和行為偵測
            results = self.yolo_model(frame)
            
            # 檢查異常行為
            for r in results:
                for box in r.boxes:
                    label = self.yolo_model.names[int(box.cls[0])]
                    if label in self.alert_actions:
                        self.send_alert(f"偵測到異常行為: {label}")
            
            # 人臉識別
            faces = self.detect_faces(frame)
            for face in faces:
                if not self.is_authorized(face):
                    self.send_alert("偵測到未授權人員")
```

### 3. 無障礙輔助工具

**功能：**
- 為視障者描述環境
- 文字轉語音
- 手語翻譯

```python
class AccessibilityAssistant:
    def __init__(self):
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.yolo_model = YOLO('yolov8n.pt')
    
    def describe_scene(self, image_path):
        """為視障者描述場景"""
        image = Image.open(image_path)
        
        # 偵測物件
        results = self.yolo_model(image)
        objects = []
        for r in results:
            for box in r.boxes:
                label = self.yolo_model.names[int(box.cls[0])]
                objects.append(label)
        
        # 生成場景描述
        description = f"場景中包含: {', '.join(set(objects))}"
        
        # 使用 CLIP 獲取更詳細的描述
        scene_types = [
            "室內場景", "室外場景", "街道", "公園", 
            "辦公室", "家庭環境", "商店"
        ]
        
        inputs = self.clip_processor(
            text=scene_types, 
            images=image, 
            return_tensors="pt", 
            padding=True
        )
        
        outputs = self.clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
        best_scene = scene_types[probs.argmax()]
        
        description += f"，這似乎是一個{best_scene}"
        
        return description
```

### 4. 內容創作助手

**功能：**
- 自動生成影片字幕
- 內容標籤建議
- 精彩片段擷取

```python
class ContentCreatorAssistant:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.yolo_model = YOLO('yolov8n.pt')
    
    def generate_subtitles(self, video_path, output_srt):
        """生成 SRT 字幕檔"""
        result = self.whisper_model.transcribe(video_path)
        
        with open(output_srt, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                # SRT 格式
                f.write(f"{i}\n")
                f.write(f"{self.format_time(segment['start'])} --> {self.format_time(segment['end'])}\n")
                f.write(f"{segment['text'].strip()}\n\n")
    
    def format_time(self, seconds):
        """轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')
    
    def suggest_tags(self, video_path, num_frames=10):
        """建議影片標籤"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_interval = total_frames // num_frames
        
        all_objects = {}
        
        for i in range(0, total_frames, sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue
            
            results = self.yolo_model(frame)
            for r in results:
                for box in r.boxes:
                    label = self.yolo_model.names[int(box.cls[0])]
                    all_objects[label] = all_objects.get(label, 0) + 1
        
        cap.release()
        
        # 排序並回傳最常出現的標籤
        sorted_tags = sorted(all_objects.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:10]]
```

---

## 📚 參考資源

### 官方文檔
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text/docs)

### 教學資源
- [PyTorch 官方教學](https://pytorch.org/tutorials/)
- [OpenCV Python 教學](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [TensorFlow.js 範例](https://www.tensorflow.org/js/demos)

### 模型庫
- [Hugging Face Model Hub](https://huggingface.co/models)
- [Ultralytics Model Zoo](https://github.com/ultralytics/ultralytics)
- [TensorFlow Hub](https://tfhub.dev/)

### 資料集
- [COCO Dataset](https://cocodataset.org/)
- [ImageNet](https://www.image-net.org/)
- [Common Voice](https://commonvoice.mozilla.org/)

---

## 🎯 下一步建議

1. **入門練習：**
   - 從 Whisper 語音轉文字開始
   - 嘗試 YOLOv8 物件偵測
   - 結合兩者做簡單應用

2. **進階專案：**
   - 建立即時翻譯系統
   - 開發智慧監控應用
   - 製作無障礙輔助工具

3. **效能優化：**
   - 學習模型量化技術
   - 使用 GPU 加速
   - 部署到邊緣裝置

4. **持續學習：**
   - 關注最新論文和技術
   - 參與開源專案
   - 加入 AI 社群討論

---

## 📝 授權與注意事項

- 使用開源模型時注意授權條款
- 處理個人資料時遵守隱私法規
- 商業使用前確認模型授權
- 注意 API 使用限制和費用
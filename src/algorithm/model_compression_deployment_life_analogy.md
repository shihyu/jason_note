# 模型壓縮與部署完整指南 - 用生活比喻理解

## 🎯 核心比喻：搬家打包 vs 直接搬

### 問題：深度學習模型太大

```
情境：訓練好一個 AI 模型

訓練環境（實驗室）：
- GPU：8 張 A100（每張 $15,000）
- 記憶體：512 GB
- 模型大小：10 GB
- 推理速度：100 ms

部署環境（手機）：
- CPU：手機晶片
- 記憶體：4 GB
- 可用空間：200 MB
- 要求速度：<50 ms

問題：
❌ 模型太大（放不下）
❌ 計算太慢（用不了）
❌ 耗電太多（電池撐不住）

比喻：
就像把「豪宅」搬到「套房」
→ 需要「壓縮」和「優化」
```

---

## 📚 模型壓縮的四大技術

### 1. 剪枝（Pruning）- 斷捨離

**比喻**：搬家時丟掉不常用的東西

```
神經網路：
1000 萬個參數

發現：
- 30% 的參數「接近零」（幾乎不起作用）
- 20% 的參數「重複」（多餘）

剪枝：
移除「不重要」的參數
→ 只保留 50% 參數
→ 模型變小一半！

關鍵問題：
如何判斷「重要性」？
```

**非結構化剪枝**：

```python
def magnitude_pruning(model, sparsity=0.5):
    """
    權重剪枝

    比喻：
    丟掉「數值小」的參數
    （認為它們不重要）

    參數：
        sparsity: 稀疏度（0.5 = 保留 50%）
    """
    for layer in model.layers:
        weights = layer.weights

        # 計算閾值（保留前 50% 大的權重）
        threshold = np.percentile(np.abs(weights), sparsity * 100)

        # 創建遮罩（mask）
        mask = np.abs(weights) >= threshold

        # 應用遮罩（小於閾值的設為 0）
        layer.weights = weights * mask

    return model

# 使用
compressed_model = magnitude_pruning(model, sparsity=0.5)
# 模型大小減少 50%
```

**結構化剪枝**：

```python
def channel_pruning(model, prune_ratio=0.3):
    """
    通道剪枝

    比喻：
    移除「整個通道」（一整排神經元）
    而不是單個權重

    優點：
    - 更規則（GPU 友好）
    - 實際加速更明顯
    """
    for layer in model.conv_layers:
        # 評估每個通道的重要性
        channel_importance = []
        for channel in layer.channels:
            # 方法 1：L1 範數
            importance = np.sum(np.abs(channel.weights))

            # 方法 2：激活值統計
            # importance = np.mean(channel.activations)

            channel_importance.append(importance)

        # 移除最不重要的 30% 通道
        num_prune = int(len(channel_importance) * prune_ratio)
        prune_indices = np.argsort(channel_importance)[:num_prune]

        # 移除通道
        layer.remove_channels(prune_indices)

    return model
```

---

### 2. 量化（Quantization）- 降低精度

**比喻**：用「簡化版」代替「完整版」

```
原始模型（FP32）：
權重 = 3.14159265358979...（32 位浮點數）
大小：每個參數 4 bytes

量化模型（INT8）：
權重 = 3（8 位整數）
大小：每個參數 1 byte
→ 縮小 4 倍！

比喻：
原本：「這個蘋果重 123.456789 公克」
量化：「這個蘋果重 123 公克」
→ 精度略降，但「夠用」
```

**量化步驟**：

```python
def quantize_weights(weights, num_bits=8):
    """
    權重量化

    比喻：
    把「連續值」轉成「離散值」

    步驟：
    1. 找出最小值和最大值
    2. 分成 256 個區間（8-bit）
    3. 每個權重映射到最近的區間
    """
    # 1. 計算範圍
    w_min = np.min(weights)
    w_max = np.max(weights)

    # 2. 計算縮放因子
    num_levels = 2 ** num_bits  # 8-bit = 256 個等級
    scale = (w_max - w_min) / (num_levels - 1)

    # 3. 量化
    quantized = np.round((weights - w_min) / scale).astype(np.int8)

    # 4. 反量化（推理時）
    dequantized = quantized * scale + w_min

    return quantized, scale, w_min


# 使用
original_weights = model.layer1.weights  # FP32
quantized, scale, offset = quantize_weights(original_weights, num_bits=8)

print(f"原始大小: {original_weights.nbytes} bytes")
print(f"量化大小: {quantized.nbytes} bytes")
print(f"壓縮比: {original_weights.nbytes / quantized.nbytes:.1f}x")
```

**量化感知訓練（QAT）**：

```python
def quantization_aware_training(model, train_data):
    """
    量化感知訓練

    比喻：
    「邊訓練邊量化」
    讓模型「適應」量化誤差

    步驟：
    1. 訓練時：插入「假量化」操作
    2. 前向傳播：模擬量化效果
    3. 反向傳播：正常計算梯度
    4. 模型學會「補償」量化誤差
    """
    for epoch in range(epochs):
        for batch_x, batch_y in train_data:
            # 前向傳播（插入假量化）
            h1 = model.layer1(batch_x)
            h1_quantized = fake_quantize(h1, num_bits=8)  # 模擬量化

            h2 = model.layer2(h1_quantized)
            h2_quantized = fake_quantize(h2, num_bits=8)

            output = model.layer3(h2_quantized)

            # 計算損失並更新
            loss = compute_loss(output, batch_y)
            model.backward(loss)

    # 訓練後，直接部署（無需重新微調）
    return model


def fake_quantize(tensor, num_bits=8):
    """
    假量化（Fake Quantization）

    比喻：
    量化後立刻反量化
    保持 FP32 格式，但模擬量化誤差
    """
    # 量化
    t_min, t_max = tensor.min(), tensor.max()
    scale = (t_max - t_min) / (2**num_bits - 1)
    quantized = np.round((tensor - t_min) / scale)

    # 反量化
    dequantized = quantized * scale + t_min

    return dequantized  # 仍是 FP32，但帶量化誤差
```

---

### 3. 知識蒸餾（Knowledge Distillation）- 老師教學生

**比喻**：名師教普通學生

```
大模型（Teacher）：
- 1000 萬參數
- 準確率 95%
- 推理慢

小模型（Student）：
- 10 萬參數
- 準確率 85%（自己訓練）
- 推理快

知識蒸餾：
讓「小模型」模仿「大模型」
→ 小模型準確率提升到 92%！

關鍵：
學生不只學「答案」（hard label）
還學「思考過程」（soft label）
```

**實作**：

```python
class KnowledgeDistillation:
    def __init__(self, teacher_model, student_model, temperature=3.0):
        """
        知識蒸餾

        比喻：
        老師（大模型）教學生（小模型）

        參數：
            teacher_model: 教師模型（已訓練好）
            student_model: 學生模型（要訓練）
            temperature: 溫度參數（控制「軟化」程度）
        """
        self.teacher = teacher_model
        self.student = student_model
        self.temperature = temperature

    def soft_labels(self, logits, temperature):
        """
        軟標籤

        比喻：
        老師不只說「答案是 A」
        還說「A 有 70% 機率，B 有 20%，C 有 10%」
        → 更多資訊！

        參數：
            logits: 原始輸出（未 softmax）
            temperature: 溫度（越高越「軟」）
        """
        # 高溫 softmax（分佈更平滑）
        scaled_logits = logits / temperature
        soft = np.exp(scaled_logits) / np.sum(np.exp(scaled_logits))

        return soft

    def distillation_loss(self, student_logits, teacher_logits, true_labels, alpha=0.5):
        """
        蒸餾損失

        比喻：
        學生的成績由兩部分組成：
        1. 模仿老師（50%）
        2. 做對題目（50%）

        公式：
            Loss = α × KL(student, teacher) + (1-α) × CE(student, labels)
                   ↑                          ↑
                模仿老師                    做對題目
        """
        # 損失 1：模仿老師（KL 散度）
        teacher_soft = self.soft_labels(teacher_logits, self.temperature)
        student_soft = self.soft_labels(student_logits, self.temperature)

        kl_loss = -np.sum(teacher_soft * np.log(student_soft + 1e-8))

        # 損失 2：做對題目（交叉熵）
        ce_loss = cross_entropy(student_logits, true_labels)

        # 總損失
        total_loss = alpha * kl_loss + (1 - alpha) * ce_loss

        return total_loss

    def train_student(self, train_data, epochs=10):
        """
        訓練學生模型

        流程：
        1. 教師模型：生成軟標籤
        2. 學生模型：學習軟標籤
        3. 評估：比較學生和教師的性能
        ```"""
        for epoch in range(epochs):
            for batch_x, batch_y in train_data:
                # 1. 教師模型：生成軟標籤（不反向傳播）
                teacher_logits = self.teacher.forward(batch_x)

                # 2. 學生模型：前向傳播
                student_logits = self.student.forward(batch_x)

                # 3. 計算蒸餾損失
                loss = self.distillation_loss(
                    student_logits,
                    teacher_logits,
                    batch_y,
                    alpha=0.5
                )

                # 4. 反向傳播（只更新學生）
                self.student.backward(loss)

            # 評估
            if epoch % 10 == 0:
                accuracy = self.evaluate_student()
                print(f"Epoch {epoch}: Student Accuracy = {accuracy:.2%}")

        return self.student


# 使用範例
def distill_model():
    """蒸餾示範"""

    # 1. 訓練大模型（教師）
    teacher = ResNet152()  # 1000 萬參數
    teacher.train(train_data)
    teacher_accuracy = 95.3%

    # 2. 創建小模型（學生）
    student = MobileNet()  # 40 萬參數

    # 3. 知識蒸餾
    distiller = KnowledgeDistillation(teacher, student, temperature=3.0)
    distilled_student = distiller.train_student(train_data)

    # 4. 評估
    student_accuracy_before = 85.2%  # 直接訓練
    student_accuracy_after = 92.1%   # 蒸餾後

    print(f"教師準確率: {teacher_accuracy}")
    print(f"學生準確率（直接訓練）: {student_accuracy_before}")
    print(f"學生準確率（蒸餾後）: {student_accuracy_after}")
    print(f"提升: +{student_accuracy_after - student_accuracy_before:.1f}%")
```

---

### 4. 低秩分解（Low-Rank Factorization）- 簡化運算

**比喻**：用「快捷方式」代替「繞遠路」

```
原始矩陣乘法：
W: 1000 × 1000（100 萬個參數）
x: 1000 × 1
y = W × x（需要 100 萬次乘法）

低秩分解：
W ≈ U × V
U: 1000 × 10（1 萬個參數）
V: 10 × 1000（1 萬個參數）
總共：2 萬個參數（壓縮 50 倍！）

計算：
y = U × (V × x)
   = 1000×10 次 + 10×1000 次
   = 2 萬次乘法（加速 50 倍！）

比喻：
原本：從台北「繞一圈」到高雄
分解：台北 → 中繼站 → 高雄（更快）
```

```python
def low_rank_decomposition(weight_matrix, rank=10):
    """
    低秩分解（SVD）

    比喻：
    把「大矩陣」拆成「兩個小矩陣」

    參數：
        weight_matrix: 原始權重矩陣 (M, N)
        rank: 秩（越小壓縮越多）

    返回：
        U: (M, rank)
        V: (rank, N)
        使得 W ≈ U × V
    """
    # 奇異值分解（SVD）
    U, S, Vt = np.linalg.svd(weight_matrix, full_matrices=False)

    # 只保留前 k 個奇異值
    U_k = U[:, :rank]
    S_k = np.diag(S[:rank])
    V_k = Vt[:rank, :]

    # 重構
    U_compressed = U_k @ np.sqrt(S_k)
    V_compressed = np.sqrt(S_k) @ V_k

    # 驗證近似誤差
    reconstructed = U_compressed @ V_compressed
    error = np.linalg.norm(weight_matrix - reconstructed) / np.linalg.norm(weight_matrix)
    print(f"重構誤差: {error:.4f}")

    return U_compressed, V_compressed


# 使用
# 原始層：1000 × 1000
W = model.layer1.weights  # (1000, 1000)

# 分解
U, V = low_rank_decomposition(W, rank=10)

# 替換
model.layer1 = TwoLayerFactorized(U, V)
# 現在只需 2 萬參數（原本 100 萬）
```

---

## 🚀 模型部署策略

### 1. ONNX（Open Neural Network Exchange）

**目的**：跨框架部署

```
問題：
訓練：PyTorch
部署：TensorFlow Lite（手機）
→ 不兼容！

解決：ONNX 中間格式
PyTorch → ONNX → TensorFlow Lite
```

```python
import torch
import torch.onnx

def export_to_onnx(pytorch_model, output_path):
    """
    導出 PyTorch 模型為 ONNX

    比喻：
    把「PyTorch 語言」翻譯成「通用語言」
    ```"""
    # 創建示例輸入
    dummy_input = torch.randn(1, 3, 224, 224)

    # 導出
    torch.onnx.export(
        pytorch_model,
        dummy_input,
        output_path,
        opset_version=11,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )

    print(f"模型已導出到: {output_path}")


# 使用
model = torchvision.models.resnet50(pretrained=True)
export_to_onnx(model, "resnet50.onnx")

# 在其他框架載入
import onnxruntime
session = onnxruntime.InferenceSession("resnet50.onnx")
```

### 2. TensorRT（NVIDIA 推理加速）

**目的**：GPU 推理優化

```python
import tensorrt as trt

def optimize_with_tensorrt(onnx_path, engine_path):
    """
    用 TensorRT 優化模型

    比喻：
    針對「NVIDIA GPU」做專門優化
    → 推理速度提升 5-10 倍

    優化技術：
    1. 層融合（Layer Fusion）
    2. 精度校準（INT8 量化）
    3. 核函數優化
    ```"""
    # 創建 builder
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network()
    parser = trt.OnnxParser(network, logger)

    # 解析 ONNX
    with open(onnx_path, 'rb') as model:
        parser.parse(model.read())

    # 配置
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1 GB
    config.set_flag(trt.BuilderFlag.FP16)  # 使用 FP16

    # 構建引擎
    engine = builder.build_engine(network, config)

    # 保存
    with open(engine_path, 'wb') as f:
        f.write(engine.serialize())

    print(f"TensorRT 引擎已保存到: {engine_path}")

# 使用
optimize_with_tensorrt("model.onnx", "model.trt")
```

### 3. TensorFlow Lite（手機部署）

**目的**：移動設備推理

```python
import tensorflow as tf

def convert_to_tflite(keras_model, output_path, quantize=True):
    """
    轉換為 TensorFlow Lite

    比喻：
    把「完整版」改成「手機版」

    優化：
    1. 量化（INT8）
    2. 算子融合
    3. 移除訓練用操作
    """
    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)

    if quantize:
        # 訓練後量化
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        # 代表性數據集（用於校準）
        def representative_dataset():
            for _ in range(100):
                yield [np.random.randn(1, 224, 224, 3).astype(np.float32)]

        converter.representative_dataset = representative_dataset

        # 強制 INT8
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8

    # 轉換
    tflite_model = converter.convert()

    # 保存
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    print(f"TFLite 模型已保存到: {output_path}")
    print(f"大小: {len(tflite_model) / 1024:.2f} KB")

# 使用
model = tf.keras.applications.MobileNetV2()
convert_to_tflite(model, "mobilenet_v2.tflite", quantize=True)
```

---

## 🎯 實戰：完整壓縮流程

```python
class ModelCompressor:
    """完整的模型壓縮流程"""

    def __init__(self, model):
        self.model = model

    def compress(self, methods=['prune', 'quantize', 'distill']):
        """
        完整壓縮流程

        比喻：
        搬家的完整流程
        1. 斷捨離（剪枝）
        2. 打包壓縮（量化）
        3. 找搬家公司（蒸餾）
        """
        compressed_model = self.model.copy()

        # 1. 剪枝
        if 'prune' in methods:
            print("步驟 1: 剪枝...")
            compressed_model = self.prune_model(compressed_model, sparsity=0.5)
            self.evaluate("剪枝後", compressed_model)

        # 2. 量化
        if 'quantize' in methods:
            print("\n步驟 2: 量化...")
            compressed_model = self.quantize_model(compressed_model, bits=8)
            self.evaluate("量化後", compressed_model)

        # 3. 知識蒸餾
        if 'distill' in methods:
            print("\n步驟 3: 知識蒸餾...")
            student_model = self.create_student_model()
            compressed_model = self.distill(self.model, student_model)
            self.evaluate("蒸餾後", compressed_model)

        return compressed_model

    def evaluate(self, stage, model):
        """評估壓縮效果"""
        size = model.get_size()
        accuracy = model.evaluate(test_data)
        latency = model.measure_latency()

        print(f"{stage}:")
        print(f"  大小: {size / 1024:.2f} MB")
        print(f"  準確率: {accuracy:.2%}")
        print(f"  延遲: {latency:.2f} ms")


# 使用
compressor = ModelCompressor(large_model)
compressed = compressor.compress(methods=['prune', 'quantize', 'distill'])
```

**輸出範例**：
```
步驟 1: 剪枝...
剪枝後:
  大小: 50.00 MB（原本 100.00 MB）
  準確率: 94.2%（原本 95.0%）
  延遲: 80.00 ms（原本 100.00 ms）

步驟 2: 量化...
量化後:
  大小: 12.50 MB（壓縮 8 倍）
  準確率: 93.8%（-1.2%）
  延遲: 30.00 ms（加速 3.3 倍）

步驟 3: 知識蒸餾...
蒸餾後:
  大小: 5.00 MB（壓縮 20 倍）
  準確率: 94.5%（僅 -0.5%）
  延遲: 15.00 ms（加速 6.7 倍）
```

---

## 📊 壓縮技術比較

| 技術 | 壓縮比 | 精度損失 | 加速比 | 難度 |
|------|--------|---------|--------|------|
| **剪枝** | 2-5x | 小 | 1-2x | 中 |
| **量化** | 4x | 小-中 | 2-4x | 易 |
| **知識蒸餾** | 10-100x | 中 | 10x+ | 難 |
| **低秩分解** | 2-3x | 小 | 2-3x | 中 |
| **組合使用** | 20-100x | 中 | 10-50x | 難 |

---

## 🎓 實務建議

### 1. 壓縮策略選擇

```
場景 1：雲端推理（有 GPU）
推薦：量化（FP16）+ TensorRT
原因：高效能，略降精度可接受

場景 2：手機 APP
推薦：蒸餾 + 量化（INT8）+ TFLite
原因：模型小、省電

場景 3：邊緣設備（IoT）
推薦：極致蒸餾 + 剪枝 + 4-bit 量化
原因：資源極度受限

場景 4：要求高精度
推薦：剪枝 + FP16 量化
原因：精度損失最小
```

### 2. 壓縮-精度 Trade-off

```python
# 實驗不同壓縮等級
compression_levels = {
    'light': {
        'prune': 0.3,
        'quantize': 'fp16',
        'distill': False,
    },
    'medium': {
        'prune': 0.5,
        'quantize': 'int8',
        'distill': False,
    },
    'aggressive': {
        'prune': 0.7,
        'quantize': 'int8',
        'distill': True,
        'distill_ratio': 0.1,  # 學生模型只有 10% 大小
    }
}

# 測試
for level, config in compression_levels.items():
    compressed = compress_model(model, config)
    evaluate(compressed, level)
```

### 3. 部署檢查清單

```
✅ 模型大小：是否符合設備限制？
✅ 推理速度：是否滿足實時要求？
✅ 準確率：是否在可接受範圍？
✅ 記憶體：峰值記憶體是否過高？
✅ 電量消耗：是否耗電過多？
✅ 兼容性：目標平台是否支持？
✅ 穩定性：長時間運行是否穩定？
```

---

## 🔗 總結

### 模型壓縮核心思想

1. **剪枝**：移除不重要參數
2. **量化**：降低數值精度
3. **蒸餾**：訓練小模型模仿大模型
4. **分解**：簡化計算過程

### 主要優勢

- ✅ 模型變小（降低存儲需求）
- ✅ 推理更快（降低延遲）
- ✅ 省電（延長電池壽命）
- ✅ 降低部署成本

### 主要挑戰

- ⚠️ 精度損失（需要權衡）
- ⚠️ 壓縮工程複雜
- ⚠️ 硬體兼容性問題
- ⚠️ 調優耗時

### 實用工具

- **PyTorch Mobile**：PyTorch 模型部署
- **TensorFlow Lite**：TF 模型部署
- **ONNX Runtime**：跨平台推理
- **TensorRT**：NVIDIA GPU 優化
- **OpenVINO**：Intel CPU 優化

### 未來方向

- 神經架構搜索（NAS）自動找小模型
- 硬體感知壓縮（針對特定晶片優化）
- 動態網路（根據輸入調整計算量）
- 混合精度訓練與推理

---

*最後更新: 2025-11-26*

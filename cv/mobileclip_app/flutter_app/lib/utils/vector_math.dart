import 'dart:math' as math;
import 'dart:typed_data';

/// 向量數學工具函式
///
/// 提供常用的向量運算功能
class VectorMath {
  /// 計算向量的 L2 範數（歐幾里德距離）
  ///
  /// [vector]: 輸入向量
  ///
  /// Returns: L2 範數值
  static double l2Norm(List<double> vector) {
    double sum = 0.0;
    for (final value in vector) {
      sum += value * value;
    }
    return math.sqrt(sum);
  }

  /// L2 正規化向量
  ///
  /// 將向量正規化為單位向量（長度為 1）
  ///
  /// [vector]: 輸入向量
  ///
  /// Returns: 正規化後的向量
  static List<double> normalize(List<double> vector) {
    final norm = l2Norm(vector);

    if (norm == 0.0) {
      return List<double>.filled(vector.length, 0.0);
    }

    return vector.map((v) => v / norm).toList();
  }

  /// 計算兩個向量的點積（Dot Product）
  ///
  /// [vectorA]: 第一個向量
  /// [vectorB]: 第二個向量
  ///
  /// Returns: 點積結果
  static double dotProduct(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    double result = 0.0;
    for (int i = 0; i < vectorA.length; i++) {
      result += vectorA[i] * vectorB[i];
    }

    return result;
  }

  /// 計算兩個向量的歐幾里德距離
  ///
  /// [vectorA]: 第一個向量
  /// [vectorB]: 第二個向量
  ///
  /// Returns: 歐幾里德距離
  static double euclideanDistance(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    double sum = 0.0;
    for (int i = 0; i < vectorA.length; i++) {
      final diff = vectorA[i] - vectorB[i];
      sum += diff * diff;
    }

    return math.sqrt(sum);
  }

  /// 計算 Cosine 相似度
  ///
  /// [vectorA]: 第一個向量
  /// [vectorB]: 第二個向量
  ///
  /// Returns: 相似度分數 (0.0 ~ 1.0)
  static double cosineSimilarity(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    final dot = dotProduct(vectorA, vectorB);
    final normA = l2Norm(vectorA);
    final normB = l2Norm(vectorB);

    if (normA == 0.0 || normB == 0.0) {
      return 0.0;
    }

    final similarity = dot / (normA * normB);
    return similarity.clamp(0.0, 1.0);
  }

  /// 將 Float64List 轉換為 List<double>
  ///
  /// [data]: Float64List 資料
  ///
  /// Returns: List<double>
  static List<double> float64ListToList(Float64List data) {
    return data.toList();
  }

  /// 將 List<double> 轉換為 Float64List
  ///
  /// [data]: List<double> 資料
  ///
  /// Returns: Float64List
  static Float64List listToFloat64List(List<double> data) {
    return Float64List.fromList(data);
  }

  /// 計算向量的平均值
  ///
  /// [vector]: 輸入向量
  ///
  /// Returns: 平均值
  static double mean(List<double> vector) {
    if (vector.isEmpty) {
      return 0.0;
    }

    double sum = 0.0;
    for (final value in vector) {
      sum += value;
    }

    return sum / vector.length;
  }

  /// 計算向量的標準差
  ///
  /// [vector]: 輸入向量
  ///
  /// Returns: 標準差
  static double standardDeviation(List<double> vector) {
    if (vector.isEmpty) {
      return 0.0;
    }

    final avg = mean(vector);
    double sum = 0.0;
    for (final value in vector) {
      final diff = value - avg;
      sum += diff * diff;
    }

    return math.sqrt(sum / vector.length);
  }

  /// 向量元素加法
  ///
  /// [vectorA]: 第一個向量
  /// [vectorB]: 第二個向量
  ///
  /// Returns: A + B
  static List<double> add(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    final result = <double>[];
    for (int i = 0; i < vectorA.length; i++) {
      result.add(vectorA[i] + vectorB[i]);
    }

    return result;
  }

  /// 向量元素減法
  ///
  /// [vectorA]: 第一個向量
  /// [vectorB]: 第二個向量
  ///
  /// Returns: A - B
  static List<double> subtract(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    final result = <double>[];
    for (int i = 0; i < vectorA.length; i++) {
      result.add(vectorA[i] - vectorB[i]);
    }

    return result;
  }

  /// 向量純量乘法
  ///
  /// [vector]: 輸入向量
  /// [scalar]: 純量值
  ///
  /// Returns: vector * scalar
  static List<double> multiply(List<double> vector, double scalar) {
    return vector.map((v) => v * scalar).toList();
  }
}

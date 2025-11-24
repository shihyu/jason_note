import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/utils/vector_math.dart';
import 'dart:typed_data';
import 'dart:math' as math;

void main() {
  group('VectorMath - L2 範數', () {
    test('單位向量的 L2 範數為 1.0', () {
      final vector = [1.0, 0.0, 0.0];
      final norm = VectorMath.l2Norm(vector);
      expect(norm, closeTo(1.0, 1e-10));
    });

    test('零向量的 L2 範數為 0.0', () {
      final vector = List<double>.filled(512, 0.0);
      final norm = VectorMath.l2Norm(vector);
      expect(norm, equals(0.0));
    });

    test('計算 [3, 4] 的 L2 範數為 5.0', () {
      final vector = [3.0, 4.0];
      final norm = VectorMath.l2Norm(vector);
      expect(norm, closeTo(5.0, 1e-10));
    });

    test('512 維向量的 L2 範數計算正確', () {
      final vector = List<double>.filled(512, 1.0);
      final expectedNorm = math.sqrt(512);
      final norm = VectorMath.l2Norm(vector);
      expect(norm, closeTo(expectedNorm, 1e-10));
    });
  });

  group('VectorMath - 正規化', () {
    test('正規化向量的 L2 範數為 1.0', () {
      final vector = [3.0, 4.0];
      final normalized = VectorMath.normalize(vector);
      final norm = VectorMath.l2Norm(normalized);
      expect(norm, closeTo(1.0, 1e-10));
    });

    test('正規化 [3, 4] 得到 [0.6, 0.8]', () {
      final vector = [3.0, 4.0];
      final normalized = VectorMath.normalize(vector);
      expect(normalized[0], closeTo(0.6, 1e-10));
      expect(normalized[1], closeTo(0.8, 1e-10));
    });

    test('正規化零向量得到零向量', () {
      final vector = List<double>.filled(10, 0.0);
      final normalized = VectorMath.normalize(vector);
      expect(normalized.every((v) => v == 0.0), isTrue);
    });

    test('512 維向量正規化正確', () {
      final vector = List<double>.generate(512, (i) => i * 0.01);
      final normalized = VectorMath.normalize(vector);
      final norm = VectorMath.l2Norm(normalized);
      expect(norm, closeTo(1.0, 1e-10));
    });
  });

  group('VectorMath - 點積', () {
    test('正交向量的點積為 0', () {
      final vectorA = [1.0, 0.0, 0.0];
      final vectorB = [0.0, 1.0, 0.0];
      final dot = VectorMath.dotProduct(vectorA, vectorB);
      expect(dot, equals(0.0));
    });

    test('平行向量的點積等於長度乘積', () {
      final vectorA = [2.0, 0.0];
      final vectorB = [3.0, 0.0];
      final dot = VectorMath.dotProduct(vectorA, vectorB);
      expect(dot, closeTo(6.0, 1e-10));
    });

    test('[1, 2, 3] · [4, 5, 6] = 32', () {
      final vectorA = [1.0, 2.0, 3.0];
      final vectorB = [4.0, 5.0, 6.0];
      final dot = VectorMath.dotProduct(vectorA, vectorB);
      expect(dot, closeTo(32.0, 1e-10));
    });

    test('維度不一致拋出異常', () {
      final vectorA = [1.0, 2.0];
      final vectorB = [1.0, 2.0, 3.0];
      expect(
        () => VectorMath.dotProduct(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('VectorMath - 歐幾里德距離', () {
    test('相同向量的距離為 0', () {
      final vector = [1.0, 2.0, 3.0];
      final distance = VectorMath.euclideanDistance(vector, vector);
      expect(distance, equals(0.0));
    });

    test('[0, 0] 到 [3, 4] 的距離為 5', () {
      final vectorA = [0.0, 0.0];
      final vectorB = [3.0, 4.0];
      final distance = VectorMath.euclideanDistance(vectorA, vectorB);
      expect(distance, closeTo(5.0, 1e-10));
    });

    test('維度不一致拋出異常', () {
      final vectorA = [1.0, 2.0];
      final vectorB = [1.0, 2.0, 3.0];
      expect(
        () => VectorMath.euclideanDistance(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('VectorMath - Cosine 相似度', () {
    test('相同向量的相似度為 1.0', () {
      final vector = [1.0, 2.0, 3.0];
      final similarity = VectorMath.cosineSimilarity(vector, vector);
      expect(similarity, closeTo(1.0, 1e-10));
    });

    test('正交向量的相似度為 0.0', () {
      final vectorA = [1.0, 0.0, 0.0];
      final vectorB = [0.0, 1.0, 0.0];
      final similarity = VectorMath.cosineSimilarity(vectorA, vectorB);
      expect(similarity, closeTo(0.0, 1e-10));
    });

    test('相反向量的相似度為 0.0 (因為 clamp)', () {
      final vectorA = [1.0, 1.0];
      final vectorB = [-1.0, -1.0];
      final similarity = VectorMath.cosineSimilarity(vectorA, vectorB);
      expect(similarity, equals(0.0));
    });

    test('零向量回傳 0.0', () {
      final vectorA = [0.0, 0.0];
      final vectorB = [1.0, 1.0];
      final similarity = VectorMath.cosineSimilarity(vectorA, vectorB);
      expect(similarity, equals(0.0));
    });

    test('維度不一致拋出異常', () {
      final vectorA = [1.0, 2.0];
      final vectorB = [1.0, 2.0, 3.0];
      expect(
        () => VectorMath.cosineSimilarity(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('VectorMath - Float64List 轉換', () {
    test('List<double> 轉換為 Float64List', () {
      final list = [1.0, 2.0, 3.0, 4.0, 5.0];
      final float64List = VectorMath.listToFloat64List(list);

      expect(float64List, isA<Float64List>());
      expect(float64List.length, equals(5));
      for (int i = 0; i < list.length; i++) {
        expect(float64List[i], equals(list[i]));
      }
    });

    test('Float64List 轉換為 List<double>', () {
      final float64List = Float64List.fromList([1.0, 2.0, 3.0, 4.0, 5.0]);
      final list = VectorMath.float64ListToList(float64List);

      expect(list, isA<List<double>>());
      expect(list.length, equals(5));
      for (int i = 0; i < float64List.length; i++) {
        expect(list[i], equals(float64List[i]));
      }
    });

    test('往返轉換保持一致', () {
      final original = [1.1, 2.2, 3.3, 4.4, 5.5];
      final float64List = VectorMath.listToFloat64List(original);
      final converted = VectorMath.float64ListToList(float64List);

      expect(converted.length, equals(original.length));
      for (int i = 0; i < original.length; i++) {
        expect(converted[i], closeTo(original[i], 1e-10));
      }
    });
  });

  group('VectorMath - 統計函式', () {
    test('計算平均值', () {
      final vector = [1.0, 2.0, 3.0, 4.0, 5.0];
      final avg = VectorMath.mean(vector);
      expect(avg, closeTo(3.0, 1e-10));
    });

    test('空向量的平均值為 0.0', () {
      final vector = <double>[];
      final avg = VectorMath.mean(vector);
      expect(avg, equals(0.0));
    });

    test('計算標準差', () {
      final vector = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0];
      final std = VectorMath.standardDeviation(vector);
      expect(std, closeTo(2.0, 1e-10));
    });

    test('空向量的標準差為 0.0', () {
      final vector = <double>[];
      final std = VectorMath.standardDeviation(vector);
      expect(std, equals(0.0));
    });

    test('常數向量的標準差為 0.0', () {
      final vector = List<double>.filled(10, 5.0);
      final std = VectorMath.standardDeviation(vector);
      expect(std, equals(0.0));
    });
  });

  group('VectorMath - 向量運算', () {
    test('向量加法', () {
      final vectorA = [1.0, 2.0, 3.0];
      final vectorB = [4.0, 5.0, 6.0];
      final result = VectorMath.add(vectorA, vectorB);

      expect(result, equals([5.0, 7.0, 9.0]));
    });

    test('向量加法維度不一致拋出異常', () {
      final vectorA = [1.0, 2.0];
      final vectorB = [1.0, 2.0, 3.0];
      expect(
        () => VectorMath.add(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('向量減法', () {
      final vectorA = [5.0, 7.0, 9.0];
      final vectorB = [1.0, 2.0, 3.0];
      final result = VectorMath.subtract(vectorA, vectorB);

      expect(result, equals([4.0, 5.0, 6.0]));
    });

    test('向量減法維度不一致拋出異常', () {
      final vectorA = [1.0, 2.0];
      final vectorB = [1.0, 2.0, 3.0];
      expect(
        () => VectorMath.subtract(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('向量純量乘法', () {
      final vector = [1.0, 2.0, 3.0];
      final result = VectorMath.multiply(vector, 2.0);

      expect(result, equals([2.0, 4.0, 6.0]));
    });

    test('向量乘以 0 得到零向量', () {
      final vector = [1.0, 2.0, 3.0];
      final result = VectorMath.multiply(vector, 0.0);

      expect(result, equals([0.0, 0.0, 0.0]));
    });
  });
}

import 'dart:math' as math;
import '../models/product_model.dart';
import 'database_service.dart';
import 'log_service.dart';

/// 向量服務 - 負責特徵向量的相似度計算與商品檢索
///
/// 功能：
/// 1. 計算兩個特徵向量的 Cosine 相似度
/// 2. 從資料庫中搜尋最相似的商品
/// 3. Top-K 檢索與閾值過濾
class VectorService {
  final DatabaseService _databaseService;

  /// 預設相似度閾值（0.0 ~ 1.0）
  static const double defaultSimilarityThreshold = 0.7;

  /// 預設回傳最相似的商品數量
  static const int defaultTopK = 5;

  VectorService(this._databaseService);

  /// 計算兩個向量的 Cosine 相似度
  ///
  /// [vectorA]: 第一個特徵向量（512 維）
  /// [vectorB]: 第二個特徵向量（512 維）
  ///
  /// Returns: 相似度分數 (0.0 ~ 1.0)，1.0 表示完全相同
  double cosineSimilarity(List<double> vectorA, List<double> vectorB) {
    if (vectorA.length != vectorB.length) {
      throw ArgumentError(
        '向量維度不一致: A=${vectorA.length}, B=${vectorB.length}',
      );
    }

    if (vectorA.isEmpty) {
      throw ArgumentError('向量不可為空');
    }

    // 計算點積
    double dotProduct = 0.0;
    for (int i = 0; i < vectorA.length; i++) {
      dotProduct += vectorA[i] * vectorB[i];
    }

    // 計算 L2 norm
    double normA = 0.0;
    double normB = 0.0;
    for (int i = 0; i < vectorA.length; i++) {
      normA += vectorA[i] * vectorA[i];
      normB += vectorB[i] * vectorB[i];
    }

    normA = math.sqrt(normA);
    normB = math.sqrt(normB);

    // 避免除以零
    if (normA == 0.0 || normB == 0.0) {
      return 0.0;
    }

    // Cosine similarity = dot(A, B) / (||A|| * ||B||)
    final similarity = dotProduct / (normA * normB);

    // 限制在 [0, 1] 範圍（處理浮點數誤差）
    return similarity.clamp(0.0, 1.0);
  }

  /// 搜尋最相似的商品
  ///
  /// [queryVector]: 查詢的特徵向量（來自相機拍攝的圖片）
  /// [topK]: 回傳前 K 個最相似的商品，預設 5
  /// [threshold]: 相似度閾值，只回傳相似度 >= threshold 的商品，預設 0.7
  ///
  /// Returns: 相似商品列表，依相似度降序排列，格式為 (Product, similarity)
  Future<List<ProductMatch>> searchSimilarProducts({
    required List<double> queryVector,
    int topK = defaultTopK,
    double threshold = defaultSimilarityThreshold,
  }) async {
    try {
      // 1. 從資料庫取得所有商品
      final allProducts = await _databaseService.getAllProducts();

      if (allProducts.isEmpty) {
        log.debug('資料庫中沒有商品');
        return [];
      }

      log.debug('開始比對 ${allProducts.length} 個商品...');

      // 2. 計算每個商品的相似度
      final matches = <ProductMatch>[];
      for (final product in allProducts) {
        final similarity = cosineSimilarity(queryVector, product.featureVector);

        // 只保留相似度 >= threshold 的商品
        if (similarity >= threshold) {
          matches.add(ProductMatch(
            product: product,
            similarity: similarity,
          ));
        }
      }

      // 3. 依相似度降序排列
      matches.sort((a, b) => b.similarity.compareTo(a.similarity));

      // 4. 回傳前 K 個
      final topMatches = matches.take(topK).toList();

      log.debug('找到 ${matches.length} 個相似商品 (threshold >= $threshold)');
      log.debug('回傳前 $topK 個: ${topMatches.map((m) => '${m.product.name} (${(m.similarity * 100).toStringAsFixed(1)}%)').join(', ')}');

      return topMatches;
    } catch (e) {
      log.debug('❌ 搜尋相似商品失敗: $e');
      rethrow;
    }
  }

  /// 尋找最相似的單一商品
  ///
  /// [queryVector]: 查詢的特徵向量
  /// [threshold]: 相似度閾值，預設 0.7
  ///
  /// Returns: 最相似的商品，若沒有符合閾值的商品則回傳 null
  Future<ProductMatch?> findMostSimilarProduct({
    required List<double> queryVector,
    double threshold = defaultSimilarityThreshold,
  }) async {
    final matches = await searchSimilarProducts(
      queryVector: queryVector,
      topK: 1,
      threshold: threshold,
    );

    return matches.isEmpty ? null : matches.first;
  }

  /// 計算兩個商品的相似度
  ///
  /// [productA]: 商品 A
  /// [productB]: 商品 B
  ///
  /// Returns: 相似度分數 (0.0 ~ 1.0)
  double compareProducts(Product productA, Product productB) {
    return cosineSimilarity(productA.featureVector, productB.featureVector);
  }

  /// 批次計算查詢向量與多個商品的相似度
  ///
  /// [queryVector]: 查詢的特徵向量
  /// [products]: 商品列表
  ///
  /// Returns: Map<Product, similarity>
  Map<Product, double> batchComputeSimilarity({
    required List<double> queryVector,
    required List<Product> products,
  }) {
    final results = <Product, double>{};

    for (final product in products) {
      final similarity = cosineSimilarity(queryVector, product.featureVector);
      results[product] = similarity;
    }

    return results;
  }
}

/// 商品匹配結果
///
/// 包含商品資訊與相似度分數
class ProductMatch {
  final Product product;
  final double similarity;

  ProductMatch({
    required this.product,
    required this.similarity,
  });

  @override
  String toString() {
    return 'ProductMatch(product: ${product.name}, similarity: ${(similarity * 100).toStringAsFixed(2)}%)';
  }
}

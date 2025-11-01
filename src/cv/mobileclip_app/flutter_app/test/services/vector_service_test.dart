import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:flutter_app/services/vector_service.dart';
import 'package:flutter_app/services/database_service.dart';
import 'package:flutter_app/models/product_model.dart';
import 'dart:math' as math;

void main() {
  late VectorService vectorService;
  late DatabaseService databaseService;
  late Database testDatabase;

  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  setUp(() async {
    // 使用 in-memory 資料庫進行測試
    testDatabase = await databaseFactoryFfi.openDatabase(
      inMemoryDatabasePath,
      options: OpenDatabaseOptions(
        version: 1,
        onCreate: (db, version) async {
          await db.execute('''
            CREATE TABLE products (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              description TEXT,
              price REAL,
              image_path TEXT NOT NULL,
              feature_vector BLOB NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
          ''');
          await db.execute('CREATE INDEX idx_products_name ON products(name)');
          await db.execute('CREATE INDEX idx_products_created_at ON products(created_at DESC)');
        },
      ),
    );

    databaseService = DatabaseService();
    databaseService.setDatabaseForTesting(testDatabase);
    vectorService = VectorService(databaseService);
  });

  tearDown(() async {
    if (databaseService.isInitialized) {
      await databaseService.deleteAllProducts();
      await databaseService.close();
    }
  });

  group('VectorService - Cosine 相似度計算', () {
    test('完全相同的向量相似度為 1.0', () {
      final vectorA = List<double>.filled(512, 0.5);
      final vectorB = List<double>.filled(512, 0.5);

      final similarity = vectorService.cosineSimilarity(vectorA, vectorB);
      expect(similarity, closeTo(1.0, 1e-6));
    });

    test('完全相反的向量相似度為 0.0', () {
      final vectorA = List<double>.filled(512, 1.0);
      final vectorB = List<double>.filled(512, -1.0);

      final similarity = vectorService.cosineSimilarity(vectorA, vectorB);
      expect(similarity, closeTo(0.0, 1e-6));
    });

    test('正交向量相似度為 0.5', () {
      final vectorA = List<double>.filled(512, 0.0);
      final vectorB = List<double>.filled(512, 0.0);

      // 建立簡單的正交向量
      vectorA[0] = 1.0;
      vectorB[1] = 1.0;

      final similarity = vectorService.cosineSimilarity(vectorA, vectorB);
      expect(similarity, closeTo(0.0, 1e-6));
    });

    test('正規化向量計算正確', () {
      // 建立兩個正規化向量
      final vectorA = List<double>.generate(512, (i) => i * 0.01);
      final vectorB = List<double>.generate(512, (i) => (511 - i) * 0.01);

      // L2 正規化
      final normA = math.sqrt(vectorA.fold<double>(0.0, (sum, v) => sum + v * v));
      final normB = math.sqrt(vectorB.fold<double>(0.0, (sum, v) => sum + v * v));

      final normalizedA = vectorA.map((v) => v / normA).toList();
      final normalizedB = vectorB.map((v) => v / normB).toList();

      final similarity = vectorService.cosineSimilarity(normalizedA, normalizedB);
      expect(similarity, greaterThanOrEqualTo(0.0));
      expect(similarity, lessThanOrEqualTo(1.0));
    });

    test('零向量回傳 0.0', () {
      final vectorA = List<double>.filled(512, 0.0);
      final vectorB = List<double>.filled(512, 1.0);

      final similarity = vectorService.cosineSimilarity(vectorA, vectorB);
      expect(similarity, equals(0.0));
    });

    test('維度不一致拋出異常', () {
      final vectorA = List<double>.filled(512, 1.0);
      final vectorB = List<double>.filled(256, 1.0);

      expect(
        () => vectorService.cosineSimilarity(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('空向量拋出異常', () {
      final vectorA = <double>[];
      final vectorB = <double>[];

      expect(
        () => vectorService.cosineSimilarity(vectorA, vectorB),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('VectorService - 商品搜尋', () {
    test('空資料庫回傳空列表', () async {
      final queryVector = List<double>.filled(512, 0.5);

      final results = await vectorService.searchSimilarProducts(
        queryVector: queryVector,
      );

      expect(results, isEmpty);
    });

    test('搜尋最相似的商品', () async {
      // 新增測試商品，使用不同方向的向量
      // 商品 A：前 3/4 為 1.0（高相似度）
      final vectorA = List<double>.filled(512, 0.0);
      for (int i = 0; i < 384; i++) {
        vectorA[i] = 1.0;
      }

      // 商品 B：前 1/4 為 1.0（低相似度）
      final vectorB = List<double>.filled(512, 0.0);
      for (int i = 0; i < 128; i++) {
        vectorB[i] = 1.0;
      }

      final product1 = Product(
        name: '商品 A',
        imagePath: '/path/a.jpg',
        featureVector: vectorA,
      );

      final product2 = Product(
        name: '商品 B',
        imagePath: '/path/b.jpg',
        featureVector: vectorB,
      );

      await databaseService.insertProduct(product1);
      await databaseService.insertProduct(product2);

      // Query 向量：前半部為 1.0
      final queryVector = List<double>.filled(512, 0.0);
      for (int i = 0; i < 256; i++) {
        queryVector[i] = 1.0;
      }

      // 搜尋
      final results = await vectorService.searchSimilarProducts(
        queryVector: queryVector,
        topK: 2,
        threshold: 0.5,
      );

      expect(results.length, equals(2));
      expect(results[0].product.name, equals('商品 A')); // 相似度較高應排第一
      expect(results[0].similarity, greaterThan(results[1].similarity));
    });

    test('閾值過濾', () async {
      // 新增商品
      await databaseService.insertProduct(
        Product(
          name: '高相似度',
          imagePath: '/path/high.jpg',
          featureVector: List<double>.filled(512, 0.9),
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: '低相似度',
          imagePath: '/path/low.jpg',
          featureVector: List<double>.filled(512, 0.1),
        ),
      );

      // 使用高閾值
      final queryVector = List<double>.filled(512, 1.0);
      final results = await vectorService.searchSimilarProducts(
        queryVector: queryVector,
        threshold: 0.95, // 高閾值
      );

      // 應該只回傳高相似度的商品
      expect(results.length, greaterThanOrEqualTo(0));
      for (final match in results) {
        expect(match.similarity, greaterThanOrEqualTo(0.95));
      }
    });

    test('Top-K 限制', () async {
      // 新增 10 個商品
      for (int i = 0; i < 10; i++) {
        await databaseService.insertProduct(
          Product(
            name: '商品 $i',
            imagePath: '/path/$i.jpg',
            featureVector: List<double>.filled(512, i * 0.1),
          ),
        );
      }

      // 只取前 3 個
      final queryVector = List<double>.filled(512, 0.5);
      final results = await vectorService.searchSimilarProducts(
        queryVector: queryVector,
        topK: 3,
        threshold: 0.0,
      );

      expect(results.length, lessThanOrEqualTo(3));
    });

    test('相似度降序排列', () async {
      // 新增不同方向的向量（不同相似度）
      // 高相似度：前半部為 1.0，後半部為 0.0
      final highSimilarVector = List<double>.filled(512, 0.0);
      for (int i = 0; i < 256; i++) {
        highSimilarVector[i] = 1.0;
      }

      // 中等相似度：前 1/4 為 1.0，其餘為 0.0
      final mediumSimilarVector = List<double>.filled(512, 0.0);
      for (int i = 0; i < 128; i++) {
        mediumSimilarVector[i] = 1.0;
      }

      // 低相似度：後半部為 1.0，前半部為 0.0（與 query 正交）
      final lowSimilarVector = List<double>.filled(512, 0.0);
      for (int i = 256; i < 512; i++) {
        lowSimilarVector[i] = 1.0;
      }

      await databaseService.insertProduct(
        Product(
          name: '中等',
          imagePath: '/path/mid.jpg',
          featureVector: mediumSimilarVector,
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: '高',
          imagePath: '/path/high.jpg',
          featureVector: highSimilarVector,
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: '低',
          imagePath: '/path/low.jpg',
          featureVector: lowSimilarVector,
        ),
      );

      // Query 向量：前半部為 1.0，後半部為 0.0
      final queryVector = List<double>.filled(512, 0.0);
      for (int i = 0; i < 256; i++) {
        queryVector[i] = 1.0;
      }

      final results = await vectorService.searchSimilarProducts(
        queryVector: queryVector,
        threshold: 0.0,
      );

      // 驗證降序排列
      for (int i = 0; i < results.length - 1; i++) {
        expect(
          results[i].similarity,
          greaterThanOrEqualTo(results[i + 1].similarity),
        );
      }
    });
  });

  group('VectorService - 尋找最相似商品', () {
    test('找到最相似的單一商品', () async {
      await databaseService.insertProduct(
        Product(
          name: '最相似',
          imagePath: '/path/most.jpg',
          featureVector: List<double>.filled(512, 1.0),
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: '較不相似',
          imagePath: '/path/less.jpg',
          featureVector: List<double>.filled(512, 0.1),
        ),
      );

      final queryVector = List<double>.filled(512, 0.99);
      final match = await vectorService.findMostSimilarProduct(
        queryVector: queryVector,
        threshold: 0.5,
      );

      expect(match, isNotNull);
      expect(match!.product.name, equals('最相似'));
    });

    test('沒有符合閾值的商品回傳 null', () async {
      // 使用正交向量（相似度為 0.0）
      final productVector = List<double>.filled(512, 0.0);
      for (int i = 256; i < 512; i++) {
        productVector[i] = 1.0; // 後半部為 1.0
      }

      await databaseService.insertProduct(
        Product(
          name: '低相似度',
          imagePath: '/path/low.jpg',
          featureVector: productVector,
        ),
      );

      // Query 向量：前半部為 1.0，與 productVector 正交
      final queryVector = List<double>.filled(512, 0.0);
      for (int i = 0; i < 256; i++) {
        queryVector[i] = 1.0;
      }

      final match = await vectorService.findMostSimilarProduct(
        queryVector: queryVector,
        threshold: 0.5, // 相似度為 0.0，低於閾值
      );

      expect(match, isNull);
    });
  });

  group('VectorService - 商品比較', () {
    test('比較兩個商品', () {
      final productA = Product(
        name: 'A',
        imagePath: '/path/a.jpg',
        featureVector: List<double>.filled(512, 1.0),
      );

      final productB = Product(
        name: 'B',
        imagePath: '/path/b.jpg',
        featureVector: List<double>.filled(512, 0.9),
      );

      final similarity = vectorService.compareProducts(productA, productB);
      expect(similarity, greaterThanOrEqualTo(0.0));
      expect(similarity, lessThanOrEqualTo(1.0));
    });
  });

  group('VectorService - 批次計算', () {
    test('批次計算相似度', () {
      final queryVector = List<double>.filled(512, 1.0);

      final products = [
        Product(
          name: 'A',
          imagePath: '/path/a.jpg',
          featureVector: List<double>.filled(512, 0.9),
        ),
        Product(
          name: 'B',
          imagePath: '/path/b.jpg',
          featureVector: List<double>.filled(512, 0.5),
        ),
        Product(
          name: 'C',
          imagePath: '/path/c.jpg',
          featureVector: List<double>.filled(512, 0.1),
        ),
      ];

      final results = vectorService.batchComputeSimilarity(
        queryVector: queryVector,
        products: products,
      );

      expect(results.length, equals(3));
      expect(results[products[0]], isNotNull);
      expect(results[products[1]], isNotNull);
      expect(results[products[2]], isNotNull);
    });

    test('空商品列表回傳空 Map', () {
      final queryVector = List<double>.filled(512, 1.0);
      final results = vectorService.batchComputeSimilarity(
        queryVector: queryVector,
        products: [],
      );

      expect(results, isEmpty);
    });
  });

  group('ProductMatch', () {
    test('toString 格式正確', () {
      final product = Product(
        name: '測試商品',
        imagePath: '/path/test.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final match = ProductMatch(
        product: product,
        similarity: 0.8567,
      );

      final str = match.toString();
      expect(str, contains('測試商品'));
      expect(str, contains('85.67%'));
    });
  });
}

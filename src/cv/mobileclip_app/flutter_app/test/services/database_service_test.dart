import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:flutter_app/services/database_service.dart';
import 'package:flutter_app/models/product_model.dart';
import 'dart:math' as math;

void main() {
  late DatabaseService databaseService;
  late Database testDatabase;

  setUpAll(() {
    // 初始化 sqflite FFI (用於測試環境)
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
    // 直接注入測試用資料庫
    databaseService.setDatabaseForTesting(testDatabase);
  });

  tearDown(() async {
    // 清理測試資料
    if (databaseService.isInitialized) {
      await databaseService.deleteAllProducts();
      await databaseService.close();
    }
  });

  group('DatabaseService - 初始化', () {
    test('資料庫初始化成功', () async {
      final db = await databaseService.database;
      expect(db, isNotNull);
      expect(databaseService.isInitialized, isTrue);
    });
  });

  group('DatabaseService - CRUD 操作', () {
    test('新增商品成功', () async {
      final product = Product(
        name: '測試商品',
        description: '測試描述',
        price: 99.99,
        imagePath: '/path/to/image.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final id = await databaseService.insertProduct(product);
      expect(id, greaterThan(0));
    });

    test('查詢單一商品', () async {
      // 新增商品
      final product = Product(
        name: '測試商品 A',
        description: '描述 A',
        price: 100.0,
        imagePath: '/path/to/a.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final id = await databaseService.insertProduct(product);

      // 查詢商品
      final retrieved = await databaseService.getProduct(id);
      expect(retrieved, isNotNull);
      expect(retrieved!.name, equals('測試商品 A'));
      expect(retrieved.description, equals('描述 A'));
      expect(retrieved.price, equals(100.0));
      expect(retrieved.featureVector.length, equals(512));
    });

    test('查詢不存在的商品回傳 null', () async {
      final retrieved = await databaseService.getProduct(99999);
      expect(retrieved, isNull);
    });

    test('查詢所有商品', () async {
      // 新增多個商品
      final products = [
        Product(
          name: '商品 1',
          imagePath: '/path/1.jpg',
          featureVector: List<double>.filled(512, 0.1),
        ),
        Product(
          name: '商品 2',
          imagePath: '/path/2.jpg',
          featureVector: List<double>.filled(512, 0.2),
        ),
        Product(
          name: '商品 3',
          imagePath: '/path/3.jpg',
          featureVector: List<double>.filled(512, 0.3),
        ),
      ];

      for (final product in products) {
        await databaseService.insertProduct(product);
      }

      // 查詢所有商品
      final allProducts = await databaseService.getAllProducts();
      expect(allProducts.length, equals(3));
      expect(allProducts[0].name, equals('商品 3')); // 預設降序
    });

    test('搜尋商品（依名稱）', () async {
      // 新增商品
      await databaseService.insertProduct(
        Product(
          name: 'iPhone 15',
          imagePath: '/path/iphone.jpg',
          featureVector: List<double>.filled(512, 0.1),
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: 'MacBook Pro',
          imagePath: '/path/macbook.jpg',
          featureVector: List<double>.filled(512, 0.2),
        ),
      );

      await databaseService.insertProduct(
        Product(
          name: 'iPad Pro',
          imagePath: '/path/ipad.jpg',
          featureVector: List<double>.filled(512, 0.3),
        ),
      );

      // 搜尋包含 "Pro" 的商品
      final results = await databaseService.searchProducts('Pro');
      expect(results.length, equals(2));
      expect(results.any((p) => p.name == 'MacBook Pro'), isTrue);
      expect(results.any((p) => p.name == 'iPad Pro'), isTrue);
    });

    test('更新商品', () async {
      // 新增商品
      final product = Product(
        name: '原始商品',
        description: '原始描述',
        price: 100.0,
        imagePath: '/path/original.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final id = await databaseService.insertProduct(product);

      // 更新商品
      final retrieved = await databaseService.getProduct(id);
      final updated = retrieved!.copyWith(
        name: '更新後商品',
        description: '更新後描述',
        price: 200.0,
      );

      final count = await databaseService.updateProduct(updated);
      expect(count, equals(1));

      // 驗證更新
      final afterUpdate = await databaseService.getProduct(id);
      expect(afterUpdate!.name, equals('更新後商品'));
      expect(afterUpdate.description, equals('更新後描述'));
      expect(afterUpdate.price, equals(200.0));
    });

    test('刪除商品', () async {
      // 新增商品
      final product = Product(
        name: '待刪除商品',
        imagePath: '/path/delete.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final id = await databaseService.insertProduct(product);

      // 確認存在
      final beforeDelete = await databaseService.getProduct(id);
      expect(beforeDelete, isNotNull);

      // 刪除商品
      final count = await databaseService.deleteProduct(id);
      expect(count, equals(1));

      // 確認已刪除
      final afterDelete = await databaseService.getProduct(id);
      expect(afterDelete, isNull);
    });

    test('刪除所有商品', () async {
      // 新增多個商品
      for (int i = 0; i < 5; i++) {
        await databaseService.insertProduct(
          Product(
            name: '商品 $i',
            imagePath: '/path/$i.jpg',
            featureVector: List<double>.filled(512, 0.1),
          ),
        );
      }

      // 確認有商品
      final before = await databaseService.getAllProducts();
      expect(before.length, equals(5));

      // 刪除所有商品
      final count = await databaseService.deleteAllProducts();
      expect(count, equals(5));

      // 確認已清空
      final after = await databaseService.getAllProducts();
      expect(after.length, equals(0));
    });

    test('取得商品總數', () async {
      // 初始為 0
      final initialCount = await databaseService.getProductCount();
      expect(initialCount, equals(0));

      // 新增商品
      for (int i = 0; i < 3; i++) {
        await databaseService.insertProduct(
          Product(
            name: '商品 $i',
            imagePath: '/path/$i.jpg',
            featureVector: List<double>.filled(512, 0.1),
          ),
        );
      }

      // 確認數量
      final afterInsert = await databaseService.getProductCount();
      expect(afterInsert, equals(3));
    });
  });

  group('DatabaseService - 特徵向量序列化', () {
    test('512 維向量可正確儲存與讀取', () async {
      // 建立測試向量（每個元素有不同值）
      final testVector = List<double>.generate(512, (i) => i * 0.01);

      final product = Product(
        name: '向量測試',
        imagePath: '/path/vector_test.jpg',
        featureVector: testVector,
      );

      final id = await databaseService.insertProduct(product);

      // 讀取並驗證
      final retrieved = await databaseService.getProduct(id);
      expect(retrieved, isNotNull);
      expect(retrieved!.featureVector.length, equals(512));

      // 驗證向量值是否一致
      for (int i = 0; i < 512; i++) {
        expect(retrieved.featureVector[i], closeTo(testVector[i], 1e-10));
      }
    });

    test('正規化向量可正確儲存', () async {
      // 建立正規化向量（L2 norm = 1）
      final vector = List<double>.filled(512, 1.0 / math.sqrt(512.0));

      final product = Product(
        name: '正規化向量',
        imagePath: '/path/normalized.jpg',
        featureVector: vector,
      );

      final id = await databaseService.insertProduct(product);
      final retrieved = await databaseService.getProduct(id);

      expect(retrieved, isNotNull);
      expect(retrieved!.featureVector.length, equals(512));
    });
  });

  group('DatabaseService - 錯誤處理', () {
    test('更新不存在的商品回傳 0', () async {
      final product = Product(
        id: 99999,
        name: '不存在的商品',
        imagePath: '/path/not_exist.jpg',
        featureVector: List<double>.filled(512, 0.5),
      );

      final count = await databaseService.updateProduct(product);
      expect(count, equals(0));
    });

    test('刪除不存在的商品回傳 0', () async {
      final count = await databaseService.deleteProduct(99999);
      expect(count, equals(0));
    });
  });
}

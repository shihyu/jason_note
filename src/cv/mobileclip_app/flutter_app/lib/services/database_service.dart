import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';
import '../models/product_model.dart';
import 'log_service.dart';

/// 資料庫服務 - 負責 SQLite CRUD 操作
///
/// 功能：
/// 1. 初始化資料庫與 schema
/// 2. 新增/查詢/更新/刪除商品
/// 3. 管理商品圖片與特徵向量
class DatabaseService {
  static const String _databaseName = 'products.db';
  static const int _databaseVersion = 1;
  static const String _tableName = 'products';

  // Singleton 實作
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  Database? _database;

  /// 是否已初始化
  bool get isInitialized => _database != null;

  /// 設定測試用資料庫（僅供測試使用）
  void setDatabaseForTesting(Database db) {
    _database = db;
  }

  /// 取得資料庫實例（單例模式）
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  /// 初始化資料庫
  Future<Database> _initDatabase() async {
    try {
      log.info('初始化資料庫...');

      // 取得應用程式文件目錄
      final documentsDirectory = await getApplicationDocumentsDirectory();
      final path = join(documentsDirectory.path, _databaseName);

      log.debug('資料庫路徑: $path');

      // 開啟資料庫
      final db = await openDatabase(
        path,
        version: _databaseVersion,
        onCreate: _onCreate,
        onUpgrade: _onUpgrade,
      );

      log.info('✅ 資料庫初始化完成');
      return db;
    } catch (e) {
      log.error('❌ 資料庫初始化失敗', e);
      rethrow;
    }
  }

  /// 建立資料庫 schema
  Future<void> _onCreate(Database db, int version) async {
    log.info('建立資料庫 schema...');

    await db.execute('''
      CREATE TABLE $_tableName (
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

    // 建立索引
    await db.execute('''
      CREATE INDEX idx_products_name ON $_tableName(name)
    ''');

    await db.execute('''
      CREATE INDEX idx_products_created_at ON $_tableName(created_at DESC)
    ''');

    log.info('✅ Schema 建立完成');
  }

  /// 資料庫升級
  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    log.info('資料庫升級: $oldVersion → $newVersion');
    // 未來版本升級時實作
  }

  /// 新增商品
  ///
  /// Returns: 新增的商品 ID
  Future<int> insertProduct(Product product) async {
    try {
      final db = await database;

      final map = product.toMap();
      map['updated_at'] = DateTime.now().toIso8601String();

      final id = await db.insert(
        _tableName,
        map,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      log.info('✅ 商品已新增: ID=$id, Name=${product.name}');
      return id;
    } catch (e) {
      log.info('❌ 新增商品失敗: $e');
      rethrow;
    }
  }

  /// 查詢單一商品
  Future<Product?> getProduct(int id) async {
    try {
      final db = await database;

      final maps = await db.query(
        _tableName,
        where: 'id = ?',
        whereArgs: [id],
        limit: 1,
      );

      if (maps.isEmpty) {
        return null;
      }

      return Product.fromMap(maps.first);
    } catch (e) {
      log.info('❌ 查詢商品失敗 (ID=$id): $e');
      rethrow;
    }
  }

  /// 查詢所有商品
  ///
  /// [orderBy]: 排序欄位，預設為建立時間降序
  Future<List<Product>> getAllProducts({String? orderBy}) async {
    try {
      final db = await database;

      final maps = await db.query(
        _tableName,
        orderBy: orderBy ?? 'created_at DESC',
      );

      return maps.map((map) => Product.fromMap(map)).toList();
    } catch (e) {
      log.info('❌ 查詢所有商品失敗: $e');
      rethrow;
    }
  }

  /// 搜尋商品（依名稱）
  Future<List<Product>> searchProducts(String query) async {
    try {
      final db = await database;

      final maps = await db.query(
        _tableName,
        where: 'name LIKE ?',
        whereArgs: ['%$query%'],
        orderBy: 'created_at DESC',
      );

      return maps.map((map) => Product.fromMap(map)).toList();
    } catch (e) {
      log.info('❌ 搜尋商品失敗: $e');
      rethrow;
    }
  }

  /// 更新商品
  Future<int> updateProduct(Product product) async {
    try {
      if (product.id == null) {
        throw ArgumentError('商品 ID 不可為 null');
      }

      final db = await database;

      final map = product.toMap();
      map['updated_at'] = DateTime.now().toIso8601String();

      final count = await db.update(
        _tableName,
        map,
        where: 'id = ?',
        whereArgs: [product.id],
      );

      log.info('✅ 商品已更新: ID=${product.id}, Name=${product.name}');
      return count;
    } catch (e) {
      log.info('❌ 更新商品失敗: $e');
      rethrow;
    }
  }

  /// 刪除商品
  Future<int> deleteProduct(int id) async {
    try {
      final db = await database;

      final count = await db.delete(
        _tableName,
        where: 'id = ?',
        whereArgs: [id],
      );

      log.info('✅ 商品已刪除: ID=$id');
      return count;
    } catch (e) {
      log.info('❌ 刪除商品失敗: $e');
      rethrow;
    }
  }

  /// 刪除所有商品
  Future<int> deleteAllProducts() async {
    try {
      final db = await database;
      final count = await db.delete(_tableName);
      log.info('✅ 已刪除所有商品 (共 $count 筆)');
      return count;
    } catch (e) {
      log.info('❌ 刪除所有商品失敗: $e');
      rethrow;
    }
  }

  /// 取得商品總數
  Future<int> getProductCount() async {
    try {
      final db = await database;
      final result = await db.rawQuery('SELECT COUNT(*) FROM $_tableName');
      final count = Sqflite.firstIntValue(result) ?? 0;
      return count;
    } catch (e) {
      log.info('❌ 取得商品總數失敗: $e');
      rethrow;
    }
  }

  /// 關閉資料庫連線
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
      log.info('資料庫連線已關閉');
    }
  }
}

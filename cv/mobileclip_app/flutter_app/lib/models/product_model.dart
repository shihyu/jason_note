import 'dart:typed_data';

/// 商品資料模型
///
/// 儲存商品的基本資訊與 MobileCLIP 特徵向量
class Product {
  final int? id;
  final String name;
  final String? description;
  final double? price;
  final String imagePath;
  final List<double> featureVector;
  final DateTime createdAt;

  Product({
    this.id,
    required this.name,
    this.description,
    this.price,
    required this.imagePath,
    required this.featureVector,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now() {
    // 驗證特徵向量維度
    if (featureVector.length != 512) {
      throw ArgumentError(
        '特徵向量必須是 512 維，當前為 ${featureVector.length} 維',
      );
    }
  }

  /// 從資料庫 Map 建立 Product
  factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      id: map['id'] as int?,
      name: map['name'] as String,
      description: map['description'] as String?,
      price: map['price'] as double?,
      imagePath: map['image_path'] as String,
      featureVector: _bytesToVector(map['feature_vector'] as Uint8List),
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }

  /// 轉換為資料庫 Map
  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'description': description,
      'price': price,
      'image_path': imagePath,
      'feature_vector': _vectorToBytes(featureVector),
      'created_at': createdAt.toIso8601String(),
    };
  }

  /// 複製並修改部分欄位
  Product copyWith({
    int? id,
    String? name,
    String? description,
    double? price,
    String? imagePath,
    List<double>? featureVector,
    DateTime? createdAt,
  }) {
    return Product(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      price: price ?? this.price,
      imagePath: imagePath ?? this.imagePath,
      featureVector: featureVector ?? this.featureVector,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() {
    return 'Product(id: $id, name: $name, price: $price, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is Product &&
        other.id == id &&
        other.name == name &&
        other.description == description &&
        other.price == price &&
        other.imagePath == imagePath &&
        other.createdAt == createdAt;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        name.hashCode ^
        description.hashCode ^
        price.hashCode ^
        imagePath.hashCode ^
        createdAt.hashCode;
  }

  /// 將 List<double> 轉換為 Uint8List (用於 SQLite BLOB)
  static Uint8List _vectorToBytes(List<double> vector) {
    final buffer = Float64List.fromList(vector);
    return buffer.buffer.asUint8List();
  }

  /// 將 Uint8List 轉換回 List<double>
  static List<double> _bytesToVector(Uint8List bytes) {
    // 檢查對齊：如果 offset 不是 8 的倍數，需要複製數據
    if (bytes.offsetInBytes % Float64List.bytesPerElement != 0) {
      // 複製到新的對齊緩衝區
      final alignedBytes = Uint8List.fromList(bytes);
      final buffer = alignedBytes.buffer.asFloat64List();
      return buffer.toList();
    } else {
      // 已對齊，可以直接轉換
      final buffer = bytes.buffer.asFloat64List(
        bytes.offsetInBytes,
        bytes.lengthInBytes ~/ Float64List.bytesPerElement,
      );
      return buffer.toList();
    }
  }
}

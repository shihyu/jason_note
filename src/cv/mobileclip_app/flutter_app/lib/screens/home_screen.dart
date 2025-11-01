import 'package:flutter/material.dart';
import 'dart:io';
import '../models/product_model.dart';
import '../services/database_service.dart';
import 'add_product_screen.dart';
import 'camera_search_screen.dart';
import 'product_detail_screen.dart';

/// 主畫面 - 顯示所有已儲存的商品
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final DatabaseService _databaseService = DatabaseService();
  List<Product> _products = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  /// 載入所有商品
  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);

    try {
      final products = await _databaseService.getAllProducts();
      setState(() {
        _products = products;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        _showErrorDialog('載入商品失敗', e.toString());
      }
    }
  }

  /// 刪除商品
  Future<void> _deleteProduct(Product product) async {
    final confirm = await _showConfirmDialog(
      '確定要刪除商品？',
      '商品「${product.name}」將被永久刪除',
    );

    if (confirm != true) return;

    try {
      await _databaseService.deleteProduct(product.id!);
      _loadProducts();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('已刪除「${product.name}」')),
        );
      }
    } catch (e) {
      if (mounted) {
        _showErrorDialog('刪除失敗', e.toString());
      }
    }
  }

  /// 刪除所有商品
  Future<void> _deleteAllProducts() async {
    if (_products.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('目前沒有商品')),
      );
      return;
    }

    final confirm = await _showConfirmDialog(
      '確定要刪除所有商品？',
      '此操作無法復原，所有商品資料將被永久刪除',
    );

    if (confirm != true) return;

    try {
      await _databaseService.deleteAllProducts();
      _loadProducts();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('已刪除所有商品')),
        );
      }
    } catch (e) {
      if (mounted) {
        _showErrorDialog('刪除失敗', e.toString());
      }
    }
  }

  /// 顯示確認對話框
  Future<bool?> _showConfirmDialog(String title, String content) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('刪除'),
          ),
        ],
      ),
    );
  }

  /// 顯示錯誤對話框
  void _showErrorDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('確定'),
          ),
        ],
      ),
    );
  }

  /// 前往新增商品畫面
  Future<void> _navigateToAddProduct() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddProductScreen()),
    );

    if (result == true) {
      _loadProducts();
    }
  }

  /// 前往相機搜尋畫面
  void _navigateToCameraSearch() {
    if (_products.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('請先新增商品後再使用搜尋功能')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CameraSearchScreen()),
    );
  }

  /// 前往商品詳情畫面
  void _navigateToProductDetail(Product product) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProductDetailScreen(product: product),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('商品管理'),
        actions: [
          // 刪除全部按鈕
          if (_products.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep),
              onPressed: _deleteAllProducts,
              tooltip: '刪除全部',
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _products.isEmpty
              ? _buildEmptyState()
              : _buildProductList(),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // 相機搜尋按鈕
          FloatingActionButton(
            heroTag: 'camera_search',
            onPressed: _navigateToCameraSearch,
            tooltip: '相機搜尋',
            child: const Icon(Icons.camera_alt),
          ),
          const SizedBox(height: 16),
          // 新增商品按鈕
          FloatingActionButton(
            heroTag: 'add_product',
            onPressed: _navigateToAddProduct,
            tooltip: '新增商品',
            child: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }

  /// 建立空狀態畫面
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inventory_2_outlined,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            '尚未新增任何商品',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '點擊右下角的 + 按鈕新增商品',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  /// 建立商品列表
  Widget _buildProductList() {
    return RefreshIndicator(
      onRefresh: _loadProducts,
      child: ListView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: _products.length,
        itemBuilder: (context, index) {
          final product = _products[index];
          return _buildProductCard(product);
        },
      ),
    );
  }

  /// 建立商品卡片
  Widget _buildProductCard(Product product) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      elevation: 2,
      child: InkWell(
        onTap: () => _navigateToProductDetail(product),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 商品圖片
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.file(
                  File(product.imagePath),
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey[300],
                      child: const Icon(Icons.broken_image, size: 40),
                    );
                  },
                ),
              ),
              const SizedBox(width: 12),
              // 商品資訊
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (product.description != null &&
                        product.description!.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        product.description!,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    if (product.price != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        'NT\$ ${product.price!.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                    const SizedBox(height: 4),
                    Text(
                      '建立時間: ${_formatDateTime(product.createdAt)}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ),
              ),
              // 刪除按鈕
              IconButton(
                icon: const Icon(Icons.delete_outline),
                color: Colors.red,
                onPressed: () => _deleteProduct(product),
                tooltip: '刪除',
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 格式化日期時間
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.year}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.day.toString().padLeft(2, '0')} '
        '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _databaseService.close();
    super.dispose();
  }
}

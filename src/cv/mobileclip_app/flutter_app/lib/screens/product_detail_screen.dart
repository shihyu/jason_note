import 'package:flutter/material.dart';
import 'dart:io';
import '../models/product_model.dart';

/// 商品詳情畫面 - 顯示商品完整資訊
class ProductDetailScreen extends StatelessWidget {
  final Product product;

  const ProductDetailScreen({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('商品詳情'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 商品圖片
            _buildProductImage(),

            // 商品資訊
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 商品名稱
                  Text(
                    product.name,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // 價格
                  if (product.price != null) ...[
                    Text(
                      'NT\$ ${product.price!.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // 分隔線
                  const Divider(),
                  const SizedBox(height: 16),

                  // 描述
                  if (product.description != null &&
                      product.description!.isNotEmpty) ...[
                    const Text(
                      '商品描述',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      product.description!,
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[700],
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 16),
                  ],

                  // 技術資訊
                  const Text(
                    '技術資訊',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),

                  _buildInfoRow(
                    icon: Icons.fingerprint,
                    label: '商品 ID',
                    value: product.id?.toString() ?? 'N/A',
                  ),

                  _buildInfoRow(
                    icon: Icons.calendar_today,
                    label: '建立時間',
                    value: _formatDateTime(product.createdAt),
                  ),

                  _buildInfoRow(
                    icon: Icons.analytics,
                    label: '特徵向量維度',
                    value: '${product.featureVector.length} 維',
                  ),

                  _buildInfoRow(
                    icon: Icons.image,
                    label: '圖片路徑',
                    value: product.imagePath.split('/').last,
                  ),

                  const SizedBox(height: 16),

                  // 特徵向量資訊卡片
                  Card(
                    color: Colors.blue[50],
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.insights, color: Colors.blue[700]),
                              const SizedBox(width: 8),
                              Text(
                                'MobileCLIP 特徵向量',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue[900],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '此商品已使用 MobileCLIP-S2 模型提取 512 維特徵向量，'
                            '可用於相似度比對與相機即時搜尋。',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.blue[800],
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 建立商品圖片
  Widget _buildProductImage() {
    return Hero(
      tag: 'product_${product.id}',
      child: Image.file(
        File(product.imagePath),
        height: 300,
        width: double.infinity,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            height: 300,
            color: Colors.grey[300],
            child: const Center(
              child: Icon(Icons.broken_image, size: 80),
            ),
          );
        },
      ),
    );
  }

  /// 建立資訊行
  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 格式化日期時間
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.year}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.day.toString().padLeft(2, '0')} '
        '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}:${dateTime.second.toString().padLeft(2, '0')}';
  }
}

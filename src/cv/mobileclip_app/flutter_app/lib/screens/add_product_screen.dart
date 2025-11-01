import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../models/product_model.dart';
import '../services/database_service.dart';
import '../services/mobileclip_service.dart';
import '../utils/image_utils.dart';

/// 新增商品畫面 - 拍照並輸入商品資訊
class AddProductScreen extends StatefulWidget {
  const AddProductScreen({super.key});

  @override
  State<AddProductScreen> createState() => _AddProductScreenState();
}

class _AddProductScreenState extends State<AddProductScreen> {
  final ImagePicker _picker = ImagePicker();
  final DatabaseService _databaseService = DatabaseService();
  final MobileCLIPService _clipService = MobileCLIPService();

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final TextEditingController _priceController = TextEditingController();

  XFile? _selectedImage;
  bool _isProcessing = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  /// 初始化服務
  Future<void> _initializeServices() async {
    try {
      await _clipService.initialize();
      setState(() => _isInitialized = true);
    } catch (e) {
      if (mounted) {
        _showErrorDialog('初始化失敗', '無法載入 MobileCLIP 模型: $e');
      }
    }
  }

  /// 從相機拍照
  Future<void> _takePicture() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() => _selectedImage = image);
      }
    } catch (e) {
      _showErrorDialog('拍照失敗', e.toString());
    }
  }

  /// 從相簿選擇圖片
  Future<void> _pickImage() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() => _selectedImage = image);
      }
    } catch (e) {
      _showErrorDialog('選擇圖片失敗', e.toString());
    }
  }

  /// 儲存商品
  Future<void> _saveProduct() async {
    // 驗證輸入
    if (_selectedImage == null) {
      _showErrorDialog('請選擇圖片', '請先拍照或從相簿選擇商品圖片');
      return;
    }

    if (_nameController.text.trim().isEmpty) {
      _showErrorDialog('請輸入商品名稱', '商品名稱不可為空');
      return;
    }

    if (!_isInitialized) {
      _showErrorDialog('服務尚未初始化', '請稍候再試');
      return;
    }

    setState(() => _isProcessing = true);

    try {
      // 1. 讀取圖片
      final imageBytes = await _selectedImage!.readAsBytes();

      // 2. 提取特徵向量
      if (!mounted) return;
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 16),
              Text('正在分析圖片...'),
            ],
          ),
        ),
      );

      final featureVector = await _clipService.extractFeatures(imageBytes);

      if (mounted) Navigator.pop(context); // 關閉進度對話框

      // 3. 儲存圖片到應用程式目錄
      final filename = ImageUtils.generateUniqueFilename(
        prefix: _nameController.text.trim().replaceAll(' ', '_'),
      );
      final imagePath = await ImageUtils.saveImage(imageBytes, filename);

      // 4. 建立商品物件
      final price = _priceController.text.isEmpty
          ? null
          : double.tryParse(_priceController.text);

      final product = Product(
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        price: price,
        imagePath: imagePath,
        featureVector: featureVector,
      );

      // 5. 儲存到資料庫
      await _databaseService.insertProduct(product);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('已新增「${product.name}」')),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) Navigator.pop(context); // 確保關閉進度對話框
      _showErrorDialog('儲存失敗', e.toString());
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('新增商品'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 圖片預覽區域
            _buildImagePreview(),
            const SizedBox(height: 16),

            // 圖片選擇按鈕
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _takePicture,
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('拍照'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _pickImage,
                    icon: const Icon(Icons.photo_library),
                    label: const Text('相簿'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // 商品資訊輸入
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: '商品名稱 *',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.shopping_bag),
              ),
              enabled: !_isProcessing,
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: '商品描述',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.description),
              ),
              maxLines: 3,
              enabled: !_isProcessing,
            ),
            const SizedBox(height: 16),

            TextField(
              controller: _priceController,
              decoration: const InputDecoration(
                labelText: '價格',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.attach_money),
                suffixText: 'NT\$',
              ),
              keyboardType: TextInputType.number,
              enabled: !_isProcessing,
            ),
            const SizedBox(height: 24),

            // 儲存按鈕
            ElevatedButton(
              onPressed: _isProcessing ? null : _saveProduct,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isProcessing
                  ? const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 12),
                        Text('處理中...'),
                      ],
                    )
                  : const Text(
                      '儲存商品',
                      style: TextStyle(fontSize: 16),
                    ),
            ),

            if (!_isInitialized) ...[
              const SizedBox(height: 16),
              Card(
                color: Colors.orange[50],
                child: const Padding(
                  padding: EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.orange),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '正在初始化模型，請稍候...',
                          style: TextStyle(color: Colors.orange),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// 建立圖片預覽區域
  Widget _buildImagePreview() {
    return Container(
      height: 300,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: _selectedImage == null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.add_photo_alternate,
                    size: 64,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '請選擇商品圖片',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            )
          : ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.file(
                File(_selectedImage!.path),
                fit: BoxFit.cover,
              ),
            ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _priceController.dispose();
    // 不要釋放 MobileCLIP Service，因為它是 Singleton
    // _clipService.dispose();
    _databaseService.close();
    super.dispose();
  }
}

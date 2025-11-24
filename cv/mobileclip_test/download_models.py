#!/usr/bin/env python3
"""下載並驗證 MobileCLIP 預訓練模型"""

import mobileclip

def download_and_verify_models():
    """下載並驗證 S0, S1, S2 模型"""
    models = ['mobileclip_s0', 'mobileclip_s1', 'mobileclip_s2']

    print("=" * 60)
    print("下載並驗證 MobileCLIP 預訓練模型")
    print("=" * 60)

    for model_name in models:
        print(f"\n[{model_name}] 正在載入...")

        try:
            # 使用本地預訓練權重
            model_path = f'ml-mobileclip/checkpoints/{model_name}.pt'
            model, _, preprocess = mobileclip.create_model_and_transforms(
                model_name,
                pretrained=model_path
            )
            model.eval()
            print(f"✓ {model_name} 載入成功")

            # 顯示模型資訊
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            print(f"  總參數數量: {total_params:,}")
            print(f"  可訓練參數: {trainable_params:,}")

        except Exception as e:
            print(f"✗ {model_name} 載入失敗: {e}")
            return False

    print("\n" + "=" * 60)
    print("✓ 所有模型驗證完成")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = download_and_verify_models()
    exit(0 if success else 1)

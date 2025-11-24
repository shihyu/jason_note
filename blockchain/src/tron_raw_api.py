"""
TRON 區塊鏈底層實現 - 純 Python 版本
=====================================

本程式直接使用 HTTP API 和密碼學庫實現 TRON 區塊鏈的核心功能，
不依賴 tronpy 等高階套件，幫助深入理解 TRON 的底層運作原理。

主要功能：
1. 地址格式轉換 (Base58 ↔ Hex)
2. 從私鑰生成公鑰和地址
3. 查詢帳戶餘額 (TRX 和 TRC20 代幣)
4. 建立、簽名、廣播交易
5. TRX 和 USDT (TRC20) 轉賬

作者：AI Assistant
版本：2.0 (重構版)
最後更新：2025-01-22
"""

import hashlib
from typing import Dict, Any, Optional

import base58
import requests
from Crypto.Hash import keccak
from ecdsa import SECP256k1, SigningKey
from ecdsa.util import sigencode_string
from ecdsa.numbertheory import square_root_mod_prime
from ecdsa.ellipticcurve import Point


# ============================================
# 常數定義
# ============================================


class TronNetwork:
    """TRON 網路配置常數"""

    # API 端點
    NILE_API = "https://nile.trongrid.io"  # Nile 測試網
    MAINNET_API = "https://api.trongrid.io"  # 主網

    # USDT 合約地址
    USDT_CONTRACT_MAINNET = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # 主網 USDT
    USDT_CONTRACT_NILE = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"  # 測試網 USDT

    # 地址前綴
    ADDRESS_PREFIX = "41"  # TRON 主網地址的 hex 前綴


class CryptoConstants:
    """密碼學相關常數"""

    # secp256k1 橢圓曲線參數
    CURVE = SECP256k1
    CURVE_ORDER = SECP256k1.order  # 曲線的階
    FIELD_PRIME = SECP256k1.curve.p()  # 有限域的模數

    # 公鑰格式
    UNCOMPRESSED_PUBKEY_PREFIX = b"\x04"  # 非壓縮公鑰前綴
    COMPRESSED_PUBKEY_EVEN_PREFIX = b"\x02"  # 壓縮公鑰前綴 (y 為偶數)
    COMPRESSED_PUBKEY_ODD_PREFIX = b"\x03"  # 壓縮公鑰前綴 (y 為奇數)

    # 長度常數
    PRIVATE_KEY_LENGTH = 64  # 私鑰長度 (hex 字符)
    PUBLIC_KEY_UNCOMPRESSED_LENGTH = 130  # 非壓縮公鑰長度 (hex 字符)
    PUBLIC_KEY_COMPRESSED_LENGTH = 66  # 壓縮公鑰長度 (hex 字符)
    ADDRESS_HEX_LENGTH = 42  # 帶前綴的 hex 地址長度
    ADDRESS_CORE_LENGTH = 40  # 不帶前綴的 hex 地址長度
    SIGNATURE_LENGTH = 65  # ECDSA 可恢復簽名長度 (bytes)


# ============================================
# 地址轉換工具
# ============================================


class AddressConverter:
    """
    TRON 地址格式轉換工具

    支援 Base58 和 Hex 格式之間的相互轉換。
    TRON 地址有兩種表示方式：
    - Base58: 以 'T' 開頭的可讀格式 (如 TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u)
    - Hex: 以 '41' 開頭的十六進制格式 (如 41a49b6890465f39fce73b18e5c9c5fd9136c70e38)
    """

    @staticmethod
    def hex_to_base58(hex_address: str) -> str:
        """
        將 Hex 格式地址轉換為 Base58 格式

        處理流程：
        1. 移除 '0x' 前綴（如果有）
        2. 檢查或添加 '41' 前綴（TRON 主網標識）
        3. 驗證長度和格式
        4. 執行 Base58Check 編碼
        5. 驗證結果以 'T' 開頭

        參數：
            hex_address: hex 格式地址，支援以下格式：
                - 帶 0x 前綴: "0x410123..."
                - 帶 41 前綴: "410123..."
                - 不帶前綴: "0123..."

        返回：
            Base58 格式的 TRON 地址 (以 'T' 開頭)

        異常：
            ValueError: 當地址格式不正確時

        範例：
            >>> AddressConverter.hex_to_base58("41a49b6890465f39fce73b18e5c9c5fd9136c70e38")
            'TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u'
        """
        # 步驟 1: 移除 0x 前綴（如果存在）
        if hex_address.startswith(("0x", "0X")):
            hex_address = hex_address[2:]

        # 步驟 2: 統一轉為小寫以便處理
        hex_address = hex_address.lower()

        # 步驟 3: 檢查並處理 41 前綴
        if hex_address.startswith("41"):
            # 已有 41 前綴，檢查總長度應為 42 字符 (21 bytes)
            if len(hex_address) != CryptoConstants.ADDRESS_HEX_LENGTH:
                raise ValueError(
                    f"帶 41 前綴的地址長度應為 {CryptoConstants.ADDRESS_HEX_LENGTH} 字符，"
                    f"實際為 {len(hex_address)} 字符"
                )
        else:
            # 沒有 41 前綴，檢查長度應為 40 字符 (20 bytes)
            if len(hex_address) != CryptoConstants.ADDRESS_CORE_LENGTH:
                raise ValueError(
                    f"不帶 41 前綴的地址長度應為 {CryptoConstants.ADDRESS_CORE_LENGTH} 字符，"
                    f"實際為 {len(hex_address)} 字符"
                )
            # 添加 41 前綴（TRON 主網標識）
            hex_address = TronNetwork.ADDRESS_PREFIX + hex_address

        # 步驟 4: 驗證是否為有效的 hex 字符串
        try:
            address_bytes = bytes.fromhex(hex_address)
        except ValueError as e:
            raise ValueError(f"無效的 hex 字符串: {hex_address}") from e

        # 步驟 5: Base58Check 編碼
        # Base58Check 會自動添加校驗和
        base58_address = base58.b58encode_check(address_bytes).decode()

        # 步驟 6: 驗證結果是否以 'T' 開頭（TRON 主網地址特徵）
        if not base58_address.startswith("T"):
            raise ValueError(
                f"轉換結果不是有效的 TRON 主網地址: {base58_address} "
                f"(TRON 主網地址應以 T 開頭)"
            )

        return base58_address

    @staticmethod
    def base58_to_hex(base58_address: str, include_prefix: bool = True) -> str:
        """
        將 Base58 格式地址轉換為 Hex 格式

        處理流程：
        1. Base58Check 解碼
        2. 驗證以 '41' 開頭
        3. 根據參數決定是否包含 '41' 前綴

        參數：
            base58_address: Base58 格式的 TRON 地址
            include_prefix: 是否包含 '41' 前綴
                - True: 返回 "410123..." (42 字符)
                - False: 返回 "0123..." (40 字符)

        返回：
            Hex 格式地址

        異常：
            ValueError: 當 Base58 解碼失敗或地址無效時

        範例：
            >>> AddressConverter.base58_to_hex("TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u")
            '41a49b6890465f39fce73b18e5c9c5fd9136c70e38'
            >>> AddressConverter.base58_to_hex("TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u", False)
            'a49b6890465f39fce73b18e5c9c5fd9136c70e38'
        """
        try:
            # 步驟 1: Base58Check 解碼（會自動驗證校驗和）
            decoded = base58.b58decode_check(base58_address)
            hex_address = decoded.hex()

            # 步驟 2: 驗證是否以 '41' 開頭（TRON 主網地址）
            if not hex_address.startswith("41"):
                raise ValueError(
                    f"不是有效的 TRON 主網地址 (應以 41 開頭): {hex_address}"
                )

            # 步驟 3: 根據參數決定是否返回 '41' 前綴
            if include_prefix:
                return hex_address  # 42 字符，包含 '41'
            else:
                return hex_address[2:]  # 40 字符，去除 '41'

        except Exception as e:
            raise ValueError(f"Base58 解碼失敗: {e}") from e


# ============================================
# 密鑰與地址生成
# ============================================


class KeyGenerator:
    """
    TRON 密鑰和地址生成工具

    實現 TRON 地址生成的完整流程，包括：
    - 從私鑰生成公鑰 (使用 secp256k1 橢圓曲線)
    - 從公鑰生成地址 (使用 Keccak256 哈希)
    """

    @staticmethod
    def private_key_to_public_key(
        private_key_hex: str, compressed: bool = False
    ) -> str:
        """
        從私鑰生成公鑰

        使用 ECDSA secp256k1 橢圓曲線算法生成公鑰。
        公鑰由橢圓曲線上的點 (x, y) 組成。

        處理流程：
        1. 驗證私鑰格式和長度
        2. 使用 secp256k1 曲線生成公鑰點
        3. 根據參數選擇輸出格式（壓縮/非壓縮）

        參數：
            private_key_hex: 私鑰的 hex 字符串 (64 字符 = 32 bytes)
            compressed: 是否返回壓縮格式的公鑰
                - True: 返回壓縮公鑰 (33 bytes, 02/03 + x)
                - False: 返回非壓縮公鑰 (65 bytes, 04 + x + y)

        返回：
            公鑰的 hex 字符串
            - 非壓縮: 130 字符 (04 + 64位x + 64位y)
            - 壓縮: 66 字符 (02/03 + 64位x)

        異常：
            ValueError: 當私鑰格式不正確時

        範例：
            >>> KeyGenerator.private_key_to_public_key(
            ...     "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"
            ... )
            '04...'  # 130 字符的非壓縮公鑰
        """
        # 步驟 1: 驗證私鑰長度
        if len(private_key_hex) != CryptoConstants.PRIVATE_KEY_LENGTH:
            raise ValueError(
                f"私鑰長度應為 {CryptoConstants.PRIVATE_KEY_LENGTH} 字符，"
                f"實際為 {len(private_key_hex)} 字符"
            )

        # 步驟 2: 驗證 hex 格式
        try:
            private_key_bytes = bytes.fromhex(private_key_hex)
        except ValueError as e:
            raise ValueError("無效的 hex 字符串") from e

        # 步驟 3: 使用 secp256k1 橢圓曲線生成公鑰
        signing_key = SigningKey.from_string(
            private_key_bytes, curve=CryptoConstants.CURVE
        )
        verifying_key = signing_key.get_verifying_key()

        # 步驟 4: 獲取公鑰坐標
        # to_string() 返回 64 bytes: x(32 bytes) + y(32 bytes)
        public_key_bytes = verifying_key.to_string()
        x_bytes = public_key_bytes[:32]  # x 坐標 (32 bytes)
        y_bytes = public_key_bytes[32:]  # y 坐標 (32 bytes)

        # 步驟 5: 根據參數選擇輸出格式
        if compressed:
            # 壓縮格式: prefix + x (33 bytes)
            # prefix 為 02 (y為偶數) 或 03 (y為奇數)
            y_int = int.from_bytes(y_bytes, byteorder="big")
            prefix = (
                CryptoConstants.COMPRESSED_PUBKEY_EVEN_PREFIX
                if y_int % 2 == 0
                else CryptoConstants.COMPRESSED_PUBKEY_ODD_PREFIX
            )
            public_key = prefix + x_bytes
        else:
            # 非壓縮格式: 04 + x + y (65 bytes)
            public_key = CryptoConstants.UNCOMPRESSED_PUBKEY_PREFIX + public_key_bytes

        return public_key.hex()

    @staticmethod
    def private_key_to_address(private_key_hex: str, show_steps: bool = False) -> str:
        """
        從私鑰生成 TRON 地址

        嚴格按照 TRON 地址生成標準流程實現：

        完整流程（10 個步驟）：
        ┌─────────────────────────────────────────────────────────────┐
        │ Step 1: 從私鑰生成非壓縮公鑰 (ECDSA secp256k1)              │
        │         格式: 04 + x(32 bytes) + y(32 bytes) = 65 bytes     │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 2: 去掉 "04" 前綴                                      │
        │         剩餘: x(32 bytes) + y(32 bytes) = 64 bytes          │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 3: Keccak256 哈希                                      │
        │         輸出: 32 bytes (64 hex 字符)                        │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 4: 取最後 20 bytes (40 hex 字符)                       │
        │         這是地址的核心部分                                  │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 5: 添加 "41" 前綴 (TRON 主網標識)                      │
        │         格式: 41 + 20 bytes = 21 bytes (42 hex 字符)        │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 6: SHA-256 哈希（第一次）                              │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 7: SHA-256 哈希（第二次）                              │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 8: 取前 4 bytes (8 hex 字符) 作為校驗和                │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 9: 連接 Step 5 結果 + Step 8 校驗和                    │
        │         格式: 21 bytes + 4 bytes = 25 bytes (50 hex 字符)   │
        ├─────────────────────────────────────────────────────────────┤
        │ Step 10: Base58 編碼                                        │
        │          得到最終的 TRON 地址 (以 'T' 開頭)                 │
        └─────────────────────────────────────────────────────────────┘

        參數：
            private_key_hex: 私鑰 (64 字符 hex)
            show_steps: 是否顯示每一步的詳細信息（用於調試和學習）

        返回：
            TRON Base58 地址 (以 'T' 開頭)

        範例：
            >>> KeyGenerator.private_key_to_address(
            ...     "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"
            ... )
            'TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u'
        """
        if show_steps:
            print("=" * 70)
            print("TRON 地址生成流程 (Address Generation Step by Step)")
            print("=" * 70)
            print(f"\n私鑰 (Private Key): {private_key_hex}")
            print(
                f"長度: {len(private_key_hex)} 字符 = {len(private_key_hex) // 2} bytes\n"
            )

        # ========================================
        # Step 1: 生成非壓縮公鑰
        # ========================================
        if show_steps:
            print("【Step 1】生成非壓縮公鑰 (Uncompressed Public Key)")
            print("算法: ECDSA secp256k1")
            print("格式: 04 + x(32 bytes) + y(32 bytes)")
            print("-" * 70)

        public_key_hex = KeyGenerator.private_key_to_public_key(
            private_key_hex, compressed=False
        )

        if show_steps:
            print(f"公鑰: {public_key_hex}")
            print(
                f"長度: {len(public_key_hex)} 字符 = {len(public_key_hex) // 2} bytes"
            )
            assert len(public_key_hex) == CryptoConstants.PUBLIC_KEY_UNCOMPRESSED_LENGTH
            assert public_key_hex.startswith("04")
            print("✓ 長度檢查通過 (130 字符 = 65 bytes)")
            print("✓ 前綴檢查通過 (04)\n")

        # ========================================
        # Step 2: 去掉 "04" 前綴
        # ========================================
        if show_steps:
            print("【Step 2】去掉 '04' 前綴")
            print("-" * 70)

        public_key_no_prefix = public_key_hex[2:]

        if show_steps:
            print(f"去前綴後: {public_key_no_prefix}")
            print(
                f"長度: {len(public_key_no_prefix)} 字符 = {len(public_key_no_prefix) // 2} bytes"
            )
            assert len(public_key_no_prefix) == 128
            print("✓ 長度檢查通過 (128 字符 = 64 bytes)\n")

        # ========================================
        # Step 3: Keccak256 哈希
        # ========================================
        if show_steps:
            print("【Step 3】Keccak256 哈希")
            print("說明: Keccak-256 是以太坊和 TRON 使用的哈希算法")
            print("-" * 70)

        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(bytes.fromhex(public_key_no_prefix))
        keccak_digest = keccak_hash.hexdigest()

        if show_steps:
            print(f"Keccak256: {keccak_digest}")
            print(f"長度: {len(keccak_digest)} 字符 = {len(keccak_digest) // 2} bytes")
            assert len(keccak_digest) == 64
            print("✓ 長度檢查通過 (64 字符 = 32 bytes)\n")

        # ========================================
        # Step 4: 取最後 20 bytes (40 hex 字符)
        # ========================================
        if show_steps:
            print("【Step 4】取最後 20 bytes (40 hex 字符)")
            print("說明: 這是地址的核心部分")
            print("-" * 70)

        address_core = keccak_digest[-40:]

        if show_steps:
            print(f"地址核心: {address_core}")
            print(f"長度: {len(address_core)} 字符 = {len(address_core) // 2} bytes")
            assert len(address_core) == 40
            print("✓ 長度檢查通過 (40 字符 = 20 bytes)\n")

        # ========================================
        # Step 5: 添加 "41" 前綴
        # ========================================
        if show_steps:
            print("【Step 5】添加 '41' 前綴")
            print("說明: 41 是 TRON 主網的網路標識符")
            print("-" * 70)

        address_with_prefix = TronNetwork.ADDRESS_PREFIX + address_core

        if show_steps:
            print(f"Hex 地址: {address_with_prefix}")
            print(
                f"長度: {len(address_with_prefix)} 字符 = {len(address_with_prefix) // 2} bytes"
            )
            assert len(address_with_prefix) == 42
            assert address_with_prefix.startswith("41")
            print("✓ 長度檢查通過 (42 字符 = 21 bytes)")
            print("✓ 前綴檢查通過 ('41')\n")

        # ========================================
        # Step 6-8: 計算校驗和
        # 使用雙重 SHA-256 並取前 4 bytes
        # ========================================
        if show_steps:
            print("【Step 6-8】計算校驗和")
            print("流程: SHA-256 → SHA-256 → 取前 4 bytes")
            print("-" * 70)

        # Step 6: 第一次 SHA-256
        sha256_first = hashlib.sha256(bytes.fromhex(address_with_prefix)).hexdigest()
        if show_steps:
            print(f"第一次 SHA-256: {sha256_first}")

        # Step 7: 第二次 SHA-256
        sha256_second = hashlib.sha256(bytes.fromhex(sha256_first)).hexdigest()
        if show_steps:
            print(f"第二次 SHA-256: {sha256_second}")

        # Step 8: 取前 4 bytes (8 hex 字符) 作為校驗和
        checksum = sha256_second[:8]
        if show_steps:
            print(f"校驗和 (Checksum): {checksum}")
            print(f"長度: {len(checksum)} 字符 = {len(checksum) // 2} bytes")
            assert len(checksum) == 8
            print("✓ 長度檢查通過 (8 字符 = 4 bytes)\n")

        # ========================================
        # Step 9: 連接地址和校驗和
        # ========================================
        if show_steps:
            print("【Step 9】連接地址和校驗和")
            print("-" * 70)

        address_with_checksum = address_with_prefix + checksum

        if show_steps:
            print(f"完整數據: {address_with_checksum}")
            print(f"  └─ 地址部分 (前 42 字符): {address_with_prefix}")
            print(f"  └─ 校驗部分 (後  8 字符): {checksum}")
            print(
                f"總長度: {len(address_with_checksum)} 字符 = {len(address_with_checksum) // 2} bytes"
            )
            assert len(address_with_checksum) == 50
            print("✓ 長度檢查通過 (50 字符 = 25 bytes)\n")

        # ========================================
        # Step 10: Base58 編碼
        # ========================================
        if show_steps:
            print("【Step 10】Base58 編碼")
            print("說明: 將二進制數據編碼為人類可讀的字符串")
            print("-" * 70)

        # 注意：這裡使用 base58.b58encode 而非 b58encode_check
        # 因為我們已經手動計算並添加了校驗和
        address_base58 = base58.b58encode(bytes.fromhex(address_with_checksum)).decode()

        if show_steps:
            print(f"Base58 地址: {address_base58}")
            print(f"長度: {len(address_base58)} 字符")
            assert address_base58.startswith("T")
            print("✓ 前綴檢查通過 (以 'T' 開頭)")
            print("✓ 這是有效的 TRON 主網地址\n")
            print("=" * 70)
            print("✅ 地址生成完成!")
            print("=" * 70)

        return address_base58


# ============================================
# HTTP API 封裝
# ============================================


class TronAPI:
    """
    TRON HTTP API 封裝類別

    提供與 TRON 節點通信的底層介面，支援：
    - 帳戶查詢
    - 合約調用（只讀和寫入）
    - 交易建立和廣播
    - 交易狀態查詢

    使用範例：
        api = TronAPI(TronNetwork.NILE_API, api_key="your-key")
        balance = api.get_account_balance("TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u")
    """

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        初始化 TRON API 客戶端

        參數：
            api_url: API 端點 URL
                - 測試網: TronNetwork.NILE_API
                - 主網: TronNetwork.MAINNET_API
            api_key: API 密鑰（可選，用於提高請求限制）
        """
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}

        # 如果提供了 API 密鑰，添加到請求頭
        if api_key:
            self.headers["TRON-PRO-API-KEY"] = api_key

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        發送 POST 請求到 TRON 節點

        參數：
            endpoint: API 端點路徑（如 "/wallet/getaccount"）
            data: 請求數據（將被轉換為 JSON）

        返回：
            API 響應的 JSON 數據

        異常：
            requests.RequestException: 當網路請求失敗時
        """
        url = f"{self.api_url}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()  # 如果狀態碼非 2xx，拋出異常
        return response.json()

    def get(self, endpoint: str) -> Dict[str, Any]:
        """
        發送 GET 請求到 TRON 節點

        參數：
            endpoint: API 端點路徑

        返回：
            API 響應的 JSON 數據

        異常：
            requests.RequestException: 當網路請求失敗時
        """
        url = f"{self.api_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # ===== 帳戶查詢方法 =====

    def get_account(self, address: str) -> Dict[str, Any]:
        """
        查詢帳戶資訊

        參數：
            address: TRON 地址 (Base58 格式)

        返回：
            帳戶資訊，包含餘額、資源等
            {
                "address": "TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u",
                "balance": 1000000000,  # TRX 餘額 (單位: SUN)
                "create_time": 1234567890000,
                ...
            }
        """
        data = {"address": address, "visible": True}  # 使用 Base58 格式地址
        return self.post("/wallet/getaccount", data)

    def get_account_balance(self, address: str) -> float:
        """
        查詢 TRX 餘額

        參數：
            address: TRON 地址 (Base58 格式)

        返回：
            TRX 餘額（單位: TRX，而非 SUN）

        注意：
            TRON 的最小單位是 SUN，1 TRX = 1,000,000 SUN
        """
        account = self.get_account(address)
        balance_sun = account.get("balance", 0)
        return balance_sun / 1_000_000  # 轉換為 TRX

    def trigger_constant_contract(
        self,
        contract_address: str,
        function_selector: str,
        parameter: str,
        owner_address: str,
    ) -> Dict[str, Any]:
        """
        調用智能合約（只讀，不上鏈）

        用於查詢合約狀態，如查詢 TRC20 代幣餘額。
        此操作不會消耗能量或帶寬，也不會改變鏈上狀態。

        參數：
            contract_address: 合約地址
            function_selector: 函數選擇器（如 "balanceOf(address)"）
            parameter: 函數參數（hex 編碼）
            owner_address: 調用者地址

        返回：
            合約執行結果
            {
                "result": {"result": true},
                "constant_result": ["0000..."],  # 返回值
                ...
            }
        """
        data = {
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": function_selector,
            "parameter": parameter,
            "visible": True,
        }
        return self.post("/wallet/triggerconstantcontract", data)

    # ===== 交易建立方法 =====

    def create_transaction(
        self, to_address: str, owner_address: str, amount: float
    ) -> Dict[str, Any]:
        """
        建立 TRX 轉賬交易

        此方法只是建立交易，不會簽名或廣播。
        建立後需要使用私鑰簽名，然後廣播到網路。

        參數：
            to_address: 接收者地址
            owner_address: 發送者地址
            amount: 轉賬金額（單位: TRX）

        返回：
            未簽名的交易數據
            {
                "visible": true,
                "txID": "abc123...",  # 交易 ID
                "raw_data": {...},     # 原始交易數據
                ...
            }
        """
        data = {
            "to_address": to_address,
            "owner_address": owner_address,
            "amount": int(amount * 1_000_000),  # 轉換為 SUN
            "visible": True,
        }
        return self.post("/wallet/createtransaction", data)

    def trigger_smart_contract(
        self,
        contract_address: str,
        function_selector: str,
        parameter: str,
        fee_limit: int,
        owner_address: str,
    ) -> Dict[str, Any]:
        """
        調用智能合約（寫入，會上鏈）

        用於執行改變鏈上狀態的合約操作，如 TRC20 代幣轉賬。
        此操作會消耗能量和帶寬，需要簽名和廣播。

        參數：
            contract_address: 合約地址
            function_selector: 函數選擇器（如 "transfer(address,uint256)"）
            parameter: 函數參數（hex 編碼）
            fee_limit: 最大手續費限制（單位: SUN）
            owner_address: 調用者地址

        返回：
            未簽名的交易數據
            {
                "result": {"result": true},
                "transaction": {
                    "txID": "abc123...",
                    "raw_data": {...},
                    ...
                }
            }
        """
        data = {
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": function_selector,
            "parameter": parameter,
            "fee_limit": fee_limit,
            "call_value": 0,  # 不發送 TRX（僅調用合約）
            "visible": True,
        }
        return self.post("/wallet/triggersmartcontract", data)

    def broadcast_transaction(
        self, signed_transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        廣播已簽名的交易到網路

        將簽名後的交易發送到 TRON 網路，等待礦工打包確認。

        參數：
            signed_transaction: 已簽名的交易數據
                必須包含 "signature" 字段

        返回：
            廣播結果
            {
                "result": true,      # 是否成功
                "code": "SUCCESS",   # 狀態碼
                "txid": "abc123...", # 交易 ID
                "message": "..."     # 訊息
            }

        注意：
            返回 {"result": true} 只表示交易已被接受，
            不代表交易已確認。需要等待區塊確認。
        """
        return self.post("/wallet/broadcasttransaction", signed_transaction)

    def get_transaction_info(self, txid: str) -> Dict[str, Any]:
        """
        查詢交易資訊

        用於確認交易是否已上鏈，以及查看執行結果。

        參數：
            txid: 交易 ID (hex 字符串)

        返回：
            交易資訊
            {
                "id": "abc123...",
                "blockNumber": 12345,      # 所在區塊號
                "blockTimeStamp": 1234567, # 區塊時間戳
                "receipt": {
                    "result": "SUCCESS",   # 執行結果
                    "net_fee": 267000,     # 帶寬費用
                    "energy_usage_total": 0 # 能量消耗
                },
                ...
            }

        注意：
            如果交易尚未上鏈，可能返回空字典或錯誤
        """
        data = {"value": txid}
        return self.post("/wallet/gettransactioninfobyid", data)


# ============================================
# 交易簽名
# ============================================


class TransactionSigner:
    """
    TRON 交易簽名工具

    實現 ECDSA 可恢復簽名，允許節點從簽名恢復公鑰。

    TRON 使用的簽名格式：
    - 65 bytes: r(32) + s(32) + recovery_id(1)
    - recovery_id 用於從簽名恢復公鑰

    技術細節：
    - 曲線: secp256k1
    - 哈希: 直接對 txID 簽名（txID 本身已是交易數據的哈希）
    - 簽名算法: ECDSA (Elliptic Curve Digital Signature Algorithm)
    """

    @staticmethod
    def sign_transaction(
        transaction: Dict[str, Any], private_key_hex: str
    ) -> Dict[str, Any]:
        """
        對交易進行簽名

        完整流程：
        1. 從交易中提取 txID（需要簽名的數據）
        2. 使用私鑰生成 ECDSA 簽名（64 bytes: r + s）
        3. 計算正確的 recovery ID（1 byte）
        4. 組合成 65 bytes 的可恢復簽名
        5. 將簽名添加到交易中

        Recovery ID 計算原理：
        ┌───────────────────────────────────────────────┐
        │ recovery_id 有 4 種可能值 (0, 1, 2, 3)：      │
        │                                               │
        │ - 最低位 (bit 0): 由公鑰 y 坐標的奇偶性決定   │
        │   - 0: y 為偶數                               │
        │   - 1: y 為奇數                               │
        │                                               │
        │ - 次低位 (bit 1): 由 r 值是否超過曲線階數決定 │
        │   - 0: r < n                                  │
        │   - 1: r >= n (罕見情況)                      │
        │                                               │
        │ 通常情況下 recovery_id 為 0 或 1              │
        └───────────────────────────────────────────────┘

        參數：
            transaction: API 返回的原始交易數據
                必須包含 "txID" 字段
            private_key_hex: 私鑰 (64 字符 hex)

        返回：
            已簽名的交易（添加了 "signature" 字段）

        異常：
            ValueError: 當交易中沒有 txID 時

        範例：
            >>> transaction = api.create_transaction(...)
            >>> signed = TransactionSigner.sign_transaction(transaction, private_key)
            >>> api.broadcast_transaction(signed)
        """
        # ========================================
        # 步驟 1: 提取 txID
        # ========================================
        txid = transaction.get("txID")
        if not txid:
            raise ValueError("交易資料中沒有 txID，無法簽名")

        txid_bytes = bytes.fromhex(txid)

        # ========================================
        # 步驟 2: 生成 ECDSA 簽名
        # ========================================
        private_key_bytes = bytes.fromhex(private_key_hex)
        signing_key = SigningKey.from_string(
            private_key_bytes, curve=CryptoConstants.CURVE
        )

        # 使用 sign_digest 直接對 txID 簽名
        # txID 本身已經是交易數據的哈希值
        signature = signing_key.sign_digest(txid_bytes, sigencode=sigencode_string)

        # ========================================
        # 步驟 3: 計算 Recovery ID
        # ========================================
        recovery_id = TransactionSigner._calculate_recovery_id(
            txid_bytes, signature, signing_key
        )

        # ========================================
        # 步驟 4: 組合成 65 bytes 簽名
        # ========================================
        signature_with_recovery = signature + bytes([recovery_id])

        # ========================================
        # 步驟 5: 添加到交易中
        # ========================================
        transaction["signature"] = [signature_with_recovery.hex()]

        return transaction

    @staticmethod
    def _calculate_recovery_id(
        message_hash: bytes, signature: bytes, signing_key: SigningKey
    ) -> int:
        """
        計算 ECDSA 簽名的 Recovery ID

        Recovery ID 允許從簽名中恢復公鑰，這樣節點就不需要
        在交易中包含完整的公鑰，節省空間。

        算法流程：
        1. 解析簽名得到 (r, s)
        2. 獲取正確的公鑰
        3. 嘗試 4 種可能的 recovery_id (0-3)
        4. 對每個 recovery_id，嘗試恢復公鑰
        5. 比對恢復的公鑰與實際公鑰
        6. 返回匹配的 recovery_id

        參數：
            message_hash: 消息哈希（即 txID）
            signature: ECDSA 簽名 (64 bytes: r + s)
            signing_key: 簽名密鑰（用於獲取公鑰）

        返回：
            recovery_id (0-3)
        """
        # 解析簽名
        r = int.from_bytes(signature[:32], byteorder="big")
        s = int.from_bytes(signature[32:64], byteorder="big")

        # 獲取正確的公鑰點
        verifying_key = signing_key.get_verifying_key()
        correct_point = verifying_key.pubkey.point

        # 曲線參數
        p = CryptoConstants.FIELD_PRIME  # 有限域的模數
        n = CryptoConstants.CURVE_ORDER  # 曲線的階

        # 嘗試所有可能的 recovery_id
        for recovery_id in range(4):
            try:
                # 計算 x 坐標
                x = r
                if recovery_id >= 2:
                    x = r + n
                    if x >= p:
                        continue

                # 從 x 計算 y
                # secp256k1 曲線方程: y^2 = x^3 + 7 (mod p)
                y_squared = (pow(x, 3, p) + 7) % p
                y = square_root_mod_prime(y_squared, p)

                # 根據 recovery_id 的最低位選擇 y 的奇偶性
                if (y % 2 == 0) != (recovery_id % 2 == 0):
                    y = p - y

                # 構造點 R
                R = Point(CryptoConstants.CURVE.curve, x, y, n)

                # 恢復公鑰: Q = r^-1 * (s*R - e*G)
                # 其中 e = int(message_hash), G = 生成點
                e = int.from_bytes(message_hash, byteorder="big")
                r_inv = pow(r, -1, n)  # r 的模逆元

                # 計算恢復的公鑰點
                recovered_point = r_inv * (
                    s * R + (-e % n) * CryptoConstants.CURVE.generator
                )

                # 檢查是否匹配
                if (
                    recovered_point.x() == correct_point.x()
                    and recovered_point.y() == correct_point.y()
                ):
                    return recovery_id

            except Exception:
                # 如果計算失敗，繼續嘗試下一個
                continue

        # 如果所有 recovery_id 都失敗，使用簡化方法
        # 通常 recovery_id 就是 y 坐標的奇偶性
        y = correct_point.y()
        return 1 if y % 2 == 1 else 0


# ============================================
# 高階功能封裝
# ============================================


class TronTransfer:
    """
    TRON 轉賬功能封裝

    提供簡單易用的轉賬介面，自動處理：
    - 地址生成
    - 交易建立
    - 交易簽名
    - 交易廣播

    支援：
    - TRX 轉賬
    - TRC20 代幣轉賬（如 USDT）
    """

    @staticmethod
    def transfer_trx(
        api: TronAPI,
        private_key_hex: str,
        to_address: str,
        amount_trx: float,
        verbose: bool = True,
    ) -> Optional[str]:
        """
        轉賬 TRX

        完整流程：
        1. 從私鑰生成發送者地址
        2. 建立轉賬交易
        3. 對交易簽名
        4. 廣播交易到網路

        參數：
            api: TronAPI 實例
            private_key_hex: 發送者私鑰 (64 字符 hex)
            to_address: 接收者地址 (Base58 格式)
            amount_trx: 轉賬金額（單位: TRX）
            verbose: 是否顯示詳細信息

        返回：
            交易 ID (成功) 或 None (失敗)

        範例：
            >>> api = TronAPI(TronNetwork.NILE_API)
            >>> txid = TronTransfer.transfer_trx(
            ...     api,
            ...     "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2",
            ...     "TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
            ...     1.0
            ... )
            >>> print(f"交易ID: {txid}")
        """
        if verbose:
            print("\n" + "=" * 60)
            print("開始 TRX 轉賬")
            print("=" * 60)

        # 步驟 1: 生成發送者地址
        from_address = KeyGenerator.private_key_to_address(private_key_hex)

        if verbose:
            print(f"\n發送方: {from_address}")
            print(f"接收方: {to_address}")
            print(f"金額: {amount_trx} TRX")

        # 步驟 2: 建立交易
        if verbose:
            print("\n[1/3] 建立交易...")

        transaction = api.create_transaction(to_address, from_address, amount_trx)

        if "Error" in transaction:
            if verbose:
                print(f"❌ 建立交易失敗: {transaction}")
            return None

        if verbose:
            print(f"✓ 交易已建立")
            print(f"  交易ID: {transaction['txID']}")

        # 步驟 3: 簽名交易
        if verbose:
            print("\n[2/3] 簽名交易...")

        signed_txn = TransactionSigner.sign_transaction(transaction, private_key_hex)

        if verbose:
            print("✓ 交易已簽名")
            print(f"  簽名: {signed_txn['signature'][0][:32]}...")

        # 步驟 4: 廣播交易
        if verbose:
            print("\n[3/3] 廣播交易...")

        result = api.broadcast_transaction(signed_txn)

        if result.get("result"):
            if verbose:
                print("✓ 交易已廣播成功")
                print(f"\n交易ID: {transaction['txID']}")
                print("=" * 60)
            return transaction["txID"]
        else:
            if verbose:
                print(f"❌ 廣播失敗: {result}")
            return None

    @staticmethod
    def transfer_usdt(
        api: TronAPI,
        private_key_hex: str,
        to_address: str,
        amount_usdt: float,
        contract_address: str,
        verbose: bool = True,
    ) -> Optional[str]:
        """
        轉賬 USDT (TRC20 代幣)

        TRC20 轉賬需要調用智能合約的 transfer 函數：
        function transfer(address _to, uint256 _value) returns (bool)

        處理流程：
        1. 從私鑰生成發送者地址
        2. 編碼合約調用參數
        3. 建立合約調用交易
        4. 對交易簽名
        5. 廣播交易到網路

        參數：
            api: TronAPI 實例
            private_key_hex: 發送者私鑰
            to_address: 接收者地址
            amount_usdt: 轉賬金額（單位: USDT）
            contract_address: USDT 合約地址
            verbose: 是否顯示詳細信息

        返回：
            交易 ID (成功) 或 None (失敗)

        注意：
            - USDT (TRC20) 使用 6 位小數
            - 需要足夠的能量或 TRX 來支付手續費

        範例：
            >>> txid = TronTransfer.transfer_usdt(
            ...     api,
            ...     private_key,
            ...     "TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
            ...     10.0,
            ...     TronNetwork.USDT_CONTRACT_NILE
            ... )
        """
        if verbose:
            print("\n" + "=" * 60)
            print("開始 USDT (TRC20) 轉賬")
            print("=" * 60)

        # 步驟 1: 生成發送者地址
        from_address = KeyGenerator.private_key_to_address(private_key_hex)

        if verbose:
            print(f"\n發送方: {from_address}")
            print(f"接收方: {to_address}")
            print(f"金額: {amount_usdt} USDT")
            print(f"合約: {contract_address}")

        # 步驟 2: 編碼合約參數
        # transfer(address _to, uint256 _value)
        # 參數格式: [address(32 bytes)][uint256(32 bytes)]

        if verbose:
            print("\n[1/4] 編碼合約參數...")

        # 將接收地址轉為 hex（去除 41 前綴，補齊到 32 bytes）
        to_hex = AddressConverter.base58_to_hex(to_address, include_prefix=False)
        to_param = to_hex.zfill(64)  # 補齊到 64 個字符（32 bytes）

        # 將金額轉為整數（USDT 有 6 位小數）
        amount_raw = int(amount_usdt * 1_000_000)
        amount_param = hex(amount_raw)[2:].zfill(64)  # 轉 hex 並補齊到 32 bytes

        # 組合參數
        parameter = to_param + amount_param

        if verbose:
            print(f"✓ 參數編碼完成")
            print(f"  接收地址 (hex): {to_param}")
            print(f"  金額 (hex): {amount_param}")

        # 步驟 3: 建立合約調用交易
        if verbose:
            print("\n[2/4] 建立交易...")

        transaction = api.trigger_smart_contract(
            contract_address=contract_address,
            function_selector="transfer(address,uint256)",
            parameter=parameter,
            fee_limit=50_000_000,  # 50 TRX（手續費上限）
            owner_address=from_address,
        )

        if "Error" in transaction or "result" not in transaction:
            if verbose:
                print(f"❌ 建立交易失敗: {transaction}")
            return None

        # 提取實際的交易數據
        if "transaction" not in transaction:
            if verbose:
                print(f"❌ 交易結構異常: {transaction}")
            return None

        actual_txn = transaction["transaction"]

        if verbose:
            print(f"✓ 交易已建立")
            print(f"  交易ID: {actual_txn['txID']}")

        # 步驟 4: 簽名交易
        if verbose:
            print("\n[3/4] 簽名交易...")

        signed_txn = TransactionSigner.sign_transaction(actual_txn, private_key_hex)

        if verbose:
            print("✓ 交易已簽名")

        # 步驟 5: 廣播交易
        if verbose:
            print("\n[4/4] 廣播交易...")

        result = api.broadcast_transaction(signed_txn)

        if result.get("result"):
            if verbose:
                print("✓ 交易已廣播成功")
                print(f"\n交易ID: {actual_txn['txID']}")
                print("=" * 60)
            return actual_txn["txID"]
        else:
            if verbose:
                print(f"❌ 廣播失敗: {result}")
            return None


class TronQuery:
    """
    TRON 查詢功能封裝

    提供各種鏈上數據查詢功能
    """

    @staticmethod
    def check_usdt_balance(api: TronAPI, address: str, contract_address: str) -> float:
        """
        查詢 USDT (TRC20) 餘額

        調用合約的 balanceOf 函數：
        function balanceOf(address _owner) returns (uint256)

        參數：
            api: TronAPI 實例
            address: 要查詢的地址
            contract_address: USDT 合約地址

        返回：
            USDT 餘額（單位: USDT）

        範例：
            >>> balance = TronQuery.check_usdt_balance(
            ...     api,
            ...     "TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u",
            ...     TronNetwork.USDT_CONTRACT_NILE
            ... )
            >>> print(f"USDT 餘額: {balance}")
        """
        # 編碼參數: address 補齊到 32 bytes
        addr_hex = AddressConverter.base58_to_hex(address, include_prefix=False)
        parameter = addr_hex.zfill(64)

        # 調用合約
        result = api.trigger_constant_contract(
            contract_address=contract_address,
            function_selector="balanceOf(address)",
            parameter=parameter,
            owner_address=address,
        )

        # 解析結果
        if "constant_result" in result and result["constant_result"]:
            balance_hex = result["constant_result"][0]
            balance_raw = int(balance_hex, 16)
            return balance_raw / 1_000_000  # USDT 有 6 位小數

        return 0.0


# ============================================
# 使用範例
# ============================================


def main():
    """
    主程式 - 示範所有功能的使用方式
    """
    print("=" * 70)
    print("TRON 區塊鏈底層實現 - 純 Python 版本")
    print("直接使用 HTTP API，深入理解底層原理")
    print("=" * 70)

    # ========================================
    # 1. 地址轉換測試
    # ========================================
    print("\n【測試 1】地址格式轉換")
    print("-" * 70)

    test_base58 = "TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u"
    test_hex = "41a49b6890465f39fce73b18e5c9c5fd9136c70e38"

    print(f"Base58 地址: {test_base58}")
    converted_hex = AddressConverter.base58_to_hex(test_base58)
    print(f"轉為 Hex: {converted_hex}")
    print(f"驗證: {'✓ 通過' if converted_hex == test_hex else '✗ 失敗'}")

    print(f"\nHex 地址: {test_hex}")
    converted_base58 = AddressConverter.hex_to_base58(test_hex)
    print(f"轉為 Base58: {converted_base58}")
    print(f"驗證: {'✓ 通過' if converted_base58 == test_base58 else '✗ 失敗'}")

    # ========================================
    # 2. 從私鑰生成地址
    # ========================================
    print("\n【測試 2】從私鑰生成地址")
    print("-" * 70)

    # 警告：這是測試用私鑰，切勿在生產環境使用！
    test_private_key = (
        "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"
    )

    print(f"私鑰: {test_private_key}")
    test_address = KeyGenerator.private_key_to_address(test_private_key)
    print(f"生成的地址: {test_address}")
    print(f"驗證: {'✓ 通過' if test_address == test_base58 else '✗ 失敗'}")

    # ========================================
    # 3. 初始化 API 連接
    # ========================================
    print("\n【測試 3】連接到 TRON 網路")
    print("-" * 70)

    api = TronAPI(TronNetwork.NILE_API, api_key=None)
    print("✓ 已連接到 Nile 測試網")
    print(f"  API 端點: {TronNetwork.NILE_API}")

    # ========================================
    # 4. 查詢帳戶餘額
    # ========================================
    print("\n【測試 4】查詢帳戶餘額")
    print("-" * 70)

    my_address = "TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u"

    # 查詢 TRX 餘額
    trx_balance = api.get_account_balance(my_address)
    print(f"地址: {my_address}")
    print(f"TRX 餘額: {trx_balance:.6f} TRX")

    # 查詢 USDT 餘額
    usdt_balance = TronQuery.check_usdt_balance(
        api, my_address, TronNetwork.USDT_CONTRACT_NILE
    )
    print(f"USDT 餘額: {usdt_balance:.6f} USDT")

    # ========================================
    # 5. TRX 轉賬示範
    # ========================================
    print("\n【測試 5】TRX 轉賬")
    print("-" * 70)

    my_private_key = "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"
    to_addr = "TTqobYiHixykLYyA3WxmCLVCMCySHfigyE"

    txid = TronTransfer.transfer_trx(api, my_private_key, to_addr, 1.0, verbose=True)

    if txid:
        print(f"\n✅ TRX 轉賬成功!")
        print(f"查看交易: https://nile.tronscan.org/#/transaction/{txid}")

    # ========================================
    # 6. USDT 轉賬示範
    # ========================================
    print("\n【測試 6】USDT 轉賬")
    print("-" * 70)

    txid = TronTransfer.transfer_usdt(
        api, my_private_key, to_addr, 1.0, TronNetwork.USDT_CONTRACT_NILE, verbose=True
    )

    if txid:
        print(f"\n✅ USDT 轉賬成功!")
        print(f"查看交易: https://nile.tronscan.org/#/transaction/{txid}")

    # ========================================
    # 總結
    # ========================================
    print("\n" + "=" * 70)
    print("測試完成!")
    print("=" * 70)
    print("\n本程式示範了 TRON 區塊鏈的底層實現原理，包括：")
    print("  ✓ 地址格式轉換 (Base58 ↔ Hex)")
    print("  ✓ 從私鑰生成公鑰和地址")
    print("  ✓ 查詢帳戶餘額 (TRX 和 TRC20)")
    print("  ✓ 建立、簽名、廣播交易")
    print("  ✓ TRX 和 USDT 轉賬")
    print("\n所有功能均直接使用 HTTP API 實現，")
    print("無需依賴 tronpy 等高階套件。")
    print("=" * 70)


if __name__ == "__main__":
    main()

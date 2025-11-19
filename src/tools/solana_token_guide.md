# 🪙 Solana 代幣系統白話文完整指南

## 🤔 首先搞懂：什麼時候需要 Rust？

### 不需要 Rust 的情況（大多數情況）
```
✅ 創建普通代幣 → 用 Solana CLI 就夠了
✅ 建立出入金系統 → 用 Python/JavaScript 就行
✅ 錢包整合 → 前端框架即可
✅ 一般 DeFi 功能 → 組合現有程式就好
```

### 需要 Rust 的情況（特殊需求）
```
❌ 自定義代幣邏輯 → 例如：每次轉帳收 1% 手續費
❌ 複雜智能合約 → 例如：多重簽名、投票系統
❌ 高性能應用 → 例如：高頻交易、遊戲引擎
❌ 創新金融產品 → 例如：新型 AMM、借貸協議
```

**總結：90% 的專案用不到 Rust！**

---

## 💰 出入金系統詳細解析

### 什麼是出入金？
- **入金（充值）**：用戶從自己錢包 → 轉到平臺
- **出金（提現）**：用戶從平臺 → 轉到自己錢包

### 為什麼需要出入金系統？
```
🏦 傳統交易所模式：
用戶錢包 ↔ 交易所繫統 ↔ 區塊鏈

優點：
✅ 交易快速（不用等區塊鏈確認）
✅ 手續費便宜（內部轉帳免費）
✅ 用戶體驗好（像銀行 APP）

缺點：
❌ 需要信任平臺
❌ 平臺可能跑路
```

---

## 🔄 出入金完整流程圖

```
📱 用戶操作流程：

1️⃣ 註冊階段：
用戶連接錢包 → 系統產生專用充值地址 → 用戶獲得帳號

2️⃣ 充值流程：
用戶錢包 → 轉帳到充值地址 → 系統監控到帳 → 更新用戶餘額

3️⃣ 內部交易：
用戶A餘額 → 扣除金額 → 用戶B餘額增加（秒到）

4️⃣ 提現流程：
檢查用戶餘額 → 從熱錢包轉出 → 到達用戶錢包 → 扣除用戶餘額
```

---

## 💻 完整系統架構

### 整體架構圖
```
🌐 前端 (React + 錢包連接)
     ↕ API 呼叫
🖥️ 後端 (Python FastAPI)
     ↕ 讀寫
🗄️ 資料庫 (PostgreSQL)
     ↕ 監控
⛓️ Solana 區塊鏈
```

### 詳細的出入金實作

#### 1. 充值監控系統（最重要！）
```python
# app/services/deposit_monitor.py - 白話版解釋
import asyncio
from decimal import Decimal
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

class DepositMonitor:
    """
    充值監控器 - 這是整個系統的核心！
    
    作用：不停地檢查用戶的充值地址，看有沒有新的轉帳進來
    就像銀行系統監控你的帳戶一樣
    """
    
    def __init__(self, solana_service):
        self.service = solana_service
        self.processed_transactions = set()  # 記住已經處理過的交易
        self.is_running = False
    
    async def start_monitoring(self):
        """開始無限循環監控"""
        self.is_running = True
        print("🔍 開始監控所有用戶的充值...")
        
        while self.is_running:
            try:
                # 每5秒檢查一次所有用戶
                await self.check_all_user_deposits()
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ 監控出錯: {e}")
                await asyncio.sleep(10)  # 出錯就等久一點再試
    
    async def check_all_user_deposits(self):
        """檢查所有用戶的充值地址"""
        
        # 從資料庫取出所有用戶的充值地址
        async with self.service.db_pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT user_id, deposit_address FROM user_balances WHERE deposit_address IS NOT NULL"
            )
        
        # 一個一個檢查
        for user in users:
            await self.check_single_user_deposit(user['user_id'], user['deposit_address'])
    
    async def check_single_user_deposit(self, user_id: str, deposit_address: str):
        """檢查單一用戶的充值"""
        try:
            # 轉換地址格式
            pubkey = Pubkey.from_string(deposit_address)
            
            # 向 Solana 區塊鏈查詢這個地址的最近交易
            signatures = await self.service.client.get_signatures_for_address(
                pubkey, 
                limit=20  # 只看最近20筆交易就夠了
            )
            
            # 檢查每一筆交易
            for sig_info in signatures.value:
                signature = sig_info.signature
                
                # 如果這筆交易已經處理過，就跳過
                if signature in self.processed_transactions:
                    continue
                
                # 處理新交易
                await self.process_new_deposit(user_id, signature)
                
                # 記住這筆交易已經處理過了
                self.processed_transactions.add(signature)
                
        except Exception as e:
            print(f"❌ 檢查用戶 {user_id} 充值失敗: {e}")
    
    async def process_new_deposit(self, user_id: str, transaction_signature: str):
        """處理新的充值交易"""
        try:
            # 獲取交易的詳細資料
            tx_detail = await self.service.client.get_transaction(transaction_signature)
            
            if not tx_detail.value:
                return  # 交易不存在就跳過
            
            # 解析交易，找出轉了多少代幣
            token_amount = await self.parse_token_amount_from_transaction(tx_detail.value)
            
            if token_amount > 0:
                # 增加用戶餘額
                await self.credit_user_balance(user_id, token_amount, transaction_signature)
                
                # 通知用戶（可選）
                await self.notify_user_deposit_success(user_id, token_amount)
                
                print(f"✅ 用戶 {user_id} 充值成功: {token_amount} 代幣")
                
        except Exception as e:
            print(f"❌ 處理充值交易失敗: {e}")
    
    async def parse_token_amount_from_transaction(self, transaction) -> Decimal:
        """
        從交易中解析出代幣數量
        這裡簡化處理，實際需要解析 Solana 交易結構
        """
        # 實際實作需要：
        # 1. 解析 transaction.transaction.message.instructions
        # 2. 找到 SPL Token 轉帳指令
        # 3. 提取轉帳金額
        # 4. 轉換小數位數
        
        # 這裡用固定值示範
        return Decimal('100.5')  # 假設轉了 100.5 個代幣
    
    async def credit_user_balance(self, user_id: str, amount: Decimal, tx_signature: str):
        """增加用戶餘額並記錄交易"""
        async with self.service.db_pool.acquire() as conn:
            async with conn.transaction():  # 使用資料庫交易確保一致性
                
                # 增加用戶餘額
                await conn.execute(
                    """
                    UPDATE user_balances 
                    SET token_balance = token_balance + $1,
                        updated_at = NOW()
                    WHERE user_id = $2
                    """,
                    amount, user_id
                )
                
                # 記錄充值交易
                await conn.execute(
                    """
                    INSERT INTO transactions 
                    (user_id, tx_signature, type, amount, status, confirmed_at)
                    VALUES ($1, $2, 'deposit', $3, 'confirmed', NOW())
                    """,
                    user_id, tx_signature, amount
                )
    
    async def notify_user_deposit_success(self, user_id: str, amount: Decimal):
        """通知用戶充值成功（可選功能）"""
        # 可以整合：
        # 1. WebSocket 即時通知
        # 2. 推播通知
        # 3. Email 通知
        # 4. Telegram Bot 通知
        pass
```

#### 2. 提現處理系統
```python
# app/services/withdrawal_service.py - 白話版
from decimal import Decimal
from typing import Dict
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

class WithdrawalService:
    """
    提現服務 - 處理用戶提現到自己錢包
    
    重要概念：
    - 熱錢包：平臺控制的錢包，用來發送代幣給用戶
    - 冷錢包：離線存儲大部分代幣，安全性高
    """
    
    def __init__(self, solana_service):
        self.service = solana_service
        self.withdrawal_fee = Decimal('0.1')    # 提現手續費
        self.min_withdrawal = Decimal('10')     # 最小提現金額
        self.max_daily_withdrawal = Decimal('10000')  # 每日提現限額
    
    async def process_user_withdrawal(self, user_id: str, amount: Decimal, target_wallet: str) -> Dict:
        """
        處理用戶提現請求
        
        流程：
        1. 檢查用戶餘額夠不夠
        2. 檢查提現限制（最小金額、每日限額等）
        3. 從熱錢包轉帳到用戶錢包
        4. 扣除用戶平臺餘額
        5. 記錄交易
        """
        try:
            # 第一步：各種檢查
            validation_result = await self.validate_withdrawal_request(user_id, amount, target_wallet)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # 第二步：計算總費用（提現金額 + 手續費）
            total_cost = amount + self.withdrawal_fee
            
            # 第三步：檢查用戶餘額
            user_balance = await self.service.get_user_balance(user_id)
            if user_balance < total_cost:
                return {
                    'success': False, 
                    'error': f'餘額不足，需要 {total_cost}（包含手續費 {self.withdrawal_fee}）'
                }
            
            # 第四步：執行區塊鏈轉帳
            blockchain_result = await self.send_tokens_on_blockchain(amount, target_wallet)
            if not blockchain_result['success']:
                return {'success': False, 'error': f'區塊鏈轉帳失敗: {blockchain_result["error"]}'}
            
            # 第五步：更新資料庫（扣除用戶餘額、記錄交易）
            await self.update_database_after_withdrawal(
                user_id, amount, target_wallet, blockchain_result['signature']
            )
            
            return {
                'success': True,
                'transaction_signature': blockchain_result['signature'],
                'amount_sent': str(amount),
                'fee_charged': str(self.withdrawal_fee),
                'target_wallet': target_wallet,
                'explorer_url': f'https://solscan.io/tx/{blockchain_result["signature"]}'
            }
            
        except Exception as e:
            # 記錄錯誤日誌
            await self.log_withdrawal_error(user_id, amount, target_wallet, str(e))
            return {'success': False, 'error': f'系統錯誤: {str(e)}'}
    
    async def validate_withdrawal_request(self, user_id: str, amount: Decimal, target_wallet: str) -> Dict:
        """驗證提現請求是否合法"""
        
        # 檢查金額是否符合限制
        if amount < self.min_withdrawal:
            return {'valid': False, 'error': f'提現金額不能少於 {self.min_withdrawal}'}
        
        # 檢查錢包地址格式
        try:
            Pubkey.from_string(target_wallet)
        except:
            return {'valid': False, 'error': '錢包地址格式錯誤'}
        
        # 檢查每日提現限額
        daily_withdrawn = await self.get_user_daily_withdrawal_amount(user_id)
        if daily_withdrawn + amount > self.max_daily_withdrawal:
            return {
                'valid': False, 
                'error': f'超過每日提現限額 {self.max_daily_withdrawal}，今日已提現 {daily_withdrawn}'
            }
        
        # 檢查用戶狀態
        user_status = await self.get_user_account_status(user_id)
        if user_status != 'active':
            return {'valid': False, 'error': '帳戶已被凍結'}
        
        return {'valid': True}
    
    async def send_tokens_on_blockchain(self, amount: Decimal, target_wallet: str) -> Dict:
        """在區塊鏈上執行實際的代幣轉帳"""
        try:
            # 建立 SPL Token 客戶端
            token_client = AsyncToken(
                self.service.client,           # Solana RPC 連接
                self.service.token_mint,       # 我們的代幣合約地址
                TOKEN_PROGRAM_ID,              # SPL Token 程式 ID
                self.service.hot_wallet        # 平臺熱錢包（用來發送代幣）
            )
            
            # 獲取目標錢包的代幣帳戶（如果沒有就創建一個）
            target_pubkey = Pubkey.from_string(target_wallet)
            target_token_account = await token_client.get_or_create_associated_account_info(target_pubkey)
            
            # 獲取平臺熱錢包的代幣帳戶
            source_token_account = await token_client.get_or_create_associated_account_info(
                self.service.hot_wallet.pubkey()
            )
            
            # 轉換金額格式（考慮代幣的小數位數）
            # 假設我們的代幣有 9 位小數
            token_amount_raw = int(amount * (10 ** 9))
            
            # 執行轉帳
            transfer_response = await token_client.transfer(
                source=source_token_account,    # 從熱錢包
                dest=target_token_account,      # 到用戶錢包
                owner=self.service.hot_wallet,  # 簽名者（熱錢包）
                amount=token_amount_raw         # 轉帳金額
            )
            
            # 等待交易確認
            confirmation = await self.service.client.confirm_transaction(transfer_response.value)
            
            return {
                'success': True,
                'signature': str(transfer_response.value)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_database_after_withdrawal(self, user_id: str, amount: Decimal, target_wallet: str, tx_signature: str):
        """提現成功後更新資料庫"""
        total_deducted = amount + self.withdrawal_fee
        
        async with self.service.db_pool.acquire() as conn:
            async with conn.transaction():
                
                # 扣除用戶餘額
                await conn.execute(
                    """
                    UPDATE user_balances 
                    SET token_balance = token_balance - $1,
                        updated_at = NOW()
                    WHERE user_id = $2
                    """,
                    total_deducted, user_id
                )
                
                # 記錄提現交易
                await conn.execute(
                    """
                    INSERT INTO transactions 
                    (user_id, tx_signature, type, amount, to_address, fee, status, confirmed_at)
                    VALUES ($1, $2, 'withdraw', $3, $4, $5, 'confirmed', NOW())
                    """,
                    user_id, tx_signature, amount, target_wallet, self.withdrawal_fee
                )
                
                print(f"✅ 用戶 {user_id} 提現 {amount} 代幣到 {target_wallet}")
    
    async def get_user_daily_withdrawal_amount(self, user_id: str) -> Decimal:
        """查詢用戶今日已提現金額"""
        async with self.service.db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions 
                WHERE user_id = $1 
                  AND type = 'withdraw' 
                  AND status = 'confirmed'
                  AND DATE(confirmed_at) = CURRENT_DATE
                """,
                user_id
            )
            return Decimal(result)
    
    async def get_user_account_status(self, user_id: str) -> str:
        """查詢用戶帳戶狀態"""
        async with self.service.db_pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT status FROM user_balances WHERE user_id = $1",
                user_id
            )
            return result or 'inactive'
```

#### 3. 內部轉帳系統（用戶之間互轉）
```python
# app/services/internal_transfer.py - 白話版
class InternalTransferService:
    """
    內部轉帳服務 - 用戶在平臺內互相轉帳
    
    優點：
    - 不用上區塊鏈，秒到帳
    - 不用付 Gas 費
    - 就像銀行內部轉帳一樣快
    """
    
    def __init__(self, solana_service):
        self.service = solana_service
        self.transfer_fee = Decimal('0')  # 內部轉帳免手續費
    
    async def transfer_between_users(self, from_user: str, to_user: str, amount: Decimal, memo: str = "") -> Dict:
        """用戶之間轉帳"""
        try:
            # 檢查轉帳金額
            if amount <= 0:
                return {'success': False, 'error': '轉帳金額必須大於 0'}
            
            # 檢查發送方餘額
            sender_balance = await self.service.get_user_balance(from_user)
            if sender_balance < amount:
                return {'success': False, 'error': '餘額不足'}
            
            # 檢查接收方是否存在
            receiver_exists = await self.check_user_exists(to_user)
            if not receiver_exists:
                return {'success': False, 'error': '接收方用戶不存在'}
            
            # 執行轉帳（原子操作）
            async with self.service.db_pool.acquire() as conn:
                async with conn.transaction():
                    
                    # 扣除發送方餘額
                    await conn.execute(
                        "UPDATE user_balances SET token_balance = token_balance - $1 WHERE user_id = $2",
                        amount, from_user
                    )
                    
                    # 增加接收方餘額
                    await conn.execute(
                        "UPDATE user_balances SET token_balance = token_balance + $1 WHERE user_id = $2",
                        amount, to_user
                    )
                    
                    # 記錄轉帳
                    transfer_id = await conn.fetchval(
                        """
                        INSERT INTO internal_transfers 
                        (from_user, to_user, amount, memo, status, created_at)
                        VALUES ($1, $2, $3, $4, 'completed', NOW())
                        RETURNING id
                        """,
                        from_user, to_user, amount, memo
                    )
            
            return {
                'success': True,
                'transfer_id': transfer_id,
                'from_user': from_user,
                'to_user': to_user,
                'amount': str(amount),
                'memo': memo
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

---

## 🗄️ 完整資料庫設計

```sql
-- 用戶餘額表
CREATE TABLE user_balances (
    user_id VARCHAR(64) PRIMARY KEY,           -- 用戶ID（通常是錢包地址）
    wallet_address VARCHAR(64) UNIQUE NOT NULL,-- 用戶的主錢包地址
    deposit_address VARCHAR(64) UNIQUE,        -- 平臺分配的充值地址
    token_balance DECIMAL(20,8) DEFAULT 0,     -- 用戶在平臺的代幣餘額
    status VARCHAR(20) DEFAULT 'active',       -- 帳戶狀態
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 交易記錄表（區塊鏈交易）
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    tx_signature VARCHAR(128) UNIQUE,          -- 區塊鏈交易簽名
    type VARCHAR(20) CHECK (type IN ('deposit', 'withdraw')),
    amount DECIMAL(20,8) NOT NULL,
    from_address VARCHAR(64),
    to_address VARCHAR(64),
    fee DECIMAL(20,8) DEFAULT 0,              -- 手續費
    status VARCHAR(20) DEFAULT 'pending',      -- pending, confirmed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_balances(user_id)
);

-- 內部轉帳表（不上鏈）
CREATE TABLE internal_transfers (
    id SERIAL PRIMARY KEY,
    from_user VARCHAR(64) NOT NULL,
    to_user VARCHAR(64) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    memo TEXT,                                -- 轉帳備註
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (from_user) REFERENCES user_balances(user_id),
    FOREIGN KEY (to_user) REFERENCES user_balances(user_id)
);

-- 系統設置表
CREATE TABLE system_settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 插入基本設置
INSERT INTO system_settings (key, value, description) VALUES
('withdrawal_fee', '0.1', '提現手續費'),
('min_withdrawal', '10', '最小提現金額'),
('max_daily_withdrawal', '10000', '每日提現限額'),
('deposit_confirmations', '12', '充值需要的確認數');
```

---

## 🎯 用戶使用流程（白話版）

### 1. 用戶註冊
```
用戶：我要註冊
1. 用戶連接 Phantom 錢包
2. 系統：看到你的錢包地址了，幫你創建帳號
3. 系統：這是你的專用充值地址：ABC123...
4. 用戶：好，我記住了
```

### 2. 充值（入金）
```
用戶：我要充值 100 個代幣
1. 用戶從自己錢包轉 100 代幣到充值地址
2. 系統監控程式：咦，ABC123 地址收到 100 代幣了
3. 系統：確認是這個用戶的，幫他加餘額
4. 用戶：看到平臺餘額變成 100 了，開心！
```

### 3. 內部交易
```
用戶A：我要轉 50 代幣給用戶B
1. 系統：檢查用戶A餘額夠不夠
2. 系統：夠，扣除用戶A的 50，增加用戶B的 50
3. 用戶A：餘額變成 50
4. 用戶B：餘額增加 50，秒到帳！
```

### 4. 提現（出金）
```
用戶：我要提現 30 代幣到我錢包
1. 系統：檢查餘額、手續費、限額
2. 系統：OK，從熱錢包轉 30 代幣到你錢包
3. 區塊鏈：交易確認
4. 系統：扣除用戶餘額 30 + 手續費
5. 用戶：錢包收到 30 代幣！
```

---

## 💡 關鍵概念解釋

### 熱錢包 vs 冷錢包
```
🔥 熱錢包（Hot Wallet）：
- 連網的錢包，平臺控制
- 用來處理日常出入金
- 風險：被駭客攻擊
- 建議：只放少量資金

🧊 冷錢包（Cold Wallet）：
- 離線錢包，超級安全
- 存放大部分資金
- 風險：操作麻煩
- 建議：定期從熱錢包轉入
```

### 託管 vs 非託管
```
🏦 託管模式（我們的系統）：
- 平臺幫你保管代幣
- 交易快速、體驗好
- 需要信任平臺

🔑 非託管模式（DeFi）：
- 用戶自己控制私鑰
- 去中心化、不用信任
- 交易慢、Gas費高
```

---

## 🚀 詳細快速啟動指南

### 準備工作（5分鐘）
```bash
# 檢查系統需求
echo "檢查 Python 版本..."
python3 --version  # 需要 3.8+

echo "檢查 Node.js 版本..."
node --version  # 需要 16+

echo "檢查 Docker..."
docker --version  # 需要最新版

echo "檢查 Git..."
git --version
```

---

## 第一步：創建代幣（詳細版 - 15分鐘）

### 1.1 安裝 Solana 工具鏈
```bash
# macOS/Linux
echo "🔧 安裝 Solana CLI..."
sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)"

# 重新載入環境變數
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# 驗證安裝
solana --version
echo "✅ Solana CLI 安裝完成"

# 安裝 SPL Token CLI
echo "🔧 安裝 SPL Token CLI..."
cargo install spl-token-cli --version 3.4.0

# 驗證安裝
spl-token --version
echo "✅ SPL Token CLI 安裝完成"
```

### 1.2 設定錢包和網路
```bash
# 設定為測試網
echo "🌐 設定 Solana 測試網..."
solana config set --url https://api.devnet.solana.com

# 創建新錢包
echo "💰 創建主錢包..."
solana-keygen new --outfile ~/solana-mainnet-wallet.json --force

# 設定為預設錢包
solana config set --keypair ~/solana-mainnet-wallet.json

# 查看錢包地址
WALLET_ADDRESS=$(solana-keygen pubkey ~/solana-mainnet-wallet.json)
echo "錢包地址: $WALLET_ADDRESS"

# 查看當前配置
solana config get
```

### 1.3 獲取測試幣並創建代幣
```bash
echo "💸 獲取測試 SOL..."
solana airdrop 2
solana balance

echo "🪙 創建新代幣..."
# 創建代幣（9位小數）
TOKEN_MINT=$(spl-token create-token --decimals 9 2>&1 | grep "Creating token" | awk '{print $3}')
echo "代幣合約地址: $TOKEN_MINT"

# 創建代幣帳戶
echo "📝 創建代幣帳戶..."
TOKEN_ACCOUNT=$(spl-token create-account $TOKEN_MINT 2>&1 | grep "Creating account" | awk '{print $3}')
echo "代幣帳戶地址: $TOKEN_ACCOUNT"

# 鑄造代幣（100萬顆）
echo "⚡ 鑄造 1,000,000 代幣..."
spl-token mint $TOKEN_MINT 1000000

# 查看餘額
spl-token balance $TOKEN_MINT
echo "✅ 代幣創建完成！"

# 保存重要資訊
echo "=== 重要資訊 ===" > token_info.txt
echo "錢包地址: $WALLET_ADDRESS" >> token_info.txt
echo "代幣合約: $TOKEN_MINT" >> token_info.txt
echo "代幣帳戶: $TOKEN_ACCOUNT" >> token_info.txt
echo "建立時間: $(date)" >> token_info.txt
echo "✅ 代幣資訊已保存到 token_info.txt"
```

---

## 第二步：建立完整系統（詳細版 - 45分鐘）

### 2.1 創建專案結構（5分鐘）
```bash
echo "📁 創建專案結構..."
mkdir -p solana-token-system
cd solana-token-system

# 創建目錄結構
mkdir -p {app/{api,services,utils,models},frontend,docker,scripts,tests,logs,secure}

# 創建 Python 模組檔案
touch app/__init__.py
touch app/api/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch app/models/__init__.py

echo "✅ 專案結構創建完成"
tree . -I '__pycache__'
```

### 2.2 設定 Python 環境（5分鐘）
```bash
echo "🐍 設定 Python 環境..."

# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# 升級 pip
pip install --upgrade pip

# 創建需求文件
cat > requirements.txt << 'EOF'
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Solana 相關
solana==0.34.2
solders==0.21.0
spl-token==0.2.0

# 資料庫
asyncpg==0.29.0
psycopg2-binary==2.9.9

# 工具庫
pydantic==2.5.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# 測試
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# 其他
aiofiles==23.2.1
websockets==12.0
redis==5.0.1
EOF

# 安裝依賴
echo "📦 安裝 Python 依賴..."
pip install -r requirements.txt

echo "✅ Python 環境設定完成"
```

### 2.3 設定資料庫（10分鐘）
```bash
echo "🗄️ 設定資料庫..."

# 創建 Docker Compose 文件
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: solana_postgres
    environment:
      POSTGRES_DB: solana_token_db
      POSTGRES_USER: solana_user
      POSTGRES_PASSWORD: solana_password_123
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    container_name: solana_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  adminer:
    image: adminer
    container_name: solana_adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
EOF

# 創建資料庫初始化腳本
cat > scripts/init_db.sql << 'EOF'
-- 用戶餘額表
CREATE TABLE IF NOT EXISTS user_balances (
    user_id VARCHAR(64) PRIMARY KEY,
    wallet_address VARCHAR(64) UNIQUE NOT NULL,
    deposit_address VARCHAR(64) UNIQUE,
    token_balance DECIMAL(20,8) DEFAULT 0,
    sol_balance DECIMAL(20,8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 交易記錄表
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    tx_signature VARCHAR(128) UNIQUE,
    type VARCHAR(20) CHECK (type IN ('deposit', 'withdraw', 'internal')),
    amount DECIMAL(20,8) NOT NULL,
    from_address VARCHAR(64),
    to_address VARCHAR(64),
    fee DECIMAL(20,8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    memo TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_balances(user_id)
);

-- 內部轉帳表
CREATE TABLE IF NOT EXISTS internal_transfers (
    id SERIAL PRIMARY KEY,
    from_user VARCHAR(64) NOT NULL,
    to_user VARCHAR(64) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    memo TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (from_user) REFERENCES user_balances(user_id),
    FOREIGN KEY (to_user) REFERENCES user_balances(user_id)
);

-- 系統設置表
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 創建索引
CREATE INDEX IF NOT EXISTS idx_user_balances_wallet ON user_balances(wallet_address);
CREATE INDEX IF NOT EXISTS idx_user_balances_deposit ON user_balances(deposit_address);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_signature ON transactions(tx_signature);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_internal_transfers_from ON internal_transfers(from_user);
CREATE INDEX IF NOT EXISTS idx_internal_transfers_to ON internal_transfers(to_user);

-- 插入基本設置
INSERT INTO system_settings (key, value, description) VALUES
('withdrawal_fee', '0.1', '提現手續費'),
('min_withdrawal', '10', '最小提現金額'),
('max_daily_withdrawal', '10000', '每日提現限額'),
('deposit_confirmations', '12', '充值確認區塊數'),
('internal_transfer_fee', '0', '內部轉帳手續費'),
('system_maintenance', 'false', '系統維護狀態')
ON CONFLICT (key) DO NOTHING;

-- 創建測試用戶
INSERT INTO user_balances (user_id, wallet_address, token_balance) VALUES
('test_user_1', 'DemoWallet111111111111111111111111111111111', 1000.00),
('test_user_2', 'DemoWallet222222222222222222222222222222222', 500.00)
ON CONFLICT (user_id) DO NOTHING;
EOF

# 啟動資料庫
echo "🚀 啟動資料庫服務..."
docker-compose up -d postgres redis

# 等待資料庫啟動
echo "⏳ 等待資料庫啟動..."
sleep 10

# 測試資料庫連接
echo "🔍 測試資料庫連接..."
docker-compose exec postgres psql -U solana_user -d solana_token_db -c "SELECT 'Database is ready!' as status;"

echo "✅ 資料庫設定完成"
echo "📊 資料庫管理介面: http://localhost:8080"
echo "   使用者名稱: solana_user"
echo "   密碼: solana_password_123"
echo "   資料庫: solana_token_db"
```

### 2.4 創建環境配置（5分鐘）
```bash
echo "⚙️ 創建環境配置..."

# 從之前保存的代幣資訊讀取
if [ -f "../token_info.txt" ]; then
    TOKEN_MINT=$(grep "代幣合約:" ../token_info.txt | cut -d' ' -f2)
    WALLET_ADDRESS=$(grep "錢包地址:" ../token_info.txt | cut -d' ' -f2)
else
    echo "⚠️ 找不到代幣資訊，請手動設定"
    TOKEN_MINT="YOUR_TOKEN_MINT_ADDRESS"
    WALLET_ADDRESS="YOUR_WALLET_ADDRESS"
fi

# 創建環境變數文件
cat > .env << EOF
# 資料庫配置
DATABASE_URL=postgresql://solana_user:solana_password_123@localhost:5432/solana_token_db
REDIS_URL=redis://localhost:6379/0

# Solana 配置
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_NETWORK=devnet
TOKEN_MINT_ADDRESS=$TOKEN_MINT
MAIN_WALLET_ADDRESS=$WALLET_ADDRESS

# 錢包路徑
HOT_WALLET_PATH=./secure/hot_wallet.json
COLD_WALLET_PATH=./secure/cold_wallet.json

# API 配置
API_V1_STR=/api/v1
PROJECT_NAME=Solana Token System
VERSION=1.0.0
DEBUG=true

# JWT 配置
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 安全配置
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# 業務配置
MIN_WITHDRAWAL_AMOUNT=10.0
MAX_WITHDRAWAL_AMOUNT=100000.0
WITHDRAWAL_FEE_RATE=0.1
DEPOSIT_CONFIRMATION_BLOCKS=12

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/app.log
EOF

# 複製主錢包到安全目錄
echo "🔐 複製錢包文件..."
cp ~/solana-mainnet-wallet.json ./secure/hot_wallet.json
cp ~/solana-mainnet-wallet.json ./secure/cold_wallet.json

# 設定文件權限
chmod 600 ./secure/*.json
chmod 600 .env

echo "✅ 環境配置完成"
```

### 2.5 創建核心服務代碼（15分鐘）
```bash
echo "💻 創建核心服務代碼..."

# 創建主要的 Solana 服務
cat > app/services/solana_service.py << 'EOF'
import asyncio
import json
import asyncpg
from decimal import Decimal
from typing import Dict, Optional, List
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
import logging

logger = logging.getLogger(__name__)

class SolanaTokenService:
    def __init__(self, rpc_url: str, token_mint: str, hot_wallet_path: str):
        self.client = AsyncClient(rpc_url)
        self.token_mint = Pubkey.from_string(token_mint)
        self.hot_wallet = self._load_wallet(hot_wallet_path)
        self.db_pool = None
        
        logger.info(f"Solana service initialized with RPC: {rpc_url}")
        logger.info(f"Token mint: {token_mint}")
        logger.info(f"Hot wallet: {self.hot_wallet.pubkey()}")
    
    def _load_wallet(self, path: str) -> Keypair:
        """載入錢包私鑰"""
        try:
            with open(path, 'r') as f:
                secret_key = json.load(f)
            return Keypair.from_bytes(bytes(secret_key))
        except Exception as e:
            logger.error(f"Failed to load wallet from {path}: {e}")
            raise
    
    async def init_db_pool(self, database_url: str):
        """初始化資料庫連接池"""
        try:
            self.db_pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def create_user_deposit_address(self, user_wallet: str) -> str:
        """為用戶創建專用充值地址"""
        try:
            # 生成新的充值地址
            new_keypair = Keypair()
            deposit_address = str(new_keypair.pubkey())
            
            # 保存到資料庫
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO user_balances (user_id, wallet_address, deposit_address, token_balance)
                    VALUES ($1, $2, $3, 0)
                    ON CONFLICT (user_id) DO UPDATE SET 
                        deposit_address = $3,
                        updated_at = NOW()
                    """,
                    user_wallet, user_wallet, deposit_address
                )
            
            # 安全保存充值地址私鑰
            deposit_wallet_path = f"./secure/deposit_{user_wallet[:8]}.json"
            with open(deposit_wallet_path, 'w') as f:
                json.dump(list(new_keypair.secret()), f)
            
            logger.info(f"Created deposit address for user {user_wallet}: {deposit_address}")
            return deposit_address
            
        except Exception as e:
            logger.error(f"Failed to create deposit address for {user_wallet}: {e}")
            raise
    
    async def get_user_balance(self, user_id: str) -> Dict[str, Decimal]:
        """查詢用戶餘額"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT token_balance, sol_balance FROM user_balances WHERE user_id = $1",
                    user_id
                )
                if row:
                    return {
                        'token': Decimal(str(row['token_balance'])),
                        'sol': Decimal(str(row['sol_balance'])) if row['sol_balance'] else Decimal('0')
                    }
                return {'token': Decimal('0'), 'sol': Decimal('0')}
        except Exception as e:
            logger.error(f"Failed to get balance for user {user_id}: {e}")
            raise
    
    async def update_user_balance(self, user_id: str, amount: Decimal, operation: str):
        """更新用戶餘額"""
        try:
            async with self.db_pool.acquire() as conn:
                if operation == 'add':
                    await conn.execute(
                        "UPDATE user_balances SET token_balance = token_balance + $1, updated_at = NOW() WHERE user_id = $2",
                        amount, user_id
                    )
                elif operation == 'subtract':
                    await conn.execute(
                        "UPDATE user_balances SET token_balance = token_balance - $1, updated_at = NOW() WHERE user_id = $2",
                        amount, user_id
                    )
                    
            logger.info(f"Updated balance for user {user_id}: {operation} {amount}")
        except Exception as e:
            logger.error(f"Failed to update balance for user {user_id}: {e}")
            raise
    
    async def get_all_deposit_addresses(self) -> List[tuple]:
        """獲取所有用戶的充值地址"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT user_id, deposit_address FROM user_balances WHERE deposit_address IS NOT NULL"
                )
                return [(row['user_id'], row['deposit_address']) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get deposit addresses: {e}")
            raise
    
    async def record_transaction(self, user_id: str, tx_signature: str, tx_type: str, 
                               amount: Decimal, from_addr: str = None, to_addr: str = None,
                               fee: Decimal = Decimal('0'), status: str = 'confirmed'):
        """記錄交易"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO transactions 
                    (user_id, tx_signature, type, amount, from_address, to_address, fee, status, confirmed_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                    ON CONFLICT (tx_signature) DO NOTHING
                    """,
                    user_id, tx_signature, tx_type, amount, from_addr, to_addr, fee, status
                )
            logger.info(f"Recorded transaction for user {user_id}: {tx_type} {amount}")
        except Exception as e:
            logger.error(f"Failed to record transaction: {e}")
            raise
EOF

# 創建充值監控服務
cat > app/services/deposit_monitor.py << 'EOF'
import asyncio
import logging
from typing import Set
from decimal import Decimal
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)

class DepositMonitor:
    def __init__(self, solana_service):
        self.service = solana_service
        self.processed_signatures: Set[str] = set()
        self.is_running = False
        self.check_interval = 10  # 每10秒檢查一次
    
    async def start_monitoring(self):
        """開始監控充值"""
        self.is_running = True
        logger.info("🔍 Deposit monitoring started")
        
        while self.is_running:
            try:
                await self.check_all_deposits()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)  # 出錯等30秒再試
    
    async def stop_monitoring(self):
        """停止監控"""
        self.is_running = False
        logger.info("🛑 Deposit monitoring stopped")
    
    async def check_all_deposits(self):
        """檢查所有用戶的充值"""
        try:
            deposit_addresses = await self.service.get_all_deposit_addresses()
            
            for user_id, deposit_address in deposit_addresses:
                if deposit_address:
                    await self.check_user_deposits(user_id, deposit_address)
                    
        except Exception as e:
            logger.error(f"Failed to check deposits: {e}")
    
    async def check_user_deposits(self, user_id: str, deposit_address: str):
        """檢查單一用戶的充值"""
        try:
            pubkey = Pubkey.from_string(deposit_address)
            
            # 獲取最近的交易簽名
            signatures = await self.service.client.get_signatures_for_address(
                pubkey,
                limit=20,
                commitment=Confirmed
            )
            
            for sig_info in signatures.value:
                signature = sig_info.signature
                
                # 跳過已處理的交易
                if signature in self.processed_signatures:
                    continue
                
                # 處理新交易
                await self.process_deposit_transaction(user_id, signature, deposit_address)
                self.processed_signatures.add(signature)
                
        except Exception as e:
            logger.error(f"Failed to check deposits for user {user_id}: {e}")
    
    async def process_deposit_transaction(self, user_id: str, signature: str, deposit_address: str):
        """處理充值交易"""
        try:
            # 獲取交易詳情
            tx_response = await self.service.client.get_transaction(
                signature,
                commitment=Confirmed
            )
            
            if not tx_response.value:
                return
            
            # 簡化版本：假設每筆到這個地址的交易都是有效充值
            # 實際需要解析交易詳情來確定準確金額
            amount = Decimal('100')  # 示例金額
            
            # 更新用戶餘額
            await self.service.update_user_balance(user_id, amount, 'add')
            
            # 記錄交易
            await self.service.record_transaction(
                user_id, signature, 'deposit', amount, 
                from_addr='external', to_addr=deposit_address
            )
            
            logger.info(f"✅ Processed deposit for user {user_id}: {amount} tokens")
            
        except Exception as e:
            logger.error(f"Failed to process deposit transaction {signature}: {e}")
EOF

# 創建 FastAPI 主應用
cat > app/main.py << 'EOF'
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from dotenv import load_dotenv

from .services.solana_service import SolanaTokenService
from .services.deposit_monitor import DepositMonitor

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全域服務實例
solana_service = None
deposit_monitor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時
    global solana_service, deposit_monitor
    
    logger.info("🚀 Starting Solana Token System...")
    
    # 初始化 Solana 服務
    solana_service = SolanaTokenService(
        rpc_url=os.getenv("SOLANA_RPC_URL"),
        token_mint=os.getenv("TOKEN_MINT_ADDRESS"),
        hot_wallet_path=os.getenv("HOT_WALLET_PATH")
    )
    
    await solana_service.init_db_pool(os.getenv("DATABASE_URL"))
    
    # 初始化充值監控
    deposit_monitor = DepositMonitor(solana_service)
    
    # 在背景啟動監控
    monitor_task = asyncio.create_task(deposit_monitor.start_monitoring())
    
    logger.info("✅ System started successfully")
    
    yield
    
    # 關閉時
    logger.info("🛑 Shutting down system...")
    if deposit_monitor:
        await deposit_monitor.stop_monitoring()
    
    monitor_task.cancel()
    logger.info("✅ System shutdown complete")

# 創建 FastAPI 應用
app = FastAPI(
    title="Solana Token System API",
    description="完整的 Solana 代幣出入金系統",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境，生產環境應限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求模型
class RegisterRequest(BaseModel):
    wallet_address: str

class WithdrawRequest(BaseModel):
    user_id: str
    amount: Decimal
    to_address: str

class TransferRequest(BaseModel):
    from_user: str
    to_user: str
    amount: Decimal
    memo: Optional[str] = ""

# 響應模型
class BalanceResponse(BaseModel):
    user_id: str
    token_balance: str
    sol_balance: str
    deposit_address: Optional[str] = None

# API 端點
@app.get("/")
async def root():
    return {
        "message": "Solana Token System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    try:
        # 檢查 Solana 連接
        health = await solana_service.client.get_health()
        
        # 檢查資料庫
        async with solana_service.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "solana_rpc": "connected",
            "database": "connected",
            "deposit_monitor": "running" if deposit_monitor.is_running else "stopped"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/api/register")
async def register_user(request: RegisterRequest):
    """用戶註冊"""
    try:
        # 驗證錢包地址格式
        from solders.pubkey import Pubkey
        Pubkey.from_string(request.wallet_address)
        
        # 創建充值地址
        deposit_address = await solana_service.create_user_deposit_address(request.wallet_address)
        
        return {
            "success": True,
            "user_id": request.wallet_address,
            "deposit_address": deposit_address,
            "message": "註冊成功"
        }
    except Exception as e:
        logger.error(f"Registration failed for {request.wallet_address}: {e}")
        raise HTTPException(status_code=400, detail=f"註冊失敗: {str(e)}")

@app.get("/api/balance/{user_id}", response_model=BalanceResponse)
async def get_balance(user_id: str):
    """查詢用戶餘額"""
    try:
        balance = await solana_service.get_user_balance(user_id)
        
        # 獲取充值地址
        async with solana_service.db_pool.acquire() as conn:
            deposit_addr = await conn.fetchval(
                "SELECT deposit_address FROM user_balances WHERE user_id = $1",
                user_id
            )
        
        return BalanceResponse(
            user_id=user_id,
            token_balance=str(balance['token']),
            sol_balance=str(balance['sol']),
            deposit_address=deposit_addr
        )
    except Exception as e:
        logger.error(f"Get balance failed for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/withdraw")
async def withdraw(request: WithdrawRequest):
    """提現到用戶錢包（簡化版本）"""
    try:
        # 檢查餘額
        balance = await solana_service.get_user_balance(request.user_id)
        if balance['token'] < request.amount:
            raise HTTPException(status_code=400, detail="餘額不足")
        
        # 簡化：直接扣除餘額（實際需要區塊鏈轉帳）
        await solana_service.update_user_balance(request.user_id, request.amount, 'subtract')
        
        # 記錄交易
        await solana_service.record_transaction(
            request.user_id, f"withdraw_{request.user_id}_{request.amount}", 
            'withdraw', request.amount, to_addr=request.to_address
        )
        
        return {
            "success": True,
            "message": f"提現 {request.amount} 代幣成功",
            "amount": str(request.amount),
            "to_address": request.to_address
        }
    except Exception as e:
        logger.error(f"Withdrawal failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transfer")
async def internal_transfer(request: TransferRequest):
    """內部轉帳"""
    try:
        # 檢查發送方餘額
        sender_balance = await solana_service.get_user_balance(request.from_user)
        if sender_balance['token'] < request.amount:
            raise HTTPException(status_code=400, detail="餘額不足")
        
        # 檢查接收方是否存在
        receiver_balance = await solana_service.get_user_balance(request.to_user)
        if receiver_balance['token'] == Decimal('0') and receiver_balance['sol'] == Decimal('0'):
            # 可能是新用戶，檢查是否在資料庫中
            async with solana_service.db_pool.acquire() as conn:
                exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM user_balances WHERE user_id = $1)",
                    request.to_user
                )
                if not exists:
                    raise HTTPException(status_code=400, detail="接收方用戶不存在")
        
        # 執行轉帳
        async with solana_service.db_pool.acquire() as conn:
            async with conn.transaction():
                # 扣除發送方餘額
                await conn.execute(
                    "UPDATE user_balances SET token_balance = token_balance - $1 WHERE user_id = $2",
                    request.amount, request.from_user
                )
                
                # 增加接收方餘額
                await conn.execute(
                    "UPDATE user_balances SET token_balance = token_balance + $1 WHERE user_id = $2",
                    request.amount, request.to_user
                )
                
                # 記錄內部轉帳
                await conn.execute(
                    """
                    INSERT INTO internal_transfers (from_user, to_user, amount, memo, status, created_at)
                    VALUES ($1, $2, $3, $4, 'completed', NOW())
                    """,
                    request.from_user, request.to_user, request.amount, request.memo
                )
        
        logger.info(f"Internal transfer: {request.from_user} -> {request.to_user}, amount: {request.amount}")
        
        return {
            "success": True,
            "message": "轉帳成功",
            "from_user": request.from_user,
            "to_user": request.to_user,
            "amount": str(request.amount),
            "memo": request.memo
        }
    except Exception as e:
        logger.error(f"Internal transfer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/{user_id}")
async def get_transactions(user_id: str, limit: int = 50):
    """查詢用戶交易歷史"""
    try:
        async with solana_service.db_pool.acquire() as conn:
            # 區塊鏈交易
            blockchain_txs = await conn.fetch(
                """
                SELECT tx_signature, type, amount, from_address, to_address, fee, status, created_at
                FROM transactions 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                user_id, limit
            )
            
            # 內部轉帳
            internal_txs = await conn.fetch(
                """
                SELECT id, from_user, to_user, amount, memo, status, created_at
                FROM internal_transfers 
                WHERE from_user = $1 OR to_user = $1
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                user_id, limit
            )
        
        transactions = []
        
        # 處理區塊鏈交易
        for tx in blockchain_txs:
            transactions.append({
                "type": "blockchain",
                "tx_type": tx['type'],
                "signature": tx['tx_signature'],
                "amount": str(tx['amount']),
                "from_address": tx['from_address'],
                "to_address": tx['to_address'],
                "fee": str(tx['fee']) if tx['fee'] else "0",
                "status": tx['status'],
                "created_at": tx['created_at'].isoformat()
            })
        
        # 處理內部轉帳
        for tx in internal_txs:
            transactions.append({
                "type": "internal",
                "tx_type": "transfer_out" if tx['from_user'] == user_id else "transfer_in",
                "id": tx['id'],
                "amount": str(tx['amount']),
                "from_user": tx['from_user'],
                "to_user": tx['to_user'],
                "memo": tx['memo'],
                "status": tx['status'],
                "created_at": tx['created_at'].isoformat()
            })
        
        # 按時間排序
        transactions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {"transactions": transactions[:limit]}
        
    except Exception as e:
        logger.error(f"Get transactions failed for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

echo "✅ 核心服務代碼創建完成"
```

### 2.6 創建啟動腳本（5分鐘）
```bash
echo "🚀 創建啟動腳本..."

# 創建開發環境啟動腳本
cat > start_dev.sh << 'EOF'
#!/bin/bash

echo "🚀 啟動 Solana Token System 開發環境..."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境不存在，請先運行設定腳本"
    exit 1
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查環境變數
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在"
    exit 1
fi

# 檢查資料庫是否運行
echo "🔍 檢查資料庫狀態..."
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "🚀 啟動資料庫..."
    docker-compose up -d postgres redis
    echo "⏳ 等待資料庫啟動..."
    sleep 10
fi

# 檢查錢包文件
if [ ! -f "./secure/hot_wallet.json" ]; then
    echo "❌ 錢包文件不存在，請檢查 ./secure/hot_wallet.json"
    exit 1
fi

# 啟動 API 伺服器
echo "🌐 啟動 API 伺服器..."
echo "📱 API 地址: http://localhost:8000"
echo "📚 API 文檔: http://localhost:8000/docs"
echo "🏥 健康檢查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服務"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# 設定執行權限
chmod +x start_dev.sh

# 創建測試腳本
cat > test_api.sh << 'EOF'
#!/bin/bash

echo "🧪 測試 API 功能..."

BASE_URL="http://localhost:8000"

echo "1. 測試健康檢查..."
curl -s "$BASE_URL/health" | python3 -m json.tool

echo -e "\n2. 測試用戶註冊..."
curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "DemoWallet111111111111111111111111111111111"}' | python3 -m json.tool

echo -e "\n3. 測試查詢餘額..."
curl -s "$BASE_URL/api/balance/DemoWallet111111111111111111111111111111111" | python3 -m json.tool

echo -e "\n4. 測試內部轉帳..."
curl -s -X POST "$BASE_URL/api/transfer" \
  -H "Content-Type: application/json" \
  -d '{"from_user": "test_user_1", "to_user": "test_user_2", "amount": 50, "memo": "測試轉帳"}' | python3 -m json.tool

echo -e "\n5. 測試交易歷史..."
curl -s "$BASE_URL/api/transactions/test_user_1" | python3 -m json.tool

echo -e "\n✅ API 測試完成"
EOF

chmod +x test_api.sh

echo "✅ 啟動腳本創建完成"
```

### 2.7 創建前端介面（10分鐘）
```bash
echo "🎨 創建簡單的前端介面..."

# 創建簡單的 HTML 測試頁面
mkdir -p frontend/static

cat > frontend/static/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solana Token System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1, h2 {
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .success {
            color: green;
            background-color: #d4edda;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .error {
            color: red;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .balance {
            font-size: 24px;
            color: #28a745;
            font-weight: bold;
        }
        .address {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <h1>🪙 Solana Token System 測試介面</h1>
    
    <!-- 用戶註冊 -->
    <div class="container">
        <h2>1. 用戶註冊</h2>
        <div class="form-group">
            <label for="wallet_address">錢包地址:</label>
            <input type="text" id="wallet_address" placeholder="例如: DemoWallet111111111111111111111111111111111">
        </div>
        <button onclick="registerUser()">註冊用戶</button>
        <div id="register_result"></div>
    </div>
    
    <!-- 查詢餘額 -->
    <div class="container">
        <h2>2. 查詢餘額</h2>
        <div class="form-group">
            <label for="user_id">用戶ID:</label>
            <input type="text" id="user_id" placeholder="錢包地址或用戶ID">
        </div>
        <button onclick="getBalance()">查詢餘額</button>
        <div id="balance_result"></div>
    </div>
    
    <!-- 內部轉帳 -->
    <div class="container">
        <h2>3. 內部轉帳</h2>
        <div class="form-group">
            <label for="from_user">發送方:</label>
            <input type="text" id="from_user" value="test_user_1">
        </div>
        <div class="form-group">
            <label for="to_user">接收方:</label>
            <input type="text" id="to_user" value="test_user_2">
        </div>
        <div class="form-group">
            <label for="amount">金額:</label>
            <input type="number" id="amount" placeholder="例如: 100" step="0.01">
        </div>
        <div class="form-group">
            <label for="memo">備註:</label>
            <input type="text" id="memo" placeholder="可選">
        </div>
        <button onclick="transferTokens()">轉帳</button>
        <div id="transfer_result"></div>
    </div>
    
    <!-- 交易歷史 -->
    <div class="container">
        <h2>4. 交易歷史</h2>
        <div class="form-group">
            <label for="history_user_id">用戶ID:</label>
            <input type="text" id="history_user_id" value="test_user_1">
        </div>
        <button onclick="getTransactions()">查詢交易</button>
        <div id="transactions_result"></div>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8000';
        
        async function registerUser() {
            const walletAddress = document.getElementById('wallet_address').value;
            if (!walletAddress) {
                showResult('register_result', '請輸入錢包地址', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/register`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({wallet_address: walletAddress})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showResult('register_result', `
                        <strong>註冊成功！</strong><br>
                        用戶ID: ${result.user_id}<br>
                        充值地址: <div class="address">${result.deposit_address}</div>
                    `, 'success');
                    
                    // 自動填入查詢餘額的欄位
                    document.getElementById('user_id').value = result.user_id;
                } else {
                    showResult('register_result', result.detail || '註冊失敗', 'error');
                }
            } catch (error) {
                showResult('register_result', `錯誤: ${error.message}`, 'error');
            }
        }
        
        async function getBalance() {
            const userId = document.getElementById('user_id').value;
            if (!userId) {
                showResult('balance_result', '請輸入用戶ID', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/balance/${encodeURIComponent(userId)}`);
                const result = await response.json();
                
                if (response.ok) {
                    showResult('balance_result', `
                        <div class="balance">代幣餘額: ${result.token_balance}</div>
                        SOL 餘額: ${result.sol_balance}<br>
                        ${result.deposit_address ? `充值地址: <div class="address">${result.deposit_address}</div>` : ''}
                    `, 'success');
                } else {
                    showResult('balance_result', result.detail || '查詢失敗', 'error');
                }
            } catch (error) {
                showResult('balance_result', `錯誤: ${error.message}`, 'error');
            }
        }
        
        async function transferTokens() {
            const fromUser = document.getElementById('from_user').value;
            const toUser = document.getElementById('to_user').value;
            const amount = document.getElementById('amount').value;
            const memo = document.getElementById('memo').value;
            
            if (!fromUser || !toUser || !amount) {
                showResult('transfer_result', '請填入必要欄位', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/transfer`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        from_user: fromUser,
                        to_user: toUser,
                        amount: parseFloat(amount),
                        memo: memo
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showResult('transfer_result', `
                        <strong>轉帳成功！</strong><br>
                        從: ${result.from_user}<br>
                        到: ${result.to_user}<br>
                        金額: ${result.amount}<br>
                        備註: ${result.memo || '無'}
                    `, 'success');
                } else {
                    showResult('transfer_result', result.detail || '轉帳失敗', 'error');
                }
            } catch (error) {
                showResult('transfer_result', `錯誤: ${error.message}`, 'error');
            }
        }
        
        async function getTransactions() {
            const userId = document.getElementById('history_user_id').value;
            if (!userId) {
                showResult('transactions_result', '請輸入用戶ID', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/transactions/${encodeURIComponent(userId)}`);
                const result = await response.json();
                
                if (response.ok && result.transactions) {
                    let html = '<h3>交易歷史:</h3>';
                    
                    if (result.transactions.length === 0) {
                        html += '<p>暫無交易記錄</p>';
                    } else {
                        result.transactions.forEach(tx => {
                            html += `
                                <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                                    <strong>${tx.tx_type}</strong> (${tx.type})<br>
                                    金額: ${tx.amount}<br>
                                    狀態: ${tx.status}<br>
                                    時間: ${new Date(tx.created_at).toLocaleString()}<br>
                                    ${tx.memo ? `備註: ${tx.memo}<br>` : ''}
                                    ${tx.signature ? `簽名: ${tx.signature}` : ''}
                                    ${tx.from_user ? `發送方: ${tx.from_user}<br>接收方: ${tx.to_user}` : ''}
                                </div>
                            `;
                        });
                    }
                    
                    showResult('transactions_result', html, 'success');
                } else {
                    showResult('transactions_result', result.detail || '查詢失敗', 'error');
                }
            } catch (error) {
                showResult('transactions_result', `錯誤: ${error.message}`, 'error');
            }
        }
        
        function showResult(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="${type}">${message}</div>`;
        }
    </script>
</body>
</html>
EOF

echo "✅ 前端介面創建完成"
echo "📱 測試頁面: ./frontend/static/index.html"
```

---

## 第三步：一鍵啟動系統（5分鐘）

### 3.1 創建總控制腳本
```bash
echo "🎯 創建一鍵啟動腳本..."

cat > launch_system.sh << 'EOF'
#!/bin/bash

echo "🚀 Solana Token System 一鍵啟動"
echo "=================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查函數
check_requirement() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 已安裝${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 未安裝${NC}"
        return 1
    fi
}

# 檢查系統需求
echo -e "${BLUE}📋 檢查系統需求...${NC}"
requirements_met=true

if ! check_requirement "python3"; then requirements_met=false; fi
if ! check_requirement "docker"; then requirements_met=false; fi
if ! check_requirement "docker-compose"; then requirements_met=false; fi

if [ "$requirements_met" = false ]; then
    echo -e "${RED}❌ 請先安裝缺少的依賴${NC}"
    exit 1
fi

# 檢查專案文件
echo -e "${BLUE}📁 檢查專案文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env 文件不存在${NC}"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt 文件不存在${NC}"
    exit 1
fi

if [ ! -f "./secure/hot_wallet.json" ]; then
    echo -e "${RED}❌ 錢包文件不存在: ./secure/hot_wallet.json${NC}"
    exit 1
fi

# 啟動虛擬環境
echo -e "${BLUE}🐍 啟動 Python 虛擬環境...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️ 虛擬環境不存在，正在創建...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 啟動資料庫
echo -e "${BLUE}🗄️ 啟動資料庫服務...${NC}"
docker-compose up -d postgres redis

# 等待資料庫啟動
echo -e "${YELLOW}⏳ 等待資料庫啟動（10秒）...${NC}"
sleep 10

# 測試資料庫連接
echo -e "${BLUE}🔍 測試資料庫連接...${NC}"
if docker-compose exec -T postgres psql -U solana_user -d solana_token_db -c "SELECT 'OK' as status;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 資料庫連接正常${NC}"
else
    echo -e "${RED}❌ 資料庫連接失敗${NC}"
    exit 1
fi

# 啟動 API 服務
echo -e "${BLUE}🌐 啟動 API 服務...${NC}"
echo ""
echo "=================================="
echo -e "${GREEN}🎉 系統啟動成功！${NC}"
echo ""
echo -e "${YELLOW}📱 API 服務: http://localhost:8000${NC}"
echo -e "${YELLOW}📚 API 文檔: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}🏥 健康檢查: http://localhost:8000/health${NC}"
echo -e "${YELLOW}🎨 測試介面: 用瀏覽器打開 frontend/static/index.html${NC}"
echo -e "${YELLOW}📊 資料庫管理: http://localhost:8080${NC}"
echo ""
echo -e "${BLUE}按 Ctrl+C 停止服務${NC}"
echo "=================================="

# 啟動 API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x launch_system.sh

echo "✅ 總控制腳本創建完成"
```

### 3.2 創建快速測試腳本
```bash
echo "🧪 創建快速測試腳本..."

cat > quick_test.sh << 'EOF'
#!/bin/bash

echo "🧪 快速功能測試"
echo "=================="

BASE_URL="http://localhost:8000"

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 測試函數
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -e "${YELLOW}測試: $name${NC}"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 201 ]; then
        echo -e "${GREEN}✅ 成功 ($status_code)${NC}"

---

## 📊 成本與時程

### 開發時程
- **第1週**：代幣創建 + 基本API
- **第2週**：充值監控 + 提現功能  
- **第3週**：前端整合 + 測試
- **第4週**：安全加固 + 部署

### 運營成本
- **伺服器**：$50-200/月
- **資料庫**：$20-100/月
- **監控告警**：$10-50/月
- **總計**：$80-350/月

### 交易成本
- **Solana 手續費**：~$0.0001/筆
- **比以太坊便宜**：1000倍以上！

現在搞懂了嗎？有什麼特別想深入瞭解的部分嗎？

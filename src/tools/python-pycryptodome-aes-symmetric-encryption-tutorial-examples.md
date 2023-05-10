# Python 以 PyCryptodome 實作 AES 對稱式加密方法教學與範例

出處：

https://officeguide.cc/python-pycryptodome-aes-symmetric-encryption-tutorial-examples/

以下將介紹如何在 Python 中安裝並使用 `PyCryptodome` 模組，以 AES 加密方法對資料進行加密與解密。

## 安裝 `PyCryptodome` 模組

使用 pip 安裝 Python 的 `PyCryptodome` 模組：

```
# 安裝 PyCryptodome 模組
sudo pip3 install pycryptodome
```

這種安裝方式會讓 `PyCryptodome` 安裝在 `Crypto` 套件路徑之下，取代舊的 `PyCrypto` 模組，這兩個模組會互相干擾，所以不可以同時安裝。

測試 `PyCryptodome` 模組是否可以正常運作：

```
# 測試 PyCryptodome 模組
python3 -m Crypto.SelfTest
```

如果不希望影響到舊的 `PyCrypto` 模組，也可以選擇以獨立模組的方式安裝，將 `PyCryptodome` 模組安裝至 `Cryptodome` 套件路徑之下：

```
# 安裝 PyCryptodome 模組
sudo pip3 install pycryptodomex

# 測試 PyCryptodome 模組
python -m Cryptodome.SelfTest
```

## 產生隨機金鑰

AES 加密方式的區塊長度固定為 128 位元，而金鑰長度則可以是 128、192 或 256 位元，在用 AES 進行資料加密之前，亦須先建立一組金鑰，最簡單的方式就是以隨機的方式產生金鑰。

```
from Crypto.Random import get_random_bytes

# 產生 256 位元隨機金鑰（32 位元組 = 256 位元）
key = get_random_bytes(32)
print(key)
b'l\n\xe8\x7f#\xec{\xf9\x8a4\xb8hye\xe9V\\\xfb\x01\x08\x854\x89\xc9\xfc\x80\xa2S\x920@}'
```

## 以密碼產生金鑰

如果希望使用一般的密碼來對資料進行加密與解密，可以根據密碼與一串固定的 salt 字串，產生對應的金鑰。

首先以亂數方式產生一串隨機的資料作為固定的 salt：

```
# 產生 salt
print(get_random_bytes(32))
b'\xd0\x18\xa7QM\xd6\x9b\xebxu\xe4\xed\xa8\x83\xf6\xa3/\x01\x9c\x9e\x86n\xda;\x10EdD\xf7\x932\xcc'
```

為了方便起見，可以將這串 salt 直接寫在程式當中，搭配自己的密碼即可產生金鑰：

```
from Crypto.Protocol.KDF import PBKDF2

# 固定的 salt
salt = b'\xd0\x18\xa7QM\xd6\x9b\xebxu\xe4\xed\xa8\x83\xf6\xa3/\x01\x9c\x9e\x86n\xda;\x10EdD\xf7\x932\xcc'

# 密碼
password = 'my#password'

# 根據密碼與 salt 產生金鑰
key = PBKDF2(password, salt, dkLen=32)
```



## 儲存金鑰

實務上我們通常會將產生的金鑰儲存在檔案中，方便後續的加密與解密使用：

```
# 金鑰儲存位置
keyPath = "my_key.bin"

# 儲存金鑰
with open(keyPath, "wb") as f:
    f.write(key)

# 讀取金鑰
with open(keyPath, "rb") as f:
    keyFromFile = f.read()

# 檢查金鑰儲存
assert key == keyFromFile, '金鑰不符'
```

## AES CBC 加密模式

以下是使用 AES 的 CBC 模式對資料進行加密的範例，以 CBC 模式加密時需要先對資料進行 padding 處理，再進行加密。

```
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# 輸出的加密檔案名稱
outputFile = 'encrypted.bin'

# 要加密的資料（必須為 bytes）
data = b'My secret data.'

# 以金鑰搭配 CBC 模式建立 cipher 物件
cipher = AES.new(key, AES.MODE_CBC)

# 將輸入資料加上 padding 後進行加密
cipheredData = cipher.encrypt(pad(data, AES.block_size))

# 將初始向量與密文寫入檔案
with open(outputFile, "wb") as f:
    f.write(cipher.iv)
    f.write(cipheredData)
```

以下則是 CBC 模式的解密方式：

```
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 輸入的加密檔案名稱
inputFile = 'encrypted.bin'

# 從檔案讀取初始向量與密文
with open(inputFile, "rb") as f:
    iv = f.read(16)         # 讀取 16 位元組的初始向量
    cipheredData = f.read() # 讀取其餘的密文

# 以金鑰搭配 CBC 模式與初始向量建立 cipher 物件
cipher = AES.new(key, AES.MODE_CBC, iv=iv)

# 解密後進行 unpadding
originalData = unpad(cipher.decrypt(cipheredData), AES.block_size)

# 輸出解密後的資料
print(originalData)
b'My secret data.'
```



## AES CFB 加密模式

AES 的 CFB 模式跟 CBC 模式很類似，不過資料在加密之前不需要經過 padding 處理。

```
from Crypto.Cipher import AES

# 輸出的加密檔案名稱
outputFile = 'encrypted.bin'

# 要加密的資料（必須為 bytes）
data = b'My secret data.'

# 以金鑰搭配 CFB 模式建立 cipher 物件
cipher = AES.new(key, AES.MODE_CFB)

# 將輸入資料進行加密
cipheredData = cipher.encrypt(data)

# 將初始向量與密文寫入檔案
with open(outputFile, "wb") as f:
    f.write(cipher.iv)
    f.write(cipheredData)
```

以下則是 CFB 模式的解密方式：

```
from Crypto.Cipher import AES

# 輸入的加密檔案名稱
inputFile = 'encrypted.bin'

# 從檔案讀取初始向量與密文
with open(inputFile, "rb") as f:
    iv = f.read(16)         # 讀取 16 位元組的初始向量
    cipheredData = f.read() # 讀取其餘的密文

# 以金鑰搭配 CFB 模式與初始向量建立 cipher 物件
cipher = AES.new(key, AES.MODE_CFB, iv=iv)

# 解密資料
originalData = cipher.decrypt(cipheredData)

# 輸出解密後的資料
print(originalData)
b'My secret data.'
```

## AES EAX 加密模式

AES 的 EAX 加密模式會產生 nonce 與 tag，這兩項必須連同密文一起儲存起來。

```
from Crypto.Cipher import AES

# 輸出的加密檔案名稱
outputFile = 'encrypted.bin'

# 要加密的資料（必須為 bytes）
data = b'My secret data.'

# 以金鑰搭配 EAX 模式建立 cipher 物件
cipher = AES.new(key, AES.MODE_EAX)

# 將輸入資料進行加密
cipheredData, tag = cipher.encrypt_and_digest(data)

# 將 nonce、tag 與密文寫入檔案
with open(outputFile, "wb") as f:
    f.write(cipher.nonce)
    f.write(tag)
    f.write(cipheredData)
```

以下則是 EAX 模式的解密方式：

```
from Crypto.Cipher import AES

# 輸入的加密檔案名稱
inputFile = 'encrypted.bin'

# 從檔案讀取初始向量與密文
with open(inputFile, "rb") as f:
    nonce = f.read(16)      # 讀取 16 位元組的 nonce
    tag = f.read(16)        # 讀取 16 位元組的 tag
    cipheredData = f.read() # 讀取其餘的密文

# 以金鑰搭配 EAX 模式與 nonce 建立 cipher 物件
cipher = AES.new(key, AES.MODE_EAX, nonce)

# 解密並驗證資料
originalData = cipher.decrypt_and_verify(cipheredData, tag)

# 輸出解密後的資料
print(originalData)
b'My secret data.'
```



## Base64 編碼與 JSON 儲存格式

如果要將密文等資料儲存至資料庫或是進行網路傳輸，可以考慮將資料經過 base64 編碼之後，放在一個 JSON 檔案中，以下是一個簡單的範例。

```
import json
from base64 import b64encode, b64decode

# 要儲存的原始資料
ciphertext = b'...'
iv = b'...'

# 建立字典結構
outputJSON = {
    'ciphertext': b64encode(ciphertext).decode('utf-8'),
    'iv': b64encode(iv).decode('utf-8')
}

# 儲存為 JSON 檔案
with open('encrypted.json', 'w') as f:
    json.dump(outputJSON, f)

# 讀取 JSON 檔案
with open('encrypted.json') as f:
    inputJSON = json.load(f)

# 取用資料
ciphertext = b64decode(inputJSON['ciphertext'].encode('utf-8'))
iv = b64decode(inputJSON['iv'].encode('utf-8'))
```

參考資料：[PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/src/examples.html)、[Nitratine](https://nitratine.net/blog/post/python-encryption-and-decryption-with-pycryptodome/)、[Nitratine](https://nitratine.net/blog/post/python-gcm-encryption-tutorial/)



---

```python
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import json


class AESCrypt:
    # 固定的 salt
    salt = b"\xd0\x18\xa7QM\xd6\x9b\xebxu\xe4\xed\xa8\x83\xf6\xa3/\x01\x9c\x9e\x86n\xda;\x10EdD\xf7\x932\xcc"

    def __init__(self, password):
        """
        建立 AESCrypt 實例
        """
        self.password = password
        # 根據密碼與 salt 產生金鑰
        self.key = self.generate_key()

    def generate_key(self):
        """
        根據密碼與 salt 生成 PBKDF2 金鑰
        """
        key = PBKDF2(self.password, AESCrypt.salt, 32)
        return key

    def encrypt(self, data):
        """
        使用 AES 加密資料
        """
        # 建立加密器
        cipher = AES.new(self.key, AES.MODE_CTR)

        # 將資料加密
        ciphertext = cipher.encrypt(data)

        # 回傳加密後的資料與 nonce
        return (b64encode(ciphertext), b64encode(cipher.nonce))

    def decrypt(self, data):
        """
        使用 AES 解密資料
        """
        # 將傳入的資料解析為密文與 nonce
        ciphertext, nonce = b64decode(data[0]), b64decode(data[1])

        # 建立解密器
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)

        # 解密資料並回傳
        return cipher.decrypt(ciphertext)

if __name__ == "__main__":
    # 創建 AESCrypt 實例
    aes = AESCrypt("my#password")

    # 需要加密的資料
    data = {"id": 12345, "name": "Alice", "age": 30}

    # 編碼為 JSON 格式
    data_json = json.dumps(data)

    # 加密
    encrypted_data = aes.encrypt(data_json.encode("utf-8"))

    # 將加密後的資料寫入文件
    with open("data.dat", "wb") as f:
        f.write(encrypted_data[0])
        f.write(b"\n")
        f.write(encrypted_data[1])

    # 從文件中讀取加密資料
    with open("data.dat", "rb") as f:
        encrypted_data = (f.readline().strip(), f.readline().strip())

    # 解密
    decrypted_data = aes.decrypt(encrypted_data)

    # 將解密後的資料反序列化為 Python 對象
    data_decrypt = json.loads(decrypted_data.decode("utf-8"))
    print(data_decrypt, type(data_decrypt))
```


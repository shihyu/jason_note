# DAY 28｜Day 28 - Web3 與資安：私鑰保存與備份

- 原文：https://ithelp.ithome.com.tw/articles/10335962
- 發佈時間：2023-10-07 15:59:15

## 章節內容

### 1. 未分章內容

今天我們會講解一般有哪些保存與備份私鑰的方法，而許多錢包 App 都有提供幫使用者備份的選項，因此也會介紹他們的作法以及背後的原理，如 Key Derivation, Shamir’s Secret Sharing 等等。以及較新型的 MPC 錢包是如何運作的。

### 2. 私鑰保存

由於去中心化的精神強調使用者應該要能自己保存自己的私鑰與註記詞，但很多時候要人們記下 12 字的註記詞並安全的保存也是一個高的門檻，會成為初次進入 Web 3 使用者的障礙。因此如何方便又安全的保存私鑰是歷久不衰的議題。

一般來說方便性跟安全性是個取捨，假設我們想自己保管註記詞，以下提供四個等級的註記詞保存方式。

### 3. Level 1

* 抄在紙上：是最簡單的方式，但如果紙張丟失或被破壞就無法復原，或是有紙張被其他人找到的風險。
  * 存在電腦的檔案中：容易存取，但有被駭客或惡意軟體竊取的風險。
  * 存到 Google Drive / Gmail / USB / …：方便跨設備存取，但同樣有被駭客或服務提供商竊取的風險。

### 4. Level 2

可以把存有註記詞的文件用密碼加密、壓縮成 zip 檔，並備份到 Google Drive。多了一層密碼保護會比 Level 1 的方式更安全，但若密碼被洩漏或忘記，一樣有資產丟失的風險。

### 5. Level 3

針對物理備份方式，如果想擁有較高的物理安全性，也有幾種能防火、防水、防銹、防毀損的備份方式，可以保護註記詞不像紙張儲存那樣容易被自然因素破壞。市面上有許多冷錢包廠商有提供這種備份方式，通常會用鋼板把註記詞排列出來，或是自己刻在上面，都是更耐久的保存方式。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294lW6SZf0dmc.png](../ironman-6262-assets/images/day28-img001-f4007ffb60.png)

### 6. Level 4

已經有許多人在思考死後要如何讓其他人取得自己的區塊鏈資產，因為以上這幾種方式都可能因為只有該使用者知道註記詞在哪，而在死後沒辦法被找回。

因此一種作法是透過智能合約搭配 Oracle 來監控是否使用者在一段時間內都沒有活動，若符合條件就自動把資金轉移給指定的人，避免使用者因意外而無法操作錢包。但目前這類的解決方案都還沒有到很成熟，畢竟要自動且準確的偵測這件事十分困難，機制也要不能被駭才行。期待未來有更成熟的作法。

以上講解了幾種使用者自己備份註記詞的作法，那麼在各種錢包 App 中是怎麼做備份的呢？

### 7. 錢包 App 備份

許多錢包 App 為了降低使用者進入 Web3 的門檻，會希望透過較直觀可理解的方式來幫使用者備份私鑰，以下舉幾個例子。

### 8. Rainbow

Rainbow Wallet 提供設定密碼備份的選項，在 Android / iOS 上分別可備份到 Google Drive 與 iCloud。而為了讓雲端服務商沒辦法解開使用者的私鑰，通常會設計成如果忘記密碼就無法幫使用者還原回來。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294LP0n9gBxYy.png](../ironman-6262-assets/images/day28-img002-1adb82daaa.png)

### 9. OKX Wallet

OKX Wallet 同樣也提供用密碼備份的作法，可以看到這是市面上錢包目前最流行的備份方式。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294jczcd7SXBK.png](../ironman-6262-assets/images/day28-img003-b052a8837e.png)

### 10. Argent

Argent Wallet 的備份方式比較特別，按照[官方文件](https://www.argent.xyz/blog/off-chain-recovery/)的寫法，他們備份的方式是會先生成一把 Key Encryption Key（KEK），也就是用來加密私鑰的私鑰，會把它存到 Argent 的雲端。並用 KEK 加密錢包的私鑰後備份到 iCloud 或 Google Drive 上。這樣的好處是 Argent 或 iCloud/Google Drive 任一方都解不出使用者的私鑰，並且可以做到不需要密碼來還原錢包。

![https://ithelp.ithome.com.tw/upload/images/20231007/2016229401P2orQlNg.png](../ironman-6262-assets/images/day28-img004-30d47194b4.png)

### 11. KryptoGO

KryptoGO Wallet 中也提供了用密碼備份的選項，並且要求至少要 12 字來確保安全性，這樣使用者在其他裝置登入也可以用密碼找回錢包。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294fdAX104Hbl.png](../ironman-6262-assets/images/day28-img005-b5520e1a9c.png)

而密碼備份本質上就是對私鑰與註記詞經過一層加密後備份上雲端，只是這個加密所使用的 Key 是從密碼算出來的，通常會把這個流程稱為 Key Derivation。常見的作法是透過密碼加上 Salt 後，經過一系列的 Slow hash function 的計算，來算出一個可用來做對稱式加密的 Key。

會選用 Slow hash function （如 Argon2, bcrypt, PBKDF2 等等）的目的是讓暴力破解的難度大幅增加，另一方面也要在計算 key derivation 時不要讓使用者等太久（例如幾百毫秒內算完）。關於 KryptoGO Wallet 中使用的密碼備份安全機制，詳細可參考[這份文件](https://www.kryptogo.com/docs/wallet-security)。

### 12. SSS 備份機制

除了以上許多錢包採用的密碼備份機制以外，還有一個備份方式可以讓使用者不需記憶密碼，又維持高的安全性，也就是 Shamir’s Secret Sharing Scheme（SSS）。

SSS 的概念是可以把一個私鑰 (Secret) 拆分成 n 個碎片，各自存放在不同的地方，只需要任選其中 k 個私鑰碎片就能恢復出完整的私鑰。例如在 n=3, k=2 的狀況會有三個私鑰碎片，而只要取得兩個碎片就能還原出完整的私鑰。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294kCi6itV24n.png](../ironman-6262-assets/images/day28-img006-9517d9af15.png)

因此在 KryptoGO Wallet 中，當使用者選擇使用 SSS 備份時，會將使用者的私鑰碎片備份到 KryptoGO 雲端、iCloud/Google Drive 雲端上，來讓使用者未來換裝置登入時也能直接還原出錢包。

而 SSS 演算法也有一個良好的特性，就是持有一個 secret share 並不會降低暴力破解出 secret 的難度，因此不管是 KryptoGO, iCloud, Google Drive 就算有一個地方的資料外洩，也不會造成資產損失。

SSS 背後的原理是利用建立一個 k-1 次方的多項式函數 `f(x)`，並在這個多項式函數圖形上找出 n 個點來作為各自的 Secret Share。至於原始的 Secret 值則是 `f(0)`，這樣就能使用「k 個點能唯一決定一個 k-1 次方的多項式」性質，透過 n 個 Secret Share 中的任意 k 個 Share 來還原出原本的多項是，進而算出 `f(0)` 也就是原始 Secret 的值。

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294cFjnc7pGk9.png](../ironman-6262-assets/images/day28-img007-758e20690b.png)

而還原出 k-1 次方多項式的作法是用到[拉格朗日差值法](https://en.wikipedia.org/wiki/Lagrange_polynomial)，已經有相關的數學公式來直接計算：

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294geV4UJS3Bu.png](../ironman-6262-assets/images/day28-img008-2cc354c62f.png)

在 KryptoGO Wallet 中也有提供透過 SSS 備份錢包私鑰的功能，結合前面提到的密碼備份選項讓使用者自由選擇：

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294wzFlTSD0Rz.png](../ironman-6262-assets/images/day28-img009-78c1ea230a.png)

### 13. MPC 錢包

近年來開始流行的是 MPC 錢包，它的全名是 Multi Party Computation 或稱多方運算，會出現的背景是因為不希望單一裝置有機會拿到完整的私鑰，因為如果私鑰的明文曾經被某個裝置計算出來過，極端情況下有裝置被入侵的風險。因此這個做法也會把私鑰拆成多份，但不同的是沒有一個人能組出完整的私鑰：

![https://ithelp.ithome.com.tw/upload/images/20231007/20162294Eyu131fqvy.png](../ironman-6262-assets/images/day28-img010-bd2f626c80.png)

而 MPC 的精神是讓一群人共同計算一個函數的回傳值，但對其他人的資訊一無所知。因此在 MPC 錢包中的作法是：

1. n 個參與者各自持有私鑰的一個 secret share（通常是使用者自己跟錢包服務商）
  2. 當要簽名時，每個人各自先基於自己的 secret share 算出部分的簽名。
  3. 由某一方透過複雜的演算法組合大家的部分簽名，算出最終的簽名。

對 BTC, ETH 鏈的 MPC 錢包來說，在計算交易簽章時需要計算的 function 是 ECDSA 簽章，因此必須設計能算出 ECDSA 結果的 MPC 演算法。這種演算法十分複雜，已經超出了今天的範圍，有興趣的讀者可以參考 [Fast Secure Two-Party ECDSA Signing](https://eprint.iacr.org/2017/552.pdf) 論文， 還有 [ZenGo 錢包的實作](https://github.com/ZenGo-X/multi-party-ecdsa)。

由於前面提到的 MPC 作法是需要所有參與者一起計算，那有沒有像 SSS 演算法那樣只需要部分參與者就能算出結果的作法呢？這個其實就是 TSS (Threshold Signature Scheme) 演算法。他可以讓 n 個參與者中只需要 k 個人就有能力一起對一個交易做簽名，來做到更好的冗余性。有興趣的讀者可以參考 OKX 錢包中的 TSS 功能是如何實作的：https://github.com/okx/threshold-lib/blob/main/docs/Threshold_Signature_Scheme.md

### 14. 小結

今天我們介紹了作為使用者可以怎麼備份自己的私鑰註記詞，以及一般錢包服務會透過哪些方式來協助使用者安全又便利的備份。接下來最後兩天會介紹一些 Web 3 世界中較前沿的技術，提供讀者對 Web 3 技術更全面的認識。

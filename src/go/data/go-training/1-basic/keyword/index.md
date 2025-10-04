
# 關鍵字
關鍵字是指被編程語言保留頁不讓編程人員作為標識符使用的字符序列。因此，關鍵字也稱為保留字

Go 語言中所有的關鍵只有25個：

- 程序聲明：import、package
- 程序實體聲明和定義：chan、const、func、interface、map、struct、type、var
- 程序流程控制：go、select、break、case、continue、default、defer、else、fallthrough、for、goto、if、range、return、switch

# 預定義標識符
在Go語言代碼中，每一個標識符可以代表一個變更或者一個類型（即標識符可以被看作是變量或者類型的代號或者名稱），標識符是由若干字母、下劃線（_）和數字組成的字符序列，第一個字符必須是字母。

在Go語言中還存在一類特殊的標識符，叫作預定義標識符，這些字符序列同樣也是不能讓開發者使用的。

- 所有基本數據類型的名稱，如int、uint、string等
- 接口類型 error
- 常量 true、false 以及 iota
- 所有內部函數的名稱，即 append、cap、close、complex、copy、delete、imag、len、make、new、panic、print、println、real和 recover

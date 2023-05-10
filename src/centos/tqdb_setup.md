## TQDB



https://github.com/wldtw2008/tqdb/tree/prepareForCulster  <==TQDB 在GitHub的最新版

https://github.com/wldtw2008/tqdb/blob/prepareForCulster/InitialTQDB.readme  <==安裝說明

https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/install/installRHEL.html <== cassandra 安裝


若不需自己安裝，我有已經裝好的VirtualBox的VM 在這裡
https://drive.google.com/open?id=16ZawNAWJNDcGV2jGirviIWzd_EwXlNfe
id:tqdb, pw:tqdb@888, root pw:tqdb@888



### 遇到問題

1. MC  8899 沒設定好 ＆ 檢查設定

2. 帳號路徑問題 需要依照帳號更改路徑 ex: trad 帳號 

   ```sh
   find . -type f -exec sed -i 's|/home/tqdb|/home/trad|g'  {} \;
   ```

3. 如果使用python3  script 需要更改因為開發是使用 python2

4. 檢查process   ps aux | grep 'tqdb'
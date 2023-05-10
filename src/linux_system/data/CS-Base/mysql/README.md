# 圖解MySQL介紹

《圖解MySQL》目前還在連載更新中，大家不要催啦:joy: ，更新完會第一時間整理 PDF 的。

目前已經更新好的文章：

- **基礎篇**:point_down:
  
   - [執行一條 SQL 查詢語句，期間發生了什麼？](/mysql/base/how_select.md)
   - [MySQL 一行記錄是怎麼存儲的？](/mysql/base/row_format.md)
   
- **索引篇** :point_down:
  
   - [索引常見面試題](/mysql/index/index_interview.md)
   - [從數據頁的角度看 B+ 樹](/mysql/index/page.md)
   - [為什麼 MySQL 採用 B+ 樹作為索引？](/mysql/index/why_index_chose_bpuls_tree.md)
   - [MySQL 單表不要超過 2000W 行，靠譜嗎？](/mysql/index/2000w.md)
   - [索引失效有哪些？](/mysql/index/index_lose.md)
   - [MySQL 使用 like “%x“，索引一定會失效嗎？](/mysql/index/index_issue.md)
   - [count(\*) 和 count(1) 有什麼區別？哪個性能最好？](/mysql/index/count.md)
   
- **事務篇** :point_down:
	- [事務隔離級別是怎麼實現的？](/mysql/transaction/mvcc.md) 	
	- [MySQL 可重複讀隔離級別，完全解決幻讀了嗎？](/mysql/transaction/phantom.md) 	
	
- **鎖篇** :point_down:
	- [MySQL 有哪些鎖？](/mysql/lock/mysql_lock.md) 	
	- [MySQL 是怎麼加鎖的？](/mysql/lock/how_to_lock.md) 	
	- [update 沒加索引會鎖全表?](/mysql/lock/update_index.md) 	
	- [MySQL 記錄鎖+間隙鎖可以防止刪除操作而導致的幻讀嗎？](/mysql/lock/lock_phantom.md) 	
	- [MySQL 死鎖了，怎麼辦？](/mysql/lock/deadlock.md) 	
	- [字節面試：加了什麼鎖，導致死鎖的？](/mysql/lock/show_lock.md)
	
- **日誌篇** :point_down:
	
	- [undo log、redo log、binlog 有什麼用？](/mysql/log/how_update.md) 	
	
- **內存篇** :point_down:
	
	- [揭開 Buffer_Pool 的面紗](/mysql/buffer_pool/buffer_pool.md) 	
	
	----
	
	最新的圖解文章都在公眾號首發，別忘記關注哦！！如果你想加入百人技術交流群，掃碼下方二維碼回覆「加群」。
	
	![img](https://cdn.xiaolincoding.com/gh/xiaolincoder/ImageHost3@main/%E5%85%B6%E4%BB%96/%E5%85%AC%E4%BC%97%E5%8F%B7%E4%BB%8B%E7%BB%8D.png)
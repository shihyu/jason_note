# GDB 基礎與指令

> GDB 基礎知識、常用指令、命令參考等入門內容。

## 📚 基礎教學

### 完整指南
- [GDB 完整知識庫整理](GDB完整知識庫整理.md) - 完整知識體系
- [GDB Debug 指南](GDB_DEBUG_GUIDE.md) - 除錯完整指南
- [GDB](gdb.md) - GDB 基礎

### 指令參考
- [GDB 指令指南](gdb_commands_guide.md)
- [GDB 指令](gdb_commands.md)
- [常用指令](常用指令.md)

## 💡 學習建議

### 新手入門路徑
1. 閱讀 [GDB 完整知識庫](GDB完整知識庫整理.md)
2. 學習 [常用指令](常用指令.md)
3. 實踐簡單程式除錯

### 常用指令分類

**程式控制**:
- `run` / `r` - 執行程式
- `continue` / `c` - 繼續執行
- `step` / `s` - 單步執行（進入函數）
- `next` / `n` - 單步執行（不進入函數）
- `finish` - 執行到函數返回

**中斷點**:
- `break` / `b` - 設置中斷點
- `delete` / `d` - 刪除中斷點
- `disable` / `dis` - 禁用中斷點
- `enable` / `en` - 啟用中斷點

**查看資訊**:
- `print` / `p` - 列印變量
- `info` / `i` - 查看資訊
- `backtrace` / `bt` - 查看調用堆疊
- `list` / `l` - 列出源代碼

**最後更新**: 2025-12-01

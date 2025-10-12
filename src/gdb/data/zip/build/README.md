# GDB 除錯環境

使用 Makefile 統一管理編譯和 GDB 調試。

## 快速開始

```bash
cd build

# 追蹤函數執行路徑(推薦)
make trace

# 詳細 GDB 追蹤
make debug

# 互動式 GDB
make gdb
```

## Makefile 指令

| 指令 | 說明 |
|------|------|
| `make` | 編譯除錯版本執行檔 |
| `make trace` | **追蹤函數執行路徑(顯示檔案:行數)** |
| `make debug` | 詳細 GDB 追蹤(含變數檢視) |
| `make gdb` | 啟動互動式 GDB |
| `make test` | 編譯 + 執行追蹤 |
| `make prepare` | 只準備測試資料 |
| `make clean` | 清理所有產生檔案 |
| `make help` | 顯示說明 |

## 追蹤結果範例

### make trace (函數執行路徑)

```
#0  main (argc=3, argv=0x7fffffffdbb8) at ../src/tools/cmdzip.c:30
#0  zip_set_error_handler (...) at ../src/zip.c:52
#0  zip_zip (...) at ../src/zip.c:321
#0  zip_open_utf8 (...) at ../src/unixutils.c:14
#0  mz_zip_writer_init_cfile (...) at ../src/miniz.c:5718
#0  zip_file_size (...) at ../src/unixutils.c:89
#0  mz_zip_writer_add_cfile (...) at ../src/miniz.c:6313
#0  zip_set_permissions (...) at ../src/zip.c:69
#0  mz_zip_writer_finalize_archive (...) at ../src/miniz.c:7086
#0  mz_zip_writer_end (...) at ../src/miniz.c:7200
```

### make debug (詳細追蹤)

```
=== Breakpoint: zip_zip() ===
Zip file: output.zip
Number of files: 1
Compression level: 9

=== Breakpoint: mz_zip_writer_add_cfile() ===
Archive key: test.txt
Uncompressed size: 189 bytes
```

## 檔案說明

- **Makefile** - 編譯和除錯控制
- **breakpoints.gdb** - 中斷點定義(直接編輯此檔案新增中斷點)
- **gdb_function_trace.gdb** - 讀取 breakpoints.gdb 並追蹤
- **gdb_trace.gdb** - 詳細 GDB 追蹤腳本
- **test.txt** - 測試檔案 (自動產生)
- **cmdzip_debug** - 除錯版執行檔 (編譯後產生)

## 自訂中斷點

直接編輯 **breakpoints.gdb**,格式:

```gdb
break <函數名>              # 例: break main
break <檔案>:<行數>         # 例: break ../src/zip.c:321
```

範例:
```gdb
break main
break zip_zip
break ../src/miniz.c:163
```

然後執行 `make trace` 即可!

## 關鍵追蹤點

1. **main()** - 程式進入點 (src/tools/cmdzip.c:30)
2. **zip_zip()** - 壓縮主函數 (src/zip.c:321)
3. **mz_zip_writer_add_cfile()** - 加入檔案到 zip (src/miniz.c:6313)

## 互動式除錯

```bash
make gdb

# 在 GDB 中
(gdb) break main
(gdb) break zip_zip
(gdb) run
(gdb) info args
(gdb) next
(gdb) print czipfile
(gdb) backtrace
(gdb) continue
```

## 自訂 GDB 命令

編輯 `gdb_trace.gdb` 增加更多中斷點或追蹤邏輯。

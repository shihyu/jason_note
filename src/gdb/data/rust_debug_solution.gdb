# Rust 完整調試解決方案 - 顯示檔案:函數:行號
set pagination off
set confirm off
set breakpoint pending on
set solib-search-path ./lib

# 關閉 debuginfod（避免警告）
set debuginfod enabled off

# Rust 符號解析設定
set print asm-demangle on
set print demangle on
set language rust
set print pretty on
set print object on

# 忽略信號
handle SIGPIPE nostop noprint pass

# 日誌設定
set logging file /tmp/rust_full_debug.log
set logging overwrite on
set logging enabled on

echo \n=== 🚀 Rust 完整調試追蹤 ===\n

# 定義完整顯示函數（類似 C/C++ 格式）
define show_full_location
  printf "\n┌────────────────────────────────────────────────────────────────────\n"

  # 取得並顯示檔案:行號:函數
  python
import gdb
try:
    frame = gdb.selected_frame()
    sal = frame.find_sal()

    # 取得檔案名
    if sal.symtab:
        filename = sal.symtab.filename
        # 簡化路徑（只顯示重要部分）
        if "/buttplug/" in filename:
            filename = "..." + filename.split("/buttplug/")[-1]
        elif "/.cargo/registry/" in filename:
            filename = ".../" + filename.split("/")[-1]
        elif "/src/" in filename:
            parts = filename.split("/src/")
            if len(parts) > 1:
                filename = ".../" + parts[-1]

        line = sal.line if sal.line else "?"
    else:
        filename = "unknown"
        line = "?"

    # 取得函數名
    func = frame.function()
    if func:
        func_name = func.name
        # 解析 Rust 函數名（簡化顯示）
        if "::" in func_name:
            parts = func_name.split("::")
            if len(parts) > 2:
                func_name = "::".join(parts[-2:])
    else:
        func_name = "unknown_function"

    # 格式化輸出（類似 C/C++）
    print(f"│ 📍 {filename}:{line}")
    print(f"│ 🔧 in function: {func_name}")

    # 顯示參數
    args = []
    try:
        for arg in frame.arguments():
            args.append(f"{arg[0]}={arg[1]}")
        if args:
            print(f"│ 📦 arguments: {', '.join(args[:3])}")  # 只顯示前3個參數
    except:
        pass

except Exception as e:
    print(f"│ ❌ Error: {e}")
end

  # 顯示源碼（如果可用）
  printf "│ 📄 Source:\n"
  list -

  printf "└────────────────────────────────────────────────────────────────────\n\n"
end

# 啟動程式
start

# 等待庫載入
catch load libintiface_engine_flutter_bridge.so
commands 1
  echo \n=== ✅ Buttplug 庫已載入 ===\n

  # 在 server.rs 的特定函數設置斷點
  break buttplug::server::server::ButtplugServer::new
  break buttplug::server::server::ButtplugServer::start
  break buttplug::server::server::ButtplugServer::stop
  break buttplug::server::server::ButtplugServer::handle_message

  # 也可以按檔案:行號設置
  break /home/shihyu/gdb-intiface-central-buttplug/buttplug/buttplug/src/server/server.rs:100
  break /home/shihyu/gdb-intiface-central-buttplug/buttplug/buttplug/src/server/server.rs:200

  # 使用更廣泛的模式
  rbreak buttplug::server::.*::new
  rbreak buttplug::server::.*::start

  echo \n=== 已設置的斷點 ===\n
  info breakpoints

  # 為所有斷點設置顯示命令
  python
import gdb
count = 0
for bp in gdb.breakpoints():
    if bp.number > 1:  # 跳過 catchpoint
        bp.commands = "silent\nshow_full_location\ncontinue"
        count += 1
print(f"\n✅ 配置了 {count} 個斷點")
end

  continue
end

# 執行
continue
#!/bin/bash
# trace_go_with_source.sh — 追蹤 Go runtime 並顯示原始碼位置
# 用法: sudo ./trace_go_with_source.sh <go_binary>

BINARY="${1:?用法: $0 <go_binary>}"
MAP_FILE=$(mktemp /tmp/go_func_map.XXXXXX)

echo "=== 建立函數對照表 ==="
go tool objdump "$BINARY" | awk '
/^TEXT / {
    match($0, /TEXT ([^ ]+)\(SB\) (.*)/, a)
    func_name = a[1]
    file_path = a[2]
    want_line = 1
    next
}
want_line && /^  / {
    split($1, parts, ":")
    line_num = parts[length(parts)]
    n = split(file_path, fp, "/")
    print func_name "\t" fp[n] ":" line_num
    want_line = 0
}
' > "$MAP_FILE"

echo "對照表已建立：$(wc -l < "$MAP_FILE") 個函數"
echo ""
echo "=== 開始追蹤 ==="

sudo bpftrace -e '
BEGIN {
    printf("%-6s %-15s %s\n", "ORDER", "TIME(us)", "FUNCTION");
    @order = 0;
}
uprobe:'"$BINARY"':* {
    if (@seen[func] == 0) {
        @seen[func] = 1;
        @order++;
        printf("%-6d %-15lu %s\n", @order, elapsed / 1000, func);
    }
}
END {
    printf("\n--- Total unique functions called: %d ---\n", @order);
    clear(@seen);
}
' -c "$BINARY" 2>/dev/null | awk -v mapfile="$MAP_FILE" '
BEGIN {
    while ((getline line < mapfile) > 0) {
        split(line, a, "\t")
        gsub(/^ +| +$/, "", a[1])
        gsub(/^ +| +$/, "", a[2])
        loc[a[1]] = a[2]
    }
    printf "%-6s %-15s %-50s %s\n", "ORDER", "TIME(us)", "FUNCTION", "SOURCE"
    printf "%-6s %-15s %-50s %s\n", "-----", "--------", "--------", "------"
}
/^ORDER/ { next }
/^[0-9]/ {
    func_name = $3
    file_info = (func_name in loc) ? loc[func_name] : "-"
    printf "%-6s %-15s %-50s %s\n", $1, $2, func_name, file_info
    next
}
/^---/ { print; next }
/^$/ { next }
'

rm -f "$MAP_FILE"

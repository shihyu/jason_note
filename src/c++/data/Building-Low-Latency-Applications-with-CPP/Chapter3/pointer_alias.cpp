// ❌ 無 restrict：編譯器必須假設 a 和 b 可能重疊
// 問題：每次迭代都從記憶體重新載入 *b（因為不確定 a[i] 是否修改 *b）
// 成本：n 次記憶體讀取（而非 1 次）
void func(int* a, int* b, int n)
{
    for (int i = 0; i < n; ++i) {
        a[i] = *b;  // *b 無法暫存在暫存器中
    }
}

// ✅ 有 restrict：告訴編譯器 a 和 b 不會重疊
// ⚡ 效能關鍵：*b 只載入一次，駐留在暫存器（節省 n-1 次記憶體存取）
// 原理：__restrict 承諾指標所指向的記憶體不會被其他指標存取
void func_restrict(int* __restrict a, int* __restrict b, int n)
{
    for (int i = 0; i < n; ++i) {
        a[i] = *b;  // *b 可安全地快取在暫存器
    }
}

int main()
{
    int a[10], b;
    func(a, &b, 10);
    func_restrict(a, &b, 10);
}
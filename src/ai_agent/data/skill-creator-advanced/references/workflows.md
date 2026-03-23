# Workflow Patterns

這份文件回答的是：長流程該怎麼拆，才不會把 skill 寫成一個巨型 prompt。

## 1) 先判斷要不要拆多回合

下列情況通常不該一回合做完：
- 同時包含分析、查證、寫作、格式化
- 需要不同工具集
- 每一階段的驗收標準不同
- 中途可能因資料不足而停止

判斷原則：
- 如果某步驟的輸出會成為下一步的明確輸入，就值得拆
- 如果某步驟失敗後的補救方式和主流程不同，也值得拆

## 2) 標準四段式

對多數知識工作型 skill，可以先用這個預設：

1. 任務分析
- 讀需求、找缺口、確認邊界

2. 資料蒐集 / 工具執行
- 搜集證據、呼叫工具、補前置資料

3. 產出草稿
- 依 `output contract` 生成第一版結果

4. QA / 格式化
- 檢查遺漏、格式、風險與交付完整度

## 3) 線性 workflow

適合：
- 步驟固定
- 依賴關係清楚
- 幾乎沒有分支

範例：

```md
<workflow>
Step 0: Read the input folder and required config.
Step 1: Validate filenames and schema.
Step 2: Transform files into the target structure.
Step 3: Run quality checks.
Step 4: Return the artifact path and validation summary.
</workflow>
```

## 4) 條件分支 workflow

適合：
- 建立新內容與修改既有內容的流程不同
- 依輸入成熟度決定是否可直接執行
- 會因風險高低切換成「先問再做」

範例：

```md
<workflow>
Step 0: Determine request type.
- If creating new content, follow Creation path.
- If editing existing artifacts, follow Editing path.

Creation path:
Step 1: Build the required structure from the template.
Step 2: Fill mandatory sections.

Editing path:
Step 1: Inspect the existing artifact and diff.
Step 2: Modify only the requested sections.
</workflow>
```

## 5) 多回合 / prompt chaining workflow

適合：
- 要先查證再下結論
- 需要不同模型或不同 reasoning effort
- 中間產物本身值得保存或審核

典型拆法：

```md
Turn 1: Analyze the task and list missing inputs.
Turn 2: Gather evidence or run tools.
Turn 3: Draft the answer or artifact.
Turn 4: Validate against the output contract and fix gaps.
```

若 skill 會用到工具，建議把：
- 讀取型工具放在前段
- 寫入型工具放到需要明確確認之後

## 6) 何時不要拆

下列情況過度拆分反而浪費：
- 任務本身很短
- 每一步沒有清楚的中間產物
- 拆開後沒有額外可驗證性

如果拆完仍無法說清楚每回合的輸入/輸出，通常代表流程設計還沒收斂。

## 7) 與 output contract 的關係

多回合流程不是為了讓 prompt 更長，而是為了讓每一段都有清楚完成條件。

建議對每一回合都定義：
- Input
- Goal
- Allowed tools
- Output
- Stop condition

最後一回合才對完整 `output contract` 負責。

## 8) 快速檢查表

- 是否存在可分離的階段性產物
- 是否有高風險工具應延後到確認後才執行
- 是否寫清楚每回合的 allowed tools
- 是否有 stop condition
- 是否有最後的 QA / format pass

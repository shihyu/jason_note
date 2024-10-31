def generate_dot_tree(levels):
    dot_string = "digraph BinaryTree {\n"
    dot_string += "    node [shape=circle];\n"

    # 定義函數以生成節點名稱
    def get_node_name(index):
        # 將索引轉換為字母名稱，超過 Z 時轉換為 AA, AB...
        name = ""
        while index >= 0:
            name = chr(index % 26 + ord("A")) + name
            index = index // 26 - 1
        return name

    def add_nodes_and_edges(node_index, depth):
        nonlocal dot_string  # 使用 nonlocal 關鍵字來引用外部變量
        if depth < levels:
            node_name = get_node_name(node_index)
            left_child_index = 2 * node_index + 1
            right_child_index = 2 * node_index + 2

            left_child_name = get_node_name(left_child_index)
            right_child_name = get_node_name(right_child_index)

            dot_string += (
                f"    {node_name} -> {{{left_child_name} {right_child_name}}};\n"
            )
            add_nodes_and_edges(left_child_index, depth + 1)
            add_nodes_and_edges(right_child_index, depth + 1)

    # 從根節點開始
    add_nodes_and_edges(0, 0)
    dot_string += "}"

    return dot_string


# 輸入二元樹層數
levels = int(input("請輸入二元樹的層數: "))
dot_output = generate_dot_tree(levels)
print(dot_output)

# 將結果寫入文件
with open("binary_tree.dot", "w") as f:
    f.write(dot_output)

import matplotlib.pyplot as plt
import networkx as nx

# 節點列表，每個節點包含名稱和二進位 path
nodes = [
    ('A', '0'), ('B', '0'), ('C', '1'),
    ('D', '00'), ('E', '01'), ('F', '10'), ('G', '11'),
    ('H', '000'), ('I', '001'), ('J', '010'), ('K', '011'),
    ('L', '100'), ('M', '101'), ('N', '110'), ('O', '111')
]

# 建立二元樹的邊列表
edges = [
    ('A', 'B'), ('A', 'C'),
    ('B', 'D'), ('B', 'E'), ('C', 'F'), ('C', 'G'),
    ('D', 'H'), ('D', 'I'), ('E', 'J'), ('E', 'K'),
    ('F', 'L'), ('F', 'M'), ('G', 'N'), ('G', 'O')
]

# 創建 NetworkX 圖形
G = nx.DiGraph()
# 添加節點和邊
for node, path in nodes:
    G.add_node(node, path=path)
G.add_edges_from(edges)

# 畫圖
plt.figure(figsize=(10, 8))
pos = nx.multipartite_layout(G, subset_key=lambda n: len(G.nodes[n]['path']))

# 畫節點和邊
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', arrows=False)

# 加上節點的 path 標籤
path_labels = {node: f"{node}\n{G.nodes[node]['path']}" for node in G.nodes}
nx.draw_networkx_labels(G, pos, labels=path_labels, font_size=10)

plt.title("Binary Tree with Node Names and Binary Paths")
plt.show()


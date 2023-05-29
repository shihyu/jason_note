##  Plotly 在 HTML 中動態更新圖表的簡單示例程序

```python
from plotly.subplots import make_subplots
import random
import dash
from dash import dcc
from dash import html


# 創建圖表
fig = make_subplots(rows=1, cols=1)
fig.add_scatter(x=[], y=[], mode="lines", name="動態更新圖表")

# 創建 Dash 應用
app = dash.Dash(__name__)

# 定義佈局
app.layout = html.Div(
    children=[
        dcc.Graph(id="live-graph", figure=fig),
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),  # 每秒更新一次
    ]
)


# 定義回調函數
@app.callback(
    dash.dependencies.Output("live-graph", "figure"),
    [dash.dependencies.Input("update-interval", "n_intervals")],
)
def update_graph(n):
    # 生成隨機數據
    x = list(range(10))
    y = [random.randint(0, 100) for _ in range(10)]

    # 更新圖表數據
    fig.data[0].x = x
    fig.data[0].y = y

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
```

了 Plotly 的 Python API 來創建了一個動態更新的折線圖，並將其嵌入到了一個 Dash 應用中。具體來說，我們使用 `make_subplots()` 函數創建了一個包含一個子圖的圖表對象，並在其中添加了一條折線。然後，我們使用 Dash 提供的 `dcc.Graph` 組件將這個圖表對象嵌入到了應用的佈局中，並使用 `dcc.Interval` 組件來定時更新圖表數據。最後，我們使用 `app.callback` 裝飾器定義了一個回調函數，該函數會在定時器觸發時被調用，並更新圖表的數據。

在運行上面的程序後，我們可以在瀏覽器中訪問 `http://localhost:8050/` 來查看動態更新的圖表。每秒鐘，圖表中的數據會更新一次，並自動重繪圖表。
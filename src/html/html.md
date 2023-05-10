## lightweight-charts

```sh
npm install lightweight-charts svelte-lightweight-charts
```

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>My Chart</title>
    <script src="https://unpkg.com/lightweight-charts@3.0.0/dist/lightweight-charts.standalone.production.js"></script>
  </head>
  <body>
    <div id="chart"></div>
    <script>
      const symbol = 'BTCUSDT';
      const interval = '1d';
      const limit = 1000;

      const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;

      fetch(url)
        .then(response => response.json())
        .then(data => {
          const chartData = data.map(item => ({
            time: item[0] / 1000,
            open: parseFloat(item[1]),
            high: parseFloat(item[2]),
            low: parseFloat(item[3]),
            close: parseFloat(item[4]),
          }));

          const chart = LightweightCharts.createChart(document.getElementById('chart'), {
            width: 600,
            height: 300,
          });

          const candlestickSeries = chart.addCandlestickSeries();

          candlestickSeries.setData(chartData);
        });
    </script>
  </body>
</html>
```

---

## trading-vue-js

https://github.com/tvjsx/trading-vue-js

```sh
npm i trading-vue-js
```





## Reference

- https://medium.com/marcius-studio/financial-charts-for-your-application-cfcceb147786
- https://codesandbox.io/examples/package/trading-vue-js

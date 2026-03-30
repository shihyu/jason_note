const SYMBOL = 'btcusdt';
const WS_URL = `wss://stream.binance.com:9443/ws/${SYMBOL}@trade`;

const priceEl = document.getElementById('price');
const quantityEl = document.getElementById('quantity');
const timestampEl = document.getElementById('timestamp');
const statusEl = document.getElementById('status');

let lastPrice = 0;
let ws = null;

function connect() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('Connected to Binance WebSocket');
        statusEl.textContent = '已連線';
        statusEl.className = 'status-connected';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateUI(data);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected. Reconnecting...');
        statusEl.textContent = '未連線 (重試中...)';
        statusEl.className = 'status-disconnected';
        setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
        console.error('WebSocket Error:', err);
        ws.close();
    };
}

function updateUI(data) {
    // Binance Trade Stream Data:
    // s: Symbol, p: Price, q: Quantity, T: Trade Time
    const price = parseFloat(data.p).toFixed(2);
    const quantity = parseFloat(data.q).toFixed(4);
    const time = new Date(data.T).toLocaleTimeString();

    // 更新價格顏色
    if (lastPrice > 0) {
        if (price > lastPrice) {
            priceEl.className = 'price up';
        } else if (price < lastPrice) {
            priceEl.className = 'price down';
        }
    }
    
    priceEl.textContent = price;
    quantityEl.textContent = quantity;
    timestampEl.textContent = time;
    
    lastPrice = price;
}

// 啟動連線
connect();

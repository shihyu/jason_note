const assert = require('assert');

// 模擬 Binance WebSocket 傳回的資料結構
const mockTradeData = {
    "e": "trade",     // Event type
    "E": 1672531200000, // Event time
    "s": "BTCUSDT",    // Symbol
    "t": 12345,        // Trade ID
    "p": "25000.50",   // Price
    "q": "0.0100",     // Quantity
    "b": 88,           // Buyer order ID
    "a": 50,           // Seller order ID
    "T": 1672531200000, // Trade time
    "m": true,         // Is the buyer the market maker?
    "M": true          // Ignore
};

function testParser() {
    console.log('Running parser test...');
    
    const data = mockTradeData;
    const price = parseFloat(data.p).toFixed(2);
    const quantity = parseFloat(data.q).toFixed(4);
    const time = new Date(data.T).toLocaleTimeString();

    assert.strictEqual(price, "25000.50", "Price parsing failed");
    assert.strictEqual(quantity, "0.0100", "Quantity parsing failed");
    assert.ok(time.length > 0, "Time formatting failed");

    console.log('✅ Parser test passed!');
}

try {
    testParser();
} catch (err) {
    console.error('❌ Test failed:');
    console.error(err);
    process.exit(1);
}

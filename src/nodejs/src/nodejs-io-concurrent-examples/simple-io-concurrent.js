// simple-io-concurrent.js
const fs = require('fs').promises;

async function task(id, delay) {
  const start = Date.now();
  console.log(`[${id}] 開始 | PID: ${process.pid} | 主線程`);

  // 模擬異步 I/O
  await new Promise(r => setTimeout(r, delay));

  const elapsed = Date.now() - start;
  console.log(`[${id}] 完成 | 耗時: ${elapsed}ms`);
  return { id, elapsed };
}

async function main() {
  console.log(`主進程 PID: ${process.pid}\n`);

  const start = Date.now();

  // 並發執行 5 個任務
  const results = await Promise.all([
    task('任務A', 1000),
    task('任務B', 500),
    task('任務C', 800),
    task('任務D', 300),
    task('任務E', 1200)
  ]);

  const total = Date.now() - start;
  console.log(`\n全部完成 | 總耗時: ${total}ms`);
  console.log('結果:', results);
}

main();

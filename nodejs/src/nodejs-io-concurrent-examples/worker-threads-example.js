// worker-threads-example.js
const { Worker, isMainThread, parentPort, threadId, workerData } = require('worker_threads');

if (isMainThread) {
  // === 主線程 ===
  console.log(`主進程 PID: ${process.pid} | TID: ${threadId}\n`);

  const start = Date.now();
  const workers = [];

  // 創建 5 個 worker
  for (let i = 1; i <= 5; i++) {
    const worker = new Worker(__filename, {
      workerData: { taskId: i, delay: Math.random() * 1000 + 500 }
    });

    workers.push(new Promise((resolve, reject) => {
      worker.on('message', msg => {
        console.log(`Task ${msg.taskId} 完成 | 耗時: ${msg.elapsed}ms`);
        resolve(msg);
      });
      worker.on('error', reject);
      worker.on('exit', code => {
        if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
      });
    }));
  }

  // 等待所有 worker 完成
  Promise.all(workers).then(results => {
    const total = Date.now() - start;
    console.log(`\n全部完成 | 總耗時: ${total}ms`);
    console.log(`處理: ${results.length} 個任務`);
  });

} else {
  // === Worker 線程 ===
  const { taskId, delay } = workerData;
  const start = Date.now();

  console.log(`[Task ${taskId}] 開始 | PID: ${process.pid} | Worker TID: ${threadId}`);

  // 模擬工作
  setTimeout(() => {
    const elapsed = Date.now() - start;
    parentPort.postMessage({ taskId: `Task ${taskId}`, elapsed });
  }, delay);
}

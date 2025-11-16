// file-io-concurrent.js
const fs = require('fs').promises;
const path = require('path');

async function readFile(filename, id) {
  console.log(`[${id}] 開始讀取 ${filename} | PID: ${process.pid}`);

  try {
    const content = await fs.readFile(filename, 'utf-8');
    console.log(`[${id}] ${filename} | 大小: ${content.length} bytes`);
    return { filename, size: content.length };
  } catch (e) {
    console.log(`[${id}] ${filename} | 錯誤: ${e.message}`);
    return { filename, error: e.message };
  }
}

async function main() {
  console.log(`PID: ${process.pid}\n`);

  // 準備測試文件（創建幾個測試文件）
  const testDir = path.join(__dirname, 'tmp');
  await fs.mkdir(testDir, { recursive: true });

  const testFiles = ['test1.txt', 'test2.txt', 'test3.txt'].map(f => path.join(testDir, f));
  for (const f of testFiles) {
    await fs.writeFile(f, `內容 ${path.basename(f)} `.repeat(1000));
  }

  const start = Date.now();

  // 並發讀取
  const results = await Promise.all(
    testFiles.map((f, i) => readFile(f, i + 1))
  );

  console.log(`\n總耗時: ${Date.now() - start}ms`);
  console.log('結果:', results);

  // 清理
  for (const f of testFiles) {
    await fs.unlink(f);
  }
  await fs.rmdir(testDir);
}

main();

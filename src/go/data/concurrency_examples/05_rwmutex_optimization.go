// Go 並行程式設計範例 05: RWMutex 讀寫鎖優化
// 展示讀寫鎖在多讀少寫場景下的效能優勢

package main

import (
	"fmt"
	"sync"
	"time"
)

// 配置快取系統
type ConfigCache struct {
	mu         sync.RWMutex
	settings   map[string]string
	version    int
	readCount  int
	writeCount int
}

func NewConfigCache() *ConfigCache {
	return &ConfigCache{
		settings: map[string]string{
			"database_url": "localhost:5432",
			"api_key":      "default_key_123",
			"timeout":      "30s",
			"max_conn":     "100",
		},
		version: 1,
	}
}

func (c *ConfigCache) ReadConfig(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	c.readCount++
	value, exists := c.settings[key]

	fmt.Printf("📖 讀取設定 '%s': %s (版本: %d, 讀取次數: %d)\n",
		key, value, c.version, c.readCount)

	return value, exists
}

func (c *ConfigCache) WriteConfig(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.settings[key] = value
	c.version++
	c.writeCount++

	fmt.Printf("✍️  更新設定 '%s' = '%s' (新版本: %d, 寫入次數: %d)\n",
		key, value, c.version, c.writeCount)
}

func (c *ConfigCache) GetAllSettings() map[string]string {
	c.mu.RLock()
	defer c.mu.RUnlock()

	c.readCount++

	// 複製 map 以避免外部修改
	result := make(map[string]string)
	for k, v := range c.settings {
		result[k] = v
	}

	fmt.Printf("📋 讀取所有設定 (版本: %d, 讀取次數: %d)\n", c.version, c.readCount)
	return result
}

func (c *ConfigCache) GetStats() (int, int, int) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return c.version, c.readCount, c.writeCount
}

func main() {
	fmt.Println("=== RWMutex 讀寫鎖優化範例 ===")

	cache := NewConfigCache()
	var wg sync.WaitGroup

	// 啟動多個讀取者 (模擬高頻讀取)
	fmt.Println("👁️  啟動 8 個讀取者...")
	for i := 1; i <= 8; i++ {
		wg.Add(1)
		go readerWorker(i, cache, &wg)
	}

	// 啟動少數寫入者 (模擬低頻寫入)
	fmt.Println("✍️  啟動 2 個寫入者...")
	for i := 1; i <= 2; i++ {
		wg.Add(1)
		go writerWorker(i, cache, &wg)
	}

	// 啟動統計讀取者
	fmt.Println("📊 啟動統計監控...")
	wg.Add(1)
	go statsWorker(cache, &wg)

	wg.Wait()

	// 顯示最終統計
	fmt.Println("\n📈 最終統計結果:")
	version, reads, writes := cache.GetStats()
	fmt.Printf("   配置版本: %d\n", version)
	fmt.Printf("   總讀取次數: %d\n", reads)
	fmt.Printf("   總寫入次數: %d\n", writes)
	fmt.Printf("   讀寫比例: %.1f:1\n", float64(reads)/float64(writes))

	fmt.Println("\n📋 最終配置:")
	settings := cache.GetAllSettings()
	for key, value := range settings {
		fmt.Printf("   %s: %s\n", key, value)
	}

	fmt.Println("✅ RWMutex 範例完成")
}

func readerWorker(id int, cache *ConfigCache, wg *sync.WaitGroup) {
	defer wg.Done()

	keys := []string{"database_url", "api_key", "timeout", "max_conn"}

	for i := 0; i < 5; i++ {
		key := keys[i%len(keys)]
		cache.ReadConfig(key)
		time.Sleep(time.Duration(50+id*10) * time.Millisecond)
	}

	fmt.Printf("✅ 讀取者 %d 完成\n", id)
}

func writerWorker(id int, cache *ConfigCache, wg *sync.WaitGroup) {
	defer wg.Done()

	updates := []struct{ key, value string }{
		{"api_key", fmt.Sprintf("updated_key_%d", id)},
		{"timeout", fmt.Sprintf("%ds", 30+id*10)},
		{"max_conn", fmt.Sprintf("%d", 100+id*50)},
	}

	for i, update := range updates {
		time.Sleep(time.Duration(300+i*200) * time.Millisecond)
		cache.WriteConfig(update.key, update.value)
	}

	fmt.Printf("✅ 寫入者 %d 完成\n", id)
}

func statsWorker(cache *ConfigCache, wg *sync.WaitGroup) {
	defer wg.Done()

	for i := 0; i < 6; i++ {
		time.Sleep(400 * time.Millisecond)
		version, reads, writes := cache.GetStats()
		fmt.Printf("📊 統計 - 版本:%d, 讀:%d, 寫:%d\n", version, reads, writes)
	}

	fmt.Println("✅ 統計監控完成")
}

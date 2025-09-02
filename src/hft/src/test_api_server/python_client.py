import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
import statistics
import argparse

class AsyncOrderClient:
    def __init__(self, base_url="http://localhost:8080", num_connections=100):
        self.base_url = base_url
        self.num_connections = num_connections
        self.session = None
        self.connector = None
        self.latencies = []
        
    async def __aenter__(self):
        self.connector = aiohttp.TCPConnector(
            limit=self.num_connections,
            limit_per_host=self.num_connections,
            force_close=False,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
    
    async def place_order(self, order_id, symbol="BTCUSDT", quantity=1, price=50000.0, side="BUY"):
        order_data = {
            "order_id": f"PY_{order_id}",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "side": side,
            "client_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            start_time = time.perf_counter()
            async with self.session.post(
                f"{self.base_url}/order",
                json=order_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                end_time = time.perf_counter()
                
                round_trip_ms = (end_time - start_time) * 1000
                self.latencies.append(round_trip_ms)
                
                return {
                    "success": response.status == 200,
                    "round_trip_ms": round_trip_ms,
                    "server_latency_ms": result.get("latency_ms", 0),
                    "response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_orders(self, num_orders):
        tasks = []
        for i in range(num_orders):
            task = self.place_order(i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    def print_stats(self):
        if self.latencies:
            print("\n=== Python Client Performance Stats ===")
            print(f"Total orders: {len(self.latencies)}")
            print(f"Min latency: {min(self.latencies):.2f} ms")
            print(f"Max latency: {max(self.latencies):.2f} ms")
            print(f"Avg latency: {statistics.mean(self.latencies):.2f} ms")
            print(f"Median latency: {statistics.median(self.latencies):.2f} ms")
            if len(self.latencies) > 1:
                print(f"Std dev: {statistics.stdev(self.latencies):.2f} ms")
            
            percentiles = [50, 90, 95, 99]
            for p in percentiles:
                if len(self.latencies) >= 100 or (p <= 95 and len(self.latencies) >= 20):
                    sorted_latencies = sorted(self.latencies)
                    index = int(len(sorted_latencies) * p / 100)
                    print(f"P{p}: {sorted_latencies[min(index, len(sorted_latencies)-1)]:.2f} ms")

async def run_test(num_orders=1000, num_connections=100, warmup=100):
    async with AsyncOrderClient(num_connections=num_connections) as client:
        print(f"Python Async Client - Starting test with {num_orders} orders")
        print(f"Using {num_connections} concurrent connections")
        
        if warmup > 0:
            print(f"\nWarming up with {warmup} orders...")
            await client.batch_orders(warmup)
            client.latencies.clear()
        
        print(f"\nSending {num_orders} orders...")
        start_time = time.perf_counter()
        
        results = await client.batch_orders(num_orders)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = num_orders - successful
        
        print(f"\nCompleted in {total_time:.2f} seconds")
        print(f"Successful: {successful}, Failed: {failed}")
        print(f"Throughput: {num_orders / total_time:.2f} orders/sec")
        
        client.print_stats()
        
        return {
            "client": "Python (aiohttp)",
            "total_orders": num_orders,
            "successful": successful,
            "failed": failed,
            "total_time": total_time,
            "throughput": num_orders / total_time,
            "latencies": client.latencies
        }

async def main():
    parser = argparse.ArgumentParser(description='Python async client for API performance testing')
    parser.add_argument('--orders', type=int, default=1000, help='Number of orders to send')
    parser.add_argument('--connections', type=int, default=100, help='Number of concurrent connections')
    parser.add_argument('--warmup', type=int, default=100, help='Number of warmup orders')
    
    args = parser.parse_args()
    
    await run_test(
        num_orders=args.orders,
        num_connections=args.connections,
        warmup=args.warmup
    )

if __name__ == "__main__":
    asyncio.run(main())
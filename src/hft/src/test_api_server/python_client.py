import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
import statistics
import argparse
from enum import Enum
from typing import Optional

class BSAction(Enum):
    Buy = "buy"
    Sell = "sell"

class MarketType(Enum):
    Common = "common"
    Warrant = "warrant"
    OddLot = "odd_lot"
    Daytime = "daytime"
    FixedPrice = "fixed_price"
    PlaceFirst = "place_first"

class PriceType(Enum):
    Limit = "limit"
    Market = "market"
    LimitUp = "limit_up"
    LimitDown = "limit_down"
    Range = "range"

class TimeInForce(Enum):
    ROD = "rod"
    IOC = "ioc"
    FOK = "fok"

class OrderType(Enum):
    Stock = "stock"
    Futures = "futures"
    Option = "option"

class Order:
    def __init__(self, buy_sell: BSAction, symbol: int, price: float, quantity: int,
                 market_type: MarketType, price_type: PriceType, 
                 time_in_force: TimeInForce, order_type: OrderType,
                 user_def: Optional[str] = None):
        self.buy_sell = buy_sell
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.market_type = market_type
        self.price_type = price_type
        self.time_in_force = time_in_force
        self.order_type = order_type
        self.user_def = user_def

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
    
    async def place_order(self, order_id, order: Order = None):
        if order is None:
            order = Order(
                buy_sell=BSAction.Buy,
                symbol=2881,
                price=66,
                quantity=2000,
                market_type=MarketType.Common,
                price_type=PriceType.Limit,
                time_in_force=TimeInForce.ROD,
                order_type=OrderType.Stock,
                user_def="From_Py"
            )
        
        order_data = {
            "buy_sell": order.buy_sell.value,
            "symbol": order.symbol,
            "price": order.price,
            "quantity": order.quantity,
            "market_type": order.market_type.value,
            "price_type": order.price_type.value,
            "time_in_force": order.time_in_force.value,
            "order_type": order.order_type.value,
            "client_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if order.user_def:
            order_data["user_def"] = order.user_def
        
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
    
    async def batch_orders(self, num_orders, demo_order: Order = None):
        # Process orders in batches to avoid creating too many concurrent tasks
        batch_size = self.num_connections * 2  # Batch size based on connection pool
        results = []

        for batch_start in range(0, num_orders, batch_size):
            batch_end = min(batch_start + batch_size, num_orders)
            tasks = []
            for i in range(batch_start, batch_end):
                task = self.place_order(i, demo_order)
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

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
            sorted_latencies = sorted(self.latencies)
            for p in percentiles:
                if len(self.latencies) >= 100 or (p <= 95 and len(self.latencies) >= 20):
                    # Use linear interpolation for percentile calculation
                    rank = p / 100 * (len(sorted_latencies) - 1)
                    lower_index = int(rank)
                    upper_index = min(lower_index + 1, len(sorted_latencies) - 1)
                    weight = rank - lower_index
                    percentile_value = sorted_latencies[lower_index] * (1 - weight) + sorted_latencies[upper_index] * weight
                    print(f"P{p}: {percentile_value:.2f} ms")

async def run_test(num_orders=1000, num_connections=100, warmup=100):
    async with AsyncOrderClient(num_connections=num_connections) as client:
        print(f"Python Async Client - Starting test with {num_orders} orders")
        print(f"Using {num_connections} concurrent connections")
        
        demo_order = Order(
            buy_sell=BSAction.Buy,
            symbol=2881,
            price=66,
            quantity=2000,
            market_type=MarketType.Common,
            price_type=PriceType.Limit,
            time_in_force=TimeInForce.ROD,
            order_type=OrderType.Stock,
            user_def="From_Py"
        )
        
        print(f"Testing with Taiwan Stock Order: Symbol={demo_order.symbol} Price=NT${demo_order.price} Qty={demo_order.quantity}")
        
        if warmup > 0:
            print(f"\nWarming up with {warmup} orders...")
            await client.batch_orders(warmup, demo_order)
            client.latencies.clear()
        
        print(f"\nSending {num_orders} orders...")
        start_time = time.perf_counter()
        
        results = await client.batch_orders(num_orders, demo_order)
        
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
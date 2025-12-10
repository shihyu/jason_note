# How to Run Stress Tests

AXS uses **k6** together with **xk6** extensions to run high-performance stress tests.
All test scripts are written in **TypeScript** for better maintainability and type safety.

---

## Getting Started

### **Prerequisites**

Make sure the following tools are installed:

* **Node.js** — [install guide](https://nodejs.org/en/download)
* **k6** — [install guide](https://grafana.com/docs/k6/latest/set-up/install-k6/)
* **xk6** — [install guide](https://github.com/grafana/xk6)
* **xk6-kafka extension** (for Kafka load generation)

Build k6 with the Kafka extension:

```sh
xk6 build --with github.com/mostafa/xk6-kafka@latest
```

Install project dependencies:

```sh
npm install
```

---

## TypeScript Setup

Our stress test environment uses:

* **webpack** – bundles TypeScript test scripts into a single ES5-compatible output that k6 can execute
* **babel** – transpiles modern TypeScript/JavaScript syntax for compatibility with the k6 runtime

The build process outputs compiled test files into the `dist/` directory, which are executed via the custom xk6 binary.

## How to Run

Before running any test scenario, set the environment variable KAFKA_CONSUME_OFFSET to the next offset of the topic balance_change_stress_test_stats.

Example:
```bash
export KAFKA_CONSUME_OFFSET=0
```

### Test Scenarios

**Single User, Multiple Currencies**

Simulates one user performing balance changes across many currencies.
```bash
KAFKA_CONSUME_OFFSET=0 npm run test:single_user_multiple_currencies
```

**Multiple Users with the Same Shard ID**

All users share the same shard_id to stress-test shard-level contention.

```bash
KAFKA_CONSUME_OFFSET=0 npm run test:multiple_users_same_shard
```

**Multiple Users with Different Shard IDs**

Users are distributed across different shard_id values to test parallelism
and throughput scaling.
```bash
KAFKA_CONSUME_OFFSET=0 npm run test:multiple_users_multiple_shards
```

### AXS Metrics

These metrics are emitted by the AXS event processor to evaluate decoding performance,
apply performance, queue latency, and overall throughput.


**Processor Timing Metrics**
| Metric                                  | Description                                                          |
| --------------------------------------- | -------------------------------------------------------------------- |
| `axs_total_process_time_cost_micro_sec` | Total time (µs) spent processing a batch of events.                  |
| `axs_decode_time_cost_micro_sec`        | Time (µs) spent decoding message payloads in a batch.                |
| `axs_apply_time_cost_micro_sec`         | Time (µs) spent applying balance updates to in-memory data.          |
| `axs_async_cost_micro_sec`              | Time (µs) spent producing apply results to the internal async queue. |
| `axs_batch_message_count`               | Number of events included in the processed batch.                    |

**Throughput Metrics**
| Metric                                 | Description                                                                                                                                |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `axs_processor_throughput_msg_per_sec` | Processor-level throughput (messages/second), calculated as:<br>`axs_batch_message_count / (axs_total_process_time_cost_micro_sec / 1e-6)` |
| `axs_total_consumed_count`             | Total number of messages consumed during the test.                                                                                         |
| `axs_total_duration_sec`               | Total wall-clock duration (seconds) of the test.                                                                                           |

**Latency Metrics**
| Metric                           | Description                                                                                                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `axs_e2e_latency_ms`       | End-to-end latency (ms) from client sending the request to the event processor finishing the event.                                                                                   |
| `axs_inqueue_latency_ms`   | Time spent in the queue before the event processor consumes the message.                                                                                                              |
| `axs_e2e_throughput_msg_per_sec` | End-to-end throughput (messages/second), calculated as:<br>`axs_total_consumed_count / axs_total_duration_sec`<br>Note: may be limited by the load-generator machine, not AXS itself. |
| `axs_message_delay_count`        | Number of delayed messages detected at the consumer side.                                                                                                                             |

### Stress Test Results Using Docker Compose Locally

**Single User, Multiple Currencies**

![image](./single_user_multiple_currencies.png)

**Multiple Users with the Same Shard ID**

![image](./multiple_users_same_shard.png)

**Multiple Users with Different Shard IDs**

![image](./multiple_users_mulitple_shards.png)

**Grpc API Latency**

![image](./grpc_req_duration.png)

### Notes

Based on the stress test results above, the `multiple_users_same_shard` and `single_user_multiple_currencies` scenarios effectively reveal shard-level bottlenecks. Under these conditions, `axs_processor_throughput_msg_per_sec` reaches approximately 100k requests per second on a single server, projecting to 1M total throughput when scaled to 10 servers.

It's worth noting that `axs_e2e_throughput_msg_per_sec` may be significantly lower than processor throughput. This discrepancy occurs because the local machine cannot generate sufficient load, and all services (database, Kafka, consumer) run on the same machine, creating resource contention (CPU, file descriptors, etc.).

For high-volume stress tests, ensure Kafka and PostgreSQL have adequate resources and deploy each service in isolated environments to avoid artificial bottlenecks.
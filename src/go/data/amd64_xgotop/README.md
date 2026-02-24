![](./images/logo.png)

# xgotop - Realtime Go Runtime Visualization

A powerful eBPF-based tool for monitoring and visualizing Goroutine events in realtime with a beautiful web UI!

`xgotop` allows you to observe what's happening inside your Go programs at the runtime level, **without modifying your code or adding any instrumentation**. It uses eBPF uprobes to hook into the Go runtime and capture goroutine lifecycle events, memory allocations, and scheduler activity as they happen.

Whether you're debugging a production issue, optimizing performance, or just curious about how your Go program behaves under the hood, `xgotop` gives you the visibility you need.

## Features

- **Realtime monitoring** of Go runtime events via eBPF uprobes
- **Web UI** with timeline visualization and goroutine memory allocations
- **Multiple storage formats**: Protobuf (default) and JSONL
- **Session replay** to replay past observations
- **Watch by binary or PID** of the target Go program

> [!NOTE]
> `xgotop` only supports `arm64` architecture for now, we will rollout support for `amd64` soon!

## Usage

Running `xgotop` is relatively straightforward. Get a Go binary ready, and run each of the commands below in a separate terminal:

```bash
# Compile the xgotop program
make compile

# Run web UI in a terminal
make web-dev

# Run xgotop with the binary path or the PID of a running program
sudo ./xgotop -b <GO_BINARY_PATH> -web
sudo ./xgotop -pid <PROCESS_ID> -web
```

Then open [localhost:5173](http://localhost:5173), and you will see this screen:

![](./images/ui.png)

For more advanced `xgotop` runtime options such as sampling, see the [Advanced Usage](#advanced-usage) section below.

## How Does it Work?

![](./images/systemdesign.png)

`xgotop` works by attaching [eBPF](https://sazak.io/articles/an-applied-introduction-to-ebpf-with-go-2024-06-06) uprobes to key functions inside the Go runtime. When you run `xgotop` with a specified Go binary or a running process, the following steps happen:

1. The kernel-level eBPF program attaches user space probes to several Go runtime functions to trace goroutine lifecycle events

2. Each time a goroutine is created, exits, or allocates memory, the eBPF program records the event with metadata like goroutine ID, timestamp, stack size, and more

3. These events are streamed to the user space via an eBPF [ringbuffer](https://docs.ebpf.io/linux/map-type/BPF_MAP_TYPE_RINGBUF/). The xgotop process running in user space reads these events in realtime.

4. Read and processed events are stored in either Protobuf (for efficient storage) or JSONL (for better readability) format. Each monitoring session gets its own directory in `sessions/` with a unique session ID.

5. Processed events are served over WebSockets to the web UI. The UI connects to xgotop's built-in HTTP server and receives events as they happen, and displays them in a detailed timeline view.

## Runtime Metrics

![](./images/r16_p1_w1_protobuf.png)

`xgotop` captures several key metrics about itself to help you understand the overhead and performance characteristics of the monitoring process. The chart above shows metrics from a test run with 16 event readers, 1 event processor and Protobuf storage.

### Key Metrics

- **LAT (Latency)**: The average time an eBPF hook takes to run. This is simply the overhead added to the observed Go program. Lower is better. Enabling debugging in the eBPF program enables bpf printk calls and increases `LAT`.

- **RPS (Reads Per Second)**: The number of eBPF events that `xgotop` reads from the ringbuffer per second. This depends on how active your Go program is. More goroutines and allocations mean higher RPS.

- **PPS (Processed Per Second)**: Similar to RPS, but specifically counts the number of events processed by the userspace program. A high difference between `RPS` and `PPS` means increased userspace event queue backpressure (see `EWP` below) and eventually failed eBPF ringbuffer sends.

- **EWP (Events Waiting to be Processed)**: Number of events waiting to be processed in the userspace event queue (channel). Increasing `EWP` means that the userspace event processors cannot keep up with the speed of event generation in kernel level. Ideally, `PRC` (see below) should be higher than `EWP` for this to happen.

- **PRC (Processing Time)**: The average time an event processor takes to process a single event. This includes basic event processing and transforming to other internal structures, and sending the event to storage manager and the API/Ws servers.

The exact metrics you'll see depend on your Go program's behavior, the sampling rate, and whether you're using the web UI or just storing events to disk.

## Advanced Usage

`xgotop` provides several CLI flags to customize its behavior. Here's the complete list of options:

```bash
# Attach to a binary
-b <path>           Path to the Go binary to monitor

# Attach to a running process
-pid <pid>          PID of the running Go process to monitor

# Silent mode (no console output)
-s                  Enable silent mode, useful for performance testing

# Event reader workers (default: 3)
-rw <count>         Number of ringbuffer read workers
                    More workers can handle higher event rates

# Event processor workers (default: 5)
-pw <count>         Number of event processing workers
                    These workers transform raw events to storage format

# Enable web UI support
-web                Enable web mode with API server and WebSocket
-web-port <port>    Port for the web API server (default: 8080)

# Storage format
-storage-format <format>     Storage format: "protobuf" or "jsonl" (default: protobuf)
                             Protobuf is faster and more space-efficient

# Storage location
-storage-dir <path>          Directory for session data (default: ./sessions)

# Batch configuration
-batch-size <size>           Number of events to batch before writing (default: 1000)
                             Higher values reduce I/O but increase memory usage

-batch-flush-interval <dur>  Max time to wait before flushing (default: 100ms)
                             Ensures events are written even with low activity
```

### Sampling Configuration

The sampling feature is one of the most powerful ways to reduce overhead when monitoring high throughput applications. Instead of capturing every single Go runtime goroutine event, you can configure `xgotop` to sample events at specific rates inside the eBPF program using the '-sample' flag:

```bash
-sample <rates>
```

You can sample the following event types:

- `newgoroutine`: Goroutine creation
- `goexit`: Goroutine exit  
- `makemap`: Map allocation
- `makeslice`: Slice allocation
- `newobject`: Object allocation
- `casgstatus`: Goroutine status change

The sampling format is a comma separated list of `event:rate` pairs, where rate is a float between 0.0 and 1.0.

Examples:

```bash
# Sample 10% of goroutine creations
sudo ./xgotop -pid 48 -sample "newgoroutine:0.1"

# Sample multiple event types at different rates
sudo ./xgotop -pid 48 -sample "newgoroutine:0.5,makemap:0.2,makeslice:0.1"

# Sample only specific events (others are not captured)
sudo ./xgotop -pid 48 -sample "newgoroutine:0.8,goexit:0.8"
```


## Testing

`xgotop` comes with several test suites to validate its functionality and measure performance characteristics. All tests use the included `testserver` binary, which is a simple HTTP API server with a single endpoint.

### Sampling Test

The sampling test validates that the sampling feature works correctly by running `xgotop` with different sampling rates and comparing the results.

```bash
make samplingtest
```

This will:

1. Run 6 different test scenarios with various sampling configurations

2. Generate 5000 HTTP requests to the testserver for each scenario

3. Save metrics to `sampling_test_results/` directory

4. Automatically validate that the sampling rates match expectations using `validate_sampling.py`

The validation script compares the baseline (100% sampling) event counts with the sampled run event counts and verifies that they match the configured sampling rates within the acceptable tolerance (5% of the baseline metrics).

### Web Overhead Test

This test measures the overhead of different `xgotop` configurations with and without the web UI enabled.

```bash
make weboverheadtest
```

This will:

1. Test multiple configurations:
   - Reader workers: 1, 2, 4, 8, 16, 32, 64, 128
   - Processor workers: 1
   - Storage formats: JSONL and Protobuf
   - Web modes: Enabled and disabled

2. Generate 50K HTTP requests in flood mode

3. Measure performance metrics (RPS, PPS, LAT, etc.)

4. Save results to `web_overhead_test_results/` directory

5. Generate comparison plots showing how different configurations affect overhead

The plots will show how metrics like latency, throughput, and processing time scale with the number of workers and which storage format performs better.

### Buffer Test

The buffer test helps finding the optimal batch size for event processing.

```bash
make buffertest
```

This will:

1. Test various batch sizes: 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000

2. Run with both JSONL and Protobuf storage formats

3. Test only with web mode enabled

4. Generate 50K HTTP requests in flood mode

5. Save results and generate plots comparing batch sizes

yfinance-rust
=============

yfinance-rust is a simple command line tool that downloads financial data from Yahoo Finance, like the popular package [yfinance](https://github.com/ranaroussi/yfinance) in python but with fewer features to offer.

This is not about re-creating wheels but rather a personal project to familiarise with rust programming. It offers me opportunities to learn many aspects of rust, such as

- move semantics
- lifetimes
- functional programming
- recursion with boxes
- async programming
- error and option handling
- macro (really like rust-analyzer's macro expanision ---- it is a dream.)
- cargo
- testing
- inline documenting

Apart from rust's language features, the community and the ecosystem of rust is fanscinating -- active, strong and full of quality projects and hence I have explored a few as listed in `cargo.toml` too,

- chrono: parse and process datetime objects
- clap: build cmd tools
- hyper: highly performant http server and client
- tokio: async programming made easy
- log/env_logger: great logging tool
- serde: great serialisation/deserialisation tool

## project structure

```
src
├── http.rs: download from yahoo
├── main.rs: program entry + write to csv
├── options.rs: cmd args
└── v8chart.rs: data class and conversion to csv
```

## command line options

```
✗ target/debug/yfinance-rust 
yfinance-rust 1.0
Hongze Xia hongzex@gmail.com>

USAGE:
    yfinance-rust <SUBCOMMAND>

FLAGS:
    -h, --help       Prints help information
    -V, --version    Prints version information

SUBCOMMANDS:
    convert     Convert yahoo finance v8 json into csv
    download    Download historical data from yahoo finance
    help        Prints this message or the help of the given subcommand(s)
```

```
✗ target/debug/yfinance-rust download -h
yfinance-rust-download 
Download historical data from yahoo finance

USAGE:
    yfinance-rust download [FLAGS] [OPTIONS] [symbols]...

ARGS:
    <symbols>...    List of symbols to download. Required

FLAGS:
        --convert             Convert JSON to CSV
    -h, --help                Prints help information
        --include-pre-post    Include pre & post market data
    -V, --version             Prints version information

OPTIONS:
        --end <end>                  An end date. Default to Now
        --interval <interval>        select a proper interval for the data 1m goes back to 4-5 days
                                     5m goes back to ~80 days others goes back to the initial
                                     trading date [default: 1d] [possible values: 1m, 5m, 1d, 5d,
                                     1wk, 1mo, 3mo]
    -o, --output-dir <output-dir>    Sets a output directory. The format of the output JSON looks
                                     like `SYMBOL_20200202_20200303.json` [default: .]
        --rate <rate>                Request rate in terms of ms [default: 100]
        --start <start>              A start date to download from. Default to the initial trading
                                     day
```

```
✗ target/debug/yfinance-rust convert -h 
yfinance-rust-convert 
Convert yahoo finance v8 json into csv

USAGE:
    yfinance-rust convert [FLAGS] <input-dir>

ARGS:
    <input-dir>    input_dir where the JSONs live

FLAGS:
    -h, --help         Prints help information
        --recursive    whether to walk the input_dir recursively
    -V, --version      Prints version information
```

## example

```
✗ RUST_LOG=info target/debug/yfinance-rust download --convert -o target/output AAPL MSFT NVDA TSLA
[2021-01-26T05:05:24Z INFO  yfinance_rust::options] Opts { subcmd: Download(DownloadOpts { symbols: ["AAPL", "MSFT", "NVDA", "TSLA"], start: None, end: None, include_pre_post: false, output_dir: "target/output", interval: "1d", rate: MyDuration { duration: 100ms }, convert: true }) }
[2021-01-26T05:05:27Z INFO  yfinance_rust::http] downloaded "target/output/NVDA_init_20210126.json"
[2021-01-26T05:05:28Z INFO  yfinance_rust::http] downloaded "target/output/TSLA_init_20210126.json"
[2021-01-26T05:05:29Z INFO  yfinance_rust::http] downloaded "target/output/MSFT_init_20210126.json"
[2021-01-26T05:05:29Z INFO  yfinance_rust::http] downloaded "target/output/AAPL_init_20210126.json"
[2021-01-26T05:05:29Z INFO  yfinance_rust::http] have successfully download 4 of 4
[2021-01-26T05:05:30Z INFO  yfinance_rust] successfully converted to "target/output/AAPL_init_20210126.csv"
[2021-01-26T05:05:30Z INFO  yfinance_rust] successfully converted to "target/output/MSFT_init_20210126.csv"
[2021-01-26T05:05:31Z INFO  yfinance_rust] successfully converted to "target/output/NVDA_init_20210126.csv"
[2021-01-26T05:05:31Z INFO  yfinance_rust] successfully converted to "target/output/TSLA_init_20210126.csv"
```
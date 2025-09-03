use chrono::{DateTime, FixedOffset, NaiveDateTime};
use csv::Writer;
use itertools::izip;
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    error::Error,
    fs::File,
    io::{BufReader, BufWriter},
    path::Path,
};

#[derive(Deserialize, Debug, Serialize)]
pub struct TradePeriod {
    pub timezone: String,
    pub start: u64,
    pub end: u64,
    pub gmtoffset: i32,
}
#[derive(Deserialize, Debug, Serialize)]
pub struct CurrentTradePeriod {
    pub pre: TradePeriod,
    pub regular: TradePeriod,
    pub post: TradePeriod,
}
#[derive(Deserialize, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct V8Meta {
    pub currency: String,
    pub symbol: String,
    pub exchange_name: String,
    pub instrument_type: String,
    pub first_trade_date: u64,
    pub regular_market_time: u64,
    pub gmtoffset: i32,
    pub timezone: String,
    pub exchange_timezone_name: String,
    pub regular_market_price: f32,
    pub chart_previous_close: f32,
    pub price_hint: f32,
    pub current_trading_period: CurrentTradePeriod,
    pub data_granularity: String,
    pub range: String,
    pub valid_ranges: Vec<String>,
}
#[derive(Deserialize, Debug)]
pub struct OHLCV {
    pub volume: Vec<Option<u64>>,
    pub high: Vec<Option<f64>>,
    pub close: Vec<Option<f64>>,
    pub low: Vec<Option<f64>>,
    pub open: Vec<Option<f64>>,
}
#[derive(Deserialize, Debug)]
pub struct AdjClose {
    pub adjclose: Vec<Option<f64>>,
}
#[derive(Deserialize, Debug)]
pub struct Indicators {
    pub quote: Vec<OHLCV>,
    pub adjclose: Vec<AdjClose>,
}

#[derive(Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Split {
    pub date: i64,
    pub numerator: u8,
    pub denominator: u8,
    pub split_ratio: String,
}

#[derive(Deserialize, Debug)]
pub struct Dividend {
    pub amount: f64,
    pub date: i64,
}

#[derive(Deserialize, Debug)]
pub struct Event {
    splits: Option<HashMap<String, Split>>,
    dividends: Option<HashMap<String, Dividend>>,
}
#[derive(Deserialize, Debug)]
pub struct V8Result {
    pub meta: V8Meta,
    pub timestamp: Vec<i64>,
    pub indicators: Indicators,
    pub events: Option<Event>,
}

#[derive(Deserialize, Debug)]
pub struct Chart {
    pub result: Vec<V8Result>,
    pub error: Option<String>,
}

#[derive(Deserialize, Debug)]
pub struct ChartWrapper {
    pub chart: Chart,
}

#[derive(Serialize, Debug)]
pub struct Record {
    pub timestamp: DateTime<FixedOffset>,
    pub volume: Option<u64>,
    pub high: Option<f64>,
    pub low: Option<f64>,
    pub open: Option<f64>,
    pub close: Option<f64>,
    pub adjclose: Option<f64>,
    pub split: Option<String>,
    pub dividend: Option<f64>,
}
#[derive(Serialize, Debug)]
pub struct DataSet {
    pub records: Vec<Record>,
    pub meta: V8Meta,
}

/// convert chart to a vec of DataSet
/// Usually there is only one element unless the symbol is ambiguious
impl From<Chart> for Vec<DataSet> {
    fn from(chart: Chart) -> Self {
        let mut dataset_vec: Vec<DataSet> = vec![];
        for result in chart.result.into_iter() {
            let vohlca_iter = result
                .indicators
                .quote
                .iter()
                .zip(result.indicators.adjclose.iter())
                .flat_map(|(ohlcv, adj)| {
                    izip!(
                        &ohlcv.volume,
                        &ohlcv.open,
                        &ohlcv.high,
                        &ohlcv.low,
                        &ohlcv.close,
                        &adj.adjclose
                    )
                });
            let gmtoffset = result.meta.gmtoffset;
            let mut ds = DataSet {
                records: Vec::new(),
                meta: result.meta,
            };
            for (t, (v, o, h, l, c, a)) in result.timestamp.iter().zip(vohlca_iter) {
                let naive = NaiveDateTime::from_timestamp(*t, 0);
                let offset = FixedOffset::east(gmtoffset);
                let tm = DateTime::<FixedOffset>::from_utc(naive, offset);
                let (split, dividend) = result
                    .events
                    .as_ref()
                    .map(|ev| {
                        let date_key = t.to_string();
                        (
                            ev.splits
                                .as_ref()
                                .and_then(|m| m.get(&date_key).map(|s| s.split_ratio.clone())),
                            ev.dividends.as_ref().and_then(|m| m.get(&date_key).map(|d| d.amount)),
                        )
                    })
                    .unwrap_or((None, None));

                ds.records.push(Record {
                    timestamp: tm,
                    volume: *v,
                    high: *h,
                    low: *l,
                    open: *o,
                    close: *c,
                    adjclose: *a,
                    split,
                    dividend,
                });
            }
            dataset_vec.push(ds);
        }
        dataset_vec
    }
}

/// read a json from file
pub fn load_from_json(path: &str) -> Result<ChartWrapper, Box<dyn Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let u = serde_json::from_reader(reader)?;
    Ok(u)
}

/// write a dataset to path
pub fn write_to_csv<P: AsRef<Path>>(ds: &DataSet, path: P) -> Result<(), Box<dyn Error>> {
    let file = File::create(path)?;
    let writer = BufWriter::new(file);
    let mut wtr = Writer::from_writer(writer);
    for r in ds.records.iter() {
        wtr.serialize(r)?;
    }
    Ok(())
}
#[cfg(test)]
mod tests {
    use std::fs::remove_file;

    use rand::{distributions::Alphanumeric, thread_rng, Rng};

    use super::*;

    #[test]
    fn test_load_json() {
        let result = load_from_json("assets/GXY.AX_20200103_20200107.json");
        assert!(result.is_ok());
        let result = load_from_json("assets/A2M.AX_20200103_20200107.json");
        assert!(result.is_ok());
    }

    #[test]
    fn test_from_chart() {
        let chart_wrapper = load_from_json("assets/GXY.AX_20200103_20200107.json").unwrap();
        let ds_vec: Vec<DataSet> = chart_wrapper.chart.into();
        assert_eq!(ds_vec.len(), 1);
        assert_eq!(ds_vec[0].records.len(), 3);
    }

    #[test]
    fn test_write_csv() {
        let chart_wrapper = load_from_json("assets/AAPL_init_20210126.json").unwrap();
        let ds_vec: Vec<DataSet> = chart_wrapper.chart.into();
        let prefix: String = thread_rng()
            .sample_iter(&Alphanumeric)
            .take(30)
            .map(char::from)
            .collect();
        let path = std::env::temp_dir().join(prefix);
        let result = write_to_csv(&ds_vec[0], path.clone());
        assert!(result.is_ok());
        let _ = remove_file(path);
    }
}

extern crate reqwest;
extern crate serde;
extern crate serde_json;

use serde::Deserialize;
use std::error::Error;

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct PriceInfo {
    symbol: String,
    price: String,
}

fn main() -> Result<(), Box<dyn Error>> {
    let response = reqwest::blocking::get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")?;
    let price_info: PriceInfo = response.json()?;
    println!("{:?}", price_info);
    Ok(())
}


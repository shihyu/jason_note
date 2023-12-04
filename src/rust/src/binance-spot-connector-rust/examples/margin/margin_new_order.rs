use binance_spot_connector_rust::{
    http::Credentials,
    hyper::{BinanceHttpClient, Error},
    margin,
};
use env_logger::Builder;
use rust_decimal_macros::dec;

#[tokio::main]
async fn main() -> Result<(), Error> {
    Builder::from_default_env()
        .filter(None, log::LevelFilter::Info)
        .init();
    let credentials = Credentials::from_hmac("api-key".to_owned(), "api-secret".to_owned());
    let client = BinanceHttpClient::default().credentials(credentials);
    let request = margin::margin_new_order("BNBUSDT", "SELL", "MARKET")
        .quantity(dec!(1.01))
        .price(dec!(10))
        .stop_price(dec!(20.01))
        .time_in_force("GTC");
    let data = client.send(request).await?.into_body_str().await?;
    log::info!("{}", data);
    Ok(())
}

use binance_spot_connector_rust::{
    http::Credentials,
    hyper::{BinanceHttpClient, Error},
    wallet,
};
use env_logger::Builder;

#[tokio::main]
async fn main() -> Result<(), Error> {
    Builder::from_default_env()
        .filter(None, log::LevelFilter::Info)
        .init();
    let credentials = Credentials::from_hmac("api-key".to_owned(), "api-secret".to_owned());
    let client = BinanceHttpClient::default().credentials(credentials);
    let request = wallet::universal_transfer_history("MAIN_UMFUTURE")
        .start_time(1640995200000)
        .end_time(1640995200000)
        .current(1)
        .size(100)
        .from_symbol("BNBUSDT")
        .to_symbol("BNBUSDT");
    let data = client.send(request).await?.into_body_str().await?;
    log::info!("{}", data);
    Ok(())
}

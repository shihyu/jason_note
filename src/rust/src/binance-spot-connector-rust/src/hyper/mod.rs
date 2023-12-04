//! Binance client using Hyper.
//!
//! # Example
//!
//! ```no_run
//! use binance_spot_connector_rust::{
//!   http::{request::RequestBuilder, Credentials, Method},
//!   hyper::{BinanceHttpClient, Error},
//! };
//! use env_logger::Builder;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Error> {
//!   Builder::from_default_env()
//!       .filter(None, log::LevelFilter::Info)
//!       .init();
//!   let credentials = Credentials::from_hmac("api-key".to_owned(), "api-secret".to_owned());
//!   let client = BinanceHttpClient::default().credentials(credentials);
//!   let request = RequestBuilder::new(Method::Post, "/api/v3/order").params(vec![
//!       ("symbol", "BNBUSDT"),
//!       ("side", "SELL"),
//!       ("type", "LIMIT"),
//!       ("quantity", "0.1"),
//!       ("price", "320.2"),
//!   ]);
//!   let data = client.send(request).await?.into_body_str().await?;
//!   log::info!("{}", data);
//!   Ok(())
//! }
//! ```

mod client;
mod error;
mod response;

pub use client::*;
pub use error::*;
pub use response::*;

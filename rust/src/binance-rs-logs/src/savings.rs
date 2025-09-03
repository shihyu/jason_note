use std::process;
use std::thread;
use stdext::function_name;
use crate::util::build_signed_request;
use crate::model::{AssetDetail, CoinInfo, DepositAddress, SpotFuturesTransferType, TransactionId};
use crate::client::Client;
use crate::errors::Result;
use std::collections::BTreeMap;
use crate::api::API;
use crate::api::Sapi;

#[derive(Clone)]
pub struct Savings {
    pub client: Client,
    pub recv_window: u64,
}

impl Savings {
    /// Get all coins available for deposit and withdrawal
    pub fn get_all_coins(&self) -> Result<Vec<CoinInfo>> {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
        let request = build_signed_request(BTreeMap::new(), self.recv_window)?;
        self.client
            .get_signed(API::Savings(Sapi::AllCoins), Some(request))
    }

    /// Fetch details of assets supported on Binance.
    pub fn asset_detail(&self, asset: Option<String>) -> Result<BTreeMap<String, AssetDetail>> {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
        let mut parameters = BTreeMap::new();
        if let Some(asset) = asset {
            parameters.insert("asset".into(), asset);
        }
        let request = build_signed_request(parameters, self.recv_window)?;
        self.client
            .get_signed(API::Savings(Sapi::AssetDetail), Some(request))
    }

    /// Fetch deposit address with network.
    ///
    /// You can get the available networks using `get_all_coins`.
    /// If no network is specified, the address for the default network is returned.
    pub fn deposit_address<S>(&self, coin: S, network: Option<String>) -> Result<DepositAddress>
    where
        S: Into<String>,
    {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
        let mut parameters = BTreeMap::new();
        parameters.insert("coin".into(), coin.into());
        if let Some(network) = network {
            parameters.insert("network".into(), network);
        }
        let request = build_signed_request(parameters, self.recv_window)?;
        self.client
            .get_signed(API::Savings(Sapi::DepositAddress), Some(request))
    }

    pub fn transfer_funds<S>(
        &self, asset: S, amount: f64, transfer_type: SpotFuturesTransferType,
    ) -> Result<TransactionId>
    where
        S: Into<String>,
    {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
        let mut parameters = BTreeMap::new();
        parameters.insert("asset".into(), asset.into());
        parameters.insert("amount".into(), amount.to_string());
        parameters.insert("type".into(), (transfer_type as u8).to_string());
        let request = build_signed_request(parameters, self.recv_window)?;
        self.client
            .post_signed(API::Savings(Sapi::SpotFuturesTransfer), request)
    }
}

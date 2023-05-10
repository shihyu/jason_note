use std::process;
use std::thread;
use stdext::function_name;
use crate::errors::Result;
use std::collections::BTreeMap;
use std::time::{SystemTime, UNIX_EPOCH};
use error_chain::bail;
use serde_json::Value;

pub fn build_request(parameters: BTreeMap<String, String>) -> String {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    let mut request = String::new();
    for (key, value) in parameters {
        let param = format!("{}={}&", key, value);
        request.push_str(param.as_ref());
    }
    request.pop();
    request
}

pub fn build_signed_request(
    parameters: BTreeMap<String, String>, recv_window: u64,
) -> Result<String> {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    build_signed_request_custom(parameters, recv_window, SystemTime::now())
}

pub fn build_signed_request_custom(
    mut parameters: BTreeMap<String, String>, recv_window: u64, start: SystemTime,
) -> Result<String> {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    if recv_window > 0 {
        parameters.insert("recvWindow".into(), recv_window.to_string());
    }
    if let Ok(timestamp) = get_timestamp(start) {
        parameters.insert("timestamp".into(), timestamp.to_string());
        return Ok(build_request(parameters));
    }
    bail!("Failed to get timestamp")
}

pub fn to_i64(v: &Value) -> i64 {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    v.as_i64().unwrap()
}

pub fn to_f64(v: &Value) -> f64 {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    v.as_str().unwrap().parse().unwrap()
}

fn get_timestamp(start: SystemTime) -> Result<u64> {
	println!("pid={},tid={:?} {}:{} {}", process::id(), thread::current().id(), file!(), line!(), function_name!());
    let since_epoch = start.duration_since(UNIX_EPOCH)?;
    Ok(since_epoch.as_secs() * 1000 + u64::from(since_epoch.subsec_nanos()) / 1_000_000)
}

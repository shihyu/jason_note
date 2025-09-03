#![allow(unused_imports)]
use env_logger;
use log::{debug, error, info, trace, warn};

fn main() {
    env_logger::init();
    trace!("trace message");
    debug!("debug message");
    info!("info message");
    warn!("warn message");
    error!("error message");
}

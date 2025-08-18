// Buttplug Rust Source Code File - See https://buttplug.io for more info.
//
// Copyright 2016-2024 Nonpolynomial Labs LLC. All rights reserved.
//
// Licensed under the BSD 3-Clause license. See LICENSE file in the project root
// for full license information.

//! Handles client sessions, as well as discovery and communication with hardware.
//!
//! The Buttplug Server is just a thin frontend for device connection and communication. The server
//! itself doesn't do much other than configuring the device system and handling a few non-device
//! related tasks like [initial connection
//! handshake](https://buttplug-spec.docs.buttplug.io/architecture.html#stages) and system timeouts.
//! Once a connection is made from a [ButtplugClient](crate::client::ButtplugClient) to a
//! [ButtplugServer], the server mostly acts as a pass-thru frontend to the [DeviceManager].
//!
//! ## Server Lifetime
//!
//! The server has following lifetime stages:
//!
//! - Configuration
//!   - This happens across the [ButtplugServerBuilder], as well as the [ButtplugServer] instance it
//!     returns. During this time, we can specify attributes of the server like its name and if it
//!     will have a ping timer. It also allows for addition of protocols and device configurations
//!     to the system, either via configuration files or through manual API calls.
//! - Connection
//!   - After configuration is done, the server can be put into a listening mode (assuming
//!     [RemoteServer](ButtplugRemoteServer) is being used. for [in-process
//!     servers](crate::connector::ButtplugInProcessClientConnector), the client own the server and just
//!     connects to it directly). At this point, a [ButtplugClient](crate::client::ButtplugClient)
//!     can connect and start the
//!     [handshake](https://buttplug-spec.docs.buttplug.io/architecture.html#stages) process.
//! - Pass-thru
//!   - Once the handshake has succeeded, the server basically becomes a pass-thru to the
//!     [DeviceManager], which manages discovery of and communication with devices. The only thing
//!     the server instance manages at this point is ownership of the [DeviceManager] and
//!     ping timer, but doesn't really do much itself. The server remains in this state until the
//!     connection to the client is severed, at which point all devices connected to the device
//!     manager will be stopped.
//! - Disconnection
//!   - The server can be put back in Connection mode without being recreated after disconnection,
//!     to listen for another client connection while still maintaining connection to whatever
//!     devices the [DeviceManager] has.
//! - Destruction
//!   - If the server object is dropped, all devices are stopped and disconnected as part
//!     of the [DeviceManager] teardown.

#[macro_use]
extern crate log;

// TODO: Re-enable WebBluetooth when web-sys features are properly configured
// #[cfg(target_arch = "wasm32")]
// mod webbluetooth;

#[macro_use]
extern crate buttplug_derive;

#[macro_use]
extern crate strum_macros;

pub mod connector;
pub mod device;
pub mod message;
mod ping_timer;
mod server;
mod server_builder;
mod server_message_conversion;

pub use server::ButtplugServer;
pub use server_builder::ButtplugServerBuilder;

use futures::future::BoxFuture;
use thiserror::Error;

use buttplug_core::{
  errors::{ButtplugDeviceError, ButtplugError},
  message::ButtplugServerMessageV4,
};

/// Result type for Buttplug Server methods, as the server will always communicate in
/// [ButtplugServerMessage] instances in order to follow the [Buttplug
/// Spec](http://buttplug-spec.docs.buttplug.io).
pub type ButtplugServerResult = Result<ButtplugServerMessageV4, ButtplugError>;
/// Future type for Buttplug Server futures, as the server will always communicate in
/// [ButtplugServerMessage] instances in order to follow the [Buttplug
/// Spec](http://buttplug-spec.docs.buttplug.io).
pub type ButtplugServerResultFuture = BoxFuture<'static, ButtplugServerResult>;

/// Error enum for Buttplug Server configuration errors.
#[derive(Error, Debug)]
pub enum ButtplugServerError {
  /// DeviceConfigurationManager could not be built.
  #[error("The DeviceConfigurationManager could not be built: {0}")]
  DeviceConfigurationManagerError(ButtplugDeviceError),
  /// DeviceCommunicationManager type has already been added to the system.
  #[error("DeviceCommunicationManager of type {0} has already been added.")]
  DeviceCommunicationManagerTypeAlreadyAdded(String),
  /// Protocol has already been added to the system.
  #[error("Buttplug Protocol of type {0} has already been added to the system.")]
  ProtocolAlreadyAdded(String),
  /// Requested protocol has not been registered with the system.
  #[error("Buttplug Protocol of type {0} does not exist in the system and cannot be removed.")]
  ProtocolDoesNotExist(String),
}

// WASM-specific exports for WebBluetooth support
#[cfg(target_arch = "wasm32")]
mod wasm_exports {
  use super::*;
  // TODO: Re-enable WebBluetooth imports when available
  // use crate::webbluetooth::*;
  use js_sys;
  use tokio_stream::StreamExt;
  use futures::pin_mut;
  use buttplug_core::util::async_manager;
  use crate::{
    server::ButtplugServer, 
    server_builder::ButtplugServerBuilder,
  };
  use console_error_panic_hook;
  use tracing_subscriber::{layer::SubscriberExt, Registry};
  use tracing_wasm::{WASMLayer, WASMLayerConfig};
  use wasm_bindgen::prelude::*;
  use std::sync::Arc;
  use js_sys::Uint8Array;

  type FFICallback = js_sys::Function;
  type FFICallbackContext = u32;

  #[derive(Clone, Copy)]
  pub struct FFICallbackContextWrapper(FFICallbackContext);

  unsafe impl Send for FFICallbackContextWrapper {
  }
  unsafe impl Sync for FFICallbackContextWrapper {
  }

  pub type ButtplugWASMServer = Arc<ButtplugServer>;

  pub fn send_server_message(
    message: &str,
    callback: &FFICallback,
  ) {
    // Simplified message sending for now
    let buf = message.as_bytes();
    {
      let this = JsValue::null();
      let uint8buf = unsafe { Uint8Array::new(&Uint8Array::view(buf)) };
      callback.call1(&this, &JsValue::from(uint8buf));
    }
  }

  #[no_mangle]
  #[wasm_bindgen]
  pub fn buttplug_create_embedded_wasm_server(
    callback: &FFICallback,
  ) -> u32 {
    console_error_panic_hook::set_once();
    
    // Create a minimal mock server but don't send ServerInfo immediately
    info!("Creating WASM server for standard Buttplug client...");
    
    // Store the callback for later use
    // Don't send ServerInfo here - wait for RequestServerInfo message
    
    // Return a dummy handle (just return 1 to indicate success)
    1
  }

  #[no_mangle]
  #[wasm_bindgen]
  pub fn buttplug_free_embedded_wasm_server(handle: u32) {
    info!("Freeing WASM server handle: {}", handle);
    // For now, this is a no-op since we're using a simple integer handle
  }

  #[no_mangle]
  #[wasm_bindgen]
  pub fn buttplug_client_send_json_message(
    server_handle: u32,
    buf: &[u8],
    callback: &FFICallback,
  ) {
    info!("Sending message to server handle: {}", server_handle);
    let callback = callback.clone();
    
    // Parse message and handle it simply
    let msg_str = std::str::from_utf8(buf).unwrap();
    info!("Received message: {}", msg_str);
    
    // For now, just handle basic messages synchronously
    // Check if it's a scanning request
    if msg_str.contains("\"StartScanning\"") {
      info!("Received StartScanning message");
      send_server_message("[{\"Ok\":{\"Id\":1}}]", &callback);
      
      // Simulate finding a mock device after a delay
      let callback_clone = callback.clone();
      wasm_bindgen_futures::spawn_local(async move {
        // Use a simple delay
        use wasm_bindgen_futures::JsFuture;
        use js_sys::Promise;
        
        // Simple delay - resolve immediately for testing
        let delay = Promise::resolve(&wasm_bindgen::JsValue::from(1));
        let _ = JsFuture::from(delay).await;
        
        // Send mock device found immediately
        send_server_message("[{\"DeviceAdded\":{\"DeviceName\":\"模擬振動器\",\"DeviceIndex\":1,\"DeviceMessages\":{\"VibrateCmd\":{\"FeatureCount\":1}},\"Id\":0}}]", &callback_clone);
        
        // Send scanning finished right after
        send_server_message("[{\"ScanningFinished\":{\"Id\":0}}]", &callback_clone);
      });
    } else if msg_str.contains("\"StopScanning\"") {
      info!("Received StopScanning message");
      send_server_message("[{\"Ok\":{\"Id\":1}}]", &callback);
    } else if msg_str.contains("\"RequestServerInfo\"") {
      info!("Received RequestServerInfo message");
      // Extract message ID from the request
      let msg_id = if msg_str.contains("\"Id\":") {
        // Try to extract ID - for simplicity, just use 1
        1
      } else {
        1
      };
      send_server_message(&format!("[{{\"ServerInfo\":{{\"ServerName\":\"Buttplug WASM Server\",\"MessageVersion\":4,\"MaxPingTime\":0,\"Id\":{}}}}}]", msg_id), &callback);
    } else {
      info!("Received other message, sending OK");
      send_server_message("[{\"Ok\":{\"Id\":1}}]", &callback);
    }
  }

  #[no_mangle]
  #[wasm_bindgen]
  pub fn buttplug_activate_env_logger(max_level: &str) {
    tracing::subscriber::set_global_default(
      Registry::default()
        //.with(EnvFilter::new(max_level))
        .with(WASMLayer::new(WASMLayerConfig::default())),
    )
    .expect("default global");
  }
}

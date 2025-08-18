#[macro_use]
extern crate tracing;
#[macro_use]
extern crate futures;


mod webbluetooth;
use js_sys;
use tokio_stream::StreamExt;
use buttplug::{
  core::message::{ButtplugServerMessageV4, ButtplugClientMessageV4, ButtplugClientMessageVariant, serializer::vec_to_protocol_json},
  server::ButtplugServer,
  util::async_manager, server::ButtplugServerBuilder, core::message::{ButtplugMessageSpecVersion, serializer::{ButtplugSerializedMessage, ButtplugMessageSerializer, ButtplugServerJSONSerializer}}
};

type FFICallback = js_sys::Function;
type FFICallbackContext = u32;

#[derive(Clone, Copy)]
pub struct FFICallbackContextWrapper(FFICallbackContext);

unsafe impl Send for FFICallbackContextWrapper {
}
unsafe impl Sync for FFICallbackContextWrapper {
}

use console_error_panic_hook;
use tracing_subscriber::{layer::SubscriberExt, Registry};
use tracing_wasm::{WASMLayer, WASMLayerConfig};
use wasm_bindgen::prelude::*;
use std::sync::Arc;
use js_sys::Uint8Array;

pub type ButtplugWASMServer = Arc<ButtplugServer>;

pub fn send_server_message(
  message: &ButtplugServerMessageV4,
  callback: &FFICallback,
) {
  let msg_array = [message.clone()];
  let json_msg = vec_to_protocol_json(&msg_array);
  let buf = json_msg.as_bytes();
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
) -> *mut ButtplugWASMServer {
  console_error_panic_hook::set_once();
  // For now, create a basic server without WebBluetooth
  // TODO: Fix WebBluetooth integration with newer API
  let server = Arc::new(ButtplugServerBuilder::default().finish().unwrap());
  let event_stream = server.event_stream();
  let callback = callback.clone();
  async_manager::spawn(async move {
    pin_mut!(event_stream);
    while let Some(message) = event_stream.next().await {
      send_server_message(&message, &callback);
    }
  });
  
  Box::into_raw(Box::new(server))
}

#[no_mangle]
#[wasm_bindgen]
pub fn buttplug_free_embedded_wasm_server(ptr: *mut ButtplugWASMServer) {
  if !ptr.is_null() {
    unsafe {
      let _ = Box::from_raw(ptr);
    }
  }
}


#[no_mangle]
#[wasm_bindgen]
pub fn buttplug_client_send_json_message(
  server_ptr: *mut ButtplugWASMServer,
  buf: &[u8],
  callback: &FFICallback,
) {
  let server = unsafe {
    assert!(!server_ptr.is_null());
    &mut *server_ptr
  };
  let callback = callback.clone();
  let serializer = ButtplugServerJSONSerializer::default();
  serializer.force_message_version(&ButtplugMessageSpecVersion::Version4);
  let input_msg = serializer.deserialize(&ButtplugSerializedMessage::Text(std::str::from_utf8(buf).unwrap().to_owned())).unwrap();
  async_manager::spawn(async move {
    // Convert to V4 message
    let msg = match &input_msg[0] {
      ButtplugClientMessageVariant::V4(v4_msg) => v4_msg.clone(),
      _ => panic!("Expected V4 message"),
    };
    let response = server.parse_message(msg).await.unwrap();
    send_server_message(&response, &callback);
  });
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

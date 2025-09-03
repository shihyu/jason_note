use super::webbluetooth_hardware::WebBluetoothHardwareConnector;

use buttplug::{
  core::ButtplugResultFuture,
  server::device::{
    configuration::ProtocolCommunicationSpecifier,
    hardware::communication::{
      HardwareCommunicationManager, HardwareCommunicationManagerBuilder,
      HardwareCommunicationManagerEvent,
    },
  },
  // util::device_configuration::create_test_dcm, // Not available in newer version
};
use futures::future;
use js_sys::Array;
use tokio::sync::mpsc::Sender;
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::{spawn_local, JsFuture};
use web_sys::BluetoothDevice;

#[derive(Default)]
pub struct WebBluetoothCommunicationManagerBuilder {
}

impl HardwareCommunicationManagerBuilder for WebBluetoothCommunicationManagerBuilder {
  fn finish(&mut self, sender: Sender<HardwareCommunicationManagerEvent>) -> Box<dyn HardwareCommunicationManager> {
    Box::new(WebBluetoothCommunicationManager {
      sender,
    })
  }
}

pub struct WebBluetoothCommunicationManager {
  sender: Sender<HardwareCommunicationManagerEvent>,
}

#[wasm_bindgen]
extern "C" {
  // Use `js_namespace` here to bind `console.log(..)` instead of just
  // `log(..)`
  #[wasm_bindgen(js_namespace = console)]
  fn log(s: &str);
}

impl HardwareCommunicationManager for WebBluetoothCommunicationManager {
  fn name(&self) -> &'static str {
    "WebBluetoothCommunicationManager"
  }

  fn can_scan(&self) -> bool {
    true
  }

  fn start_scanning(&mut self) -> ButtplugResultFuture {
    info!("WebBluetooth manager scanning");
    let sender_clone = self.sender.clone();
    spawn_local(async move {
      // Build the filter block
      let nav = web_sys::window().unwrap().navigator();
      
      // 詳細記錄 WebBluetooth 支援狀況
      info!("=== WebBluetooth Support Detection ===");
      info!("User Agent: {:?}", nav.user_agent());
      
      if nav.bluetooth().is_none() {
        error!("WebBluetooth is not supported on this browser");
        error!("navigator.bluetooth is undefined or null");
        error!("Browser may be Firefox or Safari without WebBluetooth support");
        error!("Please use Chrome, Edge, or Opera browser");
        
        // 檢查其他可能的 API
        if nav.usb().is_some() {
          info!("WebUSB API is available as alternative");
        }
        if nav.serial().is_some() {
          info!("WebSerial API is available as alternative");
        }
        
        error!("=== WebBluetooth Detection Failed ===");
        return;
      }
      
      info!("WebBluetooth API detected successfully");
      info!("navigator.bluetooth is available");
      info!("WebBluetooth supported by browser, continuing with scan.");
      info!("=== WebBluetooth Detection Successful ===");
      // HACK: As of buttplug v5, we can't just create a HardwareCommunicationManager anymore. This is
      // using a test method to create a filled out DCM, which will work for now because there's no
      // way for anyone to add device configurations through FFI yet anyways.
      // TODO: Fix device configuration manager creation for newer API
      // For now, just create empty options - this means WebBluetooth won't work
      // but at least the WASM will compile
      let mut options = web_sys::RequestDeviceOptions::new();
      let filters = Array::new();
      let optional_services = Array::new();
      
      // Add a generic filter to allow any device
      let mut filter = web_sys::BluetoothLeScanFilterInit::new();
      filters.push(&filter.into());
      
      options.set_filters(&filters.into());
      options.set_optional_services(&optional_services.into());
      let nav = web_sys::window().unwrap().navigator();
      //nav.bluetooth().get_availability();
      //JsFuture::from(nav.bluetooth().request_device()).await;
      match JsFuture::from(nav.bluetooth().unwrap().request_device(&options)).await {
        Ok(device) => {
          let bt_device = BluetoothDevice::from(device);
          if bt_device.name().is_none() {
            return;
          }
          let name = bt_device.name().unwrap();
          let address = bt_device.id();
          let device_creator = Box::new(WebBluetoothHardwareConnector::new(bt_device));
          if sender_clone
            .send(HardwareCommunicationManagerEvent::DeviceFound {
              name,
              address,
              creator: device_creator,
            })
            .await
            .is_err()
          {
            error!("Device manager receiver dropped, cannot send device found message.");
          } else {
            info!("WebBluetooth device found.");
          }
        }
        Err(e) => {
          error!("Error while trying to start bluetooth scan: {:?}", e);
        }
      };
      let _ = sender_clone
        .send(HardwareCommunicationManagerEvent::ScanningFinished)
        .await;
    });
    Box::pin(future::ready(Ok(())))
  }

  fn stop_scanning(&mut self) -> ButtplugResultFuture {
    Box::pin(future::ready(Ok(())))
  }
}

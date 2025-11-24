const s = require('shelljs')

s.cd(__dirname)
s.exec('cargo build --target wasm32-unknown-unknown --release')
s.exec(
  'wasm-bindgen target/wasm32-unknown-unknown/release/wasm_calculator.wasm --out-dir . --target web'
)

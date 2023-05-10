use binance::api::*;
use binance::futures::userstream::*;

fn main() {
    user_stream();
}

fn user_stream() {
    let api_key_user = Some("YOUR_API_KEY".into());
    let user_stream: FuturesUserStream = Binance::new(api_key_user, None);

    if let Ok(answer) = user_stream.start() {
        println!("Data Stream Started ...");
        let listen_key = answer.listen_key;

        match user_stream.keep_alive(&listen_key) {
            Ok(msg) => println!("Keepalive user data stream: {:?}", msg),
            Err(e) => println!("Error: {}", e),
        }

        match user_stream.close(&listen_key) {
            Ok(msg) => println!("Close user data stream: {:?}", msg),
            Err(e) => println!("Error: {}", e),
        }
    } else {
        println!("Not able to start an User Stream (Check your API_KEY)");
    }
}

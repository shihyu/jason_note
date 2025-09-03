use reqwest::{Client, header};
// use std::collection::HashMap;
use std::collections::HashMap;

#[tokio::main]

async fn main(){
    match send().await{
        Ok(()) => (),
        Err(e) => println!("error: {}", e),
    }
}

async fn send() -> Result<(), Box<dyn std::error::Error + Send + Sync>>{
    // let token = "Bearer [your line notify access token]";
    let token = "Bearer KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz";
    // let token = "KXwzqEGtIp1JEkS5GjqXqRAT0D4BdQQvCNcqOa7ySfz";
    let url = "https://notify-api.line.me/api/notify";
    let mess = "testtest";

    let mut message = HashMap::new();
    message.insert("message", mess);

    let mut head = header::HeaderMap::new();
    let token = header::HeaderValue::from_static(token);
    head.insert("Authorization", token);

    let client = Client::new();
    let res = client
        .post(url)
        .headers(head)
        .form(&message)
        .send()
        .await?;

    println!("Status is {:?}", res.status());

    Ok(())
}

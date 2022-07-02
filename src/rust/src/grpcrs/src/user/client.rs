use user::user_client::UserClient;
use user::HelloRequest;

pub mod user {
    tonic::include_proto!("user");
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = UserClient::connect("http://127.0.0.1:50051").await?;

    let request = tonic::Request::new(HelloRequest {
        name: "Rick".into(),
    });

    let response = client.hello(request).await?;

    println!("RESPONSE={:?}", response);

    Ok(())
}

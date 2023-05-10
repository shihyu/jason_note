use tonic::{transport::Server, Request, Response, Status};

use user::user_server::{User, UserServer};
use user::{HelloReply, HelloRequest};

pub mod user {
    tonic::include_proto!("user");
}

#[derive(Default)]
pub struct UserService {}

#[tonic::async_trait]
impl User for UserService {
    async fn hello(&self, request: Request<HelloRequest>) -> Result<Response<HelloReply>, Status> {
        println!("New user request from {:?}", request.remote_addr());

        let reply = user::HelloReply {
            message: format!("Hello {}!", request.into_inner().name),
        };
        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "127.0.0.1:50051".parse().unwrap();
    let user_service = UserService::default();

    println!("UserService listening on {}", addr);

    Server::builder()
        .add_service(UserServer::new(user_service))
        .serve(addr)
        .await?;

    Ok(())
}

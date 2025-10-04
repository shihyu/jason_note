pub struct MyRequest {
    pub name: String,
    pub age: u8,
}

pub struct MyResponse {
    pub pass: bool,
}

pub trait ApiCall {
    fn check(req: &MyRequest) -> MyResponse;
}
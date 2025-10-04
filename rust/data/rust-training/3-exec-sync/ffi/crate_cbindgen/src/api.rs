#[repr(u8)]
enum Ammo {
    Rock,
    WaterBalloon,
    Cow,
}

#[repr(C)]
struct Target {
    latitude: f64,
    longitude: f64,
}

// notice: #[repr(rust)]
struct Trebuchet {
}

#[no_mangle]
unsafe extern "C" fn trebuchet_new() -> *mut Trebuchet { ... }

#[no_mangle]
unsafe extern "C" fn trebuchet_delete(treb: *mut Trebuchet) { ... }

#[no_mangle]
unsafe extern "C" fn trebuchet_fire(treb: *mut Trebuchet,
                                    ammo: Ammo,
                                    target: Target) { ... }

#[repr(C)]
pub struct MyRequest {
    pub name: String,
    pub age: u8,
}

#[repr(C)]
pub struct MyResponse {
    pub pass: bool,
}

pub trait ApiCall {
    fn check(req: &MyRequest) -> MyResponse;
}

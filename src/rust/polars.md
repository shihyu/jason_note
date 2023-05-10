##  join with Dataframe

```rust
use polars::df;
use polars::prelude::*;

fn join_test() -> Result<DataFrame, PolarsError> {
    let df1: DataFrame = df!("Wavelength (nm)" => &[480.0, 650.0, 577.0, 1201.0, 100.0])?;
    let df2: DataFrame = df!("Color" => &["Blue", "Yellow", "Red"],
                         "Wavelength nm" => &[480.0, 577.0, 650.0])?;

    let df3: DataFrame = df1.left_join(&df2, ["Wavelength (nm)"], ["Wavelength nm"])?;
    // println!("{:?}", df3);
    Ok(df3)
}

fn main() {
    let df = join_test();
    println!("{:#?}", df)
    // match join_test() {
    //     Ok(df) => println!("DataFrame: {:#?}", df),
    //     Err(e) => println!("Error: {}", e),
    // }
}
```

```toml
[package]
name = "polars_test"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
polars = { version = "0.27.2", features = ["json"] }
```


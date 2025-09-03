use reqwest::blocking::Client;
use reqwest::Url;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();
    let url = Url::parse("https://finance.yahoo.com/quote/AAPL/history?p=AAPL")?;

    let response = client.get(url).send()?;
    let text = response.text()?;

    println!("{}", text);
    Ok(())
}

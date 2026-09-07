pub fn calculate_discount(price: f64, is_member: bool) -> Result<f64, String> {
    if price < 0.0 {
        return Err("price must be non-negative".to_string());
    }
    if is_member {
        return Ok(price * 0.8);
    }
    Ok(price)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn member_gets_20_percent_off() {
        assert_eq!(calculate_discount(100.0, true), Ok(80.0));
    }

    #[test]
    fn non_member_pays_full_price() {
        assert_eq!(calculate_discount(100.0, false), Ok(100.0));
    }

    #[test]
    fn negative_price_returns_error() {
        assert!(calculate_discount(-1.0, true).is_err());
    }
}

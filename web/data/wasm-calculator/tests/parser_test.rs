// 測試表達式解析器的基本功能

#[cfg(test)]
mod tests {
    use wasm_calculator::parser::{tokenize, parse, Token};

    #[test]
    fn test_tokenize_numbers() {
        let tokens = tokenize("123");
        assert_eq!(tokens.len(), 1);
        assert!(matches!(tokens[0], Token::Number(123.0)));
    }

    #[test]
    fn test_tokenize_decimal() {
        let tokens = tokenize("3.14");
        assert_eq!(tokens.len(), 1);
        assert!(matches!(tokens[0], Token::Number(n) if (n - 3.14).abs() < 0.001));
    }

    #[test]
    fn test_tokenize_operators() {
        let tokens = tokenize("+-*/");
        assert_eq!(tokens.len(), 4);
        assert!(matches!(tokens[0], Token::Plus));
        assert!(matches!(tokens[1], Token::Minus));
        assert!(matches!(tokens[2], Token::Multiply));
        assert!(matches!(tokens[3], Token::Divide));
    }

    #[test]
    fn test_tokenize_simple_expression() {
        let tokens = tokenize("2+3");
        assert_eq!(tokens.len(), 3);
        assert!(matches!(tokens[0], Token::Number(2.0)));
        assert!(matches!(tokens[1], Token::Plus));
        assert!(matches!(tokens[2], Token::Number(3.0)));
    }

    #[test]
    fn test_tokenize_with_spaces() {
        let tokens = tokenize("2 + 3 * 4");
        assert_eq!(tokens.len(), 5);
    }

    #[test]
    fn test_parse_simple_addition() {
        let result = parse("2+3");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 5.0);
    }

    #[test]
    fn test_parse_simple_subtraction() {
        let result = parse("10-3");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 7.0);
    }

    #[test]
    fn test_parse_simple_multiplication() {
        let result = parse("4*5");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 20.0);
    }

    #[test]
    fn test_parse_simple_division() {
        let result = parse("15/3");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 5.0);
    }

    #[test]
    fn test_tokenize_parentheses() {
        let tokens = tokenize("(2+3)*4");
        assert_eq!(tokens.len(), 7);
        assert!(matches!(tokens[0], Token::LeftParen));
        assert!(matches!(tokens[4], Token::RightParen));
    }

    #[test]
    fn test_parse_with_parentheses() {
        let result = parse("(2+3)*4");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 20.0);
    }

    #[test]
    fn test_parse_nested_parentheses() {
        let result = parse("((2+3)*4)-10");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 10.0);
    }

    #[test]
    fn test_parse_operator_precedence() {
        // 乘法優先於加法
        let result = parse("2+3*4");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 14.0);
    }

    #[test]
    fn test_parse_precedence_with_parentheses() {
        // 括號改變優先順序
        let result1 = parse("2+3*4");
        let result2 = parse("(2+3)*4");
        assert!(result1.is_ok() && result2.is_ok());
        assert_eq!(result1.unwrap(), 14.0);
        assert_eq!(result2.unwrap(), 20.0);
    }

    #[test]
    fn test_parse_complex_expression() {
        let result = parse("(10-2)*(3+4)/2");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 28.0);
    }

    #[test]
    fn test_parse_negative_numbers() {
        let result = parse("-5+3");
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), -2.0);
    }

    // 錯誤處理測試
    #[test]
    fn test_error_division_by_zero() {
        let result = parse("10/0");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Error: Division by zero");
    }

    #[test]
    fn test_error_missing_closing_paren() {
        let result = parse("(2+3");
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("parenthesis"));
    }

    #[test]
    fn test_error_empty_expression() {
        let result = parse("");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Empty expression");
    }

    #[test]
    fn test_error_invalid_expression() {
        let result = parse("++");
        assert!(result.is_err());
    }

    #[test]
    fn test_error_incomplete_expression() {
        let result = parse("2+");
        assert!(result.is_err());
    }
}

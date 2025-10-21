// 表達式解析器模組
// 負責將字串表達式解析為 tokens 並計算結果

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Number(f64),
    Plus,
    Minus,
    Multiply,
    Divide,
    LeftParen,
    RightParen,
    Percent,
}

/// 詞法分析器：將字串轉換為 Token 序列
pub fn tokenize(input: &str) -> Vec<Token> {
    let mut tokens = Vec::new();
    let mut chars = input.chars().peekable();

    while let Some(&ch) = chars.peek() {
        match ch {
            ' ' | '\t' | '\n' => {
                chars.next();
            }
            '0'..='9' | '.' => {
                let mut number = String::new();
                while let Some(&ch) = chars.peek() {
                    if ch.is_ascii_digit() || ch == '.' {
                        number.push(ch);
                        chars.next();
                    } else {
                        break;
                    }
                }
                if let Ok(num) = number.parse::<f64>() {
                    tokens.push(Token::Number(num));
                }
            }
            '+' => {
                tokens.push(Token::Plus);
                chars.next();
            }
            '-' => {
                tokens.push(Token::Minus);
                chars.next();
            }
            '*' | '×' => {
                tokens.push(Token::Multiply);
                chars.next();
            }
            '/' | '÷' => {
                tokens.push(Token::Divide);
                chars.next();
            }
            '(' => {
                tokens.push(Token::LeftParen);
                chars.next();
            }
            ')' => {
                tokens.push(Token::RightParen);
                chars.next();
            }
            '%' => {
                tokens.push(Token::Percent);
                chars.next();
            }
            _ => {
                // 忽略未知字元
                chars.next();
            }
        }
    }

    tokens
}

/// 語法分析器：解析並計算表達式
pub fn parse(input: &str) -> Result<f64, String> {
    let tokens = tokenize(input);
    if tokens.is_empty() {
        return Err("Empty expression".to_string());
    }

    let mut pos = 0;
    parse_expression(&tokens, &mut pos)
}

/// 解析表達式（處理加法和減法，優先級最低）
fn parse_expression(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_term(tokens, pos)?;

    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Plus => {
                *pos += 1;
                let right = parse_term(tokens, pos)?;
                left += right;
            }
            Token::Minus => {
                *pos += 1;
                let right = parse_term(tokens, pos)?;
                left -= right;
            }
            _ => break,
        }
    }

    Ok(left)
}

/// 解析項（處理乘法和除法，優先級較高）
fn parse_term(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    let mut left = parse_factor(tokens, pos)?;

    while *pos < tokens.len() {
        match tokens[*pos] {
            Token::Multiply => {
                *pos += 1;
                let right = parse_factor(tokens, pos)?;
                left *= right;
            }
            Token::Divide => {
                *pos += 1;
                let right = parse_factor(tokens, pos)?;
                if right == 0.0 {
                    return Err("Error: Division by zero".to_string());
                }
                left /= right;
            }
            _ => break,
        }
    }

    Ok(left)
}

/// 解析因子（處理數字和括號，優先級最高）
fn parse_factor(tokens: &[Token], pos: &mut usize) -> Result<f64, String> {
    if *pos >= tokens.len() {
        return Err("Unexpected end of expression".to_string());
    }

    match &tokens[*pos] {
        Token::Number(n) => {
            let value = *n;
            *pos += 1;
            Ok(value)
        }
        Token::LeftParen => {
            *pos += 1;
            let value = parse_expression(tokens, pos)?;
            if *pos >= tokens.len() || !matches!(tokens[*pos], Token::RightParen) {
                return Err("Missing closing parenthesis".to_string());
            }
            *pos += 1;
            Ok(value)
        }
        Token::Minus => {
            // 處理負數
            *pos += 1;
            let value = parse_factor(tokens, pos)?;
            Ok(-value)
        }
        _ => Err("Invalid expression".to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tokenize_basic() {
        let tokens = tokenize("2+3");
        assert_eq!(tokens.len(), 3);
    }

    #[test]
    fn test_parse_basic() {
        assert_eq!(parse("2+3").unwrap(), 5.0);
        assert_eq!(parse("10-3").unwrap(), 7.0);
        assert_eq!(parse("4*5").unwrap(), 20.0);
        assert_eq!(parse("15/3").unwrap(), 5.0);
    }

    #[test]
    fn test_operator_precedence() {
        assert_eq!(parse("2+3*4").unwrap(), 14.0);
        assert_eq!(parse("10-2*3").unwrap(), 4.0);
    }
}

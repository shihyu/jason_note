// 計算機核心邏輯模組
use crate::parser::parse;

/// 計算機狀態結構
pub struct Calculator {
    expression: String,        // 當前表達式
    display: String,          // 顯示內容
    memory: Option<f64>,      // 記憶值
    error: Option<String>,    // 錯誤訊息
    last_result: Option<f64>, // 上次計算結果
}

impl Calculator {
    /// 建立新的計算機實例
    pub fn new() -> Self {
        Calculator {
            expression: String::new(),
            display: String::from("0"),
            memory: None,
            error: None,
            last_result: None,
        }
    }

    /// 輸入字元（數字、運算符、括號等）
    pub fn input(&mut self, input: &str) {
        // 清除錯誤狀態
        self.error = None;

        // 如果是新的計算（上次已經按過 =）
        if self.last_result.is_some() && input.chars().all(|c| c.is_ascii_digit()) {
            // 如果輸入數字，開始新的計算
            self.expression.clear();
            self.display.clear();
            self.last_result = None;
        }

        // 處理輸入
        match input {
            "+" | "-" | "*" | "/" | "×" | "÷" | "(" | ")" | "%" => {
                // 運算符
                if !self.display.is_empty() && self.display != "0" {
                    self.expression.push_str(&self.display);
                    self.display.clear();
                }
                self.expression.push_str(input);
                self.last_result = None;
            }
            "." => {
                // 小數點
                if !self.display.contains('.') {
                    if self.display.is_empty() || self.display == "0" {
                        self.display = String::from("0.");
                    } else {
                        self.display.push('.');
                    }
                }
            }
            _ if input.chars().all(|c| c.is_ascii_digit()) => {
                // 數字
                if self.display == "0" {
                    self.display = input.to_string();
                } else {
                    self.display.push_str(input);
                }
            }
            _ => {
                // 其他字元忽略
            }
        }
    }

    /// 執行計算
    pub fn calculate(&mut self) {
        // 將當前顯示加入表達式
        if !self.display.is_empty() && self.display != "0" {
            self.expression.push_str(&self.display);
        }

        if self.expression.is_empty() {
            return;
        }

        // 解析並計算表達式
        match parse(&self.expression) {
            Ok(result) => {
                self.display = format_result(result);
                self.last_result = Some(result);
                self.expression.clear();
                self.error = None;
            }
            Err(err) => {
                self.error = Some(err.clone());
                self.display = err;
            }
        }
    }

    /// 清除當前輸入（CE）
    pub fn clear(&mut self) {
        self.display = String::from("0");
        self.error = None;
    }

    /// 清除全部（C）
    pub fn clear_all(&mut self) {
        self.expression.clear();
        self.display = String::from("0");
        self.error = None;
        self.last_result = None;
    }

    /// 取得主顯示內容
    pub fn get_display(&self) -> &str {
        &self.display
    }

    /// 取得當前表達式
    pub fn get_expression(&self) -> &str {
        &self.expression
    }

    /// 檢查是否有錯誤
    pub fn has_error(&self) -> bool {
        self.error.is_some()
    }

    /// 取得錯誤訊息
    pub fn get_error(&self) -> String {
        self.error.clone().unwrap_or_default()
    }

    /// 清除記憶（MC）
    pub fn memory_clear(&mut self) {
        self.memory = None;
    }

    /// 讀取記憶（MR）
    pub fn memory_recall(&mut self) {
        if let Some(val) = self.memory {
            self.display = format_result(val);
            self.expression.clear();
            self.last_result = None;
        }
    }

    /// 加到記憶（M+）
    pub fn memory_add(&mut self) {
        if let Ok(val) = self.display.parse::<f64>() {
            self.memory = Some(self.memory.unwrap_or(0.0) + val);
        }
    }

    /// 從記憶減去（M-）
    pub fn memory_subtract(&mut self) {
        if let Ok(val) = self.display.parse::<f64>() {
            self.memory = Some(self.memory.unwrap_or(0.0) - val);
        }
    }

    /// 檢查是否有記憶值
    pub fn has_memory(&self) -> bool {
        self.memory.is_some()
    }
}

/// 格式化結果，移除不必要的小數點
fn format_result(value: f64) -> String {
    if value.fract() == 0.0 && value.abs() < 1e10 {
        format!("{:.0}", value)
    } else {
        // 限制小數位數
        let formatted = format!("{:.10}", value);
        // 移除尾部的零
        formatted.trim_end_matches('0').trim_end_matches('.').to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_result() {
        assert_eq!(format_result(5.0), "5");
        assert_eq!(format_result(3.14), "3.14");
        assert_eq!(format_result(2.5), "2.5");
    }

    #[test]
    fn test_calculator_basic() {
        let mut calc = Calculator::new();
        calc.input("2");
        calc.input("+");
        calc.input("3");
        calc.calculate();
        assert_eq!(calc.get_display(), "5");
    }
}


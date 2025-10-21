// 測試計算機核心功能

#[cfg(test)]
mod tests {
    use wasm_calculator::Calculator;

    #[test]
    fn test_new_calculator() {
        let calc = Calculator::new();
        assert_eq!(calc.get_display(), "0");
        assert_eq!(calc.get_expression(), "");
    }

    #[test]
    fn test_input_numbers() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("2");
        calc.input("3");
        assert_eq!(calc.get_display(), "123");
    }

    #[test]
    fn test_simple_addition() {
        let mut calc = Calculator::new();
        calc.input("2");
        calc.input("+");
        calc.input("3");
        calc.calculate();
        assert_eq!(calc.get_display(), "5");
    }

    #[test]
    fn test_simple_subtraction() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("0");
        calc.input("-");
        calc.input("3");
        calc.calculate();
        assert_eq!(calc.get_display(), "7");
    }

    #[test]
    fn test_simple_multiplication() {
        let mut calc = Calculator::new();
        calc.input("4");
        calc.input("*");
        calc.input("5");
        calc.calculate();
        assert_eq!(calc.get_display(), "20");
    }

    #[test]
    fn test_simple_division() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("5");
        calc.input("/");
        calc.input("3");
        calc.calculate();
        assert_eq!(calc.get_display(), "5");
    }

    #[test]
    fn test_clear() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("2");
        calc.input("3");
        calc.clear();
        assert_eq!(calc.get_display(), "0");
    }

    #[test]
    fn test_clear_all() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("+");
        calc.input("2");
        calc.clear_all();
        assert_eq!(calc.get_display(), "0");
        assert_eq!(calc.get_expression(), "");
    }

    #[test]
    fn test_decimal_point() {
        let mut calc = Calculator::new();
        calc.input("3");
        calc.input(".");
        calc.input("1");
        calc.input("4");
        assert_eq!(calc.get_display(), "3.14");
    }

    #[test]
    fn test_expression_display() {
        let mut calc = Calculator::new();
        calc.input("2");
        calc.input("+");
        calc.input("3");
        assert!(calc.get_expression().contains("2"));
        assert!(calc.get_expression().contains("+"));
    }

    #[test]
    fn test_consecutive_operations() {
        let mut calc = Calculator::new();
        calc.input("2");
        calc.input("+");
        calc.input("3");
        calc.calculate();
        calc.input("+");
        calc.input("4");
        calc.calculate();
        assert_eq!(calc.get_display(), "9");
    }

    #[test]
    fn test_parentheses() {
        let mut calc = Calculator::new();
        calc.input("(");
        calc.input("2");
        calc.input("+");
        calc.input("3");
        calc.input(")");
        calc.input("*");
        calc.input("4");
        calc.calculate();
        assert_eq!(calc.get_display(), "20");
    }

    #[test]
    fn test_error_division_by_zero() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("0");
        calc.input("/");
        calc.input("0");
        calc.calculate();
        assert!(calc.has_error());
        assert!(
            calc.get_error().contains("Division by zero")
                || calc.get_display().contains("Division by zero")
        );
    }

    // 記憶功能測試
    #[test]
    fn test_memory_clear() {
        let mut calc = Calculator::new();
        calc.input("5");
        calc.memory_add();
        assert!(calc.has_memory());
        calc.memory_clear();
        assert!(!calc.has_memory());
    }

    #[test]
    fn test_memory_add() {
        let mut calc = Calculator::new();
        calc.input("5");
        calc.memory_add();
        calc.clear();
        calc.input("3");
        calc.memory_add();
        calc.memory_recall();
        assert_eq!(calc.get_display(), "8");
    }

    #[test]
    fn test_memory_subtract() {
        let mut calc = Calculator::new();
        calc.input("1");
        calc.input("0");
        calc.memory_add();
        calc.clear();
        calc.input("3");
        calc.memory_subtract();
        calc.memory_recall();
        assert_eq!(calc.get_display(), "7");
    }

    #[test]
    fn test_memory_recall() {
        let mut calc = Calculator::new();
        calc.input("4");
        calc.input("2");
        calc.memory_add();
        calc.clear_all();
        calc.memory_recall();
        assert_eq!(calc.get_display(), "42");
    }
}

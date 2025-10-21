// WASM Calculator 主程式

use wasm_bindgen::prelude::*;
use web_sys::{window, Document, Element, HtmlElement};

pub mod calculator;
pub mod parser;

// 重新導出主要公開 API
pub use calculator::Calculator;
pub use parser::{parse, tokenize, Token};

// 全局計算機實例
use std::cell::RefCell;
thread_local! {
    static CALCULATOR: RefCell<Calculator> = RefCell::new(Calculator::new());
}

/// WASM 主入口函數
#[wasm_bindgen]
pub fn main() -> Result<(), JsValue> {
    let window = window().expect("no global `window` exists");
    let document = window.document().expect("should have a document on window");
    let body = document.body().expect("document should have a body");

    // 建立計算機 UI
    create_calculator_ui(&document, &body)?;

    Ok(())
}

/// 建立計算機 UI
fn create_calculator_ui(document: &Document, body: &HtmlElement) -> Result<(), JsValue> {
    // 建立容器
    let container = document.create_element("div")?;
    container.set_id("calculator");

    // 建立顯示區
    let display_container = document.create_element("div")?;
    display_container.set_class_name("display-container");

    let expression_display = document.create_element("div")?;
    expression_display.set_id("expression");
    expression_display.set_class_name("expression");
    expression_display.set_inner_html("");

    let main_display = document.create_element("div")?;
    main_display.set_id("display");
    main_display.set_class_name("display");
    main_display.set_inner_html("0");

    let memory_indicator = document.create_element("div")?;
    memory_indicator.set_id("memory");
    memory_indicator.set_class_name("memory");
    memory_indicator.set_inner_html("");

    display_container.append_child(&expression_display)?;
    display_container.append_child(&main_display)?;
    display_container.append_child(&memory_indicator)?;

    container.append_child(&display_container)?;

    // 建立按鈕區
    let buttons_container = document.create_element("div")?;
    buttons_container.set_class_name("buttons");

    // 按鈕布局
    let button_layout = vec![
        vec!["MC", "MR", "M+", "M-"],
        vec!["C", "CE", "(", ")"],
        vec!["7", "8", "9", "/"],
        vec!["4", "5", "6", "*"],
        vec!["1", "2", "3", "-"],
        vec!["0", ".", "=", "+"],
    ];

    for row in button_layout {
        for btn_text in row {
            create_button(document, &buttons_container, btn_text)?;
        }
    }

    container.append_child(&buttons_container)?;
    body.append_child(&container)?;

    // 添加樣式
    add_styles(document)?;

    Ok(())
}

/// 建立按鈕
fn create_button(document: &Document, parent: &Element, text: &str) -> Result<(), JsValue> {
    let button = document.create_element("button")?;
    button.set_class_name("btn");

    // 特殊按鈕樣式
    match text {
        "=" => button.set_class_name("btn btn-equals"),
        "C" | "CE" => button.set_class_name("btn btn-clear"),
        "+" | "-" | "*" | "/" => button.set_class_name("btn btn-operator"),
        "MC" | "MR" | "M+" | "M-" => button.set_class_name("btn btn-memory"),
        _ => {}
    }

    button.set_inner_html(text);
    button.set_attribute("onclick", &format!("handle_button('{}')", text))?;

    parent.append_child(&button)?;
    Ok(())
}

/// 處理按鈕點擊
#[wasm_bindgen]
pub fn handle_button(input: &str) {
    CALCULATOR.with(|calc| {
        let mut calc = calc.borrow_mut();

        match input {
            "=" => calc.calculate(),
            "C" => calc.clear_all(),
            "CE" => calc.clear(),
            "MC" => calc.memory_clear(),
            "MR" => calc.memory_recall(),
            "M+" => calc.memory_add(),
            "M-" => calc.memory_subtract(),
            _ => calc.input(input),
        }

        update_display();
    });
}

/// 更新顯示
fn update_display() {
    CALCULATOR.with(|calc| {
        let calc = calc.borrow();

        if let Some(window) = window() {
            if let Some(document) = window.document() {
                // 更新主顯示
                if let Some(display) = document.get_element_by_id("display") {
                    display.set_inner_html(calc.get_display());
                }

                // 更新表達式顯示
                if let Some(expr) = document.get_element_by_id("expression") {
                    expr.set_inner_html(calc.get_expression());
                }

                // 更新記憶指示器
                if let Some(mem) = document.get_element_by_id("memory") {
                    if calc.has_memory() {
                        mem.set_inner_html("M");
                    } else {
                        mem.set_inner_html("");
                    }
                }
            }
        }
    });
}

/// 添加 CSS 樣式
fn add_styles(document: &Document) -> Result<(), JsValue> {
    let style = document.create_element("style")?;
    style.set_inner_html(include_str!("../style.css"));

    // 將樣式添加到 head
    if let Ok(Some(head)) = document.query_selector("head") {
        head.append_child(&style)?;
    }

    Ok(())
}

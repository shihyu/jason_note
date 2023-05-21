# 訪問者模式

## 雙重分發 

accept 調用方法是 element.accept(visitor)

visit調用方法是visitor.visit(element)

## 將處理算法從數據結構中分離出來

易於增加Visitor

難以增加Element

Element必須向Visitor公開足夠的信息
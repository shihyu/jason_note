# 對象的適配器模式

Painter為要適配的對象

Banner為適配者

PainterBanner是適配器。

適配器繼承了Painter接口，內部聚合了一個Banner對象，利用Banner已有的功能 實現Painter的接口
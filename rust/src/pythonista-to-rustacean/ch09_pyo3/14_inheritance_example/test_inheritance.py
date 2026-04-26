from inheritance_example import *

pizza = Pizza("夏威夷", "8")
print(pizza.description())

margherita = MargheritaPizza("瑪格麗特", "12", False)
print("瑪格麗特也具有 .consume() 這個繼承自 Pizza 的方法")
margherita.consume()
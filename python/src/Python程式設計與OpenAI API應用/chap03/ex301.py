class Person:
    def __init__(self, name, age):        
        self.name = name
        self.age = age

    def greet(self):
        print(f"Hello, My name is {self.name}, My age is {self.age}")

    def __str__(self):
        return f"Person({self.name}, {self.age})"

p1 = Person("John", 36)
print(p1.name)
print(p1.age)
p1.greet()
print(p1)

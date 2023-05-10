# Returning Pointer from a Function in Go



Pointers in Go programming language or Golang is a variable which is used to store the memory address of another variable. We can pass pointers to the function as well as return pointer from a function in Golang. In [C](https://www.geeksforgeeks.org/c-programming-language/)/[C++](https://www.geeksforgeeks.org/c-plus-plus/), it is not recommended to return the address of a local variable outside the function as it goes out of scope after function returns. So to execute the concept of returning a pointer from function in C/C++ you must define the local variable as a static variable.

**Example:** In the below program, the line of code(*int lv = n1 \* n1;*) will give warning as it is local to the function. To avoid warnings make it static.



```cpp
// C++ program to return the
// pointer from a function
#include <iostream>
using namespace std;
  
// taking a function having
// pointer as return type
int* rpf(int);
  
int main()
{
  
    int n = 745;
  
    // displaying the value of n
    cout << n << endl;
  
    // calling the function
    cout << *rpf(n) << endl;
}
  
// defining function
int* rpf(int n1)
{
  
    // taking a local variable
    // inside the function
    int lv = n1 * n1;
  
    // remove comment or make the above
    // declaration as static which
    // result into successful
    // compilation
    // static int lv = n1 * n1;
  
    // this will give warning as we
    // are returning the address of
    // the local variable
    return &lv;
}
```

**Output:**

```
745
```

The main reason behind this scenario is that compiler always make a stack for a function call. As soon as the function exits the function stack also get removed which causes the local variables of functions goes out of scope. Making it static will resolve the problem. As static variables have a property of preserving their value even after they are out of their scope.

But the **Go compiler is very Intelligent!**. It will not allocate the memory on the stack to the local variable of the function. It will allocate this variable on the heap. In the below program, variable *lv* will have the memory allocated on the **heap** as Go compiler will perform escape analysis to escape the variable from the local scope.

**Example:**

```go
 Go program to return the
// pointer from the function
package main
  
import "fmt"
  
// main function
func main() {
  
    // calling the function
    n := rpf()
  
    // displaying the value
    fmt.Println("Value of n is: ", *n)
  
}
  
// defining function having integer
// pointer as return type
func rpf() *int {
  
    // taking a local variable
    // inside the function
    // using short declaration
    // operator
    lv := 100
  
    // returning the address of lv
    return &lv
}
```

**Output:**

```
Value of n is:  100
```

**Note:** Golang doesn’t provide any support for the pointer arithmetic like C/C++. If you will perform then the compiler will throw an error as invalid operation.
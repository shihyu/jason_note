## map[string]interface操作

```go
package main

import "fmt"

func main() {
    datalist := make(map[string]interface{}, 0)
	fmt.Println(datalist)

	data := []string{"test1", "test2", "test3"}

	for _, name := range data {
		datalist[name] = true
	}

	fmt.Println(datalist)
}
```


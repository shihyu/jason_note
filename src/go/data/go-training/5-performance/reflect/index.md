壓測命令
```shell
$ go test -cpu=1 -benchtime=2s -benchmem -bench .
```

壓測數據
```shell
goos: darwin
goarch: arm64
pkg: go-training/5-performance/reflect
BenchmarkSet        	1000000000	         0.2544 ns/op	       
BenchmarkReflectSet 	16516573	       146.6 ns/op	     
PASS
ok  	go-training/5-performance/reflect	3.574s
```
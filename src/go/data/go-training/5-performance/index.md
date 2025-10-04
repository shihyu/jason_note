
# go benchmark用法
go bench 的各個參數
- -cpu：指定使用的 GOMAXPROCS，例如 2
- -benchtime：指定為時間長度（ 5s ），或者是次數（ 50x ）
- -count：指定 benchmark 的輪數，例如 3
- -benchmem：指定查看訪存大小、申請內存次數

各個壓測實例如下
```sh
go test -bench .
go test -cpu=2,4 -bench .
go test -cpu=1 -benchtime=5s -bench .
go test -cpu=1 -benchtime=2s -benchmem -bench .
```

# 各個壓測實驗
- [內存對齊性能優勢](align/main.go)
- [range循環性能壓測](range/main.go)
- [reflect反射性能壓測](reflect/main.go)
- [slice切片預留容量性能壓測](reflect/main.go)
- [各種字符串拼接方法性能對比](string/main.go)
- [fmt.Sprintf和strcov.FormatInt轉字符串性能對比](sprintf/main.go)
- [Golang之內存池優化](syncpool/main.go)

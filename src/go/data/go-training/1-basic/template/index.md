簡單來說分為兩步

### 解析模板
可以從字符串中解析，也可以從文件中解析，一般來說文件解析更為常用！

```golang
tmpl, err := template.ParseFiles("1-basic/template/hello.tpl")
```
### 渲染模板
解析完模板以後，就可以把變量傳入模板中，開始渲染了。
```golang
sweaters := Service{"TestNamespace", "MyApp", "Func1"}
err = tmpl.Execute(os.Stdout, sweaters)
```

參考： 
- [go標準庫的學習-text/template ](https://www.cnblogs.com/wanghui-garcia/p/10385062.html)
- [Go template高級用法](https://cloud.tencent.com/developer/article/1683688)  

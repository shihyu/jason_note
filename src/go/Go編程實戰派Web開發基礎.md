### Web開發基礎

- [第2章 Go Web開發基礎](https://blog.csdn.net/oqqyx1234567/article/details/120101351#2_Go_Web_2)
- - [2.1 helloWorldWeb](https://blog.csdn.net/oqqyx1234567/article/details/120101351#21_helloWorldWeb_4)
  - [2.2 Web程序運行原理簡介](https://blog.csdn.net/oqqyx1234567/article/details/120101351#22_Web_28)
  - - [2.2.1 Web基本原理](https://blog.csdn.net/oqqyx1234567/article/details/120101351#221_Web_29)
    - [2.2.2 HTTP簡介](https://blog.csdn.net/oqqyx1234567/article/details/120101351#222_HTTP_43)
    - [2.2.3 HTTP請求](https://blog.csdn.net/oqqyx1234567/article/details/120101351#223_HTTP_46)
    - [2.2.4 HTTP響應](https://blog.csdn.net/oqqyx1234567/article/details/120101351#224_HTTP_83)
    - [2.2.5 URI與URL](https://blog.csdn.net/oqqyx1234567/article/details/120101351#225_URIURL_155)
    - [2.2.6 HTTPS簡介](https://blog.csdn.net/oqqyx1234567/article/details/120101351#226_HTTPS_172)
    - [2.2.7 HTTP2簡介](https://blog.csdn.net/oqqyx1234567/article/details/120101351#227_HTTP2_176)
    - [2.2.8 Web應用程序的組成](https://blog.csdn.net/oqqyx1234567/article/details/120101351#228_Web_193)
  - [2.3 net/http包](https://blog.csdn.net/oqqyx1234567/article/details/120101351#23_nethttp_237)
  - - [2.3.1 創建簡單服務器端](https://blog.csdn.net/oqqyx1234567/article/details/120101351#231__238)
    - [2.3.2 創建簡單的客戶端](https://blog.csdn.net/oqqyx1234567/article/details/120101351#232__342)
  - [2.4 html/template包](https://blog.csdn.net/oqqyx1234567/article/details/120101351#24_htmltemplate_496)
  - - [2.4.1 模板原理](https://blog.csdn.net/oqqyx1234567/article/details/120101351#241__498)
    - [2.4.2 使用html/template包](https://blog.csdn.net/oqqyx1234567/article/details/120101351#242_htmltemplate_537)



# 第2章 Go Web開發基礎

## 2.1 helloWorldWeb

```go
//helloWorldWeb.go
//go run helloWorldWeb.go
//127.0.0.1
package main
import (
	"fmt"
	"net/http"
)

func hello(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello World")
}

func main() {
	server := &http.Server {
		Addr: "0.0.0.0:80",
	}
	http.HandleFunc("/", hello)
	server.ListenAndServe()
}
```

## 2.2 Web程序運行原理簡介

### 2.2.1 Web基本原理

1. 運行原理
   （1）用戶打開客戶端瀏覽器，輸入URL地址。
   （2）客戶端瀏覽器通過HTTP協議向服務器端發送瀏覽請求。
   （3）服務器端通過CGI程序接收請求，調用解釋引擎處理“動態內容”，訪問數據庫並處理數據，通過HTTP協議將得到的處理結果返回給客戶端瀏覽器。
   （4）客戶端瀏覽器解釋並顯示HTML頁面。
2. DNS（Domain Name System，域名系統）
   將主機名和域名轉換為IP地址。
   DNS解析過程：
   （1）用戶打開瀏覽器，輸入URL地址。瀏覽器從URL中抽取域名（主機名），傳給DNS應用程序的客戶端。
   （2）DNS客戶端向DNS服務器端發送查詢報文，其中包含主機名。
   （3）DNS服務器端向DNS客戶端發送回答報文，其中包含該主機名對應IP地址。
   （4）瀏覽器收到DNS的IP地址後，向該IP地址定位的HTTP服務器端發起TCP連接。

### 2.2.2 HTTP簡介

HTTP（Hyper Text Transfer Protocal，超文本傳輸協議），簡單請求-響應協議，運行在TCP協議上，無狀態。它指定客戶端發送給服務器端的消息和得到的響應。請求和響應消息頭是ASCII碼；消息內容則類似MIME格式。

### 2.2.3 HTTP請求

客戶端發送到服務器端的請求消息。

1. 請求行（Request Line）

請求方法、URI、HTTP協議/協議版本組成。

| 請求方法 | 方法描述                                                     |
| -------- | ------------------------------------------------------------ |
| GET      | 請求頁面，並返回頁面內容，請求參數包含在URL中，提交數據最多1024byte |
| HEAD     | 類似GET，只獲取報頭                                          |
| POST     | 提交表單或上傳文件，數據（含請求參數）包含在請求體中         |
| PUT      | 取代指定內容的文檔                                           |
| DELETE   | 刪除指定資源                                                 |
| OPTIONS  | 查看服務器的性能                                             |
| CONNECT  | 服務器當作跳板，訪問其他網頁                                 |
| TRACE    | 回顯服務器收到的請求，用於測試或診斷                         |

1. 請求頭（Request Header）

| 請求頭          | 示例                                          | 說明                                    |
| --------------- | --------------------------------------------- | --------------------------------------- |
| Accept          | Accept: text/plain, text/html                 | 客戶端能夠接收的內容類型                |
| Accept-charset  | Accept-charset: iso-8859-5                    | 字符編碼集                              |
| Accept-Encoding | Accept-Encoding: compress, gzip               | 壓縮編碼類型                            |
| Accept-Language | Accept-Language: en, zh                       | 語言                                    |
| Accept-Ranges   | Accept-Ranges: bytes                          | 子範圍字段                              |
| Authorization   | Authorization: Basic dbXleoOEpePOetpoe2Ftyd== | 授權證書                                |
| Cache-Control   | Cache-Control: no-cache                       | 緩存機制                                |
| Connection      | Connection: close                             | 是否需要持久連接（HTTP1.1默認持久連接） |
| Cookie          | Cookie: $version=1; Skin=new;                 | 請求域名下的所有cookie值                |
| Content-Length  | Content-Length: 348                           | 內容長度                                |

1. 請求體（Request Body）

HTTP請求中傳輸數據的實體。

### 2.2.4 HTTP響應

服務器端返回給客戶端。

1. 響應狀態碼（Response Status Code）

表示服務器的響應狀態。

| 狀態碼 | 說明               | 詳情                                                   |
| ------ | ------------------ | ------------------------------------------------------ |
| 100    | 繼續               | 服務器收到部分請求，等待客戶端繼續提出請求             |
| 101    | 切換協議           | 請求者已要求服務器切換協議，服務器已確認並準備切換協議 |
| 200    | 成功               | 成功處理請求                                           |
| 201    | 已創建             | 服務器創建了新的資源                                   |
| 202    | 已接受             | 已接收請求，但尚未處理                                 |
| 203    | 非授權信息         | 成功處理請求，但返回信息來自另一個源                   |
| 204    | 無內容             | 成功處理請求，無返回內容                               |
| 205    | 重置內容           | 成功處理請求，內容重置                                 |
| 206    | 部分內容           | 成功處理部分內容                                       |
| 300    | 多種選擇           | 可執行多種操作                                         |
| 301    | 永久移動           | 永久重定向                                             |
| 302    | 臨時移動           | 暫時重定向                                             |
| 303    | 查看其他位置       | 重定向目標文檔應通過GET獲取                            |
| 304    | 未修改             | 使用上次網頁資源                                       |
| 305    | 使用代理           | 應使用代理訪問                                         |
| 307    | 臨時重定向         | 臨時從其他位置響應                                     |
| 400    | 錯誤請求           | 無法解析                                               |
| 401    | 未授權             | 無身份驗證或驗證未通過                                 |
| 403    | 禁止訪問           | 拒絕                                                   |
| 404    | 未找到             | 找不到                                                 |
| 405    | 方法禁用           | 禁用指定方法                                           |
| 406    | 不接受             | 無法使用內容響應                                       |
| 407    | 需要代理授權       | 需要使用代理授權                                       |
| 408    | 請求超時           | 請求超時                                               |
| 409    | 沖突               | 完成請求時發生沖突                                     |
| 410    | 已刪除             | 資源永久刪除                                           |
| 411    | 需要有效長度       | 不接受標頭字段不含有效內容長度                         |
| 412    | 未滿足前提條件     | 服務器未滿足某個前提條件                               |
| 413    | 請求實體過大       | 超出能力                                               |
| 414    | 請求URI過長        | 網址過長，無法處理                                     |
| 415    | 不支持類型         | 格式不支持                                             |
| 416    | 請求範圍不符       | 頁面無法提供請求範圍                                   |
| 417    | 未滿足期望值       | 未滿足期望請求標頭字段                                 |
| 500    | 服務器內部發生錯誤 | 服務器錯誤                                             |
| 501    | 未實現             | 不具備功能                                             |
| 502    | 錯誤網關           | 收到無效響應                                           |
| 503    | 服務不可用         | 無法使用                                               |
| 504    | 網關超時           | 沒及時收到請求                                         |
| 505    | HTTP版本不支持     | 不支持HTTP協議版本                                     |

1. 響應頭（Response Headers）

包含服務器對請求的應答信息。

| 響應頭           | 說明                                                         |
| ---------------- | ------------------------------------------------------------ |
| Allow            | 服務器支持的請求方法                                         |
| Content-Encondig | 文檔編碼方法。                                               |
| Content-Length   | 內容長度，瀏覽器持久HTTP連接時需要                           |
| Content-Type     | 文檔的MIME類型                                               |
| Date             | GMT時間                                                      |
| Expires          | 過期時間後，不再緩存                                         |
| Last-Modified    | 文檔最後改動時間。通過比較客戶端頭if-Modified-Since，可能返回304（Not Modified）。 |
| Location         | 客戶端應去哪裡提取文檔。                                     |
| Refresh          | 瀏覽器應刷新時間，秒                                         |
| Server           | 服務器名字                                                   |
| Set-Cookie       | 設置頁面關聯Cookie                                           |
| WWW-Authenticate | 客戶應在Authorization中提供授權信息，通常返回401。           |

1. 響應體（Response Body）

HTTP請求返回的內容。
HTML，二進制數據，JSON文檔，XML文檔等。

### 2.2.5 URI與URL

1. URI（Uniform Resource Identifier，統一資源標識符）
   用來標識Web上每一種可用資源，概念。由資源的命名機制、存放資源的主機名、資源自身的名稱等組成。
2. URL（Uniform Resource Locator，統一資源定位符）
   用於描述網絡上的資源（描述信息資源的字符串），實現。使用統一格式，包括文件、服務器地址和目錄等。

```URL
scheme://host[:port#]/path/.../[?query-string][#anchor]
//協議（服務方式）
//主機域名或IP地址（可含端口號）
//具體地址，目錄和文件名等
```

1. URN（Uniform Resource Name，統一資源名）
   帶有名字的因特網資源，是URL的更新形式，不依賴位置，可減少失效鏈接個數。

### 2.2.6 HTTPS簡介

HTTPS（Hyper Text Transfer Protocol over SecureSocket Layer），在HTTP基礎上，通過傳輸加密和身份認證保證傳輸過程的安全型。HTTP + SSL/TLS。

TLS（Transport Layer Security，傳輸層安全性協議），及其前身SSL（Secure Socket Layer，安全套接字層），保障通信安全和數據完整性。

### 2.2.7 HTTP2簡介

1. HTTP協議歷史

- HTTP 0.9
  只支持GET方法，不支持MIME類型和HTTP各種頭信息等。
- HTTP 1.0
  增加很多方法、各種HTTP頭信息，以及對多媒體對象的處理。
- HTTP 1.1
  主流HTTP協議，改善結構性缺陷，明確語義，增刪特性，支持更復雜的Web應用程序。
- HTTP 2
  優化性能，兼容HTTP 1.1語義，是二進制協議，頭部採用HPACK壓縮，支持多路復用、服務器推送等。

1. HTTP 1.1與HTTP 2的對比

- 頭信息壓縮
  HTTP 1.1中，每一次發送和響應，都有HTTP頭信息。HTTP 2壓縮頭信息，減少帶寬。
- 推送功能
  HTTP 2之前，只能客戶端發送數據，服務器端返回數據。HTTP2中，服務器可以主動向客戶端發起一些數據傳輸（如css和png等），服務器可以並行發送html，css，js等數據。

### 2.2.8 Web應用程序的組成

1. 處理器（hendler）
   接收HTTP請求並處理。調用模板引擎生成html文檔返給客戶端。

MVC軟件架構模型

- 模型（Model）
  處理與業務邏輯相關的數據，以及封裝對數據的處理方法。有對數據直接訪問的權力，例如訪問數據庫。
- 視圖（View）
  實現有目的的顯示數據，一般沒有程序的邏輯。
- 控制器（Controller）
  組織不同層面，控制流程，處理用戶請求，模型交互等事件，並做出響應。

title模型Model控制器Controller視圖View瀏覽器模板引擎數據庫

1. 模板引擎（template engine）
   分離界面與數據（內容），組合模板（template）與數據（data），生成html文檔。
   分為置換型（模板內容中特定標記替換）、解釋型和編譯型等。

模板template數據data模板引擎HTML文檔

## 2.3 net/http包

### 2.3.1 創建簡單服務器端

1. 創建和解析HTTP服務器端

```go
package main

import (
	"net/http"
)

func sayHello(w http.ResponseWriter, req *http.Request) {
	w.Write([]byte("Hello World"))
}

func main() {
	//註冊路由
	http.HandleFunc("/hello", sayHello)
	//開啟對客戶端的監聽
	http.ListenAndServe(":8080", nil)
}
http.HandleFunc()函數

//輸入參數：監聽端口號和事件處理器handler
http.ListenAndServe()函數

type Handler interface {
	ServeHTTP(ResponseWriter, *Request)
}

type HandlerFunc func(ResponseWriter, *Request)

func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
	f(w, r)
}
package main

import (
	"net/http"
)

type Refer struct {
	handler http.Handler
	refer string
}

func (this *Refer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Referer() == this.refer {
		this.handler.ServeHTTP(w, r)
	} else {
		w.WriteHeader(403)
	}
}

func myHandler(w http.ResponseWriter, req *http.Request) {
	w.Write([]byte("this is handler"))
}

func hello(w http.ResponseWriter, req *http.Request) {
	w.Write([]byte("hello"))
}

func main() {
	referer := &Refer{
		handler: http.HandlerFunc(myHandler),
		refer: "www.shirdon.com",
	}
	http.HandleFunc("/hello", hello)
	http.ListenAndServe(":8080", referer)
}
```

1. 創建和解析HTTPS服務器端

```go
//證書文件路徑，私鑰文件路徑
func (srv *Server) ListenAndServeTLS(certFile, keyFile string) error
package main

import (
	"log"
	"net/http"
)

func handle(w http.ResponseWriter, r *http.Request) {
	log.Printf("Got connection: %s", r.Proto)
	w.Write([]byte("Hello this is a HTTP 2 message!"))
}

func main() {
	srv := &http.Server{Addr: ":8088", Handler: http.HandlerFunc(handle)}
	log.Printf("Serving on https://0.0.0.0:8088")
	log.Fatal(srv.ListenAndServeTLS("server.crt", "server.key"))
}
```

### 2.3.2 創建簡單的客戶端

```go
//src/net/http/client.go
var DefaultClient = &Client{}

func Get(url string) (resp *Response, err error) {
	return DefaultClient.Get(url)
}

func (c *Client) Get(url string) (resp *Response, err error) {
	req, err := NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	return c.Do(req)
}

func Post(url, contentType string, body io.Reader) (resp *Response, err error) {
	return DefaultClient.Post(url, contentType, body)
}

func (c *Client) Post(url, contentType string, body io.Reader) (resp *Response, err error) {
	req, err := NewRequest("POST", url, body)
	if err != nil {
		return nil, err
	}
	req.Header.set("Content-Type", contentType)
	return c.Do(req)
}
func NewRequest(method, url string, body io.Reader) (*Request, error)
//請求類型
//請求地址
//若body實現io.Closer接口，則Request返回值的Body字段會被設置為body值，並被Client的Do()、Post()和PostForm()方法關閉。
```

1. 創建GET請求

```go
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	resp, err := http.Get("https://www.baidu.com")
	if err != nil {
		fmt.Println("err:", err)
	}
	closer := resp.Body
	bytes, err := ioutil.ReadAll(closer)
	fmt.Println(string(bytes))
}
```

1. 創建POST請求

```go
package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	url := "https://www.shirdon.com/comment/add"
	body := `{"userId": 1, "articleId": 1, "comment": 這是一條評論}`
	resp, err := http.Post(url, "application/x-www-form-urlencoded", bytes.NewBuffer([]byte(body)))
	if err != nil {
		fmt.Println("err:", err)
	}
	bytes, err := ioutil.ReadAll(resp.Body)
	fmt.Println(string(bytes))
}
```

1. 創建PUT請求

```go
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {
	url := "https://www.shirdon.com/comment/update"
	payload := strings.NewReader(`{"userId": 1, "articleId": 1, "comment": 這是一條評論}`)
	req, _ := http.NewRequest("PUT", url, payload)
	req.Header.Add("Content-Type", "application/json")
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Println("err:", err)
	}
	defer res.Body.Close()
	bytes, err := ioutil.ReadAll(res.Body)
	fmt.Println(string(res))
	fmt.Println(string(bytes))
}
```

1. 創建DELETE請求

```go
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {
	url := "https://www.shirdon.com/comment/delete"
	payload := strings.NewReader(`{"userId": 1, "articleId": 1, "comment": 這是一條評論}`)
	req, _ := http.NewRequest("DELETE", url, payload)
	req.Header.Add("Content-Type", "application/json")
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Println("err:", err)
	}
	defer res.Body.Close()
	bytes, err := ioutil.ReadAll(res.Body)
	fmt.Println(string(res))
	fmt.Println(string(bytes))
}
```

1. 請求頭設置

```go
type Header map[string][]string
headers := http.Header{"token": {"feeowiwpor23dlspweh"}}
headers.Add("Accept-Charset", "UTF-8")
headers.Set("Host", "www.shirdon.com")
headers.Set("Location", "www.baidu.com")
```

## 2.4 html/template包

text/template處理任意格式的文本，html/template生成可對抗代碼注入的安全html文檔。

### 2.4.1 模板原理

1. 模板和模板引擎
   模板是事先定義好的不變的html文檔，模板渲染使用可變數據替換html文檔中的標記。模板用於顯示和數據分離（前後端分離）。模板技術，本質是模板引擎利用模板文件和數據生成html文檔。
2. Go語言模板引擎

- 模板文件後綴名通常為.tmpl和.tpl，UTF-8編碼
- 模板文件中{{和}}包裹和標識傳入數據
- 點號（.）訪問數據，{{.FieldName}}訪問字段
- 除{{和}}包裹內容外，其他內容原樣輸出

使用：
（1）定義模板文件
按照相應語法規則去定義。
（2）解析模板文件
創建指定模板名稱的模板對象

```go
func New(name string) *Template
```

解析模板內容

```go
func (t *Template) Parse(src string) (*Template, error)
```

解析模板文件

```go
func ParseFiles(filenames...string) (*Template, error)
```

正則匹配解析文件，template.ParaeGlob(“a*”)

```go
func ParseGlob(pattern string) (*Template, error)
```

（3）渲染模板文件

```go
func (t *Template) Execute(wr io.Writer, data interface{}) error

//配合ParseFiles()函數使用，需指定模板名稱
func (t *Template) ExecuteTemplate(wr io.Writer, name string, data interface{}) error
```

### 2.4.2 使用html/template包

1. 第1個模板
   template_example.tmpl

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模板使用示例</title>
</head>
<body>
   <p>加油，小夥伴， {{ . }} </p>
</body>
</html>
package main

import (
	"fmt"
	"html/template"
	"net/http"
)

func helloHandleFunc(w http.ResponseWriter, r *http.Request) {
	// 1. 解析模板
	t, err := template.ParseFiles("./template_example.tmpl")
	if err != nil {
		fmt.Println("template parsefile failed, err:", err)
		return
	}
	// 2.渲染模板
	name := "我愛Go語言"
	t.Execute(w, name)
}

func main() {
	http.HandleFunc("/", helloHandleFunc)
	http.ListenAndServe(":8086", nil)
}
```

1. 模板語法
   模板語法都包含在{{和}}中間。

```go
type UserInfo struct {
	Name string
	Gender string
	Age int
}

func sayHello(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("./hello.html")
	if err != nil {
		fmp.Println("create template failed, err:", err)
		return
	}

	user := UserInfo {
		Name: "張三",
		Gender: "男",
		Age: 28,
	}
	tmpl.Execute(w, user)
}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Hello</title>
</head>
<body>
   <p>Hello {{.Name}}</p>
   <p>性別：{{.Gender}}</p>
   <p>年齡：{{.Age}}</p>
</body>
</html>
```

常用語法：

- 注釋

```go
{{/* 這是一個注釋，不會解析 */}}
```

- 管道（pipeline）
  產生數據的操作，{{.Name}}等。支持|鏈接多個命令，類似UNIX下管道。
- 變量
  變量捕獲管道的執行結果。

```go
$variable := pipeline
```

- 條件判斷

```go
{{if pipeline}} T1 {{end}}
{{if pipeline}} T1 {{else}} T0 {{end}}
{{if pipeline}} T1 {{else if pipeline}} T0 {{end}}
```

- range關鍵字

```go
{{range pipeline}} T1 {{end}}
{{range pipeline}} T1 {{else}} T0 {{end}}
package main

import (
	"log"
	"os"
	"text/template"
)

func main() {
	//創建一個模版
	rangeTemplate := `
{{if .Kind}}
{{range $i, $v := .MapContent}}
{{$i}} => {{$v}} , {{$.OutsideContent}}
{{end}}
{{else}}
{{range .MapContent}}
{{.}} , {{$.OutsideContent}}
{{end}}    
{{end}}`

	str1 := []string{"第一次 range", "用 index 和 value"}
	str2 := []string{"第二次 range", "沒有用 index 和 value"}

	type Content struct {
		MapContent     []string
		OutsideContent string
		Kind           bool
	}
	var contents = []Content{
		{str1, "第一次外面的內容", true},
		{str2, "第二次外面的內容", false},
	}

	// 創建模板並將字符解析進去
	t := template.Must(template.New("range").Parse(rangeTemplate))

	// 接收並執行模板
	for _, c := range contents {
		err := t.Execute(os.Stdout, c)
		if err != nil {
			log.Println("executing template:", err)
		}
	}
}
/*
//輸出
0 => 第一次 range, 第一次外面的內容
1 => 用 index 和 value, 第一次外面的內容

第二次 range, 第二次外面的內容
沒有用 index 和 value, 第二次外面的內容
*/
```

- with關鍵字

```go
{{with pipeline}} T1 {{end}}
{{with pipeline}} T1 {{else}} T0 {{end}}
```

- 比較函數
  比較函數只適用於基本函數（或重定義的基本類型，如type Banance float32），整數和浮點數不能相互比較。
  布爾函數將任何類型的零值視為假。
  只有eq可以接受2個以上參數。

```go
{{eq arg1 arg2 arg3}}
eq
ne
lt
le
gt
ge
```

- 預定義函數

| 函數名   | 功能                                                         |
| -------- | ------------------------------------------------------------ |
| and      | 返回第1個空參數或最後一個參數，所有參數都執行。and x y等價於if x then y else x |
| or       | 返回第1個非空參數或最後一個參數，所有參數都執行。and x y等價於if x then y else x |
| not      | 非                                                           |
| len      | 長度                                                         |
| index    | index y 1 2 3, index[1][2][3]                                |
| print    | fmt.Sprint                                                   |
| printf   | fmt.Sprintf                                                  |
| println  | fmt.Sprintln                                                 |
| html     | html逸碼等價表示                                             |
| urlquery | 可嵌入URL查詢的逸碼等價表示                                  |
| js       | JavaScript逸碼等價表示                                       |
| call     | call func a b, func(a, b);1或2個返回值，第2個為error，非nil會中斷並返回給調用者。 |

- 自定義函數
  模板對象t的函數字典加入funcMap內的鍵值對。funcMap某個值不是函數類型，或該函數類型不符合要求，會panic。返回*Template便於鏈式調用。

```go
func (t *Template) Funcs(funcMap FuncMap) *Template
```

FuncMap映射函數要求1或2個返回值，第2個為error，非nil會中斷並返回給調用者。

```go
type FuncMap map[string]interface{}
package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
)

func Welcome() string { //沒參數
	return "Welcome"
}

func Doing(name string) string { //有參數
	return name + ", Learning Go Web template "
}

func sayHello(w http.ResponseWriter, r *http.Request) {
	htmlByte, err := ioutil.ReadFile("./funcs.html")
	if err != nil {
		fmt.Println("read html failed, err:", err)
		return
	}
	// 自定義一個匿名模板函數
	loveGo := func() (string) {
		return "歡迎一起學習《Go Web編程實戰派從入門到精通》"
	}
	// 採用鏈式操作在Parse()方法之前調用Funcs添加自定義的loveGo函數
	tmpl1, err := template.New("funcs").Funcs(template.FuncMap{"loveGo": loveGo}).Parse(string(htmlByte))
	if err != nil {
		fmt.Println("create template failed, err:", err)
		return
	}
	funcMap := template.FuncMap{
		//在FuncMap中聲明相應要使用的函數，然後就能夠在template字符串中使用該函數
		"Welcome": Welcome,
		"Doing":   Doing,
	}
	name := "Shirdon"
	tmpl2, err := template.New("test").Funcs(funcMap).Parse("{{Welcome}}<br/>{{Doing .}}")
	if err != nil {
		panic(err)
	}

	// 使用user渲染模板，並將結果寫入w
	tmpl1.Execute(w, name)
	tmpl2.Execute(w, name)
}

func main() {
	http.HandleFunc("/", sayHello)
	http.ListenAndServe(":8087", nil)
}
```

funcs.html

```html
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<meta http-equiv="X-UA-Compatible" content="ie=edge">
		<title>tmpl test</title>
	</head>
	<body>
		<h1>{{loveGo}}</h1>
	</body>
</html>
```

- 模板嵌套
  可以通過文件嵌套和define定義

```go
{{define "name"}} T {{end}}
{{template "name"}}
{{template "name" pipeline}}
{{block "name" pipeline}} T {{end}}
//等價於
{{define "name"}} T {{end}}
{{template "name" pipeline}}
```

t.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>tmpl test</title>
</head>
<body>
<h1>測試嵌套template語法</h1>
<hr>
{{template "ul.html"}}
<hr>
{{template "ol.html"}}
</body>
</html>
{{define "ol.html"}}
<h1>這是ol.html</h1>
<ol>
    <li>I love Go</li>
    <li>I love java</li>
    <li>I love c</li>
</ol>
{{end}}
```

ul.html

```html
<ul>
    <li>注釋</li>
    <li>日誌</li>
    <li>測試</li>
</ul>
package main

import (
	"fmt"
	"html/template"
	"net/http"
)

//定義一個UserInfo結構體
type UserInfo struct {
	Name string
	Gender string
	Age int
}

func tmplSample(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("./t.html", "./ul.html")
	if err != nil {
		fmt.Println("create template failed, err:", err)
		return
	}
	user := UserInfo{
		Name:   "張三",
		Gender: "男",
		Age:    28,
	}
	tmpl.Execute(w, user)
	fmt.Println(tmpl)
}

func main() {
	http.HandleFunc("/", tmplSample)
	http.ListenAndServe(":8087", nil)
}
```


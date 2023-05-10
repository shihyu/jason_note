ALSR
====

這篇要來講上一篇沒講完的部份，不知道你有沒有實際去試試看，如果不用 `gdb` 的話那個測試 RCE 的實驗還跑不跑的起來呢？如果你有試過就會知道答案是跑不起來，所以這又是發生了什麼事，上次談到堆疊的程式碼預設是禁止執行的，這只是其中一個保護機制而已，今天要來談談另一個保護機制 - ASLR

ASLR 的全名是 Address Space Layout Randomization ，它讓每次程式以及動態函式庫的載入位置都不相同，以防止你能填入固定的位置到堆疊中的返回位置中，這使得 buffer overflow 造成的 RCE 在現今的作業系統中變得幾乎不可能做到，你可以試著準備個簡單的程式，反覆執行，並在執行中看看 `maps` 中的位置是不是每次都不同，像這就是我隨意的兩次的執行 cat 的結果

```plain
55d02d7b9000-55d02d7c1000 r-xp 00000000 08:04 1706314                    /bin/cat
55d02d9c0000-55d02d9c1000 r--p 00007000 08:04 1706314                    /bin/cat
55d02d9c1000-55d02d9c2000 rw-p 00008000 08:04 1706314                    /bin/cat
55d02ec91000-55d02ecb2000 rw-p 00000000 00:00 0                          [heap]
...
```

```plain
55d2e94a1000-55d2e94a9000 r-xp 00000000 08:04 1706314                    /bin/cat
55d2e96a8000-55d2e96a9000 r--p 00007000 08:04 1706314                    /bin/cat
55d2e96a9000-55d2e96aa000 rw-p 00008000 08:04 1706314                    /bin/cat
55d2e9b7e000-55d2e9b9f000 rw-p 00000000 00:00 0                          [heap]
...
```

那為什麼 `gdb` 又可以執行出預期的結果呢？其實答案也很明顯， `gdb` 把 ASLR 關掉了，不然的話每次除錯時，上次記下來的記憶體位置就會失效，下中斷點或是要看變數的值就很麻煩啊，在 `gdb` 中你可以用這個指令來看有沒有關閉 ALSR ：

```plain
>>> show disable-randomization
Disabling randomization of debuggee's virtual address space is on.
```

也可以去設定它的開關

```plain
>>> set disable-randomization off
```

那如果要在不用 `gdb` 的情況下成功跑這個實驗的話，除了關掉整個系統的 ALSR 外還有個是用 `setarch` 的做法，我比較偏好這個：

```shell
$ setarch $(uname -m) -R <執行檔位置> < input
Hello from shellcode
```

shellcode
---------

另外講一下，前一篇的範例中把要執行的程式碼稱為 shellcode ， shellcode 是指那些利用漏洞而得以執行的程式碼，會叫做 shellcode 是因為通常它會開一個 shell 出來，畢竟對攻擊者而言，取得控制權才是最重要的事

以前對於 shellcode 方面其實有不少的研究，比如製作出不含 `\0` 的 shellcode ，甚至是完全以英數字編碼的 shellcode 也有，但在 buffer overflow 變得難以成功後這方面的東西似乎也比較沒有看到了，現在比較多的是反序列化造成的漏洞，比如像 python 的 `pickle`：

```python
import pickle

class Demo:
    def __reduce__(self):
      return (print, ("Hello world",))

pickle.loads(pickle.dumps(Demo()))
```

上面這段程式我用 python3.6 測試過，請注意字串後的 `,` 是必要的，沒意外的話應該會印出 `Hello world`，序列化是指把程式裡的物件轉成特定的表示型式，以便於交換資料，而反序列化則是把資料還原回物件，像 `json` 也算是其中一種格式，只是有些語言內建的序列化與反序列化太強大了，還可以從資料還原回任意的自訂的資料型態之類的，這就很容易遭到利用，在 pickle 中是因為它可以自訂這個型態要用什麼方式還原，於是這邊就設定讓它用一段字串當參數去呼叫 `print` 了

關於 stack overflow 的文章就到這邊結束了，下一篇要來看看我們的 `main` 真的是程式開始執行的點嗎？

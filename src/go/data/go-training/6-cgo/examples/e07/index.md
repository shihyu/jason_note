我們通過分析一個簡單的 cgo 函數調用來瞭解 cgo 的調用過程。

如下是一個簡單的 cgo 函數調用，在Go語言中調用了C語言實現的函數 println。
```go
package main

//int sum(int a, int b) { return a+b; }
import "C"

func main() {
    println(C.sum(1, 1))
}
```

通過 cgo 命令行工具在_obj 目錄生成中間文件

```
# go tool cgo main.go
```

## C.sum函數的實現
在生成的main.cgo1.go文件中，可以看到C.sum函數的實現。
```
package main

//int sum(int a, int b) { return a+b; }
import _ "unsafe"

func main() {
    println((_Cfunc_sum)(1, 1))
}
```

可以看到，C.sum函數被轉換成了一個名為_Cfunc_sum的Go語言函數。
_Cfunc_sum 函數（這是一個go函數，）在 cgo 生成的 _cgo_gotypes.go 文件中定義。

```shell
//go:cgo_unsafe_args
func _Cfunc_sum(p0 _Ctype_int, p1 _Ctype_int) (r1 _Ctype_int) {
	_cgo_runtime_cgocall(_cgo_e119c51a7968_Cfunc_sum, uintptr(unsafe.Pointer(&p0)))
	if _Cgo_always_false {
		_Cgo_use(p0)
		_Cgo_use(p1)
	}
	return
}
```
_Cfunc_sum 是C 函數 sum 在 Go 空間的入口。
在Cfunc_sum中，通過_cgo_runtime_cgocall 函數再間接調用 C 函數 sum。
它的參數 p0，p1 通過_Cgo_use 逃逸到了堆上。


## runtime.cgocall 函數
runtime.cgocall 函數是實現 Go 語言到 C 語言函數跨界調用的關鍵。其中傳入的參數中，_cgo_e119c51a7968_Cfunc_sum是一個C語言實現的函數。

其中 cgocall 的源碼位於 go 語言運行時的 runtime/cgocall.go。工作包括
- 做一些調度相關的準備動作
- 進行Go與C之間call ABI操作

```go
//file：runtime/cgocall.go
func cgocall(fn, arg unsafe.Pointer) int32 {
	......
	
    mp := getg().m // 獲取當前 goroutine 的 M
    mp.ncgocall++  // 總 cgo 計數 +1
    mp.ncgo++      // 當前 cgo 計數 +1
    
    mp.cgoCallers[0] = 0 // 重置追蹤
    
    entersyscall() // 進入系統調用,保存上下文, 標記當前 goroutine 獨佔 m, 跳過垃圾回收
    
    osPreemptExtEnter(mp) // 標記異步搶佔, 使異步搶佔邏輯失效
    
    mp.incgo = true // 修改狀態
    errno := asmcgocall(fn, arg) // 真正進行方法調用的地方
    
    mp.incgo = false // 修改狀態
    mp.ncgo-- // 當前 cgo 調用-1
    
    osPreemptExtExit(mp) // 恢復異步搶佔
    
    exitsyscall() // 退出系統調用,恢復調度器控制
    ......
	
    // 避免 GC 過早回收
    KeepAlive(fn)
    KeepAlive(arg)
    KeepAlive(mp)
    
    return errno
}
```

在上面的源碼中，有幾個重要的函數
- entersyscall 函數：將當前的 M 與 P 剝離，防止 C 程序獨佔 M 時，阻塞 P 的調度
- asmcgocall：將棧切換到 g0 的系統棧，並執行 C 函數調用
- exitsyscall：尋找合適的 P 來運行從 C 函數返回的 Go 程，優先選擇調用 C 之前依附的 P，其次選擇其他空閒的 P

值得注意的是當 Go 程在調用 C 函數時，會單獨佔用一個系統線程。因此如果在 Go 程中併發調用 C 函數。
如果 C 函數中又存在阻塞操作，就很可能會造成 Go 程序不停的創建新的系統線程，而 Go 並不會回收系統線程，過多的線程數會拖垮整個系統


### entersyscall
我們再來看 entersyscall 函數。該函數將M與P剝離，防止系統調用阻塞P的調度，保存上下文。

```go
//file:runtime/proc.go
func entersyscall() {
	reentersyscall(getcallerpc(), getcallersp())
}
func reentersyscall(pc, sp uintptr) {
    _g_ := getg()
    ......
	
	//保存g的現場信息，rsp, rbp, rip等
	save(pc, sp)
    _g_.syscallsp = sp
    _g_.syscallpc = pc
    casgstatus(_g_, _Grunning, _Gsyscall)
	...
    //解除P與M的綁定
    pp := _g_.m.p.ptr()
    pp.m = 0
    _g_.m.oldp.set(pp) //把p記錄在oldp中，等從系統調用返回時，優先綁定這個p
    _g_.m.p = 0
}
```

entersyscall 直接調用了reentersyscall函數，reentersyscall首先把現場信息保存在當前g的sched成員中，然後解除m和p的綁定關係並設置p的狀態為_Psyscall.

sysmon監控線程需要依賴該狀態實施搶佔, sysmon線程通過 retake => handoffp
- 如果調用不超過20us則不會觸發任何事件。
- 如果調用超過20us可能會導致新線程的啟動 

```go
//file:runtime/proc.go
func retake(now int64) uint32 {
    for i := 0; i < len(allp); i++ {
        _p_ := allp[i]
    }
    ......

	if s == _Psyscall { 
		...
		handoffp(_p_)
    }
}
```

handoffp 方法會調用 startm 來啟動一個新的 M,出來接管P。

```go
//file:runtime/proc.go
func handoffp(_p_ *p) {
	...
	startm(_p_, false)
}
```

### asmcgocall
asmcgocall 是一個彙編函數，用於調用 C 函數。
將當前棧移到系統棧去執行，因為 C 需要"無窮大"的棧，在 Go 的棧上執行 C 函數會導致棧溢出

該函數在不同平臺有不同的實現，拿amd64平臺為例：

```
//file:runtime/asm_amd64.s
TEXT ·asmcgocall(SB),NOSPLIT,$0-20
	MOVQ	fn+0(FP), AX
	MOVQ	arg+8(FP), BX

	MOVQ	SP, DX

	// Figure out if we need to switch to m->g0 stack.
	// We get called to create new OS threads too, and those
	// come in on the m->g0 stack already. Or we might already
	// be on the m->gsignal stack.
	// 考慮是否需要切換到 m.g0 棧
    // 也用來調用創建新的 OS 線程，這些線程已經在 m.g0 棧中了
	get_tls(CX)
	MOVQ	g(CX), DI
	CMPQ	DI, $0
	JEQ	nosave
	MOVQ	g_m(DI), R8
	MOVQ	m_gsignal(R8), SI
	CMPQ	DI, SI
	JEQ	nosave
	MOVQ	m_g0(R8), SI
	CMPQ	DI, SI
	JEQ	nosave

	// Switch to system stack.
	// 切換到系統棧
	CALL	gosave_systemstack_switch<>(SB)
	MOVQ	SI, g(CX)
	MOVQ	(g_sched+gobuf_sp)(SI), SP

	// Now on a scheduling stack (a pthread-created stack).
	// Make sure we have enough room for 4 stack-backed fast-call
	// registers as per windows amd64 calling convention.
	// 於調度棧中（pthread 新創建的棧）
    // 確保有足夠的空間給四個 stack-based fast-call 寄存器
    // 為使得 windows amd64 調用服務
	SUBQ	$64, SP
	ANDQ	$~15, SP	// 為 gcc ABI 對齊
	MOVQ	DI, 48(SP)	// save g
	MOVQ	(g_stack+stack_hi)(DI), DI
	SUBQ	DX, DI
	MOVQ	DI, 40(SP)	// 保存棧深 (不能僅保存 SP，因為棧可能在回調時被複制)
	MOVQ	BX, DI		// DI = AMD64 ABI 第一個參數
	MOVQ	BX, CX		// CX = Win64 第一個參數
	CALL	AX          // 調用 fn

	// Restore registers, g, stack pointer.
	// 恢復寄存器、 g、棧指針
	get_tls(CX)
	MOVQ	48(SP), DI
	MOVQ	(g_stack+stack_hi)(DI), SI
	SUBQ	40(SP), SI
	MOVQ	DI, g(CX)
	MOVQ	SI, SP

	MOVL	AX, ret+16(FP)
	RET

nosave:
    // 在系統棧上運行，可能沒有 g
    // 沒有 g 的情況發生在線程創建中或線程結束中（比如 Solaris 平臺上的 needm/dropm）
    // 這段代碼和上面類似，但沒有保存和恢復 g，且沒有考慮棧的移動問題（因為我們在系統棧上，而非 goroutine 棧）
    // 如果已經在系統棧上，則上面的代碼可被直接使用，在 Solaris 上會進入下面這段代碼。
    // 使用這段代碼來為所有 "已經在系統棧" 的調用進行服務，從而保持正確性。
    SUBQ    $64, SP
    ANDQ    $~15, SP // ABI 對齊
    MOVQ    $0, 48(SP) // 上面的代碼保存了 g, 確保 debug 時可用
    MOVQ    DX, 40(SP) // 保存原始的棧指針
    MOVQ    BX, DI  // DI = AMD64 ABI 第一個參數
    MOVQ    BX, CX  // CX = Win64 第一個參數
    CALL    AX
    MOVQ    40(SP), SI // 恢復原來的棧指針
    MOVQ    SI, SP
    MOVL    AX, ret+16(FP)
    RET	
```

### exitsyscall
exitsyscall的基本思路是，
- 先嚐試獲取一個p（優先嚐試獲取前面移交出去的p），若獲取到了則直接返回到用戶代碼繼續執行用戶邏輯即可；
- 否則調用mcall切換到g0棧執行exitsyscall0函數

```go
//file:runtime/proc.go
func exitsyscall() {
    _g_ := getg()

	//進入系統調用之前保存的P
	oldp := _g_.m.oldp.ptr()

	//因為在進入系統調用之前已經解除了m和p之間的綁定，所以現在需要綁定p
    if exitsyscallfast(oldp) {
		...
        // There's a cpu for us, so we can run.
		//系統調用完成，增加syscalltick計數，sysmon線程依靠它判斷是否是同一次系統調用
        _g_.m.p.ptr().syscalltick++
		
        // We need to cas the status and scan before resuming...
		//casgstatus函數會處理一些垃圾回收相關的事情，我們只需知道該函數重新把g設置成_Grunning狀態即可
        casgstatus(_g_, _Gsyscall, _Grunning)
        
        // 返回到用戶代碼繼續執行
        return
    }
	
    // Call the scheduler.
    //沒有綁定到p，調用mcall切換到g0棧執行exitsyscall0函數
    mcall(exitsyscall0)
    ......
}
```

exitsyscall0還是會繼續嘗試獲取空閒的p，若還是獲取不到就會調用stopm將當前線程睡眠，等待被其它線程喚醒

## c語言實現的_cgo_e119c51a7968_Cfunc_sum函數

對於函數C語言中的sum函數，經過cgo編譯後生成了一個名為_cgo_main.c的文件，該文件包含了C語言函數_cgo_e119c51a7968_Cfunc_sum的實現。

```c
void
_cgo_e119c51a7968_Cfunc_sum(void *v)
{
	struct {
		int p0;
		int p1;
		int r;
		char __pad12[4];
	} __attribute__((__packed__)) *_cgo_a = v;
	char *_cgo_stktop = _cgo_topofstack();
	__typeof__(_cgo_a->r) _cgo_r;
	_cgo_tsan_acquire();
	_cgo_r = sum(_cgo_a->p0, _cgo_a->p1);
	_cgo_tsan_release();
	_cgo_a = (void*)((char*)_cgo_a + (_cgo_topofstack() - _cgo_stktop));
	_cgo_a->r = _cgo_r;
	_cgo_msan_write(&_cgo_a->r, sizeof(_cgo_a->r));
}
```

函數體各段代碼含義如下
函數_cgo_e119c51a7968_Cfunc_sum接收一個參數
- 輸入參數v被轉化為_cgo_a參數，它是一個結構體，包含兩個整數成員p0和p1，以及一個整數成員r。
- _cgo_topofstack 函數用於 C 函數調用後恢復調用棧
- _cgo_tsan_acquire 和 _cgo_tsan_release 則是用於掃描 CGO 相關的函數，是對 CGO 相關函數的指針做相關檢查
- sum用於真正計算兩個數的和
- 通過_cgo_a->r = _cgo_r將結果賦值給_cgo_a->r

- 更詳細的細節可以參考 https://golang.org/src/cmd/cgo/doc.go 內部的代碼註釋和 runtime.cgocall 函數的實現

## 結論
在cgo的調用中
- cgo 調用會將當前協程棧移到系統棧
- cgo 高併發調用且阻塞超過 20 微秒時會新建線程



## 參考
- [Go與C的橋樑：CGO入門剖析與實踐](https://cloud.tencent.com/developer/article/1786332?areaId=106001)
- [cgo內部機制](https://chai2010.cn/advanced-go-programming-book/ch2-cgo/ch2-05-internal.html)
- [從源碼分析 Go 語言使用 cgo 導致的線程增長](https://www.cnblogs.com/t102011/p/17457120.html)
- [Golang調度器源碼分析](https://cs50mu.github.io/post/golang-scheduler/)
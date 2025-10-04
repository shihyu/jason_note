golang中使用的彙編是

將測試代碼編譯成彙編
```shell
# go tool compile -S -N -l main.go > main.s
# GOOS=linux GOARCH=amd64 go tool compile -S -N -l main.go > main.s
```

可以看到編譯後的彙編有對 runtime.morestack_noctxt 的調用
```shell
//file:main.S
# runtime.morestack_noctxt(SB)
```

其中 morestack_noctxt 是在 runtime 包中定義的一個彙編函數
```
//file:asm_amd64.s
TEXT runtime·morestack_noctxt(SB),NOSPLIT|NOFRAME,$0-0
	MOVD	RSP, RSP
	MOVW	$0, R26
	B runtime·morestack(SB)
	
TEXT runtime·morestack(SB),NOSPLIT|NOFRAME,$0-0
    ......
    // 在 m->g0 棧上調用 newstack.
    MOVQ	m_g0(BX), BX
	MOVQ	BX, g(CX)
	MOVQ	(g_sched+gobuf_sp)(BX), SP
	CALL	runtime·newstack(SB)
	CALL	runtime·abort(SB)	// crash if newstack returns
	RET
```

runtime·morestack 做完校驗和賦值操作後會切換到 G0 調用 runtime·newstack來完成擴容的操作

newstack 就定義在 go 代碼中了

```go
//file:runtime/stack.go
func newstack() {
	......
	//新棧大小是老棧的兩倍
    oldsize := gp.stack.hi - gp.stack.lo
    newsize := oldsize * 2
	
	//進行棧的申請和拷貝
    copystack(gp, newsize)
}
```

在 copystack 中完成新棧的分配，將舊棧拷貝到新棧，

```go
//file:runtime/stack.go
func copystack(gp *g, newsize uintptr) {
	//分配新的棧空間
	new := stackalloc(uint32(newsize))

	// 將原棧中的內存拷貝到新棧中
	memmove(unsafe.Pointer(new.hi-ncopy), unsafe.Pointer(old.hi-ncopy), ncopy)

	// 將 G 上的棧引用切換成新棧
	gp.stack = new
	gp.stackguard0 = new.lo + _StackGuard // NOTE: might clobber a preempt request
	gp.sched.sp = new.hi - used
	gp.stktopsp += adjinfo.delta

	//釋放原棧內存
	stackfree(old)
}
```

至此，棧擴張完畢！
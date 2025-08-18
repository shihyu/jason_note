; ModuleID = 'probe1.92f6170832c34087-cgu.0'
source_filename = "probe1.92f6170832c34087-cgu.0"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

%"core::fmt::rt::Argument<'_>" = type { %"core::fmt::rt::ArgumentType<'_>" }
%"core::fmt::rt::ArgumentType<'_>" = type { ptr, [1 x i32] }

@alloc_fad0cd83b7d1858a846a172eb260e593 = private unnamed_addr constant [42 x i8] c"is_aligned_to: align is not a power-of-two", align 1
@alloc_8aab646a6a00d0316fe79130e392c407 = private unnamed_addr constant <{ ptr, [4 x i8] }> <{ ptr @alloc_fad0cd83b7d1858a846a172eb260e593, [4 x i8] c"*\00\00\00" }>, align 4
@anon.55aae19ebcedabc58c8463847838c69e.0 = private unnamed_addr constant <{ [4 x i8], [4 x i8] }> <{ [4 x i8] zeroinitializer, [4 x i8] undef }>, align 4
@alloc_d77dba53dad89ca4ef60992c97e68ffd = private unnamed_addr constant [119 x i8] c"/home/shihyu/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/core/src/ptr/const_ptr.rs", align 1
@alloc_a396df32026717d6115b57c8dbe16280 = private unnamed_addr constant <{ ptr, [12 x i8] }> <{ ptr @alloc_d77dba53dad89ca4ef60992c97e68ffd, [12 x i8] c"w\00\00\00\C3\05\00\00\0D\00\00\00" }>, align 4
@alloc_bd3468a7b96187f70c1ce98a3e7a63bf = private unnamed_addr constant [283 x i8] c"unsafe precondition(s) violated: ptr::copy_nonoverlapping requires that both pointer arguments are aligned and non-null and the specified memory ranges do not overlap\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_db07ae5a9ce650d9b7cc970d048e6f0c = private unnamed_addr constant [186 x i8] c"unsafe precondition(s) violated: usize::unchecked_mul cannot overflow\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_2dff866d8f4414dd3e87cf8872473df8 = private unnamed_addr constant [227 x i8] c"unsafe precondition(s) violated: ptr::read_volatile requires that the pointer argument is aligned and non-null\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_560a59ed819b9d9a5841f6e731c4c8e5 = private unnamed_addr constant [210 x i8] c"unsafe precondition(s) violated: NonNull::new_unchecked requires that the pointer is non-null\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_64e308ef4babfeb8b6220184de794a17 = private unnamed_addr constant [221 x i8] c"unsafe precondition(s) violated: hint::assert_unchecked must never be called when the condition is false\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_1be5ea12ba708d9a11b6e93a7d387a75 = private unnamed_addr constant [281 x i8] c"unsafe precondition(s) violated: Layout::from_size_align_unchecked requires that align is a power of 2 and the rounded-up allocation size does not exceed isize::MAX\0A\0AThis indicates a bug in the program. This Undefined Behavior check is optional, and cannot be relied on for safety.", align 1
@alloc_763310d78c99c2c1ad3f8a9821e942f3 = private unnamed_addr constant [61 x i8] c"is_nonoverlapping: `size_of::<T>() * count` overflows a usize", align 1
@__rust_no_alloc_shim_is_unstable = external dso_local global i8
@alloc_04f3c4883fbcc3a90b505bd4296b8b1c = private unnamed_addr constant [112 x i8] c"/home/shihyu/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/alloc/src/slice.rs", align 1
@alloc_7fed0d2a227741441efda167863bf4e6 = private unnamed_addr constant <{ ptr, [12 x i8] }> <{ ptr @alloc_04f3c4883fbcc3a90b505bd4296b8b1c, [12 x i8] c"p\00\00\00\BE\01\00\00\1D\00\00\00" }>, align 4
@alloc_4b9523bd3933225a2ba132a1dcbebd94 = private unnamed_addr constant <{ ptr, [4 x i8] }> <{ ptr inttoptr (i32 1 to ptr), [4 x i8] zeroinitializer }>, align 4
@alloc_83ea17bf0c4f4a5a5a13d3ae7955acd0 = private unnamed_addr constant [4 x i8] zeroinitializer, align 4

; core::intrinsics::copy_nonoverlapping::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @_ZN4core10intrinsics19copy_nonoverlapping18precondition_check17h6d1c9e591616fd81E(ptr %src, ptr %dst, i32 %size, i32 %align, i32 %count) unnamed_addr #0 {
start:
  %0 = alloca [4 x i8], align 4
  %_26 = alloca [24 x i8], align 4
  %_21 = alloca [4 x i8], align 4
  %_20 = alloca [4 x i8], align 4
  %_19 = alloca [4 x i8], align 4
  %_18 = alloca [4 x i8], align 4
  %_17 = alloca [24 x i8], align 4
  %is_zst = alloca [1 x i8], align 1
  %align1 = alloca [4 x i8], align 4
  %zero_size = alloca [1 x i8], align 1
  %1 = icmp eq i32 %count, 0
  br i1 %1, label %bb1, label %bb2

bb1:                                              ; preds = %start
  store i8 1, ptr %zero_size, align 1
  store i32 %align, ptr %align1, align 4
  %2 = load i8, ptr %zero_size, align 1
  %3 = trunc nuw i8 %2 to i1
  %4 = zext i1 %3 to i8
  store i8 %4, ptr %is_zst, align 1
  %5 = call i32 @llvm.ctpop.i32(i32 %align)
  store i32 %5, ptr %_21, align 4
  %6 = load i32, ptr %_21, align 4
  %7 = icmp eq i32 %6, 1
  br i1 %7, label %bb26, label %bb15

bb2:                                              ; preds = %start
  %8 = icmp eq i32 %size, 0
  %9 = zext i1 %8 to i8
  store i8 %9, ptr %zero_size, align 1
  store i32 %align, ptr %align1, align 4
  %10 = load i8, ptr %zero_size, align 1
  %11 = trunc nuw i8 %10 to i1
  %12 = zext i1 %11 to i8
  store i8 %12, ptr %is_zst, align 1
  %13 = call i32 @llvm.ctpop.i32(i32 %align)
  store i32 %13, ptr %_21, align 4
  %14 = load i32, ptr %_21, align 4
  %15 = icmp eq i32 %14, 1
  br i1 %15, label %bb14, label %bb15

bb26:                                             ; preds = %bb1
  %16 = ptrtoint ptr %src to i32
  store i32 %16, ptr %_19, align 4
  %17 = sub i32 %align, 1
  store i32 %17, ptr %_20, align 4
  %18 = load i32, ptr %_19, align 4
  %19 = load i32, ptr %_20, align 4
  %20 = and i32 %18, %19
  store i32 %20, ptr %_18, align 4
  %21 = load i32, ptr %_18, align 4
  %22 = icmp eq i32 %21, 0
  br i1 %22, label %bb27, label %bb11

bb15:                                             ; preds = %bb2, %bb1
  store ptr @alloc_8aab646a6a00d0316fe79130e392c407, ptr %_17, align 4
  %23 = getelementptr inbounds i8, ptr %_17, i32 4
  store i32 1, ptr %23, align 4
  %24 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %25 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  %26 = getelementptr inbounds i8, ptr %_17, i32 16
  store ptr %24, ptr %26, align 4
  %27 = getelementptr inbounds i8, ptr %26, i32 4
  store i32 %25, ptr %27, align 4
  %28 = getelementptr inbounds i8, ptr %_17, i32 8
  store ptr inttoptr (i32 4 to ptr), ptr %28, align 4
  %29 = getelementptr inbounds i8, ptr %28, i32 4
  store i32 0, ptr %29, align 4
; call core::panicking::panic_fmt
  call void @_ZN4core9panicking9panic_fmt17h5b404ce146871bf2E(ptr align 4 %_17, ptr align 4 @alloc_a396df32026717d6115b57c8dbe16280) #10
  unreachable

bb27:                                             ; preds = %bb26
  br label %bb12

bb11:                                             ; preds = %bb14, %bb26
  br label %bb6

bb12:                                             ; preds = %bb10, %bb27
  br label %bb3

bb14:                                             ; preds = %bb2
  %30 = ptrtoint ptr %src to i32
  store i32 %30, ptr %_19, align 4
  %31 = sub i32 %align, 1
  store i32 %31, ptr %_20, align 4
  %32 = load i32, ptr %_19, align 4
  %33 = load i32, ptr %_20, align 4
  %34 = and i32 %32, %33
  store i32 %34, ptr %_18, align 4
  %35 = load i32, ptr %_18, align 4
  %36 = icmp eq i32 %35, 0
  br i1 %36, label %bb10, label %bb11

bb10:                                             ; preds = %bb14
  %37 = load i8, ptr %is_zst, align 1
  %38 = trunc nuw i8 %37 to i1
  br i1 %38, label %bb12, label %bb13

bb13:                                             ; preds = %bb10
  %39 = load i32, ptr %_19, align 4
  %_15 = icmp eq i32 %39, 0
  %_8 = xor i1 %_15, true
  br i1 %_8, label %bb3, label %bb6

bb6:                                              ; preds = %bb11, %bb13
  br label %bb7

bb3:                                              ; preds = %bb12, %bb13
  %40 = load i8, ptr %zero_size, align 1
  %is_zst2 = trunc nuw i8 %40 to i1
  %41 = call i32 @llvm.ctpop.i32(i32 %align)
  store i32 %41, ptr %0, align 4
  %_29 = load i32, ptr %0, align 4
  %42 = icmp eq i32 %_29, 1
  br i1 %42, label %bb21, label %bb22

bb21:                                             ; preds = %bb3
  %_28 = ptrtoint ptr %dst to i32
  %43 = load i32, ptr %_20, align 4
  %_27 = and i32 %_28, %43
  %44 = icmp eq i32 %_27, 0
  br i1 %44, label %bb17, label %bb18

bb22:                                             ; preds = %bb3
  store ptr @alloc_8aab646a6a00d0316fe79130e392c407, ptr %_26, align 4
  %45 = getelementptr inbounds i8, ptr %_26, i32 4
  store i32 1, ptr %45, align 4
  %46 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %47 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  %48 = getelementptr inbounds i8, ptr %_26, i32 16
  store ptr %46, ptr %48, align 4
  %49 = getelementptr inbounds i8, ptr %48, i32 4
  store i32 %47, ptr %49, align 4
  %50 = getelementptr inbounds i8, ptr %_26, i32 8
  store ptr inttoptr (i32 4 to ptr), ptr %50, align 4
  %51 = getelementptr inbounds i8, ptr %50, i32 4
  store i32 0, ptr %51, align 4
; call core::panicking::panic_fmt
  call void @_ZN4core9panicking9panic_fmt17h5b404ce146871bf2E(ptr align 4 %_26, ptr align 4 @alloc_a396df32026717d6115b57c8dbe16280) #10
  unreachable

bb17:                                             ; preds = %bb21
  br i1 %is_zst2, label %bb19, label %bb20

bb18:                                             ; preds = %bb21
  br label %bb5

bb20:                                             ; preds = %bb17
  %_24 = icmp eq i32 %_28, 0
  %_11 = xor i1 %_24, true
  br i1 %_11, label %bb4, label %bb5

bb19:                                             ; preds = %bb17
  br label %bb4

bb5:                                              ; preds = %bb18, %bb20
  br label %bb7

bb4:                                              ; preds = %bb19, %bb20
; call core::ub_checks::maybe_is_nonoverlapping::runtime
  %_6 = call zeroext i1 @_ZN4core9ub_checks23maybe_is_nonoverlapping7runtime17h1e293b6cbf0d2d06E(ptr %src, ptr %dst, i32 %size, i32 %count) #11
  br i1 %_6, label %bb9, label %bb8

bb8:                                              ; preds = %bb7, %bb4
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_bd3468a7b96187f70c1ce98a3e7a63bf, i32 283) #10
  unreachable

bb9:                                              ; preds = %bb4
  ret void

bb7:                                              ; preds = %bb6, %bb5
  br label %bb8
}

; core::intrinsics::cold_path
; Function Attrs: cold nounwind
define internal void @_ZN4core10intrinsics9cold_path17h663b72fd12360649E() unnamed_addr #1 {
start:
  ret void
}

; core::fmt::rt::Argument::new_lower_exp
; Function Attrs: inlinehint nounwind
define dso_local void @_ZN4core3fmt2rt8Argument13new_lower_exp17ha2863b1ea7e04ef5E(ptr sret([8 x i8]) align 4 %_0, ptr align 4 %x) unnamed_addr #0 {
start:
  %_2 = alloca [8 x i8], align 4
  store ptr %x, ptr %_2, align 4
  %0 = getelementptr inbounds i8, ptr %_2, i32 4
  store ptr @"_ZN4core3fmt3num3imp55_$LT$impl$u20$core..fmt..LowerExp$u20$for$u20$isize$GT$3fmt17hd3d241c9ee8f214fE", ptr %0, align 4
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_0, ptr align 4 %_2, i32 8, i1 false)
  ret void
}

; core::fmt::Arguments::new_v1
; Function Attrs: inlinehint nounwind
define dso_local void @_ZN4core3fmt9Arguments6new_v117h049db3261a56fa77E(ptr sret([24 x i8]) align 4 %_0, ptr align 4 %pieces, ptr align 4 %args) unnamed_addr #0 {
start:
  store ptr %pieces, ptr %_0, align 4
  %0 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 1, ptr %0, align 4
  %1 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %2 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  %3 = getelementptr inbounds i8, ptr %_0, i32 16
  store ptr %1, ptr %3, align 4
  %4 = getelementptr inbounds i8, ptr %3, i32 4
  store i32 %2, ptr %4, align 4
  %5 = getelementptr inbounds i8, ptr %_0, i32 8
  store ptr %args, ptr %5, align 4
  %6 = getelementptr inbounds i8, ptr %5, i32 4
  store i32 1, ptr %6, align 4
  ret void
}

; core::num::<impl usize>::unchecked_mul::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @"_ZN4core3num23_$LT$impl$u20$usize$GT$13unchecked_mul18precondition_check17hfc0f297104534aabE"(i32 %lhs, i32 %rhs) unnamed_addr #0 {
start:
  %0 = call { i32, i1 } @llvm.umul.with.overflow.i32(i32 %lhs, i32 %rhs)
  %_5.0 = extractvalue { i32, i1 } %0, 0
  %_5.1 = extractvalue { i32, i1 } %0, 1
  br i1 %_5.1, label %bb1, label %bb2

bb2:                                              ; preds = %start
  ret void

bb1:                                              ; preds = %start
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_db07ae5a9ce650d9b7cc970d048e6f0c, i32 186) #10
  unreachable
}

; core::ptr::read_volatile::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @_ZN4core3ptr13read_volatile18precondition_check17he9b2a04ca31f5f2eE(ptr %addr, i32 %align, i1 zeroext %is_zst) unnamed_addr #0 {
start:
  %0 = alloca [4 x i8], align 4
  %_8 = alloca [24 x i8], align 4
  %1 = call i32 @llvm.ctpop.i32(i32 %align)
  store i32 %1, ptr %0, align 4
  %_12 = load i32, ptr %0, align 4
  %2 = icmp eq i32 %_12, 1
  br i1 %2, label %bb7, label %bb8

bb7:                                              ; preds = %start
  %_10 = ptrtoint ptr %addr to i32
  %_11 = sub i32 %align, 1
  %_9 = and i32 %_10, %_11
  %3 = icmp eq i32 %_9, 0
  br i1 %3, label %bb3, label %bb4

bb8:                                              ; preds = %start
  store ptr @alloc_8aab646a6a00d0316fe79130e392c407, ptr %_8, align 4
  %4 = getelementptr inbounds i8, ptr %_8, i32 4
  store i32 1, ptr %4, align 4
  %5 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %6 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  %7 = getelementptr inbounds i8, ptr %_8, i32 16
  store ptr %5, ptr %7, align 4
  %8 = getelementptr inbounds i8, ptr %7, i32 4
  store i32 %6, ptr %8, align 4
  %9 = getelementptr inbounds i8, ptr %_8, i32 8
  store ptr inttoptr (i32 4 to ptr), ptr %9, align 4
  %10 = getelementptr inbounds i8, ptr %9, i32 4
  store i32 0, ptr %10, align 4
; call core::panicking::panic_fmt
  call void @_ZN4core9panicking9panic_fmt17h5b404ce146871bf2E(ptr align 4 %_8, ptr align 4 @alloc_a396df32026717d6115b57c8dbe16280) #10
  unreachable

bb3:                                              ; preds = %bb7
  br i1 %is_zst, label %bb5, label %bb6

bb4:                                              ; preds = %bb7
  br label %bb2

bb6:                                              ; preds = %bb3
  %_6 = icmp eq i32 %_10, 0
  %_4 = xor i1 %_6, true
  br i1 %_4, label %bb1, label %bb2

bb5:                                              ; preds = %bb3
  br label %bb1

bb2:                                              ; preds = %bb4, %bb6
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_2dff866d8f4414dd3e87cf8872473df8, i32 227) #10
  unreachable

bb1:                                              ; preds = %bb5, %bb6
  ret void
}

; core::ptr::drop_in_place<alloc::string::String>
; Function Attrs: nounwind
define dso_local void @"_ZN4core3ptr42drop_in_place$LT$alloc..string..String$GT$17h51f2dc7a1feb8fc5E"(ptr align 4 %_1) unnamed_addr #2 {
start:
; call core::ptr::drop_in_place<alloc::vec::Vec<u8>>
  call void @"_ZN4core3ptr46drop_in_place$LT$alloc..vec..Vec$LT$u8$GT$$GT$17h29263fe6c7e31f55E"(ptr align 4 %_1) #11
  ret void
}

; core::ptr::drop_in_place<alloc::vec::Vec<u8>>
; Function Attrs: nounwind
define dso_local void @"_ZN4core3ptr46drop_in_place$LT$alloc..vec..Vec$LT$u8$GT$$GT$17h29263fe6c7e31f55E"(ptr align 4 %_1) unnamed_addr #2 {
start:
; call <alloc::vec::Vec<T,A> as core::ops::drop::Drop>::drop
  call void @"_ZN70_$LT$alloc..vec..Vec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h7f645b41a7ab76bcE"(ptr align 4 %_1) #11
; call core::ptr::drop_in_place<alloc::raw_vec::RawVec<u8>>
  call void @"_ZN4core3ptr53drop_in_place$LT$alloc..raw_vec..RawVec$LT$u8$GT$$GT$17had4e69a409c6d804E"(ptr align 4 %_1) #11
  ret void
}

; core::ptr::drop_in_place<alloc::raw_vec::RawVec<u8>>
; Function Attrs: nounwind
define dso_local void @"_ZN4core3ptr53drop_in_place$LT$alloc..raw_vec..RawVec$LT$u8$GT$$GT$17had4e69a409c6d804E"(ptr align 4 %_1) unnamed_addr #2 {
start:
; call <alloc::raw_vec::RawVec<T,A> as core::ops::drop::Drop>::drop
  call void @"_ZN77_$LT$alloc..raw_vec..RawVec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h6e18edbe1264ccc5E"(ptr align 4 %_1) #11
  ret void
}

; core::ptr::non_null::NonNull<T>::new_unchecked::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @"_ZN4core3ptr8non_null16NonNull$LT$T$GT$13new_unchecked18precondition_check17h78c66a39149c7884E"(ptr %ptr) unnamed_addr #0 {
start:
  %_3 = ptrtoint ptr %ptr to i32
  %0 = icmp eq i32 %_3, 0
  br i1 %0, label %bb1, label %bb2

bb1:                                              ; preds = %start
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_560a59ed819b9d9a5841f6e731c4c8e5, i32 210) #10
  unreachable

bb2:                                              ; preds = %start
  ret void
}

; core::hint::assert_unchecked::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @_ZN4core4hint16assert_unchecked18precondition_check17h598dd15f48b19e05E(i1 zeroext %cond) unnamed_addr #0 {
start:
  br i1 %cond, label %bb2, label %bb1

bb1:                                              ; preds = %start
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_64e308ef4babfeb8b6220184de794a17, i32 221) #10
  unreachable

bb2:                                              ; preds = %start
  ret void
}

; core::alloc::layout::Layout::repeat_packed
; Function Attrs: inlinehint nounwind
define internal { i32, i32 } @_ZN4core5alloc6layout6Layout13repeat_packed17hf8f73a8773d9a801E(ptr align 4 %self, i32 %n) unnamed_addr #0 {
start:
  %_3 = alloca [8 x i8], align 4
  %_0 = alloca [8 x i8], align 4
  %0 = getelementptr inbounds i8, ptr %self, i32 4
  %self1 = load i32, ptr %0, align 4
  %1 = call { i32, i1 } @llvm.umul.with.overflow.i32(i32 %self1, i32 %n)
  %_9.0 = extractvalue { i32, i1 } %1, 0
  %_9.1 = extractvalue { i32, i1 } %1, 1
  br i1 %_9.1, label %bb2, label %bb4

bb4:                                              ; preds = %start
  %2 = getelementptr inbounds i8, ptr %_3, i32 4
  store i32 %_9.0, ptr %2, align 4
  store i32 1, ptr %_3, align 4
  %3 = getelementptr inbounds i8, ptr %_3, i32 4
  %size = load i32, ptr %3, align 4
  %align = load i32, ptr %self, align 4
  %_20 = icmp uge i32 %align, 1
  %_21 = icmp ule i32 %align, -2147483648
  %_22 = and i1 %_20, %_21
  %_15 = sub nuw i32 -2147483648, %align
  %_14 = icmp ugt i32 %size, %_15
  br i1 %_14, label %bb6, label %bb7

bb2:                                              ; preds = %start
  %4 = load i32, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %5 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store i32 %4, ptr %_0, align 4
  %6 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %5, ptr %6, align 4
  br label %bb1

bb7:                                              ; preds = %bb4
  store i32 %align, ptr %_0, align 4
  %7 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %size, ptr %7, align 4
  br label %bb5

bb6:                                              ; preds = %bb4
  %8 = load i32, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %9 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store i32 %8, ptr %_0, align 4
  %10 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %9, ptr %10, align 4
  br label %bb5

bb5:                                              ; preds = %bb6, %bb7
  br label %bb1

bb1:                                              ; preds = %bb2, %bb5
  %11 = load i32, ptr %_0, align 4
  %12 = getelementptr inbounds i8, ptr %_0, i32 4
  %13 = load i32, ptr %12, align 4
  %14 = insertvalue { i32, i32 } poison, i32 %11, 0
  %15 = insertvalue { i32, i32 } %14, i32 %13, 1
  ret { i32, i32 } %15
}

; core::alloc::layout::Layout::from_size_align_unchecked::precondition_check
; Function Attrs: inlinehint nounwind
define internal void @_ZN4core5alloc6layout6Layout25from_size_align_unchecked18precondition_check17h4f4b5d99a7f2571dE(i32 %size, i32 %align) unnamed_addr #0 {
start:
; call core::alloc::layout::Layout::is_size_align_valid
  %_3 = call zeroext i1 @_ZN4core5alloc6layout6Layout19is_size_align_valid17hed855bb201b195d2E(i32 %size, i32 %align) #11
  br i1 %_3, label %bb2, label %bb3

bb3:                                              ; preds = %start
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_1be5ea12ba708d9a11b6e93a7d387a75, i32 281) #10
  unreachable

bb2:                                              ; preds = %start
  ret void
}

; core::alloc::layout::Layout::repeat
; Function Attrs: inlinehint nounwind
define internal void @_ZN4core5alloc6layout6Layout6repeat17h3609513819fbfb75E(ptr sret([12 x i8]) align 4 %_0, ptr align 4 %self, i32 %n) unnamed_addr #0 {
start:
  %_8 = alloca [12 x i8], align 4
  %_4 = alloca [8 x i8], align 4
  %padded = alloca [8 x i8], align 4
  %align = load i32, ptr %self, align 4
  %_19 = icmp uge i32 %align, 1
  %_20 = icmp ule i32 %align, -2147483648
  %_21 = and i1 %_19, %_20
  %_12 = sub nuw i32 %align, 1
  %0 = getelementptr inbounds i8, ptr %self, i32 4
  %_15 = load i32, ptr %0, align 4
  %_14 = add nuw i32 %_15, %_12
  %_16 = xor i32 %_12, -1
  %new_size = and i32 %_14, %_16
  br label %bb5

bb5:                                              ; preds = %start
; call core::alloc::layout::Layout::from_size_align_unchecked::precondition_check
  call void @_ZN4core5alloc6layout6Layout25from_size_align_unchecked18precondition_check17h4f4b5d99a7f2571dE(i32 %new_size, i32 %align) #11
  br label %bb6

bb6:                                              ; preds = %bb5
  %1 = getelementptr inbounds i8, ptr %padded, i32 4
  store i32 %new_size, ptr %1, align 4
  store i32 %align, ptr %padded, align 4
; call core::alloc::layout::Layout::repeat_packed
  %2 = call { i32, i32 } @_ZN4core5alloc6layout6Layout13repeat_packed17hf8f73a8773d9a801E(ptr align 4 %padded, i32 %n) #11
  %3 = extractvalue { i32, i32 } %2, 0
  %4 = extractvalue { i32, i32 } %2, 1
  store i32 %3, ptr %_4, align 4
  %5 = getelementptr inbounds i8, ptr %_4, i32 4
  store i32 %4, ptr %5, align 4
  %6 = load i32, ptr %_4, align 4
  %7 = getelementptr inbounds i8, ptr %_4, i32 4
  %8 = load i32, ptr %7, align 4
  %9 = icmp eq i32 %6, 0
  %_6 = select i1 %9, i32 1, i32 0
  %10 = trunc nuw i32 %_6 to i1
  br i1 %10, label %bb3, label %bb2

bb3:                                              ; preds = %bb6
  store i32 0, ptr %_0, align 4
  br label %bb4

bb2:                                              ; preds = %bb6
  %repeated.0 = load i32, ptr %_4, align 4
  %11 = getelementptr inbounds i8, ptr %_4, i32 4
  %repeated.1 = load i32, ptr %11, align 4
  store i32 %repeated.0, ptr %_8, align 4
  %12 = getelementptr inbounds i8, ptr %_8, i32 4
  store i32 %repeated.1, ptr %12, align 4
  %13 = getelementptr inbounds i8, ptr %_8, i32 8
  store i32 %new_size, ptr %13, align 4
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_0, ptr align 4 %_8, i32 12, i1 false)
  br label %bb4

bb4:                                              ; preds = %bb3, %bb2
  ret void

bb7:                                              ; No predecessors!
  unreachable
}

; core::ub_checks::maybe_is_nonoverlapping::runtime
; Function Attrs: inlinehint nounwind
define internal zeroext i1 @_ZN4core9ub_checks23maybe_is_nonoverlapping7runtime17h1e293b6cbf0d2d06E(ptr %src, ptr %dst, i32 %size, i32 %count) unnamed_addr #0 {
start:
  %diff = alloca [4 x i8], align 4
  %_9 = alloca [8 x i8], align 4
  %src_usize = ptrtoint ptr %src to i32
  %dst_usize = ptrtoint ptr %dst to i32
  %0 = call { i32, i1 } @llvm.umul.with.overflow.i32(i32 %size, i32 %count)
  %_14.0 = extractvalue { i32, i1 } %0, 0
  %_14.1 = extractvalue { i32, i1 } %0, 1
  br i1 %_14.1, label %bb1, label %bb3

bb3:                                              ; preds = %start
  %1 = getelementptr inbounds i8, ptr %_9, i32 4
  store i32 %_14.0, ptr %1, align 4
  store i32 1, ptr %_9, align 4
  %2 = getelementptr inbounds i8, ptr %_9, i32 4
  %size1 = load i32, ptr %2, align 4
  %_22 = icmp ult i32 %src_usize, %dst_usize
  br i1 %_22, label %bb4, label %bb5

bb1:                                              ; preds = %start
; call core::panicking::panic_nounwind
  call void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1 @alloc_763310d78c99c2c1ad3f8a9821e942f3, i32 61) #10
  unreachable

bb5:                                              ; preds = %bb3
  %3 = sub i32 %src_usize, %dst_usize
  store i32 %3, ptr %diff, align 4
  br label %bb6

bb4:                                              ; preds = %bb3
  %4 = sub i32 %dst_usize, %src_usize
  store i32 %4, ptr %diff, align 4
  br label %bb6

bb6:                                              ; preds = %bb4, %bb5
  %_11 = load i32, ptr %diff, align 4
  %_0 = icmp uge i32 %_11, %size1
  ret i1 %_0
}

; alloc::fmt::format
; Function Attrs: inlinehint nounwind
define internal void @_ZN5alloc3fmt6format17h88eb5f9a1ada718eE(ptr sret([12 x i8]) align 4 %_0, ptr align 4 %args) unnamed_addr #0 {
start:
  %0 = alloca [24 x i8], align 4
  %default = alloca [4 x i8], align 4
  %bytes = alloca [12 x i8], align 4
  %_4 = alloca [4 x i8], align 4
  %self = alloca [8 x i8], align 4
  %_5.0 = load ptr, ptr %args, align 4
  %1 = getelementptr inbounds i8, ptr %args, i32 4
  %_5.1 = load i32, ptr %1, align 4
  %2 = getelementptr inbounds i8, ptr %args, i32 8
  %_6.0 = load ptr, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %2, i32 4
  %_6.1 = load i32, ptr %3, align 4
  %4 = icmp eq i32 %_5.1, 0
  br i1 %4, label %bb2, label %bb3

bb2:                                              ; preds = %start
  %5 = icmp eq i32 %_6.1, 0
  br i1 %5, label %bb6, label %bb1

bb3:                                              ; preds = %start
  %6 = icmp eq i32 %_5.1, 1
  br i1 %6, label %bb4, label %bb1

bb6:                                              ; preds = %bb2
  store ptr inttoptr (i32 1 to ptr), ptr %self, align 4
  %7 = getelementptr inbounds i8, ptr %self, i32 4
  store i32 0, ptr %7, align 4
  store ptr %args, ptr %_4, align 4
  %8 = load ptr, ptr %_4, align 4
  store ptr %8, ptr %default, align 4
  br label %bb8

bb1:                                              ; preds = %bb4, %bb3, %bb2
  %9 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %10 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store ptr %9, ptr %self, align 4
  %11 = getelementptr inbounds i8, ptr %self, i32 4
  store i32 %10, ptr %11, align 4
  store ptr %args, ptr %_4, align 4
  %12 = load ptr, ptr %_4, align 4
  store ptr %12, ptr %default, align 4
  %_15 = load ptr, ptr %_4, align 4
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %0, ptr align 4 %args, i32 24, i1 false)
; call alloc::fmt::format::format_inner
  call void @_ZN5alloc3fmt6format12format_inner17h34e78af4a048b0bbE(ptr sret([12 x i8]) align 4 %_0, ptr align 4 %0) #11
  br label %bb7

bb8:                                              ; preds = %bb5, %bb6
  %t.0 = load ptr, ptr %self, align 4
  %13 = getelementptr inbounds i8, ptr %self, i32 4
  %t.1 = load i32, ptr %13, align 4
; call <T as alloc::slice::<impl [T]>::to_vec_in::ConvertVec>::to_vec
  call void @"_ZN87_$LT$T$u20$as$u20$alloc..slice..$LT$impl$u20$$u5b$T$u5d$$GT$..to_vec_in..ConvertVec$GT$6to_vec17h53f07e914af56208E"(ptr sret([12 x i8]) align 4 %bytes, ptr align 1 %t.0, i32 %t.1) #11
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_0, ptr align 4 %bytes, i32 12, i1 false)
  br label %bb7

bb4:                                              ; preds = %bb3
  %14 = icmp eq i32 %_6.1, 0
  br i1 %14, label %bb5, label %bb1

bb5:                                              ; preds = %bb4
  %s = getelementptr inbounds nuw { ptr, i32 }, ptr %_5.0, i32 0
  %15 = getelementptr inbounds nuw { ptr, i32 }, ptr %_5.0, i32 0
  %_11.0 = load ptr, ptr %15, align 4
  %16 = getelementptr inbounds i8, ptr %15, i32 4
  %_11.1 = load i32, ptr %16, align 4
  store ptr %_11.0, ptr %self, align 4
  %17 = getelementptr inbounds i8, ptr %self, i32 4
  store i32 %_11.1, ptr %17, align 4
  store ptr %args, ptr %_4, align 4
  %18 = load ptr, ptr %_4, align 4
  store ptr %18, ptr %default, align 4
  br label %bb8

bb7:                                              ; preds = %bb1, %bb8
  ret void
}

; alloc::alloc::alloc_zeroed
; Function Attrs: inlinehint nounwind
define internal ptr @_ZN5alloc5alloc12alloc_zeroed17h1305337230548dc8E(i32 %0, i32 %1) unnamed_addr #0 {
start:
  %2 = alloca [1 x i8], align 1
  %layout = alloca [8 x i8], align 4
  store i32 %0, ptr %layout, align 4
  %3 = getelementptr inbounds i8, ptr %layout, i32 4
  store i32 %1, ptr %3, align 4
  br label %bb3

bb3:                                              ; preds = %start
; call core::ptr::read_volatile::precondition_check
  call void @_ZN4core3ptr13read_volatile18precondition_check17he9b2a04ca31f5f2eE(ptr @__rust_no_alloc_shim_is_unstable, i32 1, i1 zeroext false) #11
  br label %bb5

bb5:                                              ; preds = %bb3
  %4 = load volatile i8, ptr @__rust_no_alloc_shim_is_unstable, align 1
  store i8 %4, ptr %2, align 1
  %_2 = load i8, ptr %2, align 1
  %5 = getelementptr inbounds i8, ptr %layout, i32 4
  %_3 = load i32, ptr %5, align 4
  %_10 = load i32, ptr %layout, align 4
  %_13 = icmp uge i32 %_10, 1
  %_14 = icmp ule i32 %_10, -2147483648
  %_15 = and i1 %_13, %_14
; call __rustc::__rust_alloc_zeroed
  %_0 = call ptr @_RNvCs48KNVeGuvi1_7___rustc19___rust_alloc_zeroed(i32 %_3, i32 %_10) #11
  ret ptr %_0
}

; alloc::alloc::alloc
; Function Attrs: inlinehint nounwind
define internal ptr @_ZN5alloc5alloc5alloc17hf28d01eacfd0688bE(i32 %0, i32 %1) unnamed_addr #0 {
start:
  %2 = alloca [1 x i8], align 1
  %layout = alloca [8 x i8], align 4
  store i32 %0, ptr %layout, align 4
  %3 = getelementptr inbounds i8, ptr %layout, i32 4
  store i32 %1, ptr %3, align 4
  br label %bb3

bb3:                                              ; preds = %start
; call core::ptr::read_volatile::precondition_check
  call void @_ZN4core3ptr13read_volatile18precondition_check17he9b2a04ca31f5f2eE(ptr @__rust_no_alloc_shim_is_unstable, i32 1, i1 zeroext false) #11
  br label %bb5

bb5:                                              ; preds = %bb3
  %4 = load volatile i8, ptr @__rust_no_alloc_shim_is_unstable, align 1
  store i8 %4, ptr %2, align 1
  %_2 = load i8, ptr %2, align 1
  %5 = getelementptr inbounds i8, ptr %layout, i32 4
  %_3 = load i32, ptr %5, align 4
  %_10 = load i32, ptr %layout, align 4
  %_13 = icmp uge i32 %_10, 1
  %_14 = icmp ule i32 %_10, -2147483648
  %_15 = and i1 %_13, %_14
; call __rustc::__rust_alloc
  %_0 = call ptr @_RNvCs48KNVeGuvi1_7___rustc12___rust_alloc(i32 %_3, i32 %_10) #11
  ret ptr %_0
}

; alloc::alloc::Global::alloc_impl
; Function Attrs: inlinehint nounwind
define internal { ptr, i32 } @_ZN5alloc5alloc6Global10alloc_impl17h027ab172788223e0E(ptr align 1 %self, i32 %0, i32 %1, i1 zeroext %zeroed) unnamed_addr #0 {
start:
  %self2 = alloca [4 x i8], align 4
  %self1 = alloca [4 x i8], align 4
  %_10 = alloca [4 x i8], align 4
  %raw_ptr = alloca [4 x i8], align 4
  %_0 = alloca [8 x i8], align 4
  %layout = alloca [8 x i8], align 4
  store i32 %0, ptr %layout, align 4
  %2 = getelementptr inbounds i8, ptr %layout, i32 4
  store i32 %1, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %layout, i32 4
  %size = load i32, ptr %3, align 4
  %4 = icmp eq i32 %size, 0
  br i1 %4, label %bb2, label %bb1

bb2:                                              ; preds = %start
  %_17 = load i32, ptr %layout, align 4
  %_18 = getelementptr i8, ptr null, i32 %_17
  %data = getelementptr i8, ptr null, i32 %_17
  br label %bb7

bb1:                                              ; preds = %start
  br i1 %zeroed, label %bb3, label %bb4

bb7:                                              ; preds = %bb2
  %_23 = getelementptr i8, ptr null, i32 %_17
; call core::ptr::non_null::NonNull<T>::new_unchecked::precondition_check
  call void @"_ZN4core3ptr8non_null16NonNull$LT$T$GT$13new_unchecked18precondition_check17h78c66a39149c7884E"(ptr %_23) #11
  br label %bb9

bb9:                                              ; preds = %bb7
  store ptr %data, ptr %_0, align 4
  %5 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 0, ptr %5, align 4
  br label %bb6

bb6:                                              ; preds = %bb17, %bb10, %bb9
  %6 = load ptr, ptr %_0, align 4
  %7 = getelementptr inbounds i8, ptr %_0, i32 4
  %8 = load i32, ptr %7, align 4
  %9 = insertvalue { ptr, i32 } poison, ptr %6, 0
  %10 = insertvalue { ptr, i32 } %9, i32 %8, 1
  ret { ptr, i32 } %10

bb4:                                              ; preds = %bb1
  %11 = load i32, ptr %layout, align 4
  %12 = getelementptr inbounds i8, ptr %layout, i32 4
  %13 = load i32, ptr %12, align 4
; call alloc::alloc::alloc
  %14 = call ptr @_ZN5alloc5alloc5alloc17hf28d01eacfd0688bE(i32 %11, i32 %13) #11
  store ptr %14, ptr %raw_ptr, align 4
  br label %bb5

bb3:                                              ; preds = %bb1
  %15 = load i32, ptr %layout, align 4
  %16 = getelementptr inbounds i8, ptr %layout, i32 4
  %17 = load i32, ptr %16, align 4
; call alloc::alloc::alloc_zeroed
  %18 = call ptr @_ZN5alloc5alloc12alloc_zeroed17h1305337230548dc8E(i32 %15, i32 %17) #11
  store ptr %18, ptr %raw_ptr, align 4
  br label %bb5

bb5:                                              ; preds = %bb3, %bb4
  %ptr = load ptr, ptr %raw_ptr, align 4
  %_27 = ptrtoint ptr %ptr to i32
  %19 = icmp eq i32 %_27, 0
  br i1 %19, label %bb10, label %bb11

bb10:                                             ; preds = %bb5
  store ptr null, ptr %self2, align 4
  store ptr null, ptr %self1, align 4
  %20 = load ptr, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %21 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store ptr %20, ptr %_0, align 4
  %22 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %21, ptr %22, align 4
  br label %bb6

bb11:                                             ; preds = %bb5
  br label %bb12

bb12:                                             ; preds = %bb11
; call core::ptr::non_null::NonNull<T>::new_unchecked::precondition_check
  call void @"_ZN4core3ptr8non_null16NonNull$LT$T$GT$13new_unchecked18precondition_check17h78c66a39149c7884E"(ptr %ptr) #11
  br label %bb14

bb14:                                             ; preds = %bb12
  store ptr %ptr, ptr %self2, align 4
  %v = load ptr, ptr %self2, align 4
  store ptr %v, ptr %self1, align 4
  %v3 = load ptr, ptr %self1, align 4
  store ptr %v3, ptr %_10, align 4
  %ptr4 = load ptr, ptr %_10, align 4
  br label %bb15

bb15:                                             ; preds = %bb14
; call core::ptr::non_null::NonNull<T>::new_unchecked::precondition_check
  call void @"_ZN4core3ptr8non_null16NonNull$LT$T$GT$13new_unchecked18precondition_check17h78c66a39149c7884E"(ptr %ptr4) #11
  br label %bb17

bb17:                                             ; preds = %bb15
  store ptr %ptr4, ptr %_0, align 4
  %23 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %size, ptr %23, align 4
  br label %bb6
}

; alloc::raw_vec::RawVecInner<A>::deallocate
; Function Attrs: nounwind
define dso_local void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$10deallocate17h7bc40ca1d1ad6066E"(ptr align 4 %self, i32 %elem_layout.0, i32 %elem_layout.1) unnamed_addr #2 {
start:
  %_3 = alloca [12 x i8], align 4
; call alloc::raw_vec::RawVecInner<A>::current_memory
  call void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$14current_memory17hf8af6dc6b72bc954E"(ptr sret([12 x i8]) align 4 %_3, ptr align 4 %self, i32 %elem_layout.0, i32 %elem_layout.1) #11
  %0 = getelementptr inbounds i8, ptr %_3, i32 4
  %1 = load i32, ptr %0, align 4
  %2 = icmp eq i32 %1, 0
  %_5 = select i1 %2, i32 0, i32 1
  %3 = trunc nuw i32 %_5 to i1
  br i1 %3, label %bb2, label %bb4

bb2:                                              ; preds = %start
  %ptr = load ptr, ptr %_3, align 4
  %4 = getelementptr inbounds i8, ptr %_3, i32 4
  %layout.0 = load i32, ptr %4, align 4
  %5 = getelementptr inbounds i8, ptr %4, i32 4
  %layout.1 = load i32, ptr %5, align 4
  %_9 = getelementptr inbounds i8, ptr %self, i32 8
; call <alloc::alloc::Global as core::alloc::Allocator>::deallocate
  call void @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$10deallocate17he554ae16eded44dfE"(ptr align 1 %_9, ptr %ptr, i32 %layout.0, i32 %layout.1) #11
  br label %bb5

bb4:                                              ; preds = %start
  br label %bb5

bb5:                                              ; preds = %bb4, %bb2
  ret void

bb6:                                              ; No predecessors!
  unreachable
}

; alloc::raw_vec::RawVecInner<A>::current_memory
; Function Attrs: inlinehint nounwind
define dso_local void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$14current_memory17hf8af6dc6b72bc954E"(ptr sret([12 x i8]) align 4 %_0, ptr align 4 %self, i32 %0, i32 %1) unnamed_addr #0 {
start:
  %_15 = alloca [12 x i8], align 4
  %align = alloca [4 x i8], align 4
  %alloc_size = alloca [4 x i8], align 4
  %elem_layout = alloca [8 x i8], align 4
  store i32 %0, ptr %elem_layout, align 4
  %2 = getelementptr inbounds i8, ptr %elem_layout, i32 4
  store i32 %1, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %elem_layout, i32 4
  %self1 = load i32, ptr %3, align 4
  %4 = icmp eq i32 %self1, 0
  br i1 %4, label %bb3, label %bb1

bb3:                                              ; preds = %bb2, %start
  %5 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 0, ptr %5, align 4
  br label %bb5

bb1:                                              ; preds = %start
  %self2 = load i32, ptr %self, align 4
  %6 = icmp eq i32 %self2, 0
  br i1 %6, label %bb2, label %bb4

bb2:                                              ; preds = %bb1
  br label %bb3

bb4:                                              ; preds = %bb1
  %self3 = load i32, ptr %self, align 4
  br label %bb6

bb5:                                              ; preds = %bb9, %bb3
  ret void

bb6:                                              ; preds = %bb4
; call core::num::<impl usize>::unchecked_mul::precondition_check
  call void @"_ZN4core3num23_$LT$impl$u20$usize$GT$13unchecked_mul18precondition_check17hfc0f297104534aabE"(i32 %self1, i32 %self3) #11
  %7 = mul nuw i32 %self1, %self3
  store i32 %7, ptr %alloc_size, align 4
  %size = load i32, ptr %alloc_size, align 4
  %_18 = load i32, ptr %elem_layout, align 4
  %_21 = icmp uge i32 %_18, 1
  %_22 = icmp ule i32 %_18, -2147483648
  %_23 = and i1 %_21, %_22
  store i32 %_18, ptr %align, align 4
  br label %bb8

bb8:                                              ; preds = %bb6
  %8 = load i32, ptr %alloc_size, align 4
  %9 = load i32, ptr %align, align 4
; call core::alloc::layout::Layout::from_size_align_unchecked::precondition_check
  call void @_ZN4core5alloc6layout6Layout25from_size_align_unchecked18precondition_check17h4f4b5d99a7f2571dE(i32 %8, i32 %9) #11
  br label %bb9

bb9:                                              ; preds = %bb8
  %_25 = load i32, ptr %align, align 4
  %layout.1 = load i32, ptr %alloc_size, align 4
  %10 = getelementptr inbounds i8, ptr %self, i32 4
  %self4 = load ptr, ptr %10, align 4
  store ptr %self4, ptr %_15, align 4
  %11 = getelementptr inbounds i8, ptr %_15, i32 4
  store i32 %_25, ptr %11, align 4
  %12 = getelementptr inbounds i8, ptr %11, i32 4
  store i32 %layout.1, ptr %12, align 4
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_0, ptr align 4 %_15, i32 12, i1 false)
  br label %bb5

bb7:                                              ; No predecessors!
  unreachable
}

; alloc::raw_vec::RawVecInner<A>::try_allocate_in
; Function Attrs: nounwind
define dso_local void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$15try_allocate_in17hb54d0434a32fd4ebE"(ptr sret([12 x i8]) align 4 %_0, i32 %capacity, i1 zeroext %init, i32 %0, i32 %1) unnamed_addr #2 {
start:
  %self3 = alloca [12 x i8], align 4
  %self2 = alloca [8 x i8], align 4
  %self = alloca [8 x i8], align 4
  %result = alloca [8 x i8], align 4
  %_15 = alloca [8 x i8], align 4
  %elem_layout1 = alloca [8 x i8], align 4
  %_6 = alloca [12 x i8], align 4
  %layout = alloca [8 x i8], align 4
  %elem_layout = alloca [8 x i8], align 4
  %alloc = alloca [0 x i8], align 1
  store i32 %0, ptr %elem_layout, align 4
  %2 = getelementptr inbounds i8, ptr %elem_layout, i32 4
  store i32 %1, ptr %2, align 4
  %3 = load i32, ptr %elem_layout, align 4
  %4 = getelementptr inbounds i8, ptr %elem_layout, i32 4
  %5 = load i32, ptr %4, align 4
  store i32 %3, ptr %elem_layout1, align 4
  %6 = getelementptr inbounds i8, ptr %elem_layout1, i32 4
  store i32 %5, ptr %6, align 4
; call core::alloc::layout::Layout::repeat
  call void @_ZN4core5alloc6layout6Layout6repeat17h3609513819fbfb75E(ptr sret([12 x i8]) align 4 %self3, ptr align 4 %elem_layout1, i32 %capacity) #11
  %7 = load i32, ptr %self3, align 4
  %8 = icmp eq i32 %7, 0
  %_35 = select i1 %8, i32 1, i32 0
  %9 = trunc nuw i32 %_35 to i1
  br i1 %9, label %bb15, label %bb16

bb15:                                             ; preds = %start
  %10 = load i32, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %11 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store i32 %10, ptr %self2, align 4
  %12 = getelementptr inbounds i8, ptr %self2, i32 4
  store i32 %11, ptr %12, align 4
  %13 = load i32, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %14 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  %15 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %13, ptr %15, align 4
  %16 = getelementptr inbounds i8, ptr %15, i32 4
  store i32 %14, ptr %16, align 4
  store i32 1, ptr %_0, align 4
  br label %bb13

bb16:                                             ; preds = %start
  %t.0 = load i32, ptr %self3, align 4
  %17 = getelementptr inbounds i8, ptr %self3, i32 4
  %t.1 = load i32, ptr %17, align 4
  %18 = getelementptr inbounds i8, ptr %self3, i32 8
  %t = load i32, ptr %18, align 4
  store i32 %t.0, ptr %self2, align 4
  %19 = getelementptr inbounds i8, ptr %self2, i32 4
  store i32 %t.1, ptr %19, align 4
  %t.04 = load i32, ptr %self2, align 4
  %20 = getelementptr inbounds i8, ptr %self2, i32 4
  %t.15 = load i32, ptr %20, align 4
  %21 = getelementptr inbounds i8, ptr %_6, i32 4
  store i32 %t.04, ptr %21, align 4
  %22 = getelementptr inbounds i8, ptr %21, i32 4
  store i32 %t.15, ptr %22, align 4
  store i32 0, ptr %_6, align 4
  %23 = getelementptr inbounds i8, ptr %_6, i32 4
  %layout.0 = load i32, ptr %23, align 4
  %24 = getelementptr inbounds i8, ptr %23, i32 4
  %layout.1 = load i32, ptr %24, align 4
  store i32 %layout.0, ptr %layout, align 4
  %25 = getelementptr inbounds i8, ptr %layout, i32 4
  store i32 %layout.1, ptr %25, align 4
  %26 = icmp eq i32 %layout.1, 0
  br i1 %26, label %bb2, label %bb3

bb2:                                              ; preds = %bb16
  %align = load i32, ptr %elem_layout, align 4
  %_42 = getelementptr i8, ptr null, i32 %align
  %27 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 0, ptr %27, align 4
  %28 = getelementptr inbounds i8, ptr %27, i32 4
  store ptr %_42, ptr %28, align 4
  store i32 0, ptr %_0, align 4
  br label %bb12

bb3:                                              ; preds = %bb16
  %_43 = icmp ugt i32 %layout.1, 2147483647
  br i1 %_43, label %bb17, label %bb18

bb12:                                             ; preds = %bb13, %bb10, %bb2
  ret void

bb18:                                             ; preds = %bb3
  %_19 = zext i1 %init to i32
  %29 = trunc nuw i32 %_19 to i1
  br i1 %29, label %bb4, label %bb5

bb17:                                             ; preds = %bb3
  %30 = load i32, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, align 4
  %31 = load i32, ptr getelementptr inbounds (i8, ptr @anon.55aae19ebcedabc58c8463847838c69e.0, i32 4), align 4
  store i32 %30, ptr %_15, align 4
  %32 = getelementptr inbounds i8, ptr %_15, i32 4
  store i32 %31, ptr %32, align 4
  %err.0 = load i32, ptr %_15, align 4
  %33 = getelementptr inbounds i8, ptr %_15, i32 4
  %err.1 = load i32, ptr %33, align 4
  %34 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %err.0, ptr %34, align 4
  %35 = getelementptr inbounds i8, ptr %34, i32 4
  store i32 %err.1, ptr %35, align 4
  store i32 1, ptr %_0, align 4
  br label %bb11

bb4:                                              ; preds = %bb18
; call <alloc::alloc::Global as core::alloc::Allocator>::allocate_zeroed
  %36 = call { ptr, i32 } @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$15allocate_zeroed17h04cbd4f643216685E"(ptr align 1 %alloc, i32 %layout.0, i32 %layout.1) #11
  %37 = extractvalue { ptr, i32 } %36, 0
  %38 = extractvalue { ptr, i32 } %36, 1
  store ptr %37, ptr %result, align 4
  %39 = getelementptr inbounds i8, ptr %result, i32 4
  store i32 %38, ptr %39, align 4
  br label %bb8

bb5:                                              ; preds = %bb18
; call <alloc::alloc::Global as core::alloc::Allocator>::allocate
  %40 = call { ptr, i32 } @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$8allocate17hd9323629189a0440E"(ptr align 1 %alloc, i32 %layout.0, i32 %layout.1) #11
  %41 = extractvalue { ptr, i32 } %40, 0
  %42 = extractvalue { ptr, i32 } %40, 1
  store ptr %41, ptr %result, align 4
  %43 = getelementptr inbounds i8, ptr %result, i32 4
  store i32 %42, ptr %43, align 4
  br label %bb8

bb8:                                              ; preds = %bb4, %bb5
  %44 = load ptr, ptr %result, align 4
  %45 = getelementptr inbounds i8, ptr %result, i32 4
  %46 = load i32, ptr %45, align 4
  %47 = ptrtoint ptr %44 to i32
  %48 = icmp eq i32 %47, 0
  %_22 = select i1 %48, i32 1, i32 0
  %49 = trunc nuw i32 %_22 to i1
  br i1 %49, label %bb9, label %bb10

bb9:                                              ; preds = %bb8
  store i32 %layout.0, ptr %self, align 4
  %50 = getelementptr inbounds i8, ptr %self, i32 4
  store i32 %layout.1, ptr %50, align 4
  %_24.0 = load i32, ptr %self, align 4
  %51 = getelementptr inbounds i8, ptr %self, i32 4
  %_24.1 = load i32, ptr %51, align 4
  %52 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %_24.0, ptr %52, align 4
  %53 = getelementptr inbounds i8, ptr %52, i32 4
  store i32 %_24.1, ptr %53, align 4
  store i32 1, ptr %_0, align 4
  br label %bb11

bb10:                                             ; preds = %bb8
  %ptr.0 = load ptr, ptr %result, align 4
  %54 = getelementptr inbounds i8, ptr %result, i32 4
  %ptr.1 = load i32, ptr %54, align 4
  %55 = getelementptr inbounds i8, ptr %_0, i32 4
  store i32 %capacity, ptr %55, align 4
  %56 = getelementptr inbounds i8, ptr %55, i32 4
  store ptr %ptr.0, ptr %56, align 4
  store i32 0, ptr %_0, align 4
  br label %bb12

bb11:                                             ; preds = %bb17, %bb9
  br label %bb13

bb13:                                             ; preds = %bb15, %bb11
  br label %bb12

bb1:                                              ; No predecessors!
  unreachable
}

; alloc::raw_vec::RawVecInner<A>::with_capacity_in
; Function Attrs: inlinehint nounwind
define dso_local { i32, ptr } @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$16with_capacity_in17h74de0e3ef2349115E"(i32 %capacity, i32 %elem_layout.0, i32 %elem_layout.1, ptr align 4 %0) unnamed_addr #0 {
start:
  %self = alloca [4 x i8], align 4
  %elem_layout = alloca [8 x i8], align 4
  %this = alloca [8 x i8], align 4
  %_4 = alloca [12 x i8], align 4
; call alloc::raw_vec::RawVecInner<A>::try_allocate_in
  call void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$15try_allocate_in17hb54d0434a32fd4ebE"(ptr sret([12 x i8]) align 4 %_4, i32 %capacity, i1 zeroext false, i32 %elem_layout.0, i32 %elem_layout.1) #11
  %_5 = load i32, ptr %_4, align 4
  %1 = trunc nuw i32 %_5 to i1
  br i1 %1, label %bb3, label %bb4

bb3:                                              ; preds = %start
  %2 = getelementptr inbounds i8, ptr %_4, i32 4
  %err.0 = load i32, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %2, i32 4
  %err.1 = load i32, ptr %3, align 4
; call alloc::raw_vec::handle_error
  call void @_ZN5alloc7raw_vec12handle_error17h9443db7f79c7229aE(i32 %err.0, i32 %err.1, ptr align 4 %0) #10
  unreachable

bb4:                                              ; preds = %start
  %4 = getelementptr inbounds i8, ptr %_4, i32 4
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds i8, ptr %4, i32 4
  %7 = load ptr, ptr %6, align 4
  store i32 %5, ptr %this, align 4
  %8 = getelementptr inbounds i8, ptr %this, i32 4
  store ptr %7, ptr %8, align 4
  store i32 %elem_layout.0, ptr %elem_layout, align 4
  %9 = getelementptr inbounds i8, ptr %elem_layout, i32 4
  store i32 %elem_layout.1, ptr %9, align 4
  %10 = icmp eq i32 %elem_layout.1, 0
  br i1 %10, label %bb6, label %bb7

bb6:                                              ; preds = %bb4
  store i32 -1, ptr %self, align 4
  br label %bb5

bb7:                                              ; preds = %bb4
  %self1 = load i32, ptr %this, align 4
  store i32 %self1, ptr %self, align 4
  br label %bb5

bb5:                                              ; preds = %bb7, %bb6
  %11 = load i32, ptr %self, align 4
  %_13 = sub i32 %11, 0
  %_8 = icmp ugt i32 %capacity, %_13
  %cond = xor i1 %_8, true
  br label %bb8

bb8:                                              ; preds = %bb5
; call core::hint::assert_unchecked::precondition_check
  call void @_ZN4core4hint16assert_unchecked18precondition_check17h598dd15f48b19e05E(i1 zeroext %cond) #11
  br label %bb9

bb9:                                              ; preds = %bb8
  %_0.0 = load i32, ptr %this, align 4
  %12 = getelementptr inbounds i8, ptr %this, i32 4
  %_0.1 = load ptr, ptr %12, align 4
  %13 = insertvalue { i32, ptr } poison, i32 %_0.0, 0
  %14 = insertvalue { i32, ptr } %13, ptr %_0.1, 1
  ret { i32, ptr } %14

bb2:                                              ; No predecessors!
  unreachable
}

; <alloc::alloc::Global as core::alloc::Allocator>::deallocate
; Function Attrs: inlinehint nounwind
define internal void @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$10deallocate17he554ae16eded44dfE"(ptr align 1 %self, ptr %ptr, i32 %0, i32 %1) unnamed_addr #0 {
start:
  %layout1 = alloca [8 x i8], align 4
  %layout = alloca [8 x i8], align 4
  store i32 %0, ptr %layout, align 4
  %2 = getelementptr inbounds i8, ptr %layout, i32 4
  store i32 %1, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %layout, i32 4
  %_4 = load i32, ptr %3, align 4
  %4 = icmp eq i32 %_4, 0
  br i1 %4, label %bb2, label %bb1

bb2:                                              ; preds = %bb1, %start
  ret void

bb1:                                              ; preds = %start
  %5 = load i32, ptr %layout, align 4
  %6 = getelementptr inbounds i8, ptr %layout, i32 4
  %7 = load i32, ptr %6, align 4
  store i32 %5, ptr %layout1, align 4
  %8 = getelementptr inbounds i8, ptr %layout1, i32 4
  store i32 %7, ptr %8, align 4
  %_11 = load i32, ptr %layout, align 4
  %_14 = icmp uge i32 %_11, 1
  %_15 = icmp ule i32 %_11, -2147483648
  %_16 = and i1 %_14, %_15
; call __rustc::__rust_dealloc
  call void @_RNvCs48KNVeGuvi1_7___rustc14___rust_dealloc(ptr %ptr, i32 %_4, i32 %_11) #11
  br label %bb2
}

; <alloc::alloc::Global as core::alloc::Allocator>::allocate_zeroed
; Function Attrs: inlinehint nounwind
define internal { ptr, i32 } @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$15allocate_zeroed17h04cbd4f643216685E"(ptr align 1 %self, i32 %layout.0, i32 %layout.1) unnamed_addr #0 {
start:
; call alloc::alloc::Global::alloc_impl
  %0 = call { ptr, i32 } @_ZN5alloc5alloc6Global10alloc_impl17h027ab172788223e0E(ptr align 1 %self, i32 %layout.0, i32 %layout.1, i1 zeroext true) #11
  %_0.0 = extractvalue { ptr, i32 } %0, 0
  %_0.1 = extractvalue { ptr, i32 } %0, 1
  %1 = insertvalue { ptr, i32 } poison, ptr %_0.0, 0
  %2 = insertvalue { ptr, i32 } %1, i32 %_0.1, 1
  ret { ptr, i32 } %2
}

; <alloc::alloc::Global as core::alloc::Allocator>::allocate
; Function Attrs: inlinehint nounwind
define internal { ptr, i32 } @"_ZN63_$LT$alloc..alloc..Global$u20$as$u20$core..alloc..Allocator$GT$8allocate17hd9323629189a0440E"(ptr align 1 %self, i32 %layout.0, i32 %layout.1) unnamed_addr #0 {
start:
; call alloc::alloc::Global::alloc_impl
  %0 = call { ptr, i32 } @_ZN5alloc5alloc6Global10alloc_impl17h027ab172788223e0E(ptr align 1 %self, i32 %layout.0, i32 %layout.1, i1 zeroext false) #11
  %_0.0 = extractvalue { ptr, i32 } %0, 0
  %_0.1 = extractvalue { ptr, i32 } %0, 1
  %1 = insertvalue { ptr, i32 } poison, ptr %_0.0, 0
  %2 = insertvalue { ptr, i32 } %1, i32 %_0.1, 1
  ret { ptr, i32 } %2
}

; <alloc::vec::Vec<T,A> as core::ops::drop::Drop>::drop
; Function Attrs: nounwind
define dso_local void @"_ZN70_$LT$alloc..vec..Vec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h7f645b41a7ab76bcE"(ptr align 4 %self) unnamed_addr #2 {
start:
  %_6 = alloca [4 x i8], align 4
  %0 = getelementptr inbounds i8, ptr %self, i32 4
  %_5 = load ptr, ptr %0, align 4
  %1 = getelementptr inbounds i8, ptr %self, i32 8
  %len = load i32, ptr %1, align 4
  store i32 0, ptr %_6, align 4
  br label %bb3

bb3:                                              ; preds = %bb2, %start
  %2 = load i32, ptr %_6, align 4
  %_8 = icmp eq i32 %2, %len
  br i1 %_8, label %bb1, label %bb2

bb2:                                              ; preds = %bb3
  %3 = load i32, ptr %_6, align 4
  %_7 = getelementptr inbounds nuw i8, ptr %_5, i32 %3
  %4 = load i32, ptr %_6, align 4
  %5 = add i32 %4, 1
  store i32 %5, ptr %_6, align 4
  br label %bb3

bb1:                                              ; preds = %bb3
  ret void
}

; <alloc::raw_vec::RawVec<T,A> as core::ops::drop::Drop>::drop
; Function Attrs: nounwind
define dso_local void @"_ZN77_$LT$alloc..raw_vec..RawVec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h6e18edbe1264ccc5E"(ptr align 4 %self) unnamed_addr #2 {
start:
; call alloc::raw_vec::RawVecInner<A>::deallocate
  call void @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$10deallocate17h7bc40ca1d1ad6066E"(ptr align 4 %self, i32 1, i32 1) #11
  ret void
}

; <T as alloc::slice::<impl [T]>::to_vec_in::ConvertVec>::to_vec
; Function Attrs: inlinehint nounwind
define dso_local void @"_ZN87_$LT$T$u20$as$u20$alloc..slice..$LT$impl$u20$$u5b$T$u5d$$GT$..to_vec_in..ConvertVec$GT$6to_vec17h53f07e914af56208E"(ptr sret([12 x i8]) align 4 %_0, ptr align 1 %s.0, i32 %s.1) unnamed_addr #0 {
start:
  %v = alloca [12 x i8], align 4
; call alloc::raw_vec::RawVecInner<A>::with_capacity_in
  %0 = call { i32, ptr } @"_ZN5alloc7raw_vec20RawVecInner$LT$A$GT$16with_capacity_in17h74de0e3ef2349115E"(i32 %s.1, i32 1, i32 1, ptr align 4 @alloc_7fed0d2a227741441efda167863bf4e6) #11
  %_10.0 = extractvalue { i32, ptr } %0, 0
  %_10.1 = extractvalue { i32, ptr } %0, 1
  store i32 %_10.0, ptr %v, align 4
  %1 = getelementptr inbounds i8, ptr %v, i32 4
  store ptr %_10.1, ptr %1, align 4
  %2 = getelementptr inbounds i8, ptr %v, i32 8
  store i32 0, ptr %2, align 4
  %3 = getelementptr inbounds i8, ptr %v, i32 4
  %_12 = load ptr, ptr %3, align 4
  br label %bb2

bb2:                                              ; preds = %start
; call core::intrinsics::copy_nonoverlapping::precondition_check
  call void @_ZN4core10intrinsics19copy_nonoverlapping18precondition_check17h6d1c9e591616fd81E(ptr %s.0, ptr %_12, i32 1, i32 1, i32 %s.1) #11
  br label %bb4

bb4:                                              ; preds = %bb2
  %4 = mul i32 %s.1, 1
  call void @llvm.memcpy.p0.p0.i32(ptr align 1 %_12, ptr align 1 %s.0, i32 %4, i1 false)
  %5 = getelementptr inbounds i8, ptr %v, i32 8
  store i32 %s.1, ptr %5, align 4
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_0, ptr align 4 %v, i32 12, i1 false)
  ret void
}

; probe1::probe
; Function Attrs: nounwind
define dso_local void @_ZN6probe15probe17h7e70bd15901d44d5E() unnamed_addr #2 {
start:
  %_7 = alloca [8 x i8], align 4
  %_6 = alloca [8 x i8], align 4
  %_3 = alloca [24 x i8], align 4
  %res = alloca [12 x i8], align 4
  %_1 = alloca [12 x i8], align 4
; call core::fmt::rt::Argument::new_lower_exp
  call void @_ZN4core3fmt2rt8Argument13new_lower_exp17ha2863b1ea7e04ef5E(ptr sret([8 x i8]) align 4 %_7, ptr align 4 @alloc_83ea17bf0c4f4a5a5a13d3ae7955acd0) #11
  %0 = getelementptr inbounds nuw %"core::fmt::rt::Argument<'_>", ptr %_6, i32 0
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %0, ptr align 4 %_7, i32 8, i1 false)
; call core::fmt::Arguments::new_v1
  call void @_ZN4core3fmt9Arguments6new_v117h049db3261a56fa77E(ptr sret([24 x i8]) align 4 %_3, ptr align 4 @alloc_4b9523bd3933225a2ba132a1dcbebd94, ptr align 4 %_6) #11
; call alloc::fmt::format
  call void @_ZN5alloc3fmt6format17h88eb5f9a1ada718eE(ptr sret([12 x i8]) align 4 %res, ptr align 4 %_3) #11
  call void @llvm.memcpy.p0.p0.i32(ptr align 4 %_1, ptr align 4 %res, i32 12, i1 false)
; call core::ptr::drop_in_place<alloc::string::String>
  call void @"_ZN4core3ptr42drop_in_place$LT$alloc..string..String$GT$17h51f2dc7a1feb8fc5E"(ptr align 4 %_1) #11
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.ctpop.i32(i32) #3

; core::panicking::panic_fmt
; Function Attrs: cold noinline noreturn nounwind
declare dso_local void @_ZN4core9panicking9panic_fmt17h5b404ce146871bf2E(ptr align 4, ptr align 4) unnamed_addr #4

; core::panicking::panic_nounwind
; Function Attrs: cold noinline noreturn nounwind
declare dso_local void @_ZN4core9panicking14panic_nounwind17hc4b65355a29a8593E(ptr align 1, i32) unnamed_addr #4

; core::fmt::num::imp::<impl core::fmt::LowerExp for isize>::fmt
; Function Attrs: nounwind
declare dso_local zeroext i1 @"_ZN4core3fmt3num3imp55_$LT$impl$u20$core..fmt..LowerExp$u20$for$u20$isize$GT$3fmt17hd3d241c9ee8f214fE"(ptr align 4, ptr align 4) unnamed_addr #2

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i32(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i32, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare { i32, i1 } @llvm.umul.with.overflow.i32(i32, i32) #3

; core::alloc::layout::Layout::is_size_align_valid
; Function Attrs: nounwind
declare dso_local zeroext i1 @_ZN4core5alloc6layout6Layout19is_size_align_valid17hed855bb201b195d2E(i32, i32) unnamed_addr #2

; alloc::fmt::format::format_inner
; Function Attrs: nounwind
declare dso_local void @_ZN5alloc3fmt6format12format_inner17h34e78af4a048b0bbE(ptr sret([12 x i8]) align 4, ptr align 4) unnamed_addr #2

; __rustc::__rust_alloc_zeroed
; Function Attrs: nounwind allockind("alloc,zeroed,aligned") allocsize(0)
declare dso_local noalias ptr @_RNvCs48KNVeGuvi1_7___rustc19___rust_alloc_zeroed(i32, i32 allocalign) unnamed_addr #6

; __rustc::__rust_alloc
; Function Attrs: nounwind allockind("alloc,uninitialized,aligned") allocsize(0)
declare dso_local noalias ptr @_RNvCs48KNVeGuvi1_7___rustc12___rust_alloc(i32, i32 allocalign) unnamed_addr #7

; alloc::raw_vec::handle_error
; Function Attrs: cold minsize noreturn nounwind optsize
declare dso_local void @_ZN5alloc7raw_vec12handle_error17h9443db7f79c7229aE(i32, i32, ptr align 4) unnamed_addr #8

; __rustc::__rust_dealloc
; Function Attrs: nounwind allockind("free")
declare dso_local void @_RNvCs48KNVeGuvi1_7___rustc14___rust_dealloc(ptr allocptr, i32, i32) unnamed_addr #9

attributes #0 = { inlinehint nounwind "target-cpu"="generic" }
attributes #1 = { cold nounwind "target-cpu"="generic" }
attributes #2 = { nounwind "target-cpu"="generic" }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { cold noinline noreturn nounwind "target-cpu"="generic" }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind allockind("alloc,zeroed,aligned") allocsize(0) "alloc-family"="__rust_alloc" "target-cpu"="generic" }
attributes #7 = { nounwind allockind("alloc,uninitialized,aligned") allocsize(0) "alloc-family"="__rust_alloc" "target-cpu"="generic" }
attributes #8 = { cold minsize noreturn nounwind optsize "target-cpu"="generic" }
attributes #9 = { nounwind allockind("free") "alloc-family"="__rust_alloc" "target-cpu"="generic" }
attributes #10 = { noreturn nounwind }
attributes #11 = { nounwind }

!llvm.ident = !{!0}

!0 = !{!"rustc version 1.88.0-nightly (b8c54d635 2025-04-20)"}

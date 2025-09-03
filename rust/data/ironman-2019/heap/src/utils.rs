pub unsafe fn ptr_diff<T>(from: *mut T, to: *mut T) -> usize {
    to as usize - from as usize
}

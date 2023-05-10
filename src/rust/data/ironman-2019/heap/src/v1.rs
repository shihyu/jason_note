use crate::utils;
use std::{
    alloc::{handle_alloc_error, GlobalAlloc, Layout},
    cell::Cell,
    mem,
    ptr::{self, NonNull},
};

const DEFAULT_SIZE: usize = 1024 * 1024 * 8;
const META_SIZE: usize = mem::size_of::<usize>() * 2;

pub struct MyAlloc {
    start: Cell<*mut usize>,
    head: Cell<*mut usize>,
}

unsafe impl Sync for MyAlloc {}

impl MyAlloc {
    pub const fn new() -> Self {
        MyAlloc {
            start: Cell::new(ptr::null_mut()),
            head: Cell::new(ptr::null_mut()),
        }
    }
}

unsafe fn init_arena() -> *mut usize {
    let start = libc::sbrk(0);
    if libc::brk(start.add(DEFAULT_SIZE)) != 0 {
        panic!("brk fail");
    }
    let start = start as *mut usize;
    ptr::write(start, DEFAULT_SIZE - META_SIZE);
    ptr::write(start.add(1), 0); // unused
    ptr::write(start.add(2), 0); // next
    ptr::write(start.add(3), 0); // prev
    start
}

unsafe fn is_used_chunk(chunk: *mut usize) -> bool {
    ptr::read(chunk.add(1)) != 0
}

struct AvailableChunk(*mut usize);

impl Iterator for AvailableChunk {
    type Item = *mut usize;

    fn next(&mut self) -> Option<Self::Item> {
        if self.0 == ptr::null_mut() {
            None
        } else {
            let p = self.0;
            unsafe {
                // this should not happen
                if is_used_chunk(p) {
                    libc::abort();
                }
                let next = ptr::read(p.add(2)) as *mut usize;
                self.0 = next;
            }
            Some(p)
        }
    }
}

unsafe fn split_chunk(
    chunk: *mut usize,
    start: *mut usize,
    size: usize,
) -> (*mut usize, *mut usize) {
    let chunk_size = ptr::read(chunk);
    let used = is_used_chunk(chunk);
    if used {
        libc::puts("used chunk\0".as_ptr() as _);
        libc::abort();
    }
    assert!(chunk_size > size);
    assert!(!used);
    let next = ptr::read(chunk.add(2));
    let prev = ptr::read(chunk.add(3));
    // need align
    if chunk != start {
        let new_size = utils::ptr_diff(chunk, start);
        if new_size < META_SIZE {
            libc::puts("size not enough".as_ptr() as _);
            libc::abort();
        }
        let next_unused = (chunk as *mut u8).add(size + new_size + META_SIZE) as *mut usize;
        let next_size = chunk_size - new_size - size - META_SIZE;

        // split current chunk to get space
        ptr::write(chunk, new_size);
        ptr::write(chunk.add(2), next_unused as usize);

        // init new free chunk
        ptr::write(next_unused, next_size);
        ptr::write(next_unused.add(1), 0);
        ptr::write(next_unused.add(2), next);
        ptr::write(next_unused.add(3), chunk as usize);

        // init allocated chunk
        let allocated_chunk = (chunk as *mut u8).add(new_size) as *mut usize;
        ptr::write(allocated_chunk, size);
        ptr::write(allocated_chunk.add(1), 1);
        (allocated_chunk.add(2), chunk)
    } else {
        // modify current chunk
        ptr::write(chunk, size);
        ptr::write(chunk.add(1), 1);

        // init new free chunk
        let next_size = chunk_size - size - META_SIZE;
        let next_chunk = (chunk as *mut u8).add(size + META_SIZE) as *mut usize;
        ptr::write(next_chunk, next_size);
        ptr::write(next_chunk.add(1), 0);
        ptr::write(next_chunk.add(2), next);
        ptr::write(next_chunk.add(3), prev);
        (chunk.add(2), next_chunk)
    }
}

impl MyAlloc {
    fn init_once(&self) {
        if self.head.get() == ptr::null_mut() {
            unsafe {
                let arena = init_arena();
                self.start.set(arena);
                self.head.set(arena);
            }
        }
    }
}

const MIN_SIZE: usize = mem::size_of::<usize>();

unsafe impl GlobalAlloc for MyAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        self.init_once();
        let mut size = layout.size();
        if size == 0 {
            return NonNull::dangling().as_ptr();
        }
        if size % MIN_SIZE != 0 {
            size = size - (size % MIN_SIZE) + MIN_SIZE;
        }
        let align = layout.align().max(MIN_SIZE);
        for chunk in AvailableChunk(self.head.get()) {
            let chunk_size = ptr::read(chunk);
            if chunk_size < size {
                continue;
            }
            let mut offset = chunk.add(2).align_offset(align);
            if offset == usize::max_value() {
                libc::abort();
            }
            if offset != 0 && offset < 2 {
                offset = chunk.add(4).align_offset(align);
            }
            let start = chunk.add(offset);
            if utils::ptr_diff(chunk, start) + size + META_SIZE > chunk_size {
                continue;
            }
            let (chunk, next_chunk) = split_chunk(chunk, start, size);
            let a = chunk as usize % align;
            if a != 0 {
                libc::puts("unaligned\0".as_ptr() as _);
            }
            self.head.set(next_chunk);
            return chunk as _;
        }
        handle_alloc_error(layout);
    }

    unsafe fn dealloc(&self, p: *mut u8, layout: Layout) {
        if layout.size() == 0 {
            return;
        }
        if p == ptr::null_mut() {
            return;
        }

        let p = (p as *mut usize).sub(2);

        ptr::write(p.add(1), 0);

        let iter = AvailableChunk(self.head.get());
        let mut prev = ptr::null_mut();
        let mut next = ptr::null_mut();
        for chunk in iter {
            if chunk > p {
                next = chunk;
                break;
            } else {
                prev = chunk;
            }
        }

        if prev == ptr::null_mut() {
            let next_chunk = self.head.get();
            assert_eq!(next, next_chunk);
            ptr::write(p.add(2), next_chunk as usize);
            ptr::write(p.add(3), 0);
            ptr::write(next_chunk.add(3), p as usize);
            self.head.set(p);
        } else {
            ptr::write(prev.add(2), p as usize);
            if next != ptr::null_mut() {
                ptr::write(next.add(3), p as usize);
            }
            ptr::write(p.add(2), next as usize);
            ptr::write(p.add(3), prev as usize);
        }
    }
}

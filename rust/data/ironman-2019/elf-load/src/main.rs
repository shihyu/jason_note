use dlopen::raw::Library;
use goblin::elf::{
    program_header::{PF_W, PF_X, PT_LOAD},
    reloc::{R_X86_64_GLOB_DAT, R_X86_64_JUMP_SLOT},
    Elf,
};
use nix::sys::mman::{mmap, mprotect, munmap, MapFlags, ProtFlags};
use once_cell::sync::Lazy;
use std::{env, ffi::c_void, fs, io, mem, ops, ptr, slice};

const SIZE: usize = 1024 * 1024 * 1024;

struct MMap {
    ptr: *mut u8,
    size: usize,
}

impl MMap {
    unsafe fn new(size: usize, protect: ProtFlags, flag: MapFlags) -> Self {
        let ptr = mmap(ptr::null_mut(), size, protect, flag, 0, 0).unwrap() as *mut u8;
        if ptr == ptr::null_mut() {
            panic!("mmap fail");
        }
        MMap { ptr, size }
    }

    unsafe fn new_zeroed(size: usize, protect: ProtFlags, flag: MapFlags) -> Self {
        let mmap = MMap::new(size, protect, flag);
        ptr::write_bytes(mmap.ptr, 0, size);
        mmap
    }
}

impl ops::Deref for MMap {
    type Target = [u8];

    fn deref(&self) -> &Self::Target {
        unsafe { slice::from_raw_parts(self.ptr, self.size) }
    }
}

impl ops::DerefMut for MMap {
    fn deref_mut(&mut self) -> &mut Self::Target {
        unsafe { slice::from_raw_parts_mut(self.ptr, self.size) }
    }
}

impl Drop for MMap {
    fn drop(&mut self) {
        unsafe {
            munmap(self.ptr as *mut c_void, self.size).unwrap();
        }
    }
}

fn load_program<'a>(content: &'a [u8], elf: Elf<'a>) {
    let mut page = unsafe {
        MMap::new_zeroed(
            SIZE,
            ProtFlags::PROT_READ | ProtFlags::PROT_WRITE | ProtFlags::PROT_EXEC,
            MapFlags::MAP_PRIVATE | MapFlags::MAP_ANONYMOUS,
        )
    };

    load_into_memory(&mut page, content, &elf);

    let entry = elf
        .syms
        .iter()
        .find(|sym| elf.strtab.get(sym.st_name).unwrap().unwrap() == "main")
        .unwrap();
    let entry: unsafe extern "C" fn(i32, *mut *mut u8, *mut *mut u8) -> i32 =
        unsafe { mem::transmute(page.as_ptr().add(entry.st_value as usize)) };

    relocation(&mut page, &elf);

    unsafe {
        entry(0, ptr::null_mut(), ptr::null_mut());
    }
}

fn load_into_memory<'a>(page: &mut MMap, content: &'a [u8], elf: &Elf<'a>) {
    for header in elf.program_headers.iter() {
        if header.p_type == PT_LOAD {
            assert!(header.p_memsz >= header.p_filesz);
            if header.p_filesz == 0 {
                continue;
            }
            unsafe {
                let dst = page.as_mut_ptr().add(header.p_vaddr as usize);
                ptr::copy_nonoverlapping(
                    content.as_ptr().add(header.p_offset as usize),
                    dst,
                    header.p_filesz as usize,
                );
                if header.p_flags & PF_W == 0 {
                    mprotect(
                        dst as *mut c_void,
                        header.p_memsz as usize,
                        ProtFlags::PROT_READ,
                    )
                    .unwrap();
                }
                if header.p_flags & PF_X != 0 {
                    mprotect(
                        dst as *mut c_void,
                        header.p_memsz as usize,
                        ProtFlags::PROT_EXEC,
                    )
                    .unwrap();
                }
            }
        }
    }
}

fn relocation(page: &mut MMap, elf: &Elf<'_>) {
    for reloc in elf.pltrelocs.iter() {
        let sym = elf.dynsyms.get(reloc.r_sym).unwrap();
        let name = elf.dynstrtab.get(sym.st_name).unwrap().unwrap();
        match reloc.r_type {
            R_X86_64_GLOB_DAT | R_X86_64_JUMP_SLOT => {
                let addr = resolve(name);
                let addr = addr.to_le_bytes();
                unsafe {
                    ptr::copy_nonoverlapping(
                        addr.as_ptr(),
                        page.as_mut_ptr().add(reloc.r_offset as usize),
                        mem::size_of::<u64>(),
                    );
                }
            }
            _ => {
                panic!("unable to handle {}", reloc.r_type);
            }
        }
    }
}

fn resolve(name: &str) -> u64 {
    static LIB: Lazy<Library> =
        Lazy::new(|| Library::open("/lib/x86_64-linux-gnu/libc.so.6").unwrap());
    unsafe { LIB.symbol(name).unwrap() }
}

fn main() -> io::Result<()> {
    let content = fs::read(env::args().nth(1).unwrap())?;
    let elf = Elf::parse(&content).unwrap();
    load_program(&content, elf);
    Ok(())
}

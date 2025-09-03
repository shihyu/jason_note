use nix::{
    sys::{
        ptrace,
        signal::Signal,
        wait::{waitpid, WaitStatus},
    },
    unistd::Pid,
};
use std::{env, io, os::unix::process::CommandExt, process::Command};

fn main() -> io::Result<()> {
    let child = unsafe {
        Command::new(env::args_os().nth(1).unwrap())
            .pre_exec(|| {
                ptrace::traceme().unwrap();
                Ok(())
            })
            .spawn()?
    };
    let pid = Pid::from_raw(child.id() as _);
    if let WaitStatus::Stopped(_, sig) = waitpid(pid, None).unwrap() {
        assert_eq!(sig, Signal::SIGTRAP);
        ptrace::setoptions(pid, ptrace::Options::PTRACE_O_TRACESYSGOOD).unwrap();
        ptrace::syscall(pid).unwrap();
    } else {
        panic!("child not stop");
    }
    let mut enter = true;
    while let Ok(status) = waitpid(pid, None) {
        match status {
            WaitStatus::PtraceSyscall(_) => {
                let regs = ptrace::getregs(pid).unwrap();
                if enter {
                    match regs.orig_rax {
                        0 => print!("read(...)"),
                        1 => print!("write(...)"),
                        2 => print!("open(...)"),
                        3 => print!("close(...)"),
                        4 => print!("stat(...)"),
                        9 => print!("mmap(...)"),
                        10 => print!("mprotect(...)"),
                        11 => print!("munmap(...)"),
                        12 => print!("brk(...)"),
                        231 => println!("exit_group(...) = !"),
                        257 => print!("openat(...)"),
                        _ => print!("{}(...)", regs.orig_rax),
                    }
                } else {
                    println!(" = {}", regs.rax);
                }
                enter = !enter;
                ptrace::syscall(pid).unwrap();
            }
            WaitStatus::Exited(_, code) => {
                println!("child exit {}", code);
            }
            _ => (),
        }
    }
    Ok(())
}

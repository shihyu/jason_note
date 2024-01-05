import ctypes


def load_rust_library(library_path):
    lib = ctypes.CDLL(library_path)
    return lib


def setup_rust_function(lib, function_name, argtypes, restype):
    rust_function = getattr(lib, function_name)
    rust_function.argtypes = argtypes
    rust_function.restype = restype
    return rust_function


def is_prime_rust(num):
    return bool(lib.is_prime(num))


def calculate_sum_rust(n):
    return lib.calculate_sum(n)


if __name__ == "__main__":
    # Load the Rust library
    lib = load_rust_library("./lib.so")

    # Setup Rust functions
    is_prime_function = setup_rust_function(
        lib, "is_prime", [ctypes.c_uint64], ctypes.c_bool
    )
    calculate_sum_function = setup_rust_function(
        lib, "calculate_sum", [ctypes.c_uint64], ctypes.c_uint64
    )

    # Test the Rust is_prime function
    number_to_check = 10000000
    if is_prime_rust(number_to_check):
        print(f"{number_to_check} is prime.")
    else:
        print(f"{number_to_check} is not prime.")

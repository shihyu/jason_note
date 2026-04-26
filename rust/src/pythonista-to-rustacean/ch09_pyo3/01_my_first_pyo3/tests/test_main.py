import my_first_pyo3

def test_sum_as_string():
    assert my_first_pyo3.sum_as_string(5, 20) == "25"
    assert my_first_pyo3.sum_as_string(0, 0) == "0"
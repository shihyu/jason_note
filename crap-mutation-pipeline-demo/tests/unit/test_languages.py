from pipeline.languages.python_lang import parse_coverage as parse_python
from pipeline.languages.go_lang import parse_coverage as parse_go
from pipeline.languages.c_lang import parse_coverage as parse_c
from pipeline.languages.rust_lang import parse_coverage as parse_rust
from pipeline.languages.javascript_lang import parse_coverage as parse_js


def test_parse_coverage_python():
    output = """Name                 Stmts   Miss  Cover
----------------------------------------
foo.py                  10      2    80%
----------------------------------------
TOTAL                   10      2    80%
"""
    assert parse_python(output) == 0.8


def test_parse_coverage_go():
    output = "ok  \tdemo/pkg\t0.002s\tcoverage: 84.6% of statements\n"
    assert abs(parse_go(output) - 0.846) < 1e-9


def test_parse_coverage_c():
    output = """File 'foo.c'
Lines executed:83.33% of 12
Creating 'foo.c.gcov'
"""
    assert abs(parse_c(output) - 0.8333) < 1e-4


def test_parse_coverage_rust():
    output = "22.22% coverage, 2/9 lines covered\n"
    assert abs(parse_rust(output) - 0.2222) < 1e-4


def test_parse_coverage_javascript():
    output = """----------|---------|----------|---------|---------|-------------------
File      | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
----------|---------|----------|---------|---------|-------------------
All files |     100 |      100 |     100 |     100 |
----------|---------|----------|---------|---------|-------------------
"""
    assert parse_js(output) == 1.0

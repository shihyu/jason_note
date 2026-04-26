def test_import_parent():
    import parent_module
    ### 透過父模組存取
    assert parent_module.child_module.child_func() == "Hello from the child module!"

def test_import_child():
    ### 也可以直接 import 子模組
    from parent_module import child_module
    assert child_module.child_func() == "Hello from the child module!"

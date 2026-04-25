import data_utils

def test_module_structure():
    # 1. 檢查頂層函式是否存在且可被呼叫
    assert hasattr(data_utils, "normalize_vector"), "找不到 normalize_vector"
    assert callable(data_utils.normalize_vector), "normalize_vector 應該是函式"

    assert hasattr(data_utils, "calculate_mean"), "找不到 calculate_mean"
    assert callable(data_utils.calculate_mean), "calculate_mean 應該是函式"

    # 2. 檢查類別是否存在
    assert hasattr(data_utils, "DataPoint"), "找不到 DataPoint 類別"
    assert isinstance(data_utils.DataPoint, type), "DataPoint 應該是一個類別型別"

    # 3. 檢查巢狀子模組 (stats) 是否存在
    assert hasattr(data_utils, "stats"), "找不到 stats 子模組"
    
    # 4. 檢查子模組內的函式
    assert hasattr(data_utils.stats, "calculate_variance"), "找不到 stats.calculate_variance"
    assert callable(data_utils.stats.calculate_variance), "stats.calculate_variance 應該是函式"
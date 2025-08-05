#!/usr/bin/env python3
"""
所有 Python 鎖範例的測試執行器
自動執行所有範例並檢查結果的正確性
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """測試結果"""
    file_path: str
    success: bool
    execution_time: float
    output: str
    error: str


class TestRunner:
    """測試執行器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.results: List[TestResult] = []
        
    def find_python_files(self) -> List[Path]:
        """尋找所有 Python 檔案"""
        python_files = []
        
        # 掃描基本鎖範例
        basic_locks_path = self.base_path / "basic_locks"
        if basic_locks_path.exists():
            python_files.extend(basic_locks_path.glob("*.py"))
        
        # 掃描進階鎖範例
        advanced_locks_path = self.base_path / "advanced_locks"
        if advanced_locks_path.exists():
            python_files.extend(advanced_locks_path.glob("*.py"))
        
        # 掃描最佳實踐範例
        best_practices_path = self.base_path / "best_practices"
        if best_practices_path.exists():
            python_files.extend(best_practices_path.glob("*.py"))
        
        # 排序檔案以確保執行順序一致
        return sorted(python_files)
    
    def run_single_test(self, file_path: Path, timeout: int = 30) -> TestResult:
        """執行單個測試檔案"""
        print(f"🧪 測試: {file_path.name}")
        
        start_time = time.time()
        
        try:
            # 執行 Python 檔案
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(file_path.parent)
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            if success:
                print(f"   ✅ 成功 ({execution_time:.2f}s)")
            else:
                print(f"   ❌ 失敗 ({execution_time:.2f}s)")
                if result.stderr:
                    print(f"   錯誤: {result.stderr[:200]}...")
            
            return TestResult(
                file_path=str(file_path),
                success=success,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"   ⏰ 超時 ({timeout}s)")
            
            return TestResult(
                file_path=str(file_path),
                success=False,
                execution_time=execution_time,
                output="",
                error=f"執行超時 ({timeout}s)"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   💥 異常: {e}")
            
            return TestResult(
                file_path=str(file_path),
                success=False,
                execution_time=execution_time,
                output="",
                error=str(e)
            )
    
    def run_all_tests(self, timeout: int = 30) -> Dict[str, any]:
        """執行所有測試"""
        print("🚀 開始執行所有 Python 鎖範例測試")
        print("=" * 60)
        
        python_files = self.find_python_files()
        
        if not python_files:
            print("❌ 未找到任何 Python 檔案")
            return {"success": False, "message": "No Python files found"}
        
        print(f"📋 找到 {len(python_files)} 個測試檔案")
        print()
        
        start_time = time.time()
        
        # 執行所有測試
        for file_path in python_files:
            result = self.run_single_test(file_path, timeout)
            self.results.append(result)
            print()  # 空行分隔
        
        total_time = time.time() - start_time
        
        # 生成報告
        return self.generate_report(total_time)
    
    def generate_report(self, total_time: float) -> Dict[str, any]:
        """生成測試報告"""
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        success_rate = len(successful_tests) / len(self.results) * 100 if self.results else 0
        
        print("📊 測試報告")
        print("=" * 60)
        print(f"總測試數: {len(self.results)}")
        print(f"成功數: {len(successful_tests)}")
        print(f"失敗數: {len(failed_tests)}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"總執行時間: {total_time:.2f}s")
        
        if successful_tests:
            avg_time = sum(r.execution_time for r in successful_tests) / len(successful_tests)
            print(f"平均執行時間: {avg_time:.2f}s")
        
        if failed_tests:
            print(f"\n❌ 失敗的測試:")
            for result in failed_tests:
                file_name = Path(result.file_path).name
                print(f"   • {file_name}: {result.error[:100]}...")
        
        print(f"\n✅ 成功的測試:")
        for result in successful_tests:
            file_name = Path(result.file_path).name
            print(f"   • {file_name} ({result.execution_time:.2f}s)")
        
        return {
            "success": len(failed_tests) == 0,
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": success_rate,
            "total_time": total_time,
            "results": self.results
        }
    
    def run_specific_category(self, category: str, timeout: int = 30) -> Dict[str, any]:
        """執行特定分類的測試"""
        print(f"🎯 執行 {category} 分類測試")
        print("=" * 60)
        
        category_path = self.base_path / category
        if not category_path.exists():
            print(f"❌ 分類 {category} 不存在")
            return {"success": False, "message": f"Category {category} not found"}
        
        python_files = sorted(category_path.glob("*.py"))
        
        if not python_files:
            print(f"❌ 在 {category} 中未找到任何 Python 檔案")
            return {"success": False, "message": f"No Python files found in {category}"}
        
        print(f"📋 在 {category} 中找到 {len(python_files)} 個測試檔案")
        print()
        
        start_time = time.time()
        
        # 執行測試
        category_results = []
        for file_path in python_files:
            result = self.run_single_test(file_path, timeout)
            category_results.append(result)
            print()
        
        total_time = time.time() - start_time
        
        # 暫存原始結果，只顯示分類結果
        original_results = self.results
        self.results = category_results
        
        report = self.generate_report(total_time)
        
        # 恢復原始結果
        self.results = original_results
        
        return report


def validate_examples():
    """驗證範例的基本結構"""
    print("🔍 驗證範例結構")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    issues = []
    
    # 檢查目錄結構
    required_dirs = ["basic_locks", "advanced_locks", "best_practices"]
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            issues.append(f"缺少目錄: {dir_name}")
        else:
            python_files = list(dir_path.glob("*.py"))
            if not python_files:
                issues.append(f"目錄 {dir_name} 中沒有 Python 檔案")
            else:
                print(f"✅ {dir_name}: {len(python_files)} 個檔案")
    
    # 檢查檔案命名
    expected_files = {
        "basic_locks": [
            "01_threading_lock.py",
            "02_decorator_lock.py", 
            "03_recursive_lock.py",
            "04_semaphore.py",
            "05_condition.py",
            "06_event.py",
            "07_barrier.py"
        ],
        "advanced_locks": [
            "01_read_write_lock.py",
            "02_context_manager.py",
            "03_thread_local.py"
        ],
        "best_practices": [
            "01_performance_comparison.py",
            "02_lock_selection_guide.py"
        ]
    }
    
    for category, files in expected_files.items():
        category_path = base_path / category
        if category_path.exists():
            for expected_file in files:
                file_path = category_path / expected_file
                if not file_path.exists():
                    issues.append(f"缺少檔案: {category}/{expected_file}")
    
    if issues:
        print(f"\n⚠️  發現 {len(issues)} 個問題:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("\n✅ 所有檔案結構驗證通過")
        return True


def show_usage():
    """顯示使用說明"""
    print("📖 Python 鎖範例測試執行器")
    print("=" * 60)
    print("用法:")
    print("  python test_all_examples.py [選項]")
    print()
    print("選項:")
    print("  --all                    執行所有測試 (預設)")
    print("  --basic                  只執行基本鎖測試")
    print("  --advanced               只執行進階鎖測試")
    print("  --best-practices         只執行最佳實踐測試")
    print("  --validate               驗證檔案結構")
    print("  --timeout SECONDS        設定單個測試超時時間 (預設: 30s)")
    print("  --help                   顯示此說明")
    print()
    print("範例:")
    print("  python test_all_examples.py --all")
    print("  python test_all_examples.py --basic --timeout 60")
    print("  python test_all_examples.py --validate")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Python 鎖範例測試執行器")
    parser.add_argument("--all", action="store_true", help="執行所有測試")
    parser.add_argument("--basic", action="store_true", help="執行基本鎖測試")
    parser.add_argument("--advanced", action="store_true", help="執行進階鎖測試")
    parser.add_argument("--best-practices", action="store_true", help="執行最佳實踐測試")
    parser.add_argument("--validate", action="store_true", help="驗證檔案結構")
    parser.add_argument("--timeout", type=int, default=30, help="測試超時時間（秒）")
    
    args = parser.parse_args()
    
    # 如果沒有指定任何選項，顯示說明
    if not any([args.all, args.basic, args.advanced, args.best_practices, args.validate]):
        show_usage()
        return
    
    base_path = Path(__file__).parent.parent
    runner = TestRunner(str(base_path))
    
    try:
        if args.validate:
            validate_examples()
            return
        
        if args.all or not any([args.basic, args.advanced, args.best_practices]):
            # 執行所有測試
            report = runner.run_all_tests(args.timeout)
        else:
            # 執行特定分類測試
            if args.basic:
                report = runner.run_specific_category("basic_locks", args.timeout)
            elif args.advanced:
                report = runner.run_specific_category("advanced_locks", args.timeout)
            elif args.best_practices:
                report = runner.run_specific_category("best_practices", args.timeout)
        
        # 返回適當的退出碼
        if not report["success"]:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  測試被用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 測試執行器發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
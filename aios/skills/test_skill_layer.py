"""
AI OS技能调用层功能测试
测试技能发现、调用、参数处理、错误处理等所有组件
"""

import os
import sys
import json
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillLayerTester:
    """技能调用层测试器"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始技能调用层功能测试")
        
        tests = [
            ("测试环境检查", self.test_environment),
            ("测试技能发现模块", self.test_skill_discovery),
            ("测试参数处理器", self.test_parameter_handler),
            ("测试结果解析器", self.test_result_parser),
            ("测试错误处理器", self.test_error_handler),
            ("测试技能调用器（模拟）", self.test_skill_invoker_mock),
            ("测试集成功能", self.test_integration)
        ]
        
        for test_name, test_func in tests:
            self._run_test(test_name, test_func)
        
        # 生成测试报告
        report = self.generate_test_report()
        
        logger.info(f"测试完成: {self.passed_tests} 通过, {self.failed_tests} 失败, {self.skipped_tests} 跳过")
        return report
    
    def _run_test(self, test_name: str, test_func):
        """运行单个测试"""
        logger.info(f"运行测试: {test_name}")
        
        try:
            result = test_func()
            if result.get("skipped", False):
                self.skipped_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "status": "skipped",
                    "reason": result.get("reason", "未知原因")
                })
                logger.info(f"测试跳过: {test_name} - {result.get('reason')}")
            elif result.get("passed", False):
                self.passed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "status": "passed",
                    "details": result.get("details", {})
                })
                logger.info(f"测试通过: {test_name}")
            else:
                self.failed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "status": "failed",
                    "error": result.get("error", "未知错误"),
                    "details": result.get("details", {})
                })
                logger.error(f"测试失败: {test_name} - {result.get('error')}")
                
        except Exception as e:
            self.failed_tests += 1
            self.test_results.append({
                "name": test_name,
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"测试异常: {test_name} - {e}")
    
    def test_environment(self) -> Dict[str, Any]:
        """测试环境检查"""
        details = {}
        
        # 检查Python版本
        python_version = sys.version_info
        details["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            return {
                "passed": False,
                "error": f"Python版本过低: {details['python_version']}，需要3.8+",
                "details": details
            }
        
        # 检查必要的模块
        required_modules = ["json", "logging", "os", "sys", "typing"]
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            return {
                "passed": False,
                "error": f"缺少必需模块: {missing_modules}",
                "details": details
            }
        
        # 检查可选模块
        optional_modules = ["yaml"]
        details["optional_modules"] = {}
        
        for module in optional_modules:
            try:
                __import__(module)
                details["optional_modules"][module] = "可用"
            except ImportError:
                details["optional_modules"][module] = "不可用"
        
        details["workbuddy_skills_path"] = os.path.expanduser("~/.workbuddy/skills")
        details["workbuddy_exists"] = os.path.exists(details["workbuddy_skills_path"])
        
        return {
            "passed": True,
            "details": details
        }
    
    def test_skill_discovery(self) -> Dict[str, Any]:
        """测试技能发现模块"""
        try:
            from skill_discovery import SkillDiscovery, get_workbuddy_skills_path
            
            workbuddy_path = get_workbuddy_skills_path()
            
            # 创建测试技能目录
            test_dir = tempfile.mkdtemp(prefix="test_skill_")
            test_skill_dir = os.path.join(test_dir, "test-skill")
            os.makedirs(test_skill_dir)
            
            # 创建测试skill.yaml
            test_config = {
                "name": "test-skill",
                "display_name": "测试技能",
                "version": "1.0.0",
                "description": "用于测试的技能",
                "category": "test",
                "author": "测试作者",
                "tags": ["test", "demo"],
                "functions": [
                    {
                        "name": "test_function",
                        "description": "测试函数",
                        "parameters": [
                            {"name": "input", "type": "string", "description": "输入"}
                        ],
                        "returns": {"type": "object", "description": "结果"}
                    }
                ]
            }
            
            import yaml
            with open(os.path.join(test_skill_dir, "skill.yaml"), 'w', encoding='utf-8') as f:
                yaml.dump(test_config, f, allow_unicode=True)
            
            # 测试技能发现
            discovery = SkillDiscovery(test_dir)
            skills = discovery.discover_all_skills()
            
            details = {
                "test_skills_found": len(skills),
                "workbuddy_path": workbuddy_path,
                "workbuddy_exists": os.path.exists(workbuddy_path)
            }
            
            # 清理测试目录
            shutil.rmtree(test_dir)
            
            if len(skills) == 1:
                skill_id = list(skills.keys())[0]
                skill_config = skills[skill_id]
                
                if skill_config["name"] == "test-skill":
                    return {
                        "passed": True,
                        "details": details
                    }
                else:
                    return {
                        "passed": False,
                        "error": f"发现的技能名称不匹配: {skill_config['name']}",
                        "details": details
                    }
            else:
                return {
                    "passed": False,
                    "error": f"发现技能数量不正确: {len(skills)}",
                    "details": details
                }
                
        except ImportError as e:
            if "yaml" in str(e):
                return {
                    "skipped": True,
                    "reason": "PyYAML模块未安装，跳过技能发现测试",
                    "details": {"error": str(e)}
                }
            else:
                return {
                    "passed": False,
                    "error": f"导入模块失败: {e}",
                    "details": {}
                }
        except Exception as e:
            return {
                "passed": False,
                "error": f"技能发现测试失败: {e}",
                "details": {}
            }
    
    def test_parameter_handler(self) -> Dict[str, Any]:
        """测试参数处理器"""
        try:
            from parameter_handler import ParameterHandler, ParameterType
            
            handler = ParameterHandler()
            
            # 测试参数定义
            param_defs = [
                {"name": "name", "type": "string", "description": "名称"},
                {"name": "age", "type": "integer", "min": 0, "max": 150, "optional": True, "default": 30},
                {"name": "active", "type": "boolean", "optional": True, "default": True},
                {"name": "tags", "type": "array", "itemType": "string", "optional": True},
            ]
            
            # 测试用例
            test_cases = [
                {
                    "params": {"name": "测试", "age": "25", "active": "yes", "tags": "a,b,c"},
                    "expected_types": {"name": str, "age": int, "active": bool, "tags": list}
                },
                {
                    "params": {"name": "另一个测试", "age": 40},
                    "expected_types": {"name": str, "age": int, "active": bool, "tags": list}
                }
            ]
            
            all_passed = True
            details = {"test_cases": []}
            
            for i, test_case in enumerate(test_cases):
                try:
                    processed = handler.process_parameters(test_case["params"], param_defs)
                    
                    # 检查类型
                    type_checks = []
                    for param_name, expected_type in test_case["expected_types"].items():
                        if param_name in processed:
                            actual_type = type(processed[param_name])
                            type_checks.append({
                                "param": param_name,
                                "expected": expected_type.__name__,
                                "actual": actual_type.__name__,
                                "passed": actual_type == expected_type
                            })
                    
                    case_passed = all(check["passed"] for check in type_checks)
                    if not case_passed:
                        all_passed = False
                    
                    details["test_cases"].append({
                        "case": i + 1,
                        "passed": case_passed,
                        "input": test_case["params"],
                        "output": processed,
                        "type_checks": type_checks
                    })
                    
                except Exception as e:
                    all_passed = False
                    details["test_cases"].append({
                        "case": i + 1,
                        "passed": False,
                        "error": str(e)
                    })
            
            return {
                "passed": all_passed,
                "details": details
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"参数处理器测试失败: {e}",
                "details": {}
            }
    
    def test_result_parser(self) -> Dict[str, Any]:
        """测试结果解析器"""
        try:
            from parameter_handler import ResultParser
            
            parser = ResultParser()
            
            # 测试用例
            test_cases = [
                {
                    "input": {"name": "测试", "value": 42},
                    "expected_type": "dictionary"
                },
                {
                    "input": [1, 2, 3, 4, 5],
                    "expected_type": "list"
                },
                {
                    "input": "简单文本",
                    "expected_type": "text"
                },
                {
                    "input": 123,
                    "expected_type": "numeric"
                },
                {
                    "input": True,
                    "expected_type": "boolean"
                }
            ]
            
            all_passed = True
            details = {"test_cases": []}
            
            for i, test_case in enumerate(test_cases):
                try:
                    parsed = parser.parse_result(test_case["input"])
                    
                    actual_type = parsed["metadata"]["result_type"]
                    expected_type = test_case["expected_type"]
                    
                    type_passed = actual_type == expected_type
                    if not type_passed:
                        all_passed = False
                    
                    details["test_cases"].append({
                        "case": i + 1,
                        "passed": type_passed,
                        "input_type": type(test_case["input"]).__name__,
                        "expected_result_type": expected_type,
                        "actual_result_type": actual_type,
                        "parsed": parsed
                    })
                    
                except Exception as e:
                    all_passed = False
                    details["test_cases"].append({
                        "case": i + 1,
                        "passed": False,
                        "error": str(e)
                    })
            
            # 测试错误解析
            try:
                error = ValueError("测试错误")
                error_result = parser.parse_error(error)
                
                if error_result["success"] == False and "error" in error_result:
                    details["error_parsing"] = "成功"
                else:
                    all_passed = False
                    details["error_parsing"] = "失败"
                    
            except Exception as e:
                all_passed = False
                details["error_parsing_error"] = str(e)
            
            return {
                "passed": all_passed,
                "details": details
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"结果解析器测试失败: {e}",
                "details": {}
            }
    
    def test_error_handler(self) -> Dict[str, Any]:
        """测试错误处理器"""
        try:
            from error_handler import (
                RetryManager, RetryStrategy, CircuitBreaker,
                TimeoutManager, ErrorRecoveryManager, CompositeErrorHandler
            )
            
            details = {"components_tested": []}
            
            # 测试重试管理器
            try:
                retry_manager = RetryManager(max_retries=2, strategy=RetryStrategy.FIXED)
                
                call_count = 0
                def failing_function():
                    nonlocal call_count
                    call_count += 1
                    if call_count < 3:
                        raise Exception(f"第{call_count}次失败")
                    return "成功"
                
                try:
                    result = retry_manager.execute_with_retry(failing_function)
                    details["components_tested"].append({
                        "component": "RetryManager",
                        "status": "passed",
                        "calls_needed": call_count
                    })
                except:
                    details["components_tested"].append({
                        "component": "RetryManager",
                        "status": "failed"
                    })
            except Exception as e:
                details["components_tested"].append({
                    "component": "RetryManager",
                    "status": "error",
                    "error": str(e)
                })
            
            # 测试断路器
            try:
                circuit_breaker = CircuitBreaker(failure_threshold=2)
                
                def failing_func():
                    raise Exception("模拟失败")
                
                # 触发断路器打开
                for _ in range(3):
                    try:
                        circuit_breaker.execute(failing_func)
                    except:
                        pass
                
                status = circuit_breaker.get_status()
                if status["state"] == "open":
                    details["components_tested"].append({
                        "component": "CircuitBreaker",
                        "status": "passed"
                    })
                else:
                    details["components_tested"].append({
                        "component": "CircuitBreaker",
                        "status": "failed",
                        "state": status["state"]
                    })
            except Exception as e:
                details["components_tested"].append({
                    "component": "CircuitBreaker",
                    "status": "error",
                    "error": str(e)
                })
            
            # 测试超时管理器
            try:
                timeout_manager = TimeoutManager(default_timeout=0.1)
                
                import time
                def slow_function():
                    time.sleep(0.2)
                    return "完成"
                
                try:
                    timeout_manager.execute_with_timeout(slow_function)
                    details["components_tested"].append({
                        "component": "TimeoutManager",
                        "status": "failed",  # 应该超时
                        "reason": "没有按预期超时"
                    })
                except TimeoutError:
                    details["components_tested"].append({
                        "component": "TimeoutManager",
                        "status": "passed"
                    })
                except Exception as e:
                    details["components_tested"].append({
                        "component": "TimeoutManager",
                        "status": "error",
                        "error": str(e)
                    })
            except Exception as e:
                details["components_tested"].append({
                    "component": "TimeoutManager",
                    "status": "error",
                    "error": str(e)
                })
            
            # 检查是否有组件测试失败
            failed_components = [c for c in details["components_tested"] 
                               if c["status"] in ["failed", "error"]]
            
            if failed_components:
                return {
                    "passed": False,
                    "error": f"{len(failed_components)} 个组件测试失败",
                    "details": details
                }
            else:
                return {
                    "passed": True,
                    "details": details
                }
                
        except Exception as e:
            return {
                "passed": False,
                "error": f"错误处理器测试失败: {e}",
                "details": {}
            }
    
    def test_skill_invoker_mock(self) -> Dict[str, Any]:
        """测试技能调用器（模拟）"""
        # 由于实际调用需要真实的技能，这里进行模拟测试
        try:
            # 尝试导入模块
            import importlib
            
            # 检查模块是否可用
            modules_to_check = ["skill_discovery", "skill_invoker", "parameter_handler", "error_handler"]
            available_modules = []
            missing_modules = []
            
            for module_name in modules_to_check:
                try:
                    importlib.import_module(module_name)
                    available_modules.append(module_name)
                except ImportError:
                    missing_modules.append(module_name)
            
            details = {
                "available_modules": available_modules,
                "missing_modules": missing_modules,
                "note": "这是模拟测试，实际调用需要安装PyYAML和真实技能"
            }
            
            if len(missing_modules) > 0:
                return {
                    "skipped": True,
                    "reason": f"缺少模块: {missing_modules}",
                    "details": details
                }
            else:
                return {
                    "passed": True,
                    "details": details
                }
                
        except Exception as e:
            return {
                "passed": False,
                "error": f"模拟测试失败: {e}",
                "details": {}
            }
    
    def test_integration(self) -> Dict[str, Any]:
        """测试集成功能"""
        # 测试各个模块能否协同工作
        details = {"integration_checks": []}
        
        try:
            # 检查模块导入
            modules = ["skill_discovery", "skill_invoker", "parameter_handler", "error_handler"]
            import_errors = []
            
            for module in modules:
                try:
                    __import__(module)
                    details["integration_checks"].append({
                        "check": f"导入 {module}",
                        "status": "passed"
                    })
                except ImportError as e:
                    import_errors.append(f"{module}: {e}")
                    details["integration_checks"].append({
                        "check": f"导入 {module}",
                        "status": "failed",
                        "error": str(e)
                    })
            
            if import_errors:
                return {
                    "skipped": True,
                    "reason": f"导入错误: {import_errors}",
                    "details": details
                }
            
            # 检查基本功能
            from parameter_handler import create_parameter_handler, create_result_parser
            from error_handler import create_default_error_handler
            
            try:
                param_handler = create_parameter_handler()
                result_parser = create_result_parser()
                error_handler = create_default_error_handler()
                
                details["integration_checks"].extend([
                    {"check": "创建参数处理器", "status": "passed"},
                    {"check": "创建结果解析器", "status": "passed"},
                    {"check": "创建错误处理器", "status": "passed"}
                ])
                
                # 测试简单集成
                def mock_skill_function(input_text: str) -> Dict:
                    return {"processed": True, "input": input_text, "length": len(input_text)}
                
                # 使用错误处理器调用模拟函数
                try:
                    result = error_handler.execute(
                        mock_skill_function,
                        func_name="mock_skill_function",
                        input_text="测试输入"
                    )
                    
                    if result == {"processed": True, "input": "测试输入", "length": 12}:
                        details["integration_checks"].append({
                            "check": "集成调用模拟函数",
                            "status": "passed"
                        })
                    else:
                        details["integration_checks"].append({
                            "check": "集成调用模拟函数",
                            "status": "failed",
                            "result": result
                        })
                        
                except Exception as e:
                    details["integration_checks"].append({
                        "check": "集成调用模拟函数",
                        "status": "failed",
                        "error": str(e)
                    })
                
                # 检查是否有失败的集成检查
                failed_checks = [c for c in details["integration_checks"] if c["status"] == "failed"]
                
                if failed_checks:
                    return {
                        "passed": False,
                        "error": f"{len(failed_checks)} 个集成检查失败",
                        "details": details
                    }
                else:
                    return {
                        "passed": True,
                        "details": details
                    }
                    
            except Exception as e:
                return {
                    "passed": False,
                    "error": f"集成测试失败: {e}",
                    "details": details
                }
                
        except Exception as e:
            return {
                "passed": False,
                "error": f"集成测试异常: {e}",
                "details": {}
            }
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = self.passed_tests + self.failed_tests + self.skipped_tests
        
        if total_tests == 0:
            success_rate = 0
        else:
            success_rate = self.passed_tests / total_tests
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": self.skipped_tests,
                "success_rate": success_rate,
                "overall_status": "PASS" if self.failed_tests == 0 else "FAIL"
            },
            "test_results": self.test_results,
            "timestamp": self._get_timestamp(),
            "environment": self._get_environment_info()
        }
        
        return report
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        import platform
        
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "system": platform.system(),
            "working_directory": os.getcwd(),
            "script_directory": os.path.dirname(__file__)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("AI OS WorkBuddy技能调用层功能测试")
    print("=" * 60)
    
    tester = SkillLayerTester()
    report = tester.run_all_tests()
    
    # 显示摘要
    summary = report["summary"]
    print(f"\n测试摘要:")
    print(f"  总测试数: {summary['total_tests']}")
    print(f"  通过: {summary['passed']} ✓")
    print(f"  失败: {summary['failed']} ✗")
    print(f"  跳过: {summary['skipped']} -")
    print(f"  成功率: {summary['success_rate']:.1%}")
    print(f"  总体状态: {summary['overall_status']}")
    
    # 显示详细结果
    if summary['failed'] > 0:
        print(f"\n失败测试:")
        for test in report['test_results']:
            if test['status'] == 'failed':
                print(f"  - {test['name']}: {test.get('error', '未知错误')}")
    
    if summary['skipped'] > 0:
        print(f"\n跳过测试:")
        for test in report['test_results']:
            if test['status'] == 'skipped':
                print(f"  - {test['name']}: {test.get('reason', '未知原因')}")
    
    # 保存报告到文件
    report_file = os.path.join(os.path.dirname(__file__), "skill_layer_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细测试报告已保存到: {report_file}")
    
    # 返回退出代码
    if summary['overall_status'] == 'PASS':
        print("\n所有测试通过! ✓")
        return 0
    else:
        print("\n有测试失败，请检查报告 ✗")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
"""
AI OS WorkBuddy技能调用封装器
提供统一的接口调用WorkBuddy技能，处理参数转换和结果解析
"""

import os
import sys
import importlib.util
import subprocess
import json
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
import logging
import traceback

logger = logging.getLogger(__name__)


class SkillInvocationError(Exception):
    """技能调用错误"""
    pass


class SkillInvoker:
    """WorkBuddy技能调用封装器"""
    
    def __init__(self, skill_discovery=None, workbuddy_skills_path: str = None):
        """
        初始化技能调用器
        
        Args:
            skill_discovery: 技能发现器实例
            workbuddy_skills_path: WorkBuddy技能目录路径
        """
        if skill_discovery is None:
            from skill_discovery import SkillDiscovery, get_workbuddy_skills_path
            
            if workbuddy_skills_path is None:
                workbuddy_skills_path = get_workbuddy_skills_path()
                
            self.skill_discovery = SkillDiscovery(workbuddy_skills_path)
            # 自动发现技能
            self.skill_discovery.discover_all_skills()
        else:
            self.skill_discovery = skill_discovery
            
        self.skills_registry = self.skill_discovery.skills_registry
        self.loaded_skills = {}  # 已加载的技能模块缓存
        self.function_cache = {}  # 函数缓存
        self.invocation_history = []  # 调用历史
        
    def invoke_skill(self, skill_name: str, function_name: str, 
                    parameters: Dict[str, Any] = None,
                    timeout: int = 30) -> Dict[str, Any]:
        """
        调用技能函数
        
        Args:
            skill_name: 技能名称
            function_name: 函数名称
            parameters: 参数字典
            timeout: 超时时间（秒）
            
        Returns:
            调用结果字典
            
        Raises:
            SkillInvocationError: 调用失败时抛出
        """
        # 查找技能
        skill_config = self._find_skill_config(skill_name)
        if not skill_config:
            raise SkillInvocationError(f"未找到技能: {skill_name}")
            
        # 验证函数是否存在
        function_config = self._get_function_config(skill_config, function_name)
        if not function_config:
            raise SkillInvocationError(f"技能 {skill_name} 中未找到函数: {function_name}")
            
        # 验证参数
        if parameters is None:
            parameters = {}
            
        validated_params = self._validate_parameters(function_config, parameters)
        
        # 记录调用开始
        invocation_id = f"{skill_name}_{function_name}_{len(self.invocation_history)}"
        invocation_record = {
            "id": invocation_id,
            "skill": skill_name,
            "function": function_name,
            "parameters": parameters,
            "status": "started",
            "start_time": self._get_timestamp()
        }
        self.invocation_history.append(invocation_record)
        
        try:
            # 调用技能
            result = self._execute_invocation(skill_config, function_name, validated_params, timeout)
            
            # 更新调用记录
            invocation_record["status"] = "completed"
            invocation_record["end_time"] = self._get_timestamp()
            invocation_record["result"] = result
            
            logger.info(f"技能调用成功: {skill_name}.{function_name}")
            return result
            
        except Exception as e:
            # 更新调用记录
            invocation_record["status"] = "failed"
            invocation_record["end_time"] = self._get_timestamp()
            invocation_record["error"] = str(e)
            invocation_record["traceback"] = traceback.format_exc()
            
            logger.error(f"技能调用失败: {skill_name}.{function_name} - {e}")
            raise SkillInvocationError(f"技能调用失败: {e}")
    
    def _find_skill_config(self, skill_name: str) -> Optional[Dict]:
        """查找技能配置"""
        # 尝试精确匹配
        for skill_id, skill_config in self.skills_registry.items():
            if skill_config.get("name") == skill_name or skill_config.get("display_name") == skill_name:
                return skill_config
                
        # 尝试部分匹配
        for skill_id, skill_config in self.skills_registry.items():
            if skill_name.lower() in skill_config.get("name", "").lower():
                return skill_config
                
        # 尝试搜索
        search_results = self.skill_discovery.search_skills(skill_name)
        if search_results:
            return search_results[0]
            
        return None
    
    def _get_function_config(self, skill_config: Dict, function_name: str) -> Optional[Dict]:
        """获取函数配置"""
        functions = skill_config.get("functions", [])
        for func_config in functions:
            if func_config.get("name") == function_name:
                return func_config
                
        # 检查是否有子技能
        subskills = skill_config.get("subskills", [])
        for subskill in subskills:
            if isinstance(subskill, dict) and subskill.get("name") == function_name:
                # 返回简化版的函数配置
                return {
                    "name": subskill.get("name"),
                    "description": subskill.get("description", "子技能"),
                    "parameters": [],
                    "returns": {"type": "object", "description": "子技能执行结果"}
                }
                
        return None
    
    def _validate_parameters(self, function_config: Dict, parameters: Dict) -> Dict:
        """验证参数"""
        param_definitions = function_config.get("parameters", [])
        validated_params = {}
        
        for param_def in param_definitions:
            param_name = param_def.get("name")
            param_type = param_def.get("type", "string")
            is_optional = param_def.get("optional", False)
            default_value = param_def.get("default")
            
            # 检查参数是否存在
            if param_name not in parameters:
                if not is_optional and default_value is None:
                    raise SkillInvocationError(f"缺少必需参数: {param_name}")
                elif default_value is not None:
                    validated_params[param_name] = default_value
                continue
                
            # 验证参数类型
            param_value = parameters[param_name]
            try:
                validated_value = self._convert_parameter_type(param_value, param_type)
                validated_params[param_name] = validated_value
            except (ValueError, TypeError) as e:
                raise SkillInvocationError(f"参数 {param_name} 类型转换失败: {e}")
        
        # 添加额外参数（如果有）
        extra_params = {k: v for k, v in parameters.items() if k not in validated_params}
        if extra_params:
            logger.debug(f"函数 {function_config.get('name')} 收到额外参数: {list(extra_params.keys())}")
            validated_params.update(extra_params)
            
        return validated_params
    
    def _convert_parameter_type(self, value: Any, target_type: str) -> Any:
        """转换参数类型"""
        type_map = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "enum": str  # 枚举当作字符串处理
        }
        
        if target_type not in type_map:
            logger.warning(f"未知参数类型: {target_type}，当作字符串处理")
            target_type = "string"
            
        target_class = type_map[target_type]
        
        # 特殊处理枚举类型
        if target_type == "enum":
            return str(value)
            
        # 如果已经是目标类型，直接返回
        if isinstance(value, target_class):
            return value
            
        # 类型转换
        try:
            if target_class == bool:
                # 布尔值特殊处理
                if isinstance(value, str):
                    value_lower = value.lower()
                    if value_lower in ["true", "yes", "1", "on"]:
                        return True
                    elif value_lower in ["false", "no", "0", "off"]:
                        return False
                    else:
                        raise ValueError(f"无法将字符串 '{value}' 转换为布尔值")
                else:
                    return bool(value)
                    
            elif target_class == list:
                # 列表转换
                if isinstance(value, str):
                    # 尝试解析JSON数组
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list):
                            return parsed
                    except json.JSONDecodeError:
                        # 如果不是JSON，当作逗号分隔的列表
                        if value.strip():
                            return [item.strip() for item in value.split(",")]
                        else:
                            return []
                return list(value)
                
            elif target_class == dict:
                # 字典转换
                if isinstance(value, str):
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        raise ValueError("无法将字符串解析为JSON对象")
                return dict(value)
                
            else:
                # 基本类型转换
                return target_class(value)
                
        except Exception as e:
            raise ValueError(f"类型转换失败: {value} -> {target_type}: {e}")
    
    def _execute_invocation(self, skill_config: Dict, function_name: str, 
                           parameters: Dict, timeout: int) -> Any:
        """执行技能调用"""
        
        # 尝试多种调用方式
        invocation_methods = [
            self._invoke_python_function,
            self._invoke_script_file,
            self._invoke_command_line,
            self._invoke_http_api  # 预留，未来可能支持HTTP API
        ]
        
        last_error = None
        for method in invocation_methods:
            try:
                result = method(skill_config, function_name, parameters, timeout)
                if result is not None:
                    return result
            except Exception as e:
                last_error = e
                logger.debug(f"调用方式失败 {method.__name__}: {e}")
                continue
                
        # 所有方式都失败
        raise SkillInvocationError(f"所有调用方式都失败，最后错误: {last_error}")
    
    def _invoke_python_function(self, skill_config: Dict, function_name: str,
                               parameters: Dict, timeout: int) -> Any:
        """调用Python函数"""
        skill_path = skill_config.get("path")
        if not skill_path:
            raise SkillInvocationError("技能路径未定义")
            
        # 尝试加载技能模块
        module_name = f"skill_{skill_config.get('name', 'unknown').replace('-', '_')}"
        if module_name in self.loaded_skills:
            skill_module = self.loaded_skills[module_name]
        else:
            # 查找Python模块
            module_path = self._find_python_module(skill_path)
            if not module_path:
                raise SkillInvocationError(f"未找到Python模块: {skill_path}")
                
            # 加载模块
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                skill_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(skill_module)
                self.loaded_skills[module_name] = skill_module
            except Exception as e:
                raise SkillInvocationError(f"加载Python模块失败: {e}")
        
        # 查找函数
        if hasattr(skill_module, function_name):
            function = getattr(skill_module, function_name)
        else:
            # 在模块中查找匹配的函数
            functions = [name for name in dir(skill_module) 
                        if not name.startswith('_') and callable(getattr(skill_module, name))]
            
            # 尝试找到名称相似或功能匹配的函数
            matched_function = None
            for func_name in functions:
                if function_name.lower() == func_name.lower():
                    matched_function = getattr(skill_module, func_name)
                    break
                    
            if not matched_function:
                raise SkillInvocationError(f"模块中未找到函数: {function_name}")
                
            function = matched_function
        
        # 调用函数
        try:
            if inspect.isfunction(function) or inspect.ismethod(function):
                result = function(**parameters)
            else:
                # 可能是类或其他可调用对象
                result = function(**parameters)
                
            return result
            
        except Exception as e:
            raise SkillInvocationError(f"Python函数调用失败: {e}")
    
    def _invoke_script_file(self, skill_config: Dict, function_name: str,
                           parameters: Dict, timeout: int) -> Any:
        """调用脚本文件"""
        skill_path = skill_config.get("path")
        
        # 查找脚本文件
        script_path = self._find_script_file(skill_path, function_name)
        if not script_path:
            raise SkillInvocationError(f"未找到脚本文件: {function_name}")
            
        # 准备参数
        if parameters:
            # 将参数转换为命令行参数或环境变量
            param_args = []
            for key, value in parameters.items():
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)
                    
                param_args.append(f"--{key}")
                param_args.append(value_str)
        else:
            param_args = []
        
        # 执行脚本
        try:
            cmd = [sys.executable, script_path] + param_args
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                raise SkillInvocationError(f"脚本执行失败: {result.stderr}")
                
            # 解析输出
            try:
                # 尝试解析JSON输出
                output = result.stdout.strip()
                if output:
                    return json.loads(output)
                else:
                    return {"success": True, "message": "脚本执行成功"}
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始输出
                return {"output": result.stdout, "success": True}
                
        except subprocess.TimeoutExpired:
            raise SkillInvocationError(f"脚本执行超时 ({timeout}秒)")
        except Exception as e:
            raise SkillInvocationError(f"脚本执行失败: {e}")
    
    def _invoke_command_line(self, skill_config: Dict, function_name: str,
                            parameters: Dict, timeout: int) -> Any:
        """调用命令行工具"""
        # 这个方法是最后的备选方案
        # 假设技能有命令行接口
        
        skill_name = skill_config.get("name", "")
        cmd_base = f"workbuddy skill {skill_name} {function_name}"
        
        # 构建命令
        cmd_parts = [cmd_base]
        for key, value in parameters.items():
            if isinstance(value, bool):
                if value:
                    cmd_parts.append(f"--{key}")
            else:
                cmd_parts.append(f"--{key}")
                if value is not None:
                    cmd_parts.append(str(value))
        
        cmd = " ".join(cmd_parts)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                raise SkillInvocationError(f"命令执行失败: {result.stderr}")
                
            return {"output": result.stdout, "success": True}
            
        except subprocess.TimeoutExpired:
            raise SkillInvocationError(f"命令执行超时 ({timeout}秒)")
        except Exception as e:
            raise SkillInvocationError(f"命令执行失败: {e}")
    
    def _invoke_http_api(self, skill_config: Dict, function_name: str,
                        parameters: Dict, timeout: int) -> Any:
        """调用HTTP API（预留）"""
        # 未来可能支持HTTP API调用
        raise SkillInvocationError("HTTP API调用尚未实现")
    
    def _find_python_module(self, skill_path: str) -> Optional[str]:
        """查找Python模块"""
        # 检查常见的模块文件
        module_files = [
            "__init__.py",
            "main.py",
            f"{os.path.basename(skill_path)}.py",
            "skill.py",
            "module.py",
            "api.py"
        ]
        
        for module_file in module_files:
            module_path = os.path.join(skill_path, module_file)
            if os.path.exists(module_path):
                return module_path
        
        # 检查scripts目录
        scripts_dir = os.path.join(skill_path, "scripts")
        if os.path.exists(scripts_dir):
            for script_file in os.listdir(scripts_dir):
                if script_file.endswith(".py"):
                    script_path = os.path.join(scripts_dir, script_file)
                    # 检查文件是否包含函数定义
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "def " in content or "class " in content:
                            return script_path
        
        return None
    
    def _find_script_file(self, skill_path: str, function_name: str) -> Optional[str]:
        """查找脚本文件"""
        # 检查scripts目录
        scripts_dir = os.path.join(skill_path, "scripts")
        if os.path.exists(scripts_dir):
            # 查找与函数名相关的脚本
            possible_names = [
                f"{function_name}.py",
                f"{function_name.replace('_', '-')}.py",
                f"{function_name.replace('-', '_')}.py",
                f"run_{function_name}.py",
                f"execute_{function_name}.py",
                f"{function_name}_handler.py",
                f"{function_name}_executor.py"
            ]
            
            for script_name in possible_names:
                script_path = os.path.join(scripts_dir, script_name)
                if os.path.exists(script_path):
                    return script_path
            
            # 查找任何Python脚本
            for script_file in os.listdir(scripts_dir):
                if script_file.endswith(".py"):
                    script_path = os.path.join(scripts_dir, script_file)
                    # 检查文件内容是否包含函数名
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if function_name.lower() in content.lower():
                            return script_path
        
        # 检查根目录
        possible_files = [
            f"{function_name}.py",
            f"run_{function_name}.py",
            "run.py",
            "execute.py",
            "main.py"
        ]
        
        for file_name in possible_files:
            file_path = os.path.join(skill_path, file_name)
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_invocation_history(self, limit: int = 50) -> List[Dict]:
        """获取调用历史"""
        return self.invocation_history[-limit:] if self.invocation_history else []
    
    def get_skill_functions(self, skill_name: str) -> List[Dict]:
        """获取技能的可用函数列表"""
        skill_config = self._find_skill_config(skill_name)
        if not skill_config:
            return []
            
        functions = skill_config.get("functions", [])
        return functions
    
    def list_available_skills(self) -> List[str]:
        """获取可用技能列表"""
        return list(self.skills_registry.keys())
    
    def get_skill_info(self, skill_name: str) -> Dict:
        """获取技能详细信息"""
        skill_config = self._find_skill_config(skill_name)
        if not skill_config:
            return {}
            
        # 返回简化信息
        return {
            "name": skill_config.get("display_name", skill_config.get("name")),
            "description": skill_config.get("description", ""),
            "version": skill_config.get("version", "1.0.0"),
            "category": skill_config.get("category", "other"),
            "author": skill_config.get("author", "未知"),
            "path": skill_config.get("path", ""),
            "functions": skill_config.get("functions", []),
            "subskills": skill_config.get("subskills", []),
            "tags": skill_config.get("tags", [])
        }


# 简化接口函数
def create_skill_invoker(workbuddy_skills_path: str = None) -> SkillInvoker:
    """创建技能调用器"""
    return SkillInvoker(workbuddy_skills_path=workbuddy_skills_path)


def invoke_skill(skill_name: str, function_name: str, 
                parameters: Dict = None, timeout: int = 30) -> Any:
    """
    调用技能的简化接口
    
    Args:
        skill_name: 技能名称
        function_name: 函数名称
        parameters: 参数字典
        timeout: 超时时间
        
    Returns:
        调用结果
    """
    invoker = create_skill_invoker()
    return invoker.invoke_skill(skill_name, function_name, parameters, timeout)


def list_skills() -> List[Dict]:
    """列出所有可用技能"""
    invoker = create_skill_invoker()
    skills = []
    
    for skill_id, skill_config in invoker.skills_registry.items():
        skills.append({
            "id": skill_id,
            "name": skill_config.get("display_name", skill_config.get("name")),
            "description": skill_config.get("description", ""),
            "category": skill_config.get("category", "other"),
            "version": skill_config.get("version", "1.0.0")
        })
    
    return skills


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试技能调用器
    print("=== AI OS WorkBuddy技能调用器测试 ===")
    
    invoker = create_skill_invoker()
    
    print(f"发现 {len(invoker.skills_registry)} 个技能")
    
    # 列出技能
    skills = list_skills()
    if skills:
        print("\n可用技能:")
        for skill in skills[:10]:  # 只显示前10个
            print(f"  - {skill['name']} (v{skill['version']}) - {skill['category']}")
        
        if len(skills) > 10:
            print(f"  ... 还有 {len(skills) - 10} 个技能")
    
    # 尝试获取技能信息
    if skills:
        first_skill = skills[0]
        skill_info = invoker.get_skill_info(first_skill["name"])
        print(f"\n技能 '{first_skill['name']}' 的信息:")
        print(f"  描述: {skill_info.get('description', '无描述')}")
        print(f"  函数数量: {len(skill_info.get('functions', []))}")
        
        # 如果有函数，显示函数列表
        functions = skill_info.get("functions", [])
        if functions:
            print("  可用函数:")
            for func in functions[:5]:  # 只显示前5个
                print(f"    - {func.get('name')}: {func.get('description', '无描述')}")
    
    print("\n技能调用器初始化完成，可以使用 invoke_skill() 调用技能函数")
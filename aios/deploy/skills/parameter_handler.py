"""
AI OS技能参数处理器和结果解析器
处理技能调用参数的验证、转换和标准化，以及结果的解析和格式化
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """参数类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    DATE = "date"
    DATETIME = "datetime"
    FILE = "file"
    PATH = "path"


class ParameterHandler:
    """技能参数处理器"""
    
    def __init__(self):
        self.type_converters = {
            ParameterType.STRING: self._convert_to_string,
            ParameterType.INTEGER: self._convert_to_integer,
            ParameterType.FLOAT: self._convert_to_float,
            ParameterType.BOOLEAN: self._convert_to_boolean,
            ParameterType.ARRAY: self._convert_to_array,
            ParameterType.OBJECT: self._convert_to_object,
            ParameterType.ENUM: self._convert_to_enum,
            ParameterType.DATE: self._convert_to_date,
            ParameterType.DATETIME: self._convert_to_datetime,
            ParameterType.FILE: self._convert_to_file,
            ParameterType.PATH: self._convert_to_path
        }
        
        self.validators = {
            ParameterType.STRING: self._validate_string,
            ParameterType.INTEGER: self._validate_integer,
            ParameterType.FLOAT: self._validate_float,
            ParameterType.BOOLEAN: self._validate_boolean,
            ParameterType.ARRAY: self._validate_array,
            ParameterType.OBJECT: self._validate_object,
            ParameterType.ENUM: self._validate_enum,
            ParameterType.DATE: self._validate_date,
            ParameterType.DATETIME: self._validate_datetime,
            ParameterType.FILE: self._validate_file,
            ParameterType.PATH: self._validate_path
        }
    
    def process_parameters(self, parameters: Dict[str, Any], 
                          parameter_definitions: List[Dict]) -> Dict[str, Any]:
        """
        处理参数：验证、转换和填充默认值
        
        Args:
            parameters: 原始参数字典
            parameter_definitions: 参数定义列表
            
        Returns:
            处理后的参数字典
        """
        processed_params = {}
        errors = []
        
        for param_def in parameter_definitions:
            param_name = param_def.get("name")
            if not param_name:
                continue
                
            param_type_str = param_def.get("type", "string")
            param_type = self._parse_parameter_type(param_type_str)
            is_optional = param_def.get("optional", False)
            default_value = param_def.get("default")
            allowed_values = param_def.get("values", [])
            min_value = param_def.get("min")
            max_value = param_def.get("max")
            pattern = param_def.get("pattern")
            description = param_def.get("description", "")
            
            # 检查参数是否存在
            if param_name not in parameters:
                if not is_optional and default_value is None:
                    errors.append(f"缺少必需参数: {param_name}")
                    continue
                elif default_value is not None:
                    processed_params[param_name] = default_value
                    logger.debug(f"使用默认值: {param_name} = {default_value}")
                    continue
                else:
                    # 可选参数且没有默认值，跳过
                    continue
            
            param_value = parameters[param_name]
            
            try:
                # 类型转换
                converted_value = self.convert_value(param_value, param_type, param_def)
                
                # 验证
                validation_error = self.validate_value(converted_value, param_type, param_def)
                if validation_error:
                    errors.append(f"参数 {param_name} 验证失败: {validation_error}")
                    continue
                    
                processed_params[param_name] = converted_value
                
            except Exception as e:
                errors.append(f"参数 {param_name} 处理失败: {e}")
        
        # 检查额外参数
        extra_params = {k: v for k, v in parameters.items() 
                       if k not in [p.get("name") for p in parameter_definitions]}
        if extra_params:
            logger.warning(f"发现额外参数: {list(extra_params.keys())}")
            # 可以选择是否包含额外参数
            # processed_params.update(extra_params)
        
        if errors:
            raise ValueError(f"参数处理失败: {'; '.join(errors)}")
            
        return processed_params
    
    def convert_value(self, value: Any, param_type: ParameterType, 
                     param_def: Dict = None) -> Any:
        """转换参数值到目标类型"""
        if param_def is None:
            param_def = {}
            
        # 获取转换器
        converter = self.type_converters.get(param_type)
        if not converter:
            logger.warning(f"未知参数类型: {param_type}，当作字符串处理")
            converter = self._convert_to_string
            
        # 执行转换
        try:
            return converter(value, param_def)
        except Exception as e:
            raise ValueError(f"类型转换失败 ({param_type.value}): {e}")
    
    def validate_value(self, value: Any, param_type: ParameterType, 
                      param_def: Dict = None) -> Optional[str]:
        """验证参数值"""
        if param_def is None:
            param_def = {}
            
        # 获取验证器
        validator = self.validators.get(param_type)
        if not validator:
            return None
            
        try:
            return validator(value, param_def)
        except Exception as e:
            return str(e)
    
    def _parse_parameter_type(self, type_str: str) -> ParameterType:
        """解析参数类型字符串"""
        type_str_lower = type_str.lower().strip()
        
        type_mapping = {
            "str": ParameterType.STRING,
            "string": ParameterType.STRING,
            "text": ParameterType.STRING,
            
            "int": ParameterType.INTEGER,
            "integer": ParameterType.INTEGER,
            "number": ParameterType.INTEGER,
            
            "float": ParameterType.FLOAT,
            "double": ParameterType.FLOAT,
            "decimal": ParameterType.FLOAT,
            
            "bool": ParameterType.BOOLEAN,
            "boolean": ParameterType.BOOLEAN,
            
            "list": ParameterType.ARRAY,
            "array": ParameterType.ARRAY,
            
            "dict": ParameterType.OBJECT,
            "object": ParameterType.OBJECT,
            "json": ParameterType.OBJECT,
            
            "enum": ParameterType.ENUM,
            "choice": ParameterType.ENUM,
            
            "date": ParameterType.DATE,
            "datetime": ParameterType.DATETIME,
            "timestamp": ParameterType.DATETIME,
            
            "file": ParameterType.FILE,
            "path": ParameterType.PATH,
            "directory": ParameterType.PATH
        }
        
        if type_str_lower in type_mapping:
            return type_mapping[type_str_lower]
        else:
            logger.warning(f"未知参数类型: {type_str}，默认使用STRING")
            return ParameterType.STRING
    
    # 类型转换方法
    def _convert_to_string(self, value: Any, param_def: Dict) -> str:
        """转换为字符串"""
        if value is None:
            return ""
        return str(value)
    
    def _convert_to_integer(self, value: Any, param_def: Dict) -> int:
        """转换为整数"""
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            try:
                return int(float(value)) if '.' in value else int(value)
            except ValueError:
                raise ValueError(f"无法将 '{value}' 转换为整数")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_float(self, value: Any, param_def: Dict) -> float:
        """转换为浮点数"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"无法将 '{value}' 转换为浮点数")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_boolean(self, value: Any, param_def: Dict) -> bool:
        """转换为布尔值"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ["true", "yes", "1", "on", "enable"]:
                return True
            elif value_lower in ["false", "no", "0", "off", "disable"]:
                return False
            else:
                raise ValueError(f"无法将字符串 '{value}' 转换为布尔值")
        elif isinstance(value, (int, float)):
            return bool(value)
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_array(self, value: Any, param_def: Dict) -> List:
        """转换为数组"""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            # 尝试解析JSON数组
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # 尝试解析逗号分隔的列表
            if value.strip():
                # 支持多种分隔符：逗号、分号、换行
                separators = [',', ';', '\n']
                for sep in separators:
                    if sep in value:
                        items = [item.strip() for item in value.split(sep) if item.strip()]
                        return items
                
                # 如果没有分隔符，返回单元素列表
                return [value.strip()]
            else:
                return []
        elif isinstance(value, tuple):
            return list(value)
        else:
            # 其他类型转换为单元素列表
            return [value]
    
    def _convert_to_object(self, value: Any, param_def: Dict) -> Dict:
        """转换为对象"""
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError("JSON字符串不是对象")
            except json.JSONDecodeError as e:
                raise ValueError(f"无法解析JSON: {e}")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_enum(self, value: Any, param_def: Dict) -> str:
        """转换为枚举值"""
        allowed_values = param_def.get("values", [])
        value_str = str(value)
        
        if allowed_values and value_str not in allowed_values:
            # 尝试不区分大小写匹配
            value_lower = value_str.lower()
            allowed_lower = [str(v).lower() for v in allowed_values]
            
            if value_lower in allowed_lower:
                idx = allowed_lower.index(value_lower)
                return str(allowed_values[idx])
            else:
                raise ValueError(f"值 '{value_str}' 不在允许的范围内: {allowed_values}")
        
        return value_str
    
    def _convert_to_date(self, value: Any, param_def: Dict) -> str:
        """转换为日期字符串"""
        if isinstance(value, datetime):
            return value.date().isoformat()
        elif isinstance(value, str):
            # 尝试解析常见日期格式
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
                r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
                r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
            ]
            
            for pattern in date_patterns:
                if re.match(pattern, value):
                    # 简单验证，实际应用中可能需要更严格的验证
                    return value
            
            raise ValueError(f"无法识别的日期格式: {value}")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_datetime(self, value: Any, param_def: Dict) -> str:
        """转换为日期时间字符串"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, str):
            # 尝试解析ISO格式
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.isoformat()
            except ValueError:
                raise ValueError(f"无法识别的日期时间格式: {value}")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_file(self, value: Any, param_def: Dict) -> str:
        """转换为文件路径"""
        if isinstance(value, str):
            # 简单验证文件路径格式
            if '/' in value or '\\' in value or '.' in value:
                return value
            else:
                raise ValueError(f"无效的文件路径: {value}")
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    def _convert_to_path(self, value: Any, param_def: Dict) -> str:
        """转换为路径"""
        if isinstance(value, str):
            return value
        else:
            raise ValueError(f"不支持的类型: {type(value)}")
    
    # 验证方法
    def _validate_string(self, value: str, param_def: Dict) -> Optional[str]:
        """验证字符串"""
        pattern = param_def.get("pattern")
        min_length = param_def.get("minLength")
        max_length = param_def.get("maxLength")
        
        if pattern and not re.match(pattern, value):
            return f"字符串不匹配模式: {pattern}"
            
        if min_length is not None and len(value) < min_length:
            return f"字符串长度小于最小值 {min_length}"
            
        if max_length is not None and len(value) > max_length:
            return f"字符串长度大于最大值 {max_length}"
            
        return None
    
    def _validate_integer(self, value: int, param_def: Dict) -> Optional[str]:
        """验证整数"""
        min_value = param_def.get("min")
        max_value = param_def.get("max")
        
        if min_value is not None and value < min_value:
            return f"整数小于最小值 {min_value}"
            
        if max_value is not None and value > max_value:
            return f"整数大于最大值 {max_value}"
            
        return None
    
    def _validate_float(self, value: float, param_def: Dict) -> Optional[str]:
        """验证浮点数"""
        min_value = param_def.get("min")
        max_value = param_def.get("max")
        
        if min_value is not None and value < min_value:
            return f"浮点数小于最小值 {min_value}"
            
        if max_value is not None and value > max_value:
            return f"浮点数大于最大值 {max_value}"
            
        return None
    
    def _validate_boolean(self, value: bool, param_def: Dict) -> Optional[str]:
        """验证布尔值"""
        # 布尔值总是有效的
        return None
    
    def _validate_array(self, value: List, param_def: Dict) -> Optional[str]:
        """验证数组"""
        min_items = param_def.get("minItems")
        max_items = param_def.get("maxItems")
        
        if min_items is not None and len(value) < min_items:
            return f"数组元素数量小于最小值 {min_items}"
            
        if max_items is not None and len(value) > max_items:
            return f"数组元素数量大于最大值 {max_items}"
            
        # 验证数组元素类型（如果指定）
        item_type = param_def.get("itemType")
        if item_type:
            item_param_def = {"type": item_type}
            for i, item in enumerate(value):
                try:
                    item_type_enum = self._parse_parameter_type(item_type)
                    self.convert_value(item, item_type_enum, item_param_def)
                except Exception as e:
                    return f"数组元素 {i} 无效: {e}"
        
        return None
    
    def _validate_object(self, value: Dict, param_def: Dict) -> Optional[str]:
        """验证对象"""
        # 可以添加更复杂的对象验证逻辑
        return None
    
    def _validate_enum(self, value: str, param_def: Dict) -> Optional[str]:
        """验证枚举值"""
        allowed_values = param_def.get("values", [])
        if allowed_values and value not in allowed_values:
            return f"值 '{value}' 不在允许的范围内: {allowed_values}"
        return None
    
    def _validate_date(self, value: str, param_def: Dict) -> Optional[str]:
        """验证日期"""
        # 简单验证日期格式
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, value):
            return f"无效的日期格式，应为YYYY-MM-DD: {value}"
        return None
    
    def _validate_datetime(self, value: str, param_def: Dict) -> Optional[str]:
        """验证日期时间"""
        # 简单验证ISO格式
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return f"无效的日期时间格式，应为ISO格式: {value}"
        return None
    
    def _validate_file(self, value: str, param_def: Dict) -> Optional[str]:
        """验证文件"""
        # 可以添加文件存在性检查
        # 但为了灵活性，不强制要求文件必须存在
        return None
    
    def _validate_path(self, value: str, param_def: Dict) -> Optional[str]:
        """验证路径"""
        # 可以添加路径存在性检查
        return None


class ResultParser:
    """技能结果解析器"""
    
    def __init__(self):
        self.formatters = {
            "default": self._format_default,
            "json": self._format_json,
            "text": self._format_text,
            "table": self._format_table,
            "markdown": self._format_markdown,
            "html": self._format_html
        }
    
    def parse_result(self, result: Any, format_spec: Dict = None) -> Dict[str, Any]:
        """
        解析技能调用结果
        
        Args:
            result: 原始结果
            format_spec: 格式规范
            
        Returns:
            标准化的结果字典
        """
        if format_spec is None:
            format_spec = {}
            
        # 确定结果类型
        result_type = self._determine_result_type(result)
        
        # 标准化结果
        standardized = self._standardize_result(result, result_type)
        
        # 应用格式（如果需要）
        output_format = format_spec.get("format", "default")
        formatter = self.formatters.get(output_format, self._format_default)
        
        formatted_result = formatter(standardized, format_spec)
        
        # 构建最终结果
        final_result = {
            "success": True,
            "data": standardized.get("data", result),
            "metadata": {
                "result_type": result_type,
                "timestamp": datetime.now().isoformat(),
                "processing_time": None,  # 可以由调用者填充
                **standardized.get("metadata", {})
            },
            "formatted": formatted_result
        }
        
        return final_result
    
    def parse_error(self, error: Exception, context: Dict = None) -> Dict[str, Any]:
        """
        解析错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            标准化的错误结果字典
        """
        if context is None:
            context = {}
            
        error_result = {
            "success": False,
            "error": {
                "type": error.__class__.__name__,
                "message": str(error),
                "details": self._extract_error_details(error)
            },
            "context": context,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "error_type": "skill_invocation_error"
            }
        }
        
        return error_result
    
    def _determine_result_type(self, result: Any) -> str:
        """确定结果类型"""
        if isinstance(result, dict):
            # 检查是否是标准化结果
            if "success" in result and "data" in result:
                return "standardized"
            else:
                return "dictionary"
        elif isinstance(result, list):
            return "list"
        elif isinstance(result, str):
            # 检查是否是JSON字符串
            try:
                json.loads(result)
                return "json_string"
            except json.JSONDecodeError:
                return "text"
        elif isinstance(result, (int, float)):
            return "numeric"
        elif isinstance(result, bool):
            return "boolean"
        elif result is None:
            return "null"
        else:
            return "object"
    
    def _standardize_result(self, result: Any, result_type: str) -> Dict[str, Any]:
        """标准化结果"""
        if result_type == "standardized":
            # 已经是标准化格式
            return result
            
        standardized = {
            "data": result,
            "metadata": {
                "original_type": result_type,
                "size": self._estimate_size(result)
            }
        }
        
        # 添加类型特定的元数据
        if result_type == "dictionary":
            standardized["metadata"]["key_count"] = len(result) if isinstance(result, dict) else 0
        elif result_type == "list":
            standardized["metadata"]["item_count"] = len(result) if isinstance(result, list) else 0
        elif result_type == "text":
            standardized["metadata"]["length"] = len(result) if isinstance(result, str) else 0
        
        return standardized
    
    def _estimate_size(self, data: Any) -> int:
        """估计数据大小（字节）"""
        try:
            return len(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except:
            return len(str(data).encode('utf-8'))
    
    def _extract_error_details(self, error: Exception) -> Dict:
        """提取错误详情"""
        import traceback
        
        details = {
            "exception_args": list(error.args) if hasattr(error, 'args') else [],
            "exception_module": error.__class__.__module__,
        }
        
        # 添加堆栈跟踪（限制长度）
        try:
            tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
            # 只保留最后5行以避免过大
            if len(tb_lines) > 5:
                tb_lines = tb_lines[:2] + ["...\n"] + tb_lines[-3:]
            details["traceback"] = "".join(tb_lines)
        except:
            details["traceback"] = "无法获取堆栈跟踪"
            
        return details
    
    # 格式化方法
    def _format_default(self, standardized: Dict, format_spec: Dict) -> Any:
        """默认格式化：返回原始数据"""
        return standardized.get("data")
    
    def _format_json(self, standardized: Dict, format_spec: Dict) -> str:
        """JSON格式化"""
        indent = format_spec.get("indent", 2)
        ensure_ascii = format_spec.get("ensure_ascii", False)
        
        try:
            return json.dumps(standardized.get("data"), indent=indent, 
                             ensure_ascii=ensure_ascii, default=str)
        except:
            # 如果无法序列化，返回字符串表示
            return str(standardized.get("data"))
    
    def _format_text(self, standardized: Dict, format_spec: Dict) -> str:
        """文本格式化"""
        data = standardized.get("data")
        
        if isinstance(data, str):
            return data
        elif isinstance(data, (dict, list)):
            # 尝试转换为可读文本
            try:
                return json.dumps(data, ensure_ascii=False, indent=2, default=str)
            except:
                return str(data)
        else:
            return str(data)
    
    def _format_table(self, standardized: Dict, format_spec: Dict) -> str:
        """表格格式化（简化版）"""
        data = standardized.get("data")
        
        if isinstance(data, list):
            if not data:
                return "空列表"
                
            # 如果是字典列表，创建表格
            if all(isinstance(item, dict) for item in data):
                headers = set()
                for item in data:
                    headers.update(item.keys())
                headers = list(headers)
                
                # 构建表格
                table_lines = []
                table_lines.append(" | ".join(headers))
                table_lines.append("-|-".join(["---"] * len(headers)))
                
                for item in data:
                    row = []
                    for header in headers:
                        value = item.get(header, "")
                        # 简化显示
                        if isinstance(value, (dict, list)):
                            value = str(type(value)).split("'")[1]
                        row.append(str(value))
                    table_lines.append(" | ".join(row))
                    
                return "\n".join(table_lines)
            else:
                # 简单列表
                return "\n".join([f"- {item}" for item in data])
                
        elif isinstance(data, dict):
            # 字典显示为键值对
            lines = []
            for key, value in data.items():
                lines.append(f"{key}: {value}")
            return "\n".join(lines)
        else:
            return str(data)
    
    def _format_markdown(self, standardized: Dict, format_spec: Dict) -> str:
        """Markdown格式化"""
        data = standardized.get("data")
        title = format_spec.get("title", "结果")
        
        lines = [f"# {title}", ""]
        
        if isinstance(data, dict):
            lines.append("## 数据详情")
            lines.append("")
            for key, value in data.items():
                lines.append(f"**{key}**: {value}")
                
        elif isinstance(data, list):
            lines.append("## 列表数据")
            lines.append("")
            for i, item in enumerate(data, 1):
                lines.append(f"{i}. {item}")
                
        else:
            lines.append("## 结果")
            lines.append("")
            lines.append(str(data))
            
        return "\n".join(lines)
    
    def _format_html(self, standardized: Dict, format_spec: Dict) -> str:
        """HTML格式化（简化版）"""
        data = standardized.get("data")
        title = format_spec.get("title", "结果")
        
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>"
        ]
        
        if isinstance(data, dict):
            html_lines.append("<table>")
            html_lines.append("<tr><th>键</th><th>值</th></tr>")
            for key, value in data.items():
                html_lines.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
            html_lines.append("</table>")
            
        elif isinstance(data, list):
            html_lines.append("<ul>")
            for item in data:
                html_lines.append(f"<li>{item}</li>")
            html_lines.append("</ul>")
            
        else:
            html_lines.append(f"<p>{data}</p>")
            
        html_lines.append("</body>")
        html_lines.append("</html>")
        
        return "\n".join(html_lines)


# 工具函数
def create_parameter_handler() -> ParameterHandler:
    """创建参数处理器"""
    return ParameterHandler()


def create_result_parser() -> ResultParser:
    """创建结果解析器"""
    return ResultParser()


def process_and_invoke(skill_invoker, skill_name: str, function_name: str,
                      parameters: Dict, parameter_definitions: List[Dict],
                      timeout: int = 30) -> Dict[str, Any]:
    """
    处理参数并调用技能的简化函数
    
    Args:
        skill_invoker: 技能调用器实例
        skill_name: 技能名称
        function_name: 函数名称
        parameters: 原始参数字典
        parameter_definitions: 参数定义
        timeout: 超时时间
        
    Returns:
        标准化的结果
    """
    param_handler = create_parameter_handler()
    result_parser = create_result_parser()
    
    try:
        # 处理参数
        processed_params = param_handler.process_parameters(parameters, parameter_definitions)
        
        # 调用技能
        start_time = datetime.now()
        raw_result = skill_invoker.invoke_skill(skill_name, function_name, 
                                               processed_params, timeout)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 解析结果
        format_spec = {
            "format": "default",
            "processing_time": processing_time
        }
        
        result = result_parser.parse_result(raw_result, format_spec)
        result["metadata"]["processing_time"] = processing_time
        
        return result
        
    except Exception as e:
        # 解析错误
        context = {
            "skill": skill_name,
            "function": function_name,
            "parameters": parameters
        }
        
        return result_parser.parse_error(e, context)


if __name__ == "__main__":
    # 测试参数处理器
    print("=== 参数处理器测试 ===")
    
    handler = create_parameter_handler()
    
    # 测试用例
    param_defs = [
        {"name": "name", "type": "string", "description": "名称"},
        {"name": "age", "type": "integer", "min": 0, "max": 150, "optional": True, "default": 30},
        {"name": "active", "type": "boolean", "optional": True, "default": True},
        {"name": "tags", "type": "array", "itemType": "string", "optional": True},
        {"name": "options", "type": "object", "optional": True}
    ]
    
    test_params = {
        "name": "测试用户",
        "age": "25",  # 字符串，应该转换为整数
        "active": "yes",  # 应该转换为True
        "tags": "python,ai,machine learning",  # 逗号分隔字符串
        "options": '{"theme": "dark", "notifications": true}'
    }
    
    try:
        processed = handler.process_parameters(test_params, param_defs)
        print("处理后的参数:")
        for key, value in processed.items():
            print(f"  {key}: {value} ({type(value).__name__})")
    except Exception as e:
        print(f"参数处理失败: {e}")
    
    print("\n=== 结果解析器测试 ===")
    
    parser = create_result_parser()
    
    # 测试结果
    test_results = [
        {"name": "张三", "age": 25, "city": "北京"},
        [1, 2, 3, 4, 5],
        "简单的文本结果",
        42,
        True
    ]
    
    for i, test_result in enumerate(test_results):
        print(f"\n测试结果 {i+1} ({type(test_result).__name__}):")
        parsed = parser.parse_result(test_result)
        print(f"  类型: {parsed['metadata']['result_type']}")
        print(f"  格式化: {parsed['formatted']}")
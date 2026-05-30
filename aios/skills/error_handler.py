"""
AI OS技能调用错误处理和重试逻辑
提供重试策略、断路器模式、超时处理和错误恢复机制
"""

import time
import random
from typing import Dict, List, Any, Optional, Callable, Tuple
import logging
from datetime import datetime, timedelta
from enum import Enum
import functools

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略"""
    NO_RETRY = "no_retry"
    FIXED = "fixed"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    RANDOM_BACKOFF = "random_backoff"


class CircuitBreakerState(Enum):
    """断路器状态"""
    CLOSED = "closed"      # 正常状态，允许请求通过
    OPEN = "open"          # 断路状态，拒绝所有请求
    HALF_OPEN = "half_open"  # 半开状态，允许有限请求测试恢复


class SkillInvocationError(Exception):
    """技能调用错误（增强版）"""
    def __init__(self, message: str, skill_name: str = None, 
                 function_name: str = None, original_error: Exception = None,
                 retry_count: int = 0):
        super().__init__(message)
        self.skill_name = skill_name
        self.function_name = function_name
        self.original_error = original_error
        self.retry_count = retry_count
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "message": str(self),
            "skill_name": self.skill_name,
            "function_name": self.function_name,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp.isoformat(),
            "original_error": str(self.original_error) if self.original_error else None
        }


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_retries: int = 3, 
                 strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 jitter: bool = True):
        """
        初始化重试管理器
        
        Args:
            max_retries: 最大重试次数
            strategy: 重试策略
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
            jitter: 是否添加随机抖动
        """
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        带重试的执行
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
            
        Returns:
            函数执行结果
            
        Raises:
            SkillInvocationError: 重试耗尽后抛出
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):  # +1 包括第一次尝试
            try:
                if attempt > 0:
                    logger.info(f"重试 {attempt}/{self.max_retries} 次调用 {func.__name__}")
                    
                return func(*args, **kwargs)
                
            except Exception as e:
                last_error = e
                
                # 检查是否应该重试
                if attempt >= self.max_retries or not self._should_retry(e):
                    break
                    
                # 计算延迟并等待
                delay = self._calculate_delay(attempt)
                logger.debug(f"调用失败，等待 {delay:.2f} 秒后重试: {e}")
                time.sleep(delay)
        
        # 所有重试都失败
        error_msg = f"函数 {func.__name__} 调用失败，重试 {self.max_retries} 次后仍失败"
        raise SkillInvocationError(
            message=error_msg,
            original_error=last_error,
            retry_count=self.max_retries
        )
    
    def _should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        # 根据错误类型决定是否重试
        error_str = str(error).lower()
        
        # 通常应该重试的错误
        retryable_errors = [
            "timeout", "timed out", "connection", "network",
            "busy", "temporary", "retry", "again", "429", "503"
        ]
        
        for retryable in retryable_errors:
            if retryable in error_str:
                return True
                
        # 通常不应该重试的错误
        non_retryable_errors = [
            "not found", "404", "invalid", "validation",
            "permission", "auth", "unauthorized", "syntax"
        ]
        
        for non_retryable in non_retryable_errors:
            if non_retryable in error_str:
                return False
                
        # 默认重试（保守策略）
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        if self.strategy == RetryStrategy.NO_RETRY:
            return 0
            
        elif self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
            
        elif self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
            
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = min(self.base_delay * (attempt + 1), self.max_delay)
            
        elif self.strategy == RetryStrategy.RANDOM_BACKOFF:
            delay = random.uniform(self.base_delay, 
                                  min(self.base_delay * (2 ** attempt), self.max_delay))
            
        else:
            delay = self.base_delay
        
        # 添加抖动
        if self.jitter and delay > 0:
            jitter_amount = delay * 0.1  # 10% 抖动
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.1, delay)  # 确保最小延迟
        
        return delay


class CircuitBreaker:
    """断路器"""
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: float = 30.0,
                 half_open_max_attempts: int = 3):
        """
        初始化断路器
        
        Args:
            failure_threshold: 失败阈值，达到此值时断路器打开
            recovery_timeout: 恢复超时（秒），断路器打开后多久进入半开状态
            half_open_max_attempts: 半开状态最大尝试次数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_attempts = half_open_max_attempts
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0
        self.success_count = 0
        
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过断路器执行函数
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 函数执行错误或断路器打开时抛出
        """
        # 检查断路器状态
        self._check_state()
        
        if self.state == CircuitBreakerState.OPEN:
            raise SkillInvocationError("断路器打开，拒绝请求")
            
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 成功处理
            self._on_success()
            return result
            
        except Exception as e:
            # 失败处理
            self._on_failure(e)
            raise
    
    def _check_state(self):
        """检查并更新断路器状态"""
        if self.state == CircuitBreakerState.OPEN:
            # 检查是否应该进入半开状态
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    logger.info(f"断路器从 OPEN 进入 HALF_OPEN 状态")
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_attempts = 0
                    self.success_count = 0
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # 检查是否应该关闭或重新打开
            if self.half_open_attempts >= self.half_open_max_attempts:
                if self.success_count > 0:
                    # 有成功请求，关闭断路器
                    logger.info(f"断路器从 HALF_OPEN 进入 CLOSED 状态")
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                else:
                    # 没有成功请求，重新打开
                    logger.warning(f"断路器从 HALF_OPEN 重新进入 OPEN 状态")
                    self.state = CircuitBreakerState.OPEN
                    self.last_failure_time = datetime.now()
    
    def _on_success(self):
        """成功处理"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            self.half_open_attempts += 1
        else:
            # 重置失败计数
            self.failure_count = 0
            
        logger.debug(f"断路器成功处理，状态: {self.state.value}")
    
    def _on_failure(self, error: Exception):
        """失败处理"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_attempts += 1
        elif self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.warning(f"断路器从 CLOSED 进入 OPEN 状态，失败次数: {self.failure_count}")
                self.state = CircuitBreakerState.OPEN
        
        logger.debug(f"断路器失败处理，状态: {self.state.value}, 失败计数: {self.failure_count}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取断路器状态"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "half_open_attempts": self.half_open_attempts,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "is_open": self.state == CircuitBreakerState.OPEN
        }


class TimeoutManager:
    """超时管理器"""
    
    def __init__(self, default_timeout: float = 30.0):
        """
        初始化超时管理器
        
        Args:
            default_timeout: 默认超时时间（秒）
        """
        self.default_timeout = default_timeout
        
    def execute_with_timeout(self, func: Callable, timeout: float = None,
                            *args, **kwargs) -> Any:
        """
        带超时的执行
        
        Args:
            func: 要执行的函数
            timeout: 超时时间（秒），None使用默认值
            *args, **kwargs: 函数参数
            
        Returns:
            函数执行结果
            
        Raises:
            TimeoutError: 超时时抛出
        """
        if timeout is None:
            timeout = self.default_timeout
            
        # 使用简单的线程超时（实际实现可能需要使用线程或异步）
        # 注意：这是一个简化实现，实际应用中可能需要更复杂的超时机制
        start_time = time.time()
        
        try:
            # 执行函数（简化实现，实际可能需要多线程）
            result = func(*args, **kwargs)
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.warning(f"函数 {func.__name__} 执行时间 ({elapsed:.2f}s) 超过超时时间 ({timeout}s)")
                
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"函数 {func.__name__} 执行超时 ({timeout}s)")
            else:
                raise  # 重新抛出原始异常


class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self, fallback_functions: Dict[str, Callable] = None):
        """
        初始化错误恢复管理器
        
        Args:
            fallback_functions: 降级函数字典 {function_name: fallback_function}
        """
        self.fallback_functions = fallback_functions or {}
        self.recovery_strategies = {}
        
    def execute_with_fallback(self, func: Callable, fallback_func: Callable = None,
                             func_name: str = None, *args, **kwargs) -> Any:
        """
        带降级执行的函数
        
        Args:
            func: 主函数
            fallback_func: 降级函数，None时尝试从字典中查找
            func_name: 函数名称，用于查找降级函数
            *args, **kwargs: 函数参数
            
        Returns:
            主函数或降级函数的执行结果
        """
        if func_name is None:
            func_name = func.__name__ if hasattr(func, '__name__') else 'unknown'
            
        if fallback_func is None:
            fallback_func = self.fallback_functions.get(func_name)
            
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            logger.warning(f"主函数 {func_name} 执行失败，尝试降级: {e}")
            
            if fallback_func:
                try:
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"降级函数也失败: {fallback_error}")
                    raise SkillInvocationError(
                        f"主函数和降级函数都失败: {e}; {fallback_error}",
                        original_error=e
                    )
            else:
                # 没有降级函数，重新抛出错误
                raise
    
    def add_recovery_strategy(self, error_pattern: str, 
                             recovery_func: Callable,
                             description: str = ""):
        """
        添加错误恢复策略
        
        Args:
            error_pattern: 错误模式（字符串匹配）
            recovery_func: 恢复函数
            description: 策略描述
        """
        self.recovery_strategies[error_pattern] = {
            "func": recovery_func,
            "description": description
        }
    
    def attempt_recovery(self, error: Exception, context: Dict = None) -> Optional[Any]:
        """
        尝试错误恢复
        
        Args:
            error: 错误异常
            context: 错误上下文
            
        Returns:
            恢复结果，如果无法恢复则返回None
        """
        error_str = str(error).lower()
        
        for pattern, strategy in self.recovery_strategies.items():
            if pattern.lower() in error_str:
                logger.info(f"尝试恢复策略: {pattern} - {strategy['description']}")
                
                try:
                    return strategy["func"](error, context)
                except Exception as recovery_error:
                    logger.error(f"恢复策略失败: {recovery_error}")
                    
        return None


class CompositeErrorHandler:
    """复合错误处理器（整合重试、断路器、超时、恢复）"""
    
    def __init__(self, skill_name: str = None, config: Dict = None):
        """
        初始化复合错误处理器
        
        Args:
            skill_name: 技能名称
            config: 配置字典
        """
        self.skill_name = skill_name
        
        if config is None:
            config = {}
            
        # 初始化各个组件
        retry_config = config.get("retry", {})
        self.retry_manager = RetryManager(
            max_retries=retry_config.get("max_retries", 3),
            strategy=RetryStrategy(retry_config.get("strategy", "exponential_backoff")),
            base_delay=retry_config.get("base_delay", 1.0),
            max_delay=retry_config.get("max_delay", 30.0),
            jitter=retry_config.get("jitter", True)
        )
        
        circuit_config = config.get("circuit_breaker", {})
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_config.get("failure_threshold", 5),
            recovery_timeout=circuit_config.get("recovery_timeout", 30.0),
            half_open_max_attempts=circuit_config.get("half_open_max_attempts", 3)
        )
        
        timeout_config = config.get("timeout", {})
        self.timeout_manager = TimeoutManager(
            default_timeout=timeout_config.get("default_timeout", 30.0)
        )
        
        recovery_config = config.get("recovery", {})
        self.recovery_manager = ErrorRecoveryManager(
            fallback_functions=recovery_config.get("fallback_functions", {})
        )
        
        # 统计信息
        self.stats = {
            "total_invocations": 0,
            "successful_invocations": 0,
            "failed_invocations": 0,
            "retry_attempts": 0,
            "circuit_breaker_trips": 0,
            "fallback_executions": 0
        }
        
        # 错误历史
        self.error_history = []
        
    def execute(self, func: Callable, func_name: str = None, 
               timeout: float = None, use_circuit_breaker: bool = True,
               use_retry: bool = True, fallback_func: Callable = None,
               *args, **kwargs) -> Any:
        """
        执行函数，应用所有错误处理机制
        
        Args:
            func: 要执行的函数
            func_name: 函数名称
            timeout: 超时时间
            use_circuit_breaker: 是否使用断路器
            use_retry: 是否使用重试
            fallback_func: 降级函数
            *args, **kwargs: 函数参数
            
        Returns:
            函数执行结果
        """
        self.stats["total_invocations"] += 1
        
        if func_name is None:
            func_name = func.__name__ if hasattr(func, '__name__') else 'unknown'
            
        # 定义内部执行函数
        def _execute_with_timeout():
            return self.timeout_manager.execute_with_timeout(func, timeout, *args, **kwargs)
            
        def _execute_with_circuit_breaker():
            return self.circuit_breaker.execute(_execute_with_timeout)
            
        def _execute_with_retry():
            return self.retry_manager.execute_with_retry(_execute_with_circuit_breaker)
            
        # 确定执行链
        if use_circuit_breaker and use_retry:
            execution_chain = _execute_with_retry
        elif use_circuit_breaker:
            execution_chain = _execute_with_circuit_breaker
        elif use_retry:
            execution_chain = lambda: self.retry_manager.execute_with_retry(_execute_with_timeout)
        else:
            execution_chain = _execute_with_timeout
            
        try:
            # 执行
            result = execution_chain()
            
            # 成功
            self.stats["successful_invocations"] += 1
            return result
            
        except Exception as e:
            # 失败
            self.stats["failed_invocations"] += 1
            
            # 记录错误
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "skill_name": self.skill_name,
                "function_name": func_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "args": str(args),
                "kwargs": str(kwargs)
            }
            self.error_history.append(error_record)
            
            # 限制错误历史大小
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-50:]
            
            # 尝试恢复
            recovery_context = {
                "skill_name": self.skill_name,
                "function_name": func_name,
                "args": args,
                "kwargs": kwargs
            }
            
            recovery_result = self.recovery_manager.attempt_recovery(e, recovery_context)
            if recovery_result is not None:
                logger.info(f"错误恢复成功: {func_name}")
                self.stats["successful_invocations"] += 1  # 恢复成功也算成功
                return recovery_result
                
            # 尝试降级
            if fallback_func:
                try:
                    logger.info(f"尝试执行降级函数: {func_name}")
                    fallback_result = self.recovery_manager.execute_with_fallback(
                        func, fallback_func, func_name, *args, **kwargs
                    )
                    self.stats["fallback_executions"] += 1
                    self.stats["successful_invocations"] += 1
                    return fallback_result
                except Exception as fallback_error:
                    logger.error(f"降级函数也失败: {fallback_error}")
            
            # 所有恢复尝试都失败，重新抛出错误
            raise SkillInvocationError(
                f"技能调用失败且无法恢复: {e}",
                skill_name=self.skill_name,
                function_name=func_name,
                original_error=e
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        success_rate = 0
        if self.stats["total_invocations"] > 0:
            success_rate = self.stats["successful_invocations"] / self.stats["total_invocations"]
            
        return {
            **self.stats,
            "success_rate": success_rate,
            "circuit_breaker_status": self.circuit_breaker.get_status(),
            "error_history_size": len(self.error_history)
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_invocations": 0,
            "successful_invocations": 0,
            "failed_invocations": 0,
            "retry_attempts": 0,
            "circuit_breaker_trips": 0,
            "fallback_executions": 0
        }
        self.error_history = []


# 装饰器版本
def with_error_handling(skill_name: str = None, config: Dict = None):
    """
    错误处理装饰器
    
    Args:
        skill_name: 技能名称
        config: 错误处理配置
    """
    def decorator(func):
        handler = CompositeErrorHandler(skill_name, config)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute(func, func.__name__, *args, **kwargs)
            
        # 添加属性以便访问处理器
        wrapper.error_handler = handler
        return wrapper
        
    return decorator


# 工具函数
def create_default_error_handler(skill_name: str = None) -> CompositeErrorHandler:
    """创建默认错误处理器"""
    config = {
        "retry": {
            "max_retries": 3,
            "strategy": "exponential_backoff",
            "base_delay": 1.0,
            "max_delay": 30.0,
            "jitter": True
        },
        "circuit_breaker": {
            "failure_threshold": 5,
            "recovery_timeout": 30.0,
            "half_open_max_attempts": 3
        },
        "timeout": {
            "default_timeout": 30.0
        }
    }
    
    return CompositeErrorHandler(skill_name, config)


if __name__ == "__main__":
    # 测试错误处理器
    print("=== 错误处理器测试 ===")
    
    # 配置日志
    logging.basicConfig(level=logging.DEBUG)
    
    # 测试函数
    def unreliable_function(success_rate: float = 0.3):
        """不可靠的函数，有一定概率失败"""
        import random
        if random.random() < success_rate:
            return "成功!"
        else:
            raise Exception("随机失败")
    
    def fallback_function():
        """降级函数"""
        return "降级成功!"
    
    # 创建错误处理器
    handler = create_default_error_handler("测试技能")
    
    # 测试执行
    print("\n测试带错误处理的函数调用:")
    
    results = []
    for i in range(10):
        try:
            result = handler.execute(
                lambda: unreliable_function(0.3),
                func_name="unreliable_function",
                fallback_func=fallback_function
            )
            results.append(("成功", result))
        except Exception as e:
            results.append(("失败", str(e)))
    
    # 显示结果
    for i, (status, result) in enumerate(results):
        print(f"  调用 {i+1}: {status} - {result}")
    
    # 显示统计信息
    stats = handler.get_stats()
    print(f"\n统计信息:")
    print(f"  总调用: {stats['total_invocations']}")
    print(f"  成功: {stats['successful_invocations']}")
    print(f"  失败: {stats['failed_invocations']}")
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  降级执行: {stats['fallback_executions']}")
    
    # 测试装饰器版本
    print("\n测试装饰器版本:")
    
    @with_error_handling("装饰器测试")
    def decorated_function():
        return unreliable_function(0.5)
    
    try:
        result = decorated_function()
        print(f"  装饰器函数结果: {result}")
        print(f"  处理器统计: {decorated_function.error_handler.get_stats()}")
    except Exception as e:
        print(f"  装饰器函数失败: {e}")
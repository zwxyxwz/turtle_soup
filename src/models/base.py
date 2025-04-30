from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional, List, Union
from loguru import logger

class AIInterface(ABC):
    """AI接口抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化AI接口
        
        Args:
            config: 配置字典
        """
        self.config = config
        self._validate_config()
        
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置
        
        Raises:
            ValueError: 配置无效时抛出
        """
        pass
    
    @abstractmethod
    async def generate_story(self, theme: str, difficulty: str) -> Dict[str, str]:
        """生成海龟汤故事
        
        Args:
            theme: 故事主题
            difficulty: 难度级别
            
        Returns:
            Dict包含 'surface'（汤面）和 'bottom'（汤底）
        """
        pass
    
    @abstractmethod
    async def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """回答玩家问题
        
        Args:
            question: 玩家的问题
            context: 游戏上下文，包含故事信息等
            
        Returns:
            '是'、'否'或'无关'
        """
        pass
        
    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """生成自定义内容
        
        Args:
            prompt: 提示文本
            
        Returns:
            生成的内容
        """
        pass
        
    def _handle_error(self, error: Exception, context: str) -> None:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
        """
        logger.error(f"Error in {context}: {str(error)}")
        # 记录错误但不抛出，避免程序崩溃
        # 如果需要在特定情况下抛出异常，可以在调用处决定
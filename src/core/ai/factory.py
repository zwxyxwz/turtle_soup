"""
AI模型工厂模块，负责创建和管理AI模型实例
"""
from typing import Dict, Type, Any, Optional
from loguru import logger
from .base import AIInterface
from src.models.custom import CustomAIInterface
from src.models.ali import AliInterface
from src.models.deepseek import DeepSeekInterface
from src.models.openai import OpenAIInterface
from src.models.gemini import GeminiInterface
from src.models.claude import ClaudeInterface

class ModelFactory:
    """AI模型工厂类，使用单例模式"""
    
    _instance = None
    _models: Dict[str, Type[AIInterface]] = {
        "custom": CustomAIInterface,
        "ali": AliInterface,
        "deepseek": DeepSeekInterface,
        "openai": OpenAIInterface,
        "gemini": GeminiInterface,
        "claude": ClaudeInterface
    }
    
    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register_model(cls, model_type: str, model_class: Type[AIInterface]) -> None:
        """注册新的模型类型
        
        Args:
            model_type: 模型类型名称
            model_class: 模型类
        """
        if model_type in cls._models:
            logger.warning(f"模型类型 {model_type} 已存在，将被覆盖")
        cls._models[model_type] = model_class
        logger.info(f"成功注册模型类型: {model_type}")
    
    @classmethod
    def create_model(cls, model_type: str, config: Dict[str, Any]) -> AIInterface:
        """创建模型实例
        
        Args:
            model_type: 模型类型名称
            config: 模型配置
            
        Returns:
            AI模型实例
            
        Raises:
            ValueError: 模型类型不存在或配置无效
            Exception: 创建模型实例失败
        """
        if model_type not in cls._models:
            raise ValueError(f"未知的模型类型: {model_type}")
            
        try:
            model_class = cls._models[model_type]
            logger.info(f"正在创建 {model_type} 模型实例")
            return model_class(config)
        except Exception as e:
            logger.error(f"创建模型实例失败: {str(e)}")
            raise
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Type[AIInterface]]:
        """获取所有可用的模型类型
        
        Returns:
            模型类型字典
        """
        return cls._models.copy()
    
    @classmethod
    def is_model_available(cls, model_type: str) -> bool:
        """检查模型类型是否可用
        
        Args:
            model_type: 模型类型名称
            
        Returns:
            是否可用
        """
        return model_type in cls._models 
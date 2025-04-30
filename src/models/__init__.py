"""
AI 模型接口模块
"""
from typing import Dict, Any, Union
import yaml
from .base import AIInterface
from .openai import OpenAIInterface
from .claude import ClaudeInterface
from .gemini import GeminiInterface
from .deepseek import DeepSeekInterface
from .custom import CustomAIInterface
from .ali import AliInterface

__all__ = [
    'AIInterface',
    'OpenAIInterface',
    'ClaudeInterface',
    'GeminiInterface',
    'DeepSeekInterface',
    'CustomAIInterface',
    'AliInterface',
    'create_ai_interface'
]

def create_ai_interface(config: Union[str, Dict[str, Any]]) -> AIInterface:
    """创建 AI 接口实例
    
    Args:
        config: 配置文件路径或配置字典
        
    Returns:
        AIInterface 实例
        
    Raises:
        ValueError: 配置无效时抛出
    """
    if isinstance(config, str):
        with open(config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary or path to YAML file")
        
    ai_config = config.get('ai', {})
    model_type = ai_config.get('current_model')
    if not model_type:
        raise ValueError("No model type specified in config")
        
    model_config = ai_config.get(model_type)
    if not model_config:
        raise ValueError(f"No configuration found for model type: {model_type}")
        
    if model_type == 'openai':
        return OpenAIInterface(model_config)
    elif model_type == 'claude':
        return ClaudeInterface(model_config)
    elif model_type == 'gemini':
        return GeminiInterface(model_config)
    elif model_type == 'deepseek':
        return DeepSeekInterface(model_config)
    elif model_type == 'custom':
        return CustomAIInterface(model_config)
    elif model_type == 'ali':
        return AliInterface(model_config)
    else:
        raise ValueError(f"Unsupported model type: {model_type}") 
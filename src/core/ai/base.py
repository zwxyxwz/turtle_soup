"""
AI接口基类模块，定义所有AI模型必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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
        
    def _get_story_length(self, difficulty: str) -> str:
        """获取故事长度建议
        
        Args:
            difficulty: 难度级别
            
        Returns:
            长度建议字符串
        """
        lengths = {
            "easy": "100-200字",
            "medium": "150-300字",
            "hard": "200-400字"
        }
        return lengths.get(difficulty, "150-300字")
        
    def _get_difficulty_guidelines(self, difficulty: str) -> str:
        """获取难度指南
        
        Args:
            difficulty: 难度级别
            
        Returns:
            难度指南字符串
        """
        guidelines = {
            "easy": """- 线索明显，容易推理
- 真相简单直接
- 不需要太多背景知识""",
            "medium": """- 线索适中，需要一定推理
- 真相有一定转折
- 可能需要一些常识""",
            "hard": """- 线索隐蔽，需要深入推理
- 真相出人意料
- 可能需要专业知识"""
        }
        return guidelines.get(difficulty, guidelines["medium"])
        
    @abstractmethod
    async def generate_story(self, theme: str, difficulty: str) -> Dict[str, str]:
        """生成海龟汤故事
        
        Args:
            theme: 故事主题
            difficulty: 难度级别
            
        Returns:
            Dict包含 'surface'（汤面）和 'bottom'（汤底）
            
        Raises:
            Exception: 生成失败时抛出
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
            
        Raises:
            Exception: 回答失败时抛出
        """
        pass
        
    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """生成自定义内容
        
        Args:
            prompt: 提示文本
            
        Returns:
            生成的内容
            
        Raises:
            Exception: 生成失败时抛出
        """
        pass 
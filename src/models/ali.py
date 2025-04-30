"""
OpenAI API 接口实现
"""
import os
from typing import Dict, Any
from openai import OpenAI
from .base import AIInterface
from loguru import logger

class AliInterface(AIInterface):
    """Ali API 接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 OpenAI 接口
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        self.client = OpenAI(
            api_key=self.config["api_key"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
    def _validate_config(self) -> None:
        """验证配置
        
        Raises:
            ValueError: 配置无效时抛出
        """
        if not self.config.get("api_key"):
            raise ValueError("API key is required")
            
        if not self.config.get("model"):
            raise ValueError("Model name is required")
            
        if not isinstance(self.config.get("temperature", 0.7), (int, float)) or not 0 <= self.config.get("temperature", 0.7) <= 1:
            raise ValueError("Temperature must be between 0 and 1")
            
        if not isinstance(self.config.get("max_tokens", 1000), int) or self.config.get("max_tokens", 1000) <= 0:
            raise ValueError("Max tokens must be a positive integer")
            
        logger.info("OpenAI configuration validated successfully")
        
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
        try:
            prompt = f"""请根据以下要求生成一个海龟汤故事：
主题：{theme}
难度：{difficulty}

请按以下格式返回：
汤面：[故事表面]
汤底：[故事真相]"""
            
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000)
            )
            
            content = response.choices[0].message.content
            surface = content.split("汤面：")[1].split("汤底：")[0].strip()
            bottom = content.split("汤底：")[1].strip()
            
            return {"surface": surface, "bottom": bottom}
            
        except Exception as e:
            error_msg = f"Failed to generate story: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
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
        try:
            prompt = f"""请根据以下海龟汤故事回答玩家的问题：
故事：{context['surface']}
真相：{context['bottom']}
问题：{question}

请只回答：是、否或无关"""
            
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 使用较低的温度以获得更确定的答案
                max_tokens=10  # 答案很短，不需要太多token
            )
            
            answer = response.choices[0].message.content.strip()
            
            # 标准化答案
            if "是" in answer:
                return "是"
            elif "否" in answer:
                return "否"
            else:
                return "无关"
                
        except Exception as e:
            error_msg = f"Failed to answer question: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    async def generate_content(self, prompt: str) -> str:
        """生成自定义内容
        
        Args:
            prompt: 提示文本
            
        Returns:
            生成的内容
            
        Raises:
            Exception: 生成失败时抛出
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = f"Failed to generate content: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) 
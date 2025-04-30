"""
Gemini API 接口实现
"""
import os
from typing import Dict, Any
import google.generativeai as genai
from .base import AIInterface
from loguru import logger

class GeminiInterface(AIInterface):
    """Gemini API 接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Gemini 接口
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        genai.configure(api_key=self.config["api_key"])
        self.model = genai.GenerativeModel(self.config["model"])
        
    def _validate_config(self) -> None:
        """验证配置
        
        Raises:
            ValueError: 配置无效时抛出
        """
        required_keys = ["api_key", "model"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
                
        if not isinstance(self.config["api_key"], str):
            raise ValueError("api_key must be a string")
            
        if not isinstance(self.config["model"], str):
            raise ValueError("model must be a string")
            
        if not isinstance(self.config.get("temperature", 0.7), (int, float)) or not 0 <= self.config.get("temperature", 0.7) <= 1:
            raise ValueError("Temperature must be between 0 and 1")
            
        if not isinstance(self.config.get("max_tokens", 1000), int) or self.config.get("max_tokens", 1000) <= 0:
            raise ValueError("Max tokens must be a positive integer")
            
        logger.info("Gemini configuration validated successfully")
        
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
            prompt = f"""你是一位海龟汤游戏专家，请根据以下要求创作一个故事：

主题：{theme}
难度：{difficulty}

故事要求：
1. 汤面（故事表面）：
   - 简洁明了，包含关键信息
   - 留有推理空间
   - 避免直接揭示真相
   - 长度适中（{self._get_story_length(difficulty)}）

2. 汤底（故事真相）：
   - 出人意料但合乎逻辑
   - 与汤面紧密相关
   - 解释所有看似矛盾的地方
   - 避免过于复杂或牵强

3. 难度要求：
{self._get_difficulty_guidelines(difficulty)}

4. 回答限制：
   - 玩家只能通过提问来获取信息
   - 所有问题只能用"是"、"否"或"无关"回答
   - 答案必须明确且唯一

请按以下格式返回：
汤面：[故事表面]
汤底：[故事真相]"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.get("temperature", 0.7),
                    max_output_tokens=self.config.get("max_tokens", 1000)
                )
            )
            
            content = response.text
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
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # 使用较低的温度以获得更确定的答案
                    max_output_tokens=10
                )
            )
            
            answer = response.text.strip()
            
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
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.get("temperature", 0.7),
                    max_output_tokens=self.config.get("max_tokens", 1000)
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Failed to generate content: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) 
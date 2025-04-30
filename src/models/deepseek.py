"""
DeepSeek API 接口实现
"""
import os
import requests
import json
from typing import Dict, Any, Optional
from .base import AIInterface
from loguru import logger

class DeepSeekInterface(AIInterface):
    """DeepSeek API 接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 DeepSeek 接口
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 1000)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
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
            
        logger.info("DeepSeek configuration validated successfully")
        
    def _make_api_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应
            
        Raises:
            Exception: API请求失败时抛出
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_url}{endpoint}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    def _parse_story_response(self, content: str) -> Dict[str, str]:
        """解析故事响应
        
        Args:
            content: API响应内容
            
        Returns:
            解析后的故事字典
            
        Raises:
            ValueError: 解析失败时抛出
        """
        try:
            surface = content.split("汤面：")[1].split("汤底：")[0].strip()
            bottom = content.split("汤底：")[1].strip()
            return {"surface": surface, "bottom": bottom}
        except Exception as e:
            error_msg = f"Failed to parse story response: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
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
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
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
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,  # 使用较低的温度以获得更确定的答案
                "max_tokens": 10
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            answer = response.json()["choices"][0]["message"]["content"].strip()
            
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
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            error_msg = f"Failed to generate content: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) 
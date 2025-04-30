"""
游戏核心逻辑模块，实现海龟汤游戏的主要流程控制
"""
from typing import Dict, Any, Optional, List, Tuple
import random
import os
from loguru import logger
from .config.config_manager import ConfigManager
from .logging.log_manager import LogManager
from .models import create_ai_interface
from .tts import TTSInterface

class Game:
    """海龟汤游戏核心类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化游戏
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化配置管理器
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化日志管理器
        self.log_manager = LogManager(self.config.get('logging', {}))
        self.logger = self.log_manager.get_logger()
        
        # 初始化AI接口
        self.ai_interface = create_ai_interface(self.config)
        
        # 游戏状态
        self.current_riddle = None
        self.current_theme = None
        self.current_bottom = None  # 添加汤底存储
        self.questions_asked = 0
        self.hints_used = 0
        self.game_mode = self.config["game"]["mode"]
        self.difficulty = self.config["game"]["difficulty"]
        self.max_questions = self.config["game"]["max_questions"][self.difficulty]
        self.max_hints = self.config["game"]["hints"]["max_hints"][self.difficulty]
        
        self.logger.info("Game initialized successfully")
        
    def set_game_mode(self, mode: str) -> bool:
        """设置游戏模式
        
        Args:
            mode: 游戏模式
            
        Returns:
            是否设置成功
        """
        valid_modes = ["standard", "challenge", "story"]
        if mode not in valid_modes:
            self.logger.warning(f"Invalid game mode: {mode}")
            return False
            
        self.game_mode = mode
        self.logger.info(f"Game mode set to: {mode}")
        return True
        
    def set_difficulty(self, difficulty: str) -> bool:
        """设置游戏难度
        
        Args:
            difficulty: 游戏难度
            
        Returns:
            是否设置成功
        """
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            self.logger.warning(f"Invalid difficulty: {difficulty}")
            return False
            
        self.difficulty = difficulty
        self.max_questions = self.config["game"]["max_questions"][difficulty]
        self.max_hints = self.config["game"]["hints"]["max_hints"][difficulty]
        self.logger.info(f"Game difficulty set to: {difficulty}")
        return True
        
    async def start_new_game(self) -> Tuple[str, str]:
        """开始新游戏
        
        Returns:
            谜题和主题的元组
            
        Raises:
            Exception: 生成谜题失败时抛出
        """
        try:
            self.current_theme = self._select_random_theme()
            self.logger.info(f"Selected theme: {self.current_theme}")
            
            story = await self.ai_interface.generate_story(self.current_theme, self.difficulty)
            self.current_riddle = story["surface"]
            self.current_bottom = story["bottom"]  # 存储汤底
            
            self.questions_asked = 0
            self.hints_used = 0
            
            self.logger.info("New game started successfully")
            return self.current_riddle, self.current_theme
            
        except Exception as e:
            self.logger.error(f"Failed to start new game: {str(e)}")
            raise Exception(f"Failed to start new game: {str(e)}")
        
    def _select_random_theme(self) -> str:
        """随机选择一个主题
        
        Returns:
            选中的主题
        """
        themes = self.config["game"]["themes"]
        theme = random.choice(themes)
        self.logger.info(f"Selected random theme: {theme}")
        return theme
        
    async def ask_question(self, question: str) -> str:
        """提问并获取回答
        
        Args:
            question: 玩家的问题
            
        Returns:
            AI的回答
            
        Raises:
            Exception: 提问失败时抛出
        """
        try:
            if self.questions_asked >= self.max_questions:
                self.logger.warning("Maximum questions reached")
                return "已达到最大提问次数，请尝试猜答案或使用提示。"
                
            self.questions_asked += 1
            self.logger.info(f"Question asked: {question}")
            
            context = {
                "surface": self.current_riddle,
                "bottom": self.current_bottom  # 使用存储的汤底
            }
            
            response = await self.ai_interface.answer_question(question, context)
            self.logger.info(f"Question answered: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to answer question: {str(e)}")
            raise Exception(f"Failed to answer question: {str(e)}")
        
    async def get_hint(self) -> str:
        """获取提示
        
        Returns:
            提示内容
            
        Raises:
            Exception: 获取提示失败时抛出
        """
        try:
            if not self.config["game"]["hints"]["enabled"]:
                self.logger.warning("Hints are disabled")
                return "提示功能已禁用。"
                
            if self.hints_used >= self.max_hints:
                self.logger.warning("Maximum hints reached")
                return "已达到最大提示次数。"
                
            self.hints_used += 1
            self.logger.info("Getting hint")
            
            prompt = f"""请为以下海龟汤故事提供一个提示：
故事：{self.current_riddle}
真相：{self.current_bottom}
难度：{self.difficulty}

请给出一个有助于推理的提示，但不要直接揭示答案。"""
            
            hint = await self.ai_interface.generate_content(prompt)
            self.logger.info("Hint generated successfully")
            return hint
            
        except Exception as e:
            self.logger.error(f"Failed to get hint: {str(e)}")
            raise Exception(f"Failed to get hint: {str(e)}")
        
    async def check_answer(self, answer: str) -> Tuple[bool, str]:
        """检查答案是否正确
        
        Args:
            answer: 玩家的答案
            
        Returns:
            是否正确和解释的元组
            
        Raises:
            Exception: 检查答案失败时抛出
        """
        try:
            self.logger.info(f"Checking answer: {answer}")
            
            prompt = f"""请判断以下答案是否正确：
故事：{self.current_riddle}
真相：{self.current_bottom}
玩家答案：{answer}

请判断答案是否正确，并给出解释。"""
            
            explanation = await self.ai_interface.generate_content(prompt)
            
            # 简单判断答案是否正确
            is_correct = "正确" in explanation or "对" in explanation
            
            if not is_correct:
                explanation += f"\n\n正确答案是：{self.current_bottom}"
            
            self.logger.info(f"Answer checked: {'correct' if is_correct else 'incorrect'}")
            return is_correct, explanation
            
        except Exception as e:
            self.logger.error(f"Failed to check answer: {str(e)}")
            raise Exception(f"Failed to check answer: {str(e)}")
        
    def get_game_status(self) -> Dict:
        """获取游戏状态
        
        Returns:
            游戏状态字典
        """
        status = {
            "theme": self.current_theme,
            "questions_asked": self.questions_asked,
            "max_questions": self.max_questions,
            "hints_used": self.hints_used,
            "max_hints": self.max_hints,
            "game_mode": self.game_mode,
            "difficulty": self.difficulty
        }
        self.logger.info(f"Game status: {status}")
        return status

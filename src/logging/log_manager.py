"""
日志管理模块，负责配置和管理日志
"""
import os
import sys
from typing import Dict, Any
from loguru import logger

class LogManager:
    """日志管理器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化日志管理器
        
        Args:
            config: 日志配置
        """
        self.config = config
        self._setup_logger()
        
    def _setup_logger(self) -> None:
        """设置日志器"""
        # 移除默认的处理器
        logger.remove()
        
        # 获取日志配置
        log_dir = self.config.get('log_dir', 'logs')
        log_level = self.config.get('level', 'INFO')
        rotation = self.config.get('rotation', '1 day')
        retention = self.config.get('retention', '7 days')
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 添加文件处理器
        log_file = os.path.join(log_dir, 'game.log')
        logger.add(
            log_file,
            rotation=rotation,
            retention=retention,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            encoding='utf-8'
        )
        
        # 添加控制台处理器
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
    def get_logger(self):
        """获取日志器
        
        Returns:
            logger实例
        """
        return logger
        
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新日志配置
        
        Args:
            config: 新的日志配置
        """
        self.config = config
        self._setup_logger() 
"""
配置管理模块，负责加载和验证配置
"""
import os
import yaml
from typing import Dict, Any, Optional
from loguru import logger

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.yaml"
        )
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self._validate_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise
            
    def _validate_config(self) -> None:
        """验证配置
        
        Raises:
            ValueError: 配置无效时抛出
        """
        required_sections = ['ai', 'game', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"配置缺少必要部分: {section}")
                
        # 验证AI配置
        ai_config = self.config['ai']
        if 'current_model' not in ai_config:
            raise ValueError("AI配置缺少current_model")
            
        current_model = ai_config['current_model']
        if current_model not in ai_config:
            raise ValueError(f"未找到{current_model}的配置")
            
        # 验证游戏配置
        game_config = self.config['game']
        required_game_settings = ['mode', 'difficulty', 'max_questions', 'hints']
        for setting in required_game_settings:
            if setting not in game_config:
                raise ValueError(f"游戏配置缺少{setting}")
                
    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取配置
        
        Args:
            section: 配置部分，如果为None则返回全部配置
            
        Returns:
            配置字典
        """
        if section is None:
            return self.config
        return self.config.get(section, {})
        
    def reload_config(self) -> None:
        """重新加载配置"""
        self._load_config()
        
    def update_config(self, section: str, config: Dict[str, Any]) -> None:
        """更新配置
        
        Args:
            section: 配置部分
            config: 新的配置
        """
        self.config[section] = config
        self._validate_config()
        
        # 保存到文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            raise 
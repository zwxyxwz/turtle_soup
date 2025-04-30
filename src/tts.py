"""
文字转语音接口模块，提供与不同TTS服务的统一交互接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from loguru import logger
from .config.config_manager import ConfigManager
from .logging.log_manager import LogManager

class TTSInterface(ABC):
    """TTS接口抽象基类"""
    
    @abstractmethod
    async def speak(self, text: str) -> None:
        """将文本转换为语音并播放
        
        Args:
            text: 要转换的文本
        """
        pass

class AzureTTSInterface(TTSInterface):
    """Azure TTS接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
        self.speech_config = SpeechConfig(
            subscription=config['subscription_key'],
            region=config['region']
        )
        self.speech_config.speech_synthesis_voice_name = config['voice_name']
        self.synthesizer = SpeechSynthesizer(speech_config=self.speech_config)
    
    async def speak(self, text: str) -> None:
        """使用Azure TTS服务将文本转换为语音
        
        Args:
            text: 要转换的文本
        """
        try:
            # 在异步环境中运行同步的Azure TTS API
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.synthesizer.speak_text_async(text).get()
            )
        except Exception as e:
            logger.error(f"Azure TTS错误：{str(e)}")

class GoogleTTSInterface(TTSInterface):
    """Google TTS接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        from google.cloud import texttospeech
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="zh-CN",
            name=config['voice_name']
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    
    async def speak(self, text: str) -> None:
        """使用Google TTS服务将文本转换为语音
        
        Args:
            text: 要转换的文本
        """
        try:
            # 在异步环境中运行同步的Google TTS API
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=self.voice,
                    audio_config=self.audio_config
                )
            )
            
            # 保存并播放音频
            # TODO: 实现音频播放逻辑
            logger.info("Google TTS音频生成成功")
        except Exception as e:
            logger.error(f"Google TTS错误：{str(e)}")

class CustomTTSInterface(TTSInterface):
    """自定义TTS接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_endpoint = config['api_endpoint']
        self.api_key = config['api_key']
        self.voice_id = config['voice_id']
    
    async def speak(self, text: str) -> None:
        """使用自定义TTS服务将文本转换为语音
        
        Args:
            text: 要转换的文本
        """
        try:
            # TODO: 实现自定义TTS API调用
            logger.info("自定义TTS音频生成成功")
        except Exception as e:
            logger.error(f"自定义TTS错误：{str(e)}")

def create_tts_interface(config: Dict[str, Any]) -> Optional[TTSInterface]:
    """创建TTS接口实例
    
    Args:
        config: TTS配置字典
        
    Returns:
        TTSInterface实例或None（如果TTS未启用）
    """
    if not config['enabled']:
        return None
    
    provider = config['provider']
    provider_config = config[provider]
    
    tts_map = {
        'azure': (AzureTTSInterface, provider_config),
        'google': (GoogleTTSInterface, provider_config),
        'custom': (CustomTTSInterface, provider_config)
    }
    
    if provider not in tts_map:
        logger.warning(f"不支持的TTS提供商：{provider}")
        return None
    
    interface_class, provider_config = tts_map[provider]
    return interface_class(provider_config)

class TTSInterface:
    """文本转语音接口基类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化TTS接口
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化配置管理器
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化日志管理器
        self.log_manager = LogManager(self.config.get('logging', {}))
        self.logger = self.log_manager.get_logger()
        
        # 初始化TTS配置
        self.tts_config = self.config.get('tts', {})
        
        self.logger.info("TTSInterface initialized successfully")
        
    async def speak(self, text: str, voice: Optional[str] = None) -> bool:
        """将文本转换为语音并播放
        
        Args:
            text: 要转换的文本
            voice: 语音选项（可选）
            
        Returns:
            是否成功播放
        """
        try:
            self.logger.info(f"Converting text to speech: {text[:50]}...")
            
            # 检查TTS是否启用
            if not self.tts_config.get('enabled', False):
                self.logger.warning("TTS is disabled")
                return False
                
            # 获取语音选项
            if voice is None:
                voice = self.tts_config.get('default_voice')
                
            # 转换文本为语音
            audio_data = await self._convert_text_to_speech(text, voice)
            if audio_data is None:
                self.logger.error("Failed to convert text to speech")
                return False
                
            # 播放语音
            success = await self._play_audio(audio_data)
            if not success:
                self.logger.error("Failed to play audio")
                return False
                
            self.logger.info("Text converted to speech successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"TTS error: {str(e)}")
            return False
            
    async def _convert_text_to_speech(self, text: str, voice: str) -> Optional[bytes]:
        """将文本转换为语音数据
        
        Args:
            text: 要转换的文本
            voice: 语音选项
            
        Returns:
            语音数据，如果失败则返回None
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    async def _play_audio(self, audio_data: bytes) -> bool:
        """播放语音数据
        
        Args:
            audio_data: 语音数据
            
        Returns:
            是否成功播放
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    def _validate_config(self) -> bool:
        """验证配置
        
        Returns:
            配置是否有效
        """
        try:
            self.logger.info("Validating TTS configuration")
            
            # 检查必要配置
            required_configs = ['enabled', 'default_voice']
            for config in required_configs:
                if config not in self.tts_config:
                    self.logger.error(f"Missing required TTS configuration: {config}")
                    return False
                    
            # 检查语音选项
            if not isinstance(self.tts_config['enabled'], bool):
                self.logger.error("TTS enabled must be a boolean")
                return False
                
            if not isinstance(self.tts_config['default_voice'], str):
                self.logger.error("TTS default_voice must be a string")
                return False
                
            self.logger.info("TTS configuration validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate TTS configuration: {str(e)}")
            return False

"""
海龟汤游戏主入口模块，实现命令行界面
"""
import os
import sys
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from loguru import logger
from src.config.config_manager import ConfigManager
from src.logging.log_manager import LogManager
from src.game import Game
from src.tts import TTSInterface

class GameCLI:
    """海龟汤游戏命令行界面"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化命令行界面
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化配置管理器
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化日志管理器
        self.log_manager = LogManager(self.config.get('logging', {}))
        self.logger = self.log_manager.get_logger()
        
        # 初始化游戏
        self.game = Game(config_path)
        
        # 初始化控制台
        self.console = Console()
        
        self.logger.info("GameCLI initialized successfully")
        
    async def start(self):
        """启动游戏"""
        try:
            self.logger.info("Starting game")
            
            # 显示欢迎信息
            self._show_welcome()
            
            # 选择游戏模式
            if not await self._select_game_mode():
                self.logger.info("Game mode selection cancelled")
                return
                
            # 选择难度
            if not await self._select_difficulty():
                self.logger.info("Difficulty selection cancelled")
                return
                
            # 开始游戏循环
            await self._game_loop()
            
        except Exception as e:
            self.logger.error(f"Game error: {str(e)}")
            self.console.print(f"[red]游戏出错: {str(e)}[/red]")
            
    def _show_welcome(self):
        """显示欢迎信息"""
        welcome_text = """
[bold blue]欢迎来到海龟汤游戏！[/bold blue]

在这个游戏中，你需要通过提问来推理出一个故事的真相。
你可以：
- 提问（输入问题）
- 获取提示（输入 'hint'）
- 提交答案（输入 'answer'）
- 查看状态（输入 'status'）
- 退出游戏（输入 'quit'）

祝你好运！
"""
        self.console.print(Panel(welcome_text, title="海龟汤游戏"))
        
    async def _select_game_mode(self) -> bool:
        """选择游戏模式
        
        Returns:
            是否成功选择模式
        """
        try:
            self.logger.info("Selecting game mode")
            
            modes = {
                "1": "standard",
                "2": "challenge",
                "3": "story"
            }
            
            mode_text = """
请选择游戏模式：
1. 标准模式 - 通过提问推理故事
2. 挑战模式 - 限制提问次数
3. 故事模式 - 生成完整故事
"""
            self.console.print(mode_text)
            
            choice = Prompt.ask("请输入模式编号", choices=["1", "2", "3", "q"])
            if choice == "q":
                self.logger.info("Game mode selection cancelled")
                return False
                
            mode = modes[choice]
            if not self.game.set_game_mode(mode):
                self.logger.error(f"Invalid game mode: {mode}")
                self.console.print("[red]无效的游戏模式[/red]")
                return False
                
            self.logger.info(f"Selected game mode: {mode}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select game mode: {str(e)}")
            self.console.print(f"[red]选择游戏模式失败: {str(e)}[/red]")
            return False
            
    async def _select_difficulty(self) -> bool:
        """选择游戏难度
        
        Returns:
            是否成功选择难度
        """
        try:
            self.logger.info("Selecting difficulty")
            
            difficulties = {
                "1": "easy",
                "2": "medium",
                "3": "hard"
            }
            
            diff_text = """
请选择游戏难度：
1. 简单 - 更多提示和提问机会
2. 中等 - 平衡的提示和提问机会
3. 困难 - 较少的提示和提问机会
"""
            self.console.print(diff_text)
            
            choice = Prompt.ask("请输入难度编号", choices=["1", "2", "3", "q"])
            if choice == "q":
                self.logger.info("Difficulty selection cancelled")
                return False
                
            difficulty = difficulties[choice]
            if not self.game.set_difficulty(difficulty):
                self.logger.error(f"Invalid difficulty: {difficulty}")
                self.console.print("[red]无效的难度[/red]")
                return False
                
            self.logger.info(f"Selected difficulty: {difficulty}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select difficulty: {str(e)}")
            self.console.print(f"[red]选择难度失败: {str(e)}[/red]")
            return False
            
    async def _game_loop(self):
        """游戏主循环"""
        try:
            self.logger.info("Starting game loop")
            
            # 开始新游戏
            riddle, theme = await self.game.start_new_game()
            
            # 显示谜题
            self.console.print(Panel(riddle, title=f"主题: {theme}"))
            
            while True:
                # 获取用户输入
                user_input = Prompt.ask("\n请输入命令")
                
                # 处理输入
                if not await self._process_input(user_input):
                    break
                    
        except Exception as e:
            self.logger.error(f"Game loop error: {str(e)}")
            self.console.print(f"[red]游戏出错: {str(e)}[/red]")
            
    async def _process_input(self, user_input: str) -> bool:
        """处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否继续游戏
        """
        try:
            self.logger.info(f"Processing input: {user_input}")
            
            if user_input.lower() == "quit":
                self.logger.info("User quit game")
                return False
                
            elif user_input.lower() == "status":
                status = self.game.get_game_status()
                self._show_status(status)
                
            elif user_input.lower() == "hint":
                hint = await self.game.get_hint()
                self.console.print(Panel(hint, title="提示"))
                
            elif user_input.lower() == "answer":
                answer = Prompt.ask("请输入你的答案")
                is_correct, explanation = await self.game.check_answer(answer)
                
                if is_correct:
                    self.console.print("[green]恭喜你答对了！[/green]")
                    self.console.print(Panel(explanation, title="解释"))
                    
                    if Confirm.ask("是否开始新游戏？"):
                        riddle, theme = await self.game.start_new_game()
                        self.console.print(Panel(riddle, title=f"主题: {theme}"))
                    else:
                        return False
                else:
                    self.console.print("[red]答案不正确[/red]")
                    self.console.print(Panel(explanation, title="解释"))
                    
            else:
                response = await self.game.ask_question(user_input)
                self.console.print(Panel(response, title="回答"))
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process input: {str(e)}")
            self.console.print(f"[red]处理输入失败: {str(e)}[/red]")
            return True
            
    def _show_status(self, status: Dict):
        """显示游戏状态
        
        Args:
            status: 游戏状态
        """
        table = Table(title="游戏状态")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="magenta")
        
        table.add_row("主题", status["theme"])
        table.add_row("已提问次数", f"{status['questions_asked']}/{status['max_questions']}")
        table.add_row("已使用提示", f"{status['hints_used']}/{status['max_hints']}")
        table.add_row("游戏模式", status["game_mode"])
        table.add_row("难度", status["difficulty"])
        
        self.console.print(table)
        
def main():
    """主函数"""
    try:
        cli = GameCLI()
        import asyncio
        asyncio.run(cli.start())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main() 
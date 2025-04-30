"""
主程序入口模块，实现命令行交互界面
"""
import asyncio
import os
import sys
import yaml
from typing import Dict, Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from loguru import logger
from src.game import Game

# 配置日志
logger.add(
    "game.log",
    rotation="10 MB",
    retention="5 days",
    level="INFO",
    encoding="utf-8"
)

class GameCLI:
    """海龟汤游戏命令行界面"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化游戏界面
        
        Args:
            config_path: 配置文件路径
        """
        self.console = Console()
        self.game = Game(config_path)
        self.config = self.game.config
        self.is_running = False
    
    def _print_welcome(self):
        """打印欢迎信息"""
        welcome_text = """
欢迎来到海龟汤游戏！
====================

游戏规则：
1. 系统会随机选择一个主题，并生成一个谜题
2. 你可以通过提问来推理谜题的答案
3. 每个难度级别有不同的最大提问次数
4. 你可以使用提示来获取帮助（次数有限）
5. 当你认为知道答案时，可以直接输入答案

游戏模式：
1. 标准模式：经典的海龟汤玩法
2. 挑战模式：限时答题，难度更高
3. 故事模式：更注重剧情和推理过程

请选择游戏模式：
1. 标准模式
2. 挑战模式
3. 故事模式
"""
        self.console.print(Panel(welcome_text, title="海龟汤游戏", border_style="cyan"))
    
    def _select_game_mode(self) -> bool:
        """选择游戏模式"""
        while True:
            try:
                choice = Prompt.ask("\n请输入模式编号(1-3): ").strip()
                if choice == "1":
                    return self.game.set_game_mode("standard")
                elif choice == "2":
                    return self.game.set_game_mode("challenge")
                elif choice == "3":
                    return self.game.set_game_mode("story")
                else:
                    self.console.print("\n无效的选择，请重新输入。")
            except Exception as e:
                self.console.print(f"\n选择游戏模式时出错: {e}")
                return False
    
    def _print_difficulty_info(self):
        """打印难度信息"""
        self.console.print("\n请选择游戏难度：\n1. 简单 - 更多提问次数，更多提示\n2. 中等 - 平衡的难度\n3. 困难 - 更少提问次数，更少提示\n")
    
    def _select_difficulty(self) -> bool:
        """选择游戏难度"""
        while True:
            try:
                choice = Prompt.ask("\n请输入难度编号(1-3): ").strip()
                if choice == "1":
                    return self.game.set_difficulty("easy")
                elif choice == "2":
                    return self.game.set_difficulty("medium")
                elif choice == "3":
                    return self.game.set_difficulty("hard")
                else:
                    self.console.print("\n无效的选择，请重新输入。")
            except Exception as e:
                self.console.print(f"\n选择游戏难度时出错: {e}")
                return False
    
    def _print_game_info(self):
        """打印游戏信息"""
        status = self.game.get_game_status()
        self.console.print(f"""
游戏开始！
主题：{status['theme']}
模式：{status['game_mode']}
难度：{status['difficulty']}
最大提问次数：{status['max_questions']}
最大提示次数：{status['max_hints']}

你可以：
1. 输入问题来推理答案
2. 输入"提示"获取提示
3. 输入"答案"来猜答案
4. 输入"退出"结束游戏

请开始你的推理！
""")
    
    async def _process_input(self, user_input: str) -> bool:
        """处理用户输入
        
        Args:
            user_input: 用户输入的内容
            
        Returns:
            是否继续游戏
        """
        try:
            if user_input.lower() == ["退出", "exit"]:
                return False
            
            if user_input.lower() in ["提示", "hint"]:
                hint = await self.game.get_hint()
                self.console.print(Panel(hint, title="提示", border_style="yellow"))
                return True
            
            if user_input.lower() == "答案":
                answer = Prompt.ask("请输入你的答案: ").strip()
                is_correct, explanation = await self.game.check_answer(answer)
                if is_correct:
                    self.console.print("\n恭喜你答对了！")
                else:
                    self.console.print("\n很遗憾，答案不正确。")
                self.console.print(explanation)
                return True
            
            # 处理问题
            response = await self.game.ask_question(user_input)
            self.console.print(Panel(response, title="问答", border_style="blue"))
            return True
        except Exception as e:
            logger.error(f"处理输入时出错: {e}")
            self.console.print(f"\n处理输入时出错: {e}")
            return True
    
    async def run(self):
        """运行游戏"""
        try:
            self.is_running = True
            self._print_welcome()
            
            if not self._select_game_mode():
                self.console.print("\n选择游戏模式失败，游戏结束。")
                self.is_running = False
                return
            
            self._print_difficulty_info()
            if not self._select_difficulty():
                self.console.print("\n选择游戏难度失败，游戏结束。")
                self.is_running = False
                return
            
            riddle, theme = await self.game.start_new_game()
            self.console.print(f"\n谜题：{riddle}\n")
            self._print_game_info()
            
            while self.is_running:
                try:
                    user_input = Prompt.ask("\n请输入问题或命令: ").strip()
                    self.is_running = await self._process_input(user_input)
                except KeyboardInterrupt:
                    self.console.print("\n游戏已终止")
                    self.is_running = False
                except Exception as e:
                    logger.error(f"游戏运行错误：{e}")
                    self.console.print(f"\n发生错误：{e}")
                    self.is_running = False
                    
        except Exception as e:
            logger.error(f"游戏运行错误：{e}")
            self.console.print(f"\n发生错误：{e}")
            self.is_running = False

async def main():
    """主函数"""
    try:
        # 获取配置文件路径
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        
        # 创建并运行游戏
        cli = GameCLI(config_path)
        await cli.run()
    except Exception as e:
        logger.error(f"程序运行错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行错误：{e}")
        sys.exit(1)

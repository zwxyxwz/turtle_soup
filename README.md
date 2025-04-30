# AI海龟汤游戏

一个基于AI的海龟汤推理游戏，支持多种AI模型接口，提供沉浸式的推理体验。

## 功能特点

- 支持多种AI模型接口
  - OpenAI (GPT-3.5/4)
  - Claude (Claude-2/3)
  - DeepSeek (DeepSeek-V3)
  - Gemini (Gemini-Pro)
  - 自定义AI接口
- 智能故事生成和回答系统
- 实时对话式游戏体验
- 支持TTS语音输出
- 可配置的游戏参数
- 多语言支持（中文/英文）
- 丰富的主题和难度选择

## 安装说明

1. 克隆项目
```bash
git clone [repository_url]
cd ai_turtle_soup
```

2. 创建虚拟环境（推荐）
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置AI模型API密钥
- 复制 `config/config.yaml.example` 为 `config/config.yaml`
- 在配置文件中填入相应的API密钥
- 选择要使用的AI模型（在 `ai.current_model` 中设置）

## 使用方法

1. 启动游戏
```bash
python src/main.py
```

2. 游戏规则
- AI会给出一个"汤面"（故事背景）
- 玩家通过提问来推理完整故事
- AI只能回答"是"、"否"或"无关"
- 目标是推理出完整的"汤底"（故事真相）

3. 游戏命令
- `hint`: 获取提示
- `answer <你的答案>`: 提交答案
- `quit`: 退出游戏
- `help`: 显示帮助信息

## 项目结构

```
ai_turtle_soup/
├── src/                    # 源代码
│   ├── main.py            # 主程序入口
│   ├── game.py            # 游戏核心逻辑
│   ├── core/              # 核心模块
│   │   ├── ai/           # AI接口基类
│   │   ├── config/       # 配置管理
│   │   └── log/          # 日志管理
│   ├── models/            # AI模型实现
│   │   ├── openai.py     # OpenAI接口
│   │   ├── claude.py     # Claude接口
│   │   ├── deepseek.py   # DeepSeek接口
│   │   ├── gemini.py     # Gemini接口
│   │   └── custom.py     # 自定义接口
│   ├── utils/            # 工具函数
│   └── tts.py            # 文字转语音接口
├── tests/                 # 测试文件
├── data/                  # 数据文件
├── config/                # 配置文件
└── requirements.txt       # 项目依赖
```

## 配置说明

在 `config/config.yaml` 中可以配置：

1. AI模型配置
```yaml
ai:
  current_model: "openai"  # 可选: openai, claude, deepseek, gemini, custom
  openai:
    api_key: "your-api-key"
    model: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 1000
  # 其他模型配置...
```

2. 游戏参数
```yaml
game:
  themes: ["恐怖", "悬疑", "科幻", "日常"]
  difficulties: ["简单", "中等", "困难"]
  max_questions: 20
  hint_penalty: 2
```

3. TTS设置
```yaml
tts:
  enabled: true
  voice: "zh-CN-XiaoxiaoNeural"
  rate: 1.0
  volume: 1.0
```

## 开发指南

1. 添加新的AI模型
- 在 `src/models/` 下创建新的模型实现文件
- 继承 `AIInterface` 基类
- 实现必要的方法：`generate_story`, `answer_question`, `generate_content`
- 在 `src/models/__init__.py` 中注册新模型

2. 添加新的游戏功能
- 在 `src/game.py` 中扩展游戏逻辑
- 在 `src/main.py` 中添加相应的命令处理

3. 运行测试
```bash
python -m pytest tests/
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在提交PR时，请确保：

1. 代码符合PEP 8规范
2. 添加必要的测试用例
3. 更新相关文档
4. 提供清晰的提交信息

## 许可证

MIT License

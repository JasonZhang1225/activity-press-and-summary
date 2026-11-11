# 北京交通大学计算机科学与技术学院学生会活动文稿撰写与智能选片 Agent Skill

<p align="center">
  <img src="https://img.shields.io/badge/Version-v1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-GPLv3-green.svg" alt="License">
  <a href="https://docs.qq.com/aio/DZXZUQ05hWmh0cGdU"><img src="https://img.shields.io/badge/腾讯文档-理事在线操作手册-0052D9.svg" alt="Tencent Docs"></a>
  <img src="https://img.shields.io/badge/Platform-Antigravity%20%7C%20Workbuddy%20%7C%20Claude-orange.svg" alt="Platform">
  <img src="https://img.shields.io/badge/BJTU-Computer%20Science%20and%20Technology-red.svg" alt="BJTU-SCST">
</p>

面向北京交通大学计算机科学与技术学院学生会及高校学生骨干的校园活动文稿智能归档与自动化交付 Skill。支持将杂乱的策划案、签到表、问卷统计与活动照片素材，一键转化为符合高校体制内标准规范的对外新闻稿、对内复盘工作总结与原生排版 Word 文档。

> 📖 **官方在线培训手册（腾讯文档）**：
> **[👉 点击在线阅读《校园活动文稿撰写与智能选片AI助手使用手册（理事培训版）》](https://docs.qq.com/aio/DZXZUQ05hWmh0cGdU)**
> 包含：各系统环境准备、Miniforge 清华镜像直链一键配置、Skill 导入使用、拍照选片 4 组原则、文案去 AI 味前后对比图表，以及“三关六查” 5 分钟极速人工核验法。

---

---

## ✨ 核心特性

- 📰 **对外新闻稿（严格 500—520 字符）**：
  - **对齐 Office 真实字数**：以 Microsoft Word / WPS 状态栏“字符数（不计空格）”为唯一权威标准，杜绝纯汉字漏算标点数字的假达标。
  - **过程段限 <= 30%**：140—160 字符，多环节高度归并，严禁流水账剧本式铺陈。
  - **公文高阶雅化**：家丑不外扬，寝室摩擦、情感纠葛、手工翻车全部提炼为规范育人语汇。
  - **去 AI 味拦截**：清零“不仅是一次……更是一场……”等刻板框架与虚浮拔高词。
- 📋 **对内工作总结（严格 800—2000 字符）**：
  - 八大模块结构完整：活动名称、来源、分工、实施、归档、成果、不足改进、感想。
  - 问题导向复盘：成对“问题—实招”，杜绝以偏概全，自动过滤非共性个例杂音。
  - 勾稽关系核查：报名数、签到数、到场数、问卷数严密校验，严防数据打架。
- 📸 **智能选片与合规拼图**：
  - 4 组固定叙事视角（师生互动特写、专注操作特写、作品与交流全景）。
  - 内置 `stitch_photos.py` 自动化拼图工具，智能等高缩放，剔除边缘断头/断手废片。
- 📄 **原生 Word 双稿排版交付**：
  - 内置标准 WordprocessingML 原生模板，一键直接生成带样式、标题加粗、首行缩进、图注居中的标准 `.docx` 文档。
- 🛠️ **自动化脚本体检闭环**：
  - `word_count.py`：对齐 Word 状态栏底层字数与分块切片诊断，支持 `.md` 与 `.docx`。
  - `de-ai-check.py`：公文合规、字数红线与高危 AI 套话扫描。

---

## 📂 技能资产与目录结构

```text
activity-press-and-summary/
├── SKILL.md                 # 核心技能规范、字段核对清单、公文雅化准则与质量红线
├── README.md                # 技能说明文档与安装指引
├── LICENSE                  # GNU General Public License v3.0 (GPLv3)
├── scripts/                 # 自动化脚本工具箱
│   ├── word_count.py        # 独立 Word 真实字数与分块切片统计（对齐 Office 状态栏，支持 .md / .docx）
│   ├── de-ai-check.py       # 去 AI 味与公文合规自动化体检脚本
│   └── stitch_photos.py     # 智能等高自适应与多宫格照片拼接工具
└── references/              # 格式模板与往期范文资产
    ├── 模板-新闻稿格式.xml    # 新闻稿原生排版模板（微软雅黑小二加粗 + 仿宋小四 1.5 倍行距）
    ├── 模板-新闻稿格式.docx   # 新闻稿标准样例文档
    ├── 模板-工作总结格式.xml  # 工作总结原生排版模板（等线一号/三号/五号）
    ├── 模板-工作总结格式.docx # 工作总结标准样例文档
    └── [往期优秀活动范文.md]  # 掐丝珐琅、宋锦团扇、肌理画、拼豆、银杏书签等真实归档案例
```

---

## 🚀 快速安装与配置

### 方式 1：作为 Antigravity / Gemini CLI Skill

在你的工作区根目录下执行：
```bash
git clone https://github.com/JasonZhang1225/activity-press-and-summary.git .agents/skills/学生会活动文稿撰写
```

### 方式 2：作为 Workbuddy Skill

在工作区中直接引入：
```bash
git clone https://github.com/JasonZhang1225/activity-press-and-summary.git .workbuddy/skills/activity-press-and-summary
```

### 方式 3：作为 Claude Code / Cursor / 通用 Agent Skill

直接克隆至项目的 `.agent/skills/` 或配置到全局 skills 目录中即可自动识别激活。

---

## 💡 自动化校验工具使用

### 1. 真实 Word 字符数与分块切片统计
支持传入 Markdown 文本或原生 `.docx` 文件：
```bash
# 检测新闻稿（自动切片导语、过程、成果、展望并计算过程段占比）
python3 scripts/word_count.py 8.文稿成果/新闻稿_第一期活动.docx --type news

# 检测工作总结（自动统计八大模块篇幅分布）
python3 scripts/word_count.py 8.文稿成果/工作总结_第一期活动.md --type summary
```

### 2. 去 AI 味与公文合规深度扫描
```bash
python3 scripts/de-ai-check.py 8.文稿成果/新闻稿_第一期活动.md --type news
```

### 3. 照片标准化等高横版拼接
```bash
# 二合一横版拼接（等高自动对齐）
python3 scripts/stitch_photos.py 原图1.jpg 原图2.jpg -o 拼图1.jpg

# 四宫格田字拼图
python3 scripts/stitch_photos.py 图1.jpg 图2.jpg 图3.jpg 图4.jpg --layout grid -o 拼图2.jpg
```

---

## 📜 开源许可协议 (License)

本项目采用 [GNU General Public License v3.0 (GPLv3)](./LICENSE) 协议开源。
欢迎各高校学生组织、团学联及校园开发者自由复用与拓展改进。

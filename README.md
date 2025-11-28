# Lean4 Auto Formalizer with GLM-4 & LeanSearch

一个基于大语言模型（GLM-4.6）和语义搜索（LeanSearch）的 Lean 4 自动化形式化代理。

![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.10+-green)

## 简介 (Introduction)

本项目旨在探索 **LLM (Large Language Model)** 与 **ITP (Interactive Theorem Prover)** 的结合。它通过模拟人类专家的工作流程来实现数学命题的自动形式化和证明：

1.  **Blueprinting**: 使用 GLM-4.6 将自然语言数学问题转化为 Lean 4 代码。
2.  **Verification**: 调用本地 Lean 编译器进行实时验证。
3.  **RAG Loop**: 当编译失败时，自动分析报错，调用 [LeanSearch.net](https://leansearch.net/) 获取相关定理。
4.  **Self-Correction**: 基于搜索结果和报错信息，自动修正代码，直到通过编译。


## 安装与配置 (Installation)

### 1. 环境要求
*   Python 3.10+
*   [Lean 4](https://lean-lang.org/) (需要在本地安装并配置好 Mathlib)

### 2. 克隆项目
```bash
git clone https://github.com/LitDarkness/Lean4-Gluer
cd Lean4-Gluer
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置文件
将配置文件模板复制一份：
```bash
cp config.py.example config.py
```
打开 `config.py` 并修改以下两项：
*   `GLM_API_KEY`: 填写你的智谱 AI API Key。
*   `LEAN_PROJECT_PATH`: 填写你本地 Lean 项目的根目录（包含 `lakefile.lean` 的那个目录）。

## 🏃‍♂️ 使用方法 (Usage)

1.  在 `problem.txt` 中输入你想形式化的数学问题（自然语言）。
    > 例子：证明如果素数 p 整除 finset S 的乘积，则 p 整除 S 中的某一个元素。

2.  运行主程序：
    ```bash
    python main.py
    ```

3.  程序将自动开始思考、编写代码、验证并修复。成功的代码将保存在 `solutions/` 目录下。

## 项目结构

*   `main.py`: 核心代理逻辑 (Agent Loop)。
*   `leansearch.py`: 封装 LeanSearch.net 的逆向 API 客户端。
*   `utils.py`: 包含日志记录、代码提取和等待动画等工具。
*   `logs/`: 记录每次尝试的详细报错和搜索意图，方便调试。

## 贡献

欢迎提交 Issue 和 PR！目前的 Prompt 还有很大优化空间，欢迎以此为基础开发更强的 Prover。

## 许可证

MIT License
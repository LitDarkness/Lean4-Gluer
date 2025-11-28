import subprocess
import os
import time
import sys
from zai import ZhipuAiClient 
from leansearch import LeanSearchClient
import config
import utils

# 初始化
client = ZhipuAiClient(api_key=config.GLM_API_KEY)
searcher = LeanSearchClient()

def call_glm_with_spinner(messages, temp=0.7, desc="GLM 思考中"):
    """带动画的 GLM 调用"""
    try:
        with utils.Spinner(f"🧠 {desc}... (Thinking Mode ON)"):
            response = client.chat.completions.create(
                model="glm-4.6", # 确认你的 API 支持 thinking
                messages=messages,
                temperature=temp,
                thinking={ "type": "enabled" }, 
                timeout=1200 # 设置超时，防止无限等待
            )
            return response.choices[0].message.content
    except Exception as e:
        print(f"\n❌ GLM API Error: {e}")
        return ""

def run_lean_verification(code):
    # 强制添加 import Mathlib
    if "import Mathlib" not in code:
        full_code = "import Mathlib\n\n" + code
    else:
        full_code = code

    file_path = os.path.join(config.LEAN_PROJECT_PATH, config.TEMP_FILE_NAME)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_code)
    except Exception as e:
        return False, f"Write Error: {e}", 0

    print(" 正在编译 (Lean)...")
    start = time.time()
    
    try:
        result = subprocess.run(
            ["lake", "env", "lean", config.TEMP_FILE_NAME],
            cwd=config.LEAN_PROJECT_PATH,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        duration = time.time() - start
        is_success = (result.returncode == 0)
        output = result.stderr + result.stdout
        return is_success, output, duration
        
    except Exception as e:
        return False, f"Subprocess Error: {e}", 0

def get_search_intent(error_msg):
    prompt = f"""
    Lean 代码编译报错：
    {error_msg[:8000]} 
    
    请分析原因。如果是 'unknown identifier' 或类型错误，请给出**英语搜索关键词**（自然语言描述或数学符号意图）。
    只输出关键词。请你针对当下最重要的错误，只输出一条关键词（一些紧密相关的）
    """
    # 这里的 temperature 设低一点，让它更专注
    return call_glm_with_spinner([{"role": "user", "content": prompt}], temp=0.1, desc="分析报错意图")

def main():
    # 1. 读取题目
    if not os.path.exists(config.PROBLEM_FILE):
        print(f"请先在 {config.PROBLEM_FILE} 中输入你的数学问题。")
        # 创建一个空文件方便用户
        with open(config.PROBLEM_FILE, "w", encoding="utf-8") as f:
            f.write("证明：两个奇数之和是偶数。")
        return

    with open(config.PROBLEM_FILE, "r", encoding="utf-8") as f:
        problem_statement = f.read().strip()

    print(f"\n 当前任务: {problem_statement}")
    print(f" 日志将写入: {config.LOGS_DIR}")

    # --- Round 1: 初稿 ---
    messages = [
        {"role": "system", "content": "你是一个 Lean 4 形式化助手。请将自然语言问题翻译为 Lean 4 定理。请你按照标准的格式写入！注意，我们已经内置了 import Mathlib，所以你不需要写 import 部分了。请你先思考，给出一个完整的**形式化定理陈述**再写证明部分！如果证明已经给出，那么你只需要把证明的内容形式化，否则你需要自己思考怎么证明并且给出形式化，禁止使用 sorry。请使用 ```lean 包裹代码。证明的陈述是极其重要的，包括了定理前提条件，设定的性质和最终的结论，请你务必先确保它正确"},
        {"role": "user", "content": problem_statement}
    ]
    
    raw_response = call_glm_with_spinner(messages, desc="生成初稿")
    code = utils.extract_lean_code(raw_response)
    
    max_retries = 100
    for i in range(max_retries):
        print(f"\n--- Round {i+1} ---")
        
        # 1. 验证
        success, output, t = run_lean_verification(code)
        print(f"⏱  Lean 耗时: {t:.2f}s")
        
        if success:
            print(" 验证通过！")
            print("-" * 40)
            print(code)
            print("-" * 40)
            # 保存结果
            saved_path = utils.save_solution(code, problem_statement)
            print(f" 已保存到: {saved_path}")
            return
        
        # 2. 失败处理
        print(" 编译失败")
        short_error = output[:8000] # 截断避免 Token 溢出
        
        # 3. 搜索介入
        search_intent = get_search_intent(short_error).strip()
        print(f" 搜索关键词: {search_intent}")
        
        # 记录日志
        utils.log_attempt(i+1, code, short_error, search_intent)
        
        # 带 Spinner 的搜索
        with utils.Spinner("Searching LeanSearch..."):
            search_results = searcher.search(search_intent)
        
        # 4. 修复
        fix_prompt = f"""
        你的代码报错了。
        
        【报错信息 (Top 8k chars)】
        {short_error}
        
        【LeanSearch 知识库】
        {search_results}
        
        请参考知识库中的 'Name' 和 'Type' 修正代码。
        务必使用正确的定理名称。
        只输出修正后的全部完整代码块 (```lean ... ```)，绝对不要只输出片段。。
        如果代码里有多个错误，你可以先修复最要紧的一个，如果提示 unsolved goals 之类的可能表示你的整个证明有问题，你可能需要先跳过。
        """
        
        messages.append({"role": "assistant", "content": code})
        messages.append({"role": "user", "content": fix_prompt})
        
        raw_response = call_glm_with_spinner(messages, desc=f"修复 Bug (第 {i+1} 次)")
        code = utils.extract_lean_code(raw_response)

    print("超过最大重试次数，任务失败。请检查 logs 目录。")

if __name__ == "__main__":
    main()
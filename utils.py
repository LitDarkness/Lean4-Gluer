import sys
import time
import threading
import re
import os
from datetime import datetime
import config

class Spinner:
    """一个在控制台转圈圈的类，缓解等待焦虑"""
    def __init__(self, message="Processing..."):
        self.message = message
        self.spinning = False
        self.spinner_cycle = ['|', '/', '-', '\\']

    def spin(self):
        i = 0
        while self.spinning:
            sys.stdout.write(f"\r{self.message} {self.spinner_cycle[i % len(self.spinner_cycle)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def __enter__(self):
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.spinning = False
        self.thread.join()
        sys.stdout.write(f"\r{self.message} Done!          \n")
        sys.stdout.flush()

def extract_lean_code(text):
    """
    使用正则智能提取 Lean 代码块。
    如果包含 ```lean ... ```，提取中间内容。
    否则返回原始内容。
    """
    pattern = r"```lean(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[-1].strip() 
    return text.replace("```", "").strip() 

def save_solution(code, problem_text):
    """保存成功的代码"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[\\/*?:"<>|]', "", problem_text[:10]).strip()
    filename = f"{safe_name}_{timestamp}.lean"
    path = os.path.join(config.SOLUTIONS_DIR, filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"/- Problem:\n{problem_text}\n-/\nimport Mathlib\n\n")
        f.write(code)
    return path

def log_attempt(round_num, code, error, search_intent):
    """简单的文件日志"""
    log_file = os.path.join(config.LOGS_DIR, "latest_run.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*20} Round {round_num} {'='*20}\n")
        f.write(f"[Code]:\n{code}\n")
        f.write(f"[Error (Truncated)]:\n{error[:500]}\n")
        f.write(f"[Search Intent]: {search_intent}\n")
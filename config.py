import os

# 你的 GLM API Key
GLM_API_KEY = "YOUR API Key"

# Lean 项目路径
LEAN_PROJECT_PATH = r"YOUR LEAN PATH"

# 临时文件名
TEMP_FILE_NAME = "Agent_Temp.lean"

# 输入输出路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEM_FILE = os.path.join(BASE_DIR, "problem.txt")
SOLUTIONS_DIR = os.path.join(BASE_DIR, "solutions")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 确保目录存在
os.makedirs(SOLUTIONS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
import requests
import json

class LeanSearchClient:
    def __init__(self):
        self.url = "https://leansearch.net/search"
        # 伪装成浏览器，避免被拦截
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://leansearch.net",
            "Referer": "https://leansearch.net/",
            # 如果遇到 403 错误，可以把 cURL 里的 cookie 贴到这里，但在 Python Session 中通常不需要
        }

    def search(self, query_text, limit=5):
        """
        Args:
            query_text (str): 你想搜的内容，例如 "prime number"
            limit (int): 返回结果数量
        """
        # 构造 Payload，注意 query 必须是列表
        payload = {
            "query": [query_text], 
            "num_results": limit
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # data 结构是 [[{result...}, {result...}]]
                # 因为我们只发了一个 query，所以取 data[0]
                if not data or not data[0]:
                    return "No results found."

                hits = data[0]
                formatted_results = []

                for item in hits:
                    res = item.get('result', {})
                    
                    # 提取关键字段
                    name = ".".join(res.get('name', []))
                    lean_type = res.get('type', 'N/A')
                    # informal_description 是 LLM 最需要的，如果没有就用 docstring
                    desc = res.get('informal_description') or res.get('docstring') or "No description"
                    
                    # 格式化
                    entry = (
                        f"Target Name: {name}\n"
                        f"Lean Type:   {lean_type}\n"
                        f"Meaning:     {desc}"
                    )
                    formatted_results.append(entry)

                return "\n\n".join(formatted_results)
            
            else:
                return f"API Error: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Network Error: {str(e)}"

# --- 测试代码 ---
if __name__ == "__main__":
    client = LeanSearchClient()
    # 测试你的例子
    print("正在搜索 'prime p' ...")
    result = client.search("prime p", limit=3)
    print(result)
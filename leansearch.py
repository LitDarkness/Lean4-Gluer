import requests
import json

class LeanSearchClient:
    def __init__(self):
        self.url = "https://leansearch.net/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://leansearch.net",
            "Referer": "https://leansearch.net/",
        }

    def search(self, query_text, limit=5):
        """
        Args:
            query_text (str): 你想搜的内容，例如 "prime number"
            limit (int): 返回结果数量
        """
        payload = {
            "query": [query_text], 
            "num_results": limit
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data or not data[0]:
                    return "No results found."

                hits = data[0]
                formatted_results = []

                for item in hits:
                    res = item.get('result', {})
                    
                    name = ".".join(res.get('name', []))
                    lean_type = res.get('type', 'N/A')
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
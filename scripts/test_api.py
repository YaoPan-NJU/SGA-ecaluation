"""
测试API连接
"""
import os
import requests

API_BASE_URL = "https://token-plan-ams.xiaomimimo.com/v1"
API_KEY = os.environ.get("MIMO_API_KEY", "")

def test_api_connection():
    """测试API连接"""
    print("🔍 测试API连接...")
    print(f"API地址: {API_BASE_URL}")
    print(f"API密钥: {'已设置' if API_KEY else '❌ 未设置'}")
    
    if not API_KEY:
        print("\n❌ 错误: MIMO_API_KEY环境变量未设置")
        print("\n请先设置API密钥:")
        print("  Windows PowerShell: $env:MIMO_API_KEY='your-key'")
        print("  Windows CMD: set MIMO_API_KEY=your-key")
        return False
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mimo-v2.5-pro",
        "messages": [
            {"role": "user", "content": "请回复'API连接成功'"}
        ],
        "max_tokens": 20
    }
    
    try:
        print("\n📡 发送测试请求...")
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print(f"✅ API连接成功！")
        print(f"📝 模型回复: {content}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}")
        return False
    except (KeyError, IndexError) as e:
        print(f"❌ 解析响应失败: {e}")
        print(f"原始响应: {response.text}")
        return False

if __name__ == '__main__':
    test_api_connection()

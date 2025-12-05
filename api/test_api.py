#!/usr/bin/env python3
"""
API 测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """打印响应"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)

def test_status():
    """测试状态"""
    response = requests.get(f"{BASE_URL}/status")
    print_response("状态信息", response)

def test_analyze_code():
    """测试代码分析"""
    data = {
        "code": """
public class Test {
    public static void main(String[] args) {
        int a = 10;
        int b = 0;
        System.out.println(a / b);  // Division by zero
    }
}
        """,
        "language": "java",
        "save": True
    }
    response = requests.post(f"{BASE_URL}/analyze", json=data)
    print_response("代码分析", response)

def test_list_reports():
    """测试报告列表"""
    response = requests.get(f"{BASE_URL}/reports?limit=5")
    print_response("报告列表", response)

def main():
    """主函数"""
    print("=" * 60)
    print("Code Analyzer API 测试")
    print("=" * 60)
    
    try:
        test_health()
        test_status()
        test_analyze_code()
        test_list_reports()
        
        print(f"\n{'='*60}")
        print("所有测试完成！")
        print(f"{'='*60}\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到 API 服务器")
        print("请确保 API 服务器正在运行: python3 api/server.py\n")
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LangChain 智能代理测试示例
演示如何使用智能代理进行代码分析
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from agent.langchain_agent import CodeAnalysisAgent
import json


def example_1_basic_analysis():
    """示例 1: 基本代码分析"""
    print("=" * 80)
    print("示例 1: 基本代码分析")
    print("=" * 80 + "\n")
    
    # 创建智能代理
    agent = CodeAnalysisAgent()
    
    # 示例代码
    code = """
def process_user_input(user_input):
    # 直接执行用户输入 - 存在安全风险！
    result = eval(user_input)
    return result

def calculate_discount(price, discount):
    # 没有验证输入
    final_price = price - (price * discount / 100)
    return final_price
"""
    
    # 执行分析
    result = agent.analyze(
        task="请分析这段代码的安全问题和潜在 bug",
        code=code
    )
    
    print("分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def example_2_plan_and_execute():
    """示例 2: 规划和执行复杂分析"""
    print("\n" + "=" * 80)
    print("示例 2: 规划和执行复杂分析")
    print("=" * 80 + "\n")
    
    agent = CodeAnalysisAgent()
    
    code = """
public class UserController {
    private Database db;
    
    public User getUser(String userId) {
        String query = "SELECT * FROM users WHERE id = '" + userId + "'";
        return db.execute(query);
    }
    
    public void updateUser(String userId, String name, String email) {
        String query = "UPDATE users SET name = '" + name + 
                      "', email = '" + email + "' WHERE id = '" + userId + "'";
        db.execute(query);
    }
}
"""
    
    result = agent.plan_and_execute(
        objective="对这个 Java 类进行全面的安全审查和代码质量分析",
        context={
            "language": "Java",
            "code": code,
            "file_path": "UserController.java"
        }
    )
    
    print("分析计划:")
    print(result.get('plan', ''))
    print("\n执行结果:")
    print(json.dumps(result.get('execution_result', {}), indent=2, ensure_ascii=False))


def example_3_multiple_files():
    """示例 3: 分析多个文件"""
    print("\n" + "=" * 80)
    print("示例 3: 分析多个文件")
    print("=" * 80 + "\n")
    
    agent = CodeAnalysisAgent()
    
    files = {
        "config.py": """
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"
DEBUG = True
""",
        "auth.py": """
def authenticate(username, password):
    if username == "admin" and password == "admin":
        return True
    return False
""",
        "api.py": """
import requests

def fetch_data(url):
    response = requests.get(url, verify=False)
    return response.json()
"""
    }
    
    for filename, code in files.items():
        print(f"\n分析文件: {filename}")
        print("-" * 40)
        
        result = agent.analyze(
            task=f"请分析 {filename} 的安全问题",
            code=code
        )
        
        if result['status'] == 'success':
            print(f"✓ 分析完成")
            print(f"结果: {result['result'][:200]}...")
        else:
            print(f"✗ 分析失败: {result.get('error', 'Unknown error')}")


def example_4_custom_task():
    """示例 4: 自定义分析任务"""
    print("\n" + "=" * 80)
    print("示例 4: 自定义分析任务")
    print("=" * 80 + "\n")
    
    agent = CodeAnalysisAgent()
    
    code = """
class DataProcessor:
    def __init__(self):
        self.cache = {}
    
    def process(self, data):
        result = []
        for item in data:
            if item['id'] not in self.cache:
                processed = self.expensive_operation(item)
                self.cache[item['id']] = processed
            result.append(self.cache[item['id']])
        return result
    
    def expensive_operation(self, item):
        # 模拟耗时操作
        import time
        time.sleep(0.1)
        return item['value'] * 2
"""
    
    # 自定义分析任务
    custom_tasks = [
        "这段代码的性能如何？有什么优化建议？",
        "缓存策略是否合理？",
        "是否存在内存泄漏的风险？"
    ]
    
    for task in custom_tasks:
        print(f"\n任务: {task}")
        print("-" * 40)
        
        result = agent.analyze(task=task, code=code)
        
        if result['status'] == 'success':
            print(f"回答: {result['result'][:300]}...")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 80)
    print("LangChain 智能代理测试示例")
    print("=" * 80)
    
    try:
        # 运行示例
        example_1_basic_analysis()
        example_2_plan_and_execute()
        example_3_multiple_files()
        example_4_custom_task()
        
        print("\n" + "=" * 80)
        print("所有示例运行完成！")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

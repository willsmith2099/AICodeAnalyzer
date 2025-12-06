#!/usr/bin/env python3
"""
LangChain Agent - 智能代码分析代理
使用 LangChain 框架实现智能规划和工具调用
"""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool, StructuredTool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests
import json


class OllamaLLM(LLM):
    """自定义 Ollama LLM 包装器，用于 LangChain"""
    
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:0.5b"
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用 Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"Error calling Ollama: {e}"


class CodeAnalysisAgent:
    """代码分析智能代理"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5:0.5b"):
        """
        初始化智能代理
        
        Args:
            ollama_url: Ollama 服务地址
            model: 使用的模型名称
        """
        self.llm = OllamaLLM(base_url=ollama_url, model=model)
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """创建智能代理可用的工具集"""
        
        tools = [
            Tool(
                name="analyze_code_quality",
                func=self._analyze_code_quality,
                description="分析代码质量，包括代码结构、命名规范、注释完整性等。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="detect_bugs",
                func=self._detect_bugs,
                description="检测代码中的潜在 bug 和逻辑错误。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="suggest_improvements",
                func=self._suggest_improvements,
                description="提供代码改进建议，包括重构、性能优化等。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="analyze_security",
                func=self._analyze_security,
                description="分析代码的安全隐患，如 SQL 注入、XSS 等。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="extract_dependencies",
                func=self._extract_dependencies,
                description="提取代码的依赖关系和导入的库。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="calculate_complexity",
                func=self._calculate_complexity,
                description="计算代码复杂度（圈复杂度、认知复杂度等）。输入应该是代码内容（字符串）。"
            ),
            Tool(
                name="generate_summary",
                func=self._generate_summary,
                description="生成代码功能摘要和文档。输入应该是代码内容（字符串）。"
            ),
        ]
        
        return tools
    
    def _analyze_code_quality(self, code: str) -> str:
        """分析代码质量"""
        prompt = f"""请分析以下代码的质量，重点关注：
1. 代码结构和组织
2. 命名规范（变量、函数、类名）
3. 注释完整性
4. 代码可读性

代码：
```
{code[:1000]}  # 限制长度
```

请给出简洁的分析结果。"""
        
        return self.llm._call(prompt)
    
    def _detect_bugs(self, code: str) -> str:
        """检测潜在 bug"""
        prompt = f"""请检测以下代码中的潜在 bug 和逻辑错误：

代码：
```
{code[:1000]}
```

请列出发现的问题。"""
        
        return self.llm._call(prompt)
    
    def _suggest_improvements(self, code: str) -> str:
        """提供改进建议"""
        prompt = f"""请为以下代码提供改进建议：

代码：
```
{code[:1000]}
```

请提供具体的改进方案。"""
        
        return self.llm._call(prompt)
    
    def _analyze_security(self, code: str) -> str:
        """分析安全隐患"""
        prompt = f"""请分析以下代码的安全隐患：

代码：
```
{code[:1000]}
```

请列出安全问题和建议。"""
        
        return self.llm._call(prompt)
    
    def _extract_dependencies(self, code: str) -> str:
        """提取依赖关系"""
        # 简单的依赖提取逻辑
        dependencies = []
        for line in code.split('\n')[:50]:  # 只看前50行
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                dependencies.append(line)
        
        if dependencies:
            return "发现的依赖:\n" + "\n".join(dependencies)
        else:
            return "未发现明显的依赖导入语句"
    
    def _calculate_complexity(self, code: str) -> str:
        """计算代码复杂度"""
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # 简单的复杂度估算
        complexity_indicators = {
            'if': code.count('if '),
            'for': code.count('for '),
            'while': code.count('while '),
            'try': code.count('try:'),
            'functions': code.count('def '),
            'classes': code.count('class '),
        }
        
        total_complexity = sum(complexity_indicators.values())
        
        return f"""代码复杂度分析:
- 总行数: {total_lines}
- 代码行数: {code_lines}
- 条件语句: {complexity_indicators['if']}
- 循环: {complexity_indicators['for'] + complexity_indicators['while']}
- 异常处理: {complexity_indicators['try']}
- 函数数量: {complexity_indicators['functions']}
- 类数量: {complexity_indicators['classes']}
- 复杂度评分: {total_complexity}"""
    
    def _generate_summary(self, code: str) -> str:
        """生成代码摘要"""
        prompt = f"""请为以下代码生成简洁的功能摘要：

代码：
```
{code[:1000]}
```

请用 2-3 句话描述代码的主要功能。"""
        
        return self.llm._call(prompt)
    
    def _create_agent(self):
        """创建 ReAct 智能代理"""
        
        template = """你是一个专业的代码分析助手。你的任务是帮助用户分析代码并提供有价值的见解。

你可以使用以下工具：
{tools}

工具名称: {tool_names}

使用以下格式回答：

Question: 用户的问题或任务
Thought: 你应该思考要做什么
Action: 要使用的工具，应该是 [{tool_names}] 中的一个
Action Input: 工具的输入
Observation: 工具的输出
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我现在知道最终答案了
Final Answer: 对原始问题的最终答案

开始！

Question: {input}
Thought: {agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(template)
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def analyze(self, task: str, code: str = None) -> Dict[str, Any]:
        """
        执行智能分析任务
        
        Args:
            task: 分析任务描述
            code: 要分析的代码（可选）
            
        Returns:
            分析结果字典
        """
        try:
            # 如果提供了代码，将其添加到任务描述中
            if code:
                full_task = f"{task}\n\n代码内容:\n```\n{code[:2000]}\n```"
            else:
                full_task = task
            
            result = self.agent_executor.invoke({"input": full_task})
            
            return {
                "status": "success",
                "task": task,
                "result": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            return {
                "status": "error",
                "task": task,
                "error": str(e)
            }
    
    def plan_and_execute(self, objective: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        规划并执行复杂的分析任务
        
        Args:
            objective: 分析目标
            context: 上下文信息（文件路径、语言等）
            
        Returns:
            执行结果
        """
        # 构建规划提示
        planning_prompt = f"""
作为代码分析专家，请为以下目标制定分析计划：

目标: {objective}

上下文信息:
{json.dumps(context or {}, indent=2, ensure_ascii=False)}

请列出需要执行的步骤，每个步骤应该使用一个工具。
"""
        
        try:
            # 让 LLM 制定计划
            plan = self.llm._call(planning_prompt)
            
            # 执行计划
            execution_result = self.analyze(
                task=f"根据以下计划执行分析:\n{plan}\n\n目标: {objective}",
                code=context.get('code') if context else None
            )
            
            return {
                "status": "success",
                "objective": objective,
                "plan": plan,
                "execution_result": execution_result
            }
        except Exception as e:
            return {
                "status": "error",
                "objective": objective,
                "error": str(e)
            }


def main():
    """示例用法"""
    # 创建智能代理
    agent = CodeAnalysisAgent()
    
    # 示例代码
    sample_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def process_order(order):
    if order['status'] == 'pending':
        total = calculate_total(order['items'])
        order['total'] = total
        order['status'] = 'processed'
    return order
"""
    
    # 执行分析任务
    print("=" * 80)
    print("示例 1: 基本代码分析")
    print("=" * 80)
    
    result1 = agent.analyze(
        task="请全面分析这段代码的质量、潜在问题和改进建议",
        code=sample_code
    )
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("示例 2: 规划和执行")
    print("=" * 80)
    
    result2 = agent.plan_and_execute(
        objective="对这段代码进行完整的代码审查",
        context={
            "language": "Python",
            "code": sample_code,
            "file_path": "order_processor.py"
        }
    )
    print(json.dumps(result2, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

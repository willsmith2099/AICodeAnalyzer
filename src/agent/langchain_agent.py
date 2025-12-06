#!/usr/bin/env python3
"""
LangChain Agent - 优化版智能代码分析代理
包含缓存机制、并行调用、更多工具和优化的提示词
"""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests
import json
import hashlib
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed


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
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"Error calling Ollama: {e}"


class ToolCache:
    """工具调用缓存机制"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间（秒）
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _get_cache_key(self, tool_name: str, input_data: str) -> str:
        """生成缓存键"""
        data = f"{tool_name}:{input_data}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, tool_name: str, input_data: str) -> Optional[str]:
        """获取缓存结果"""
        key = self._get_cache_key(tool_name, input_data)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]
        return None
    
    def set(self, tool_name: str, input_data: str, result: str):
        """设置缓存结果"""
        if len(self.cache) >= self.max_size:
            # 删除最旧的条目
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        key = self._get_cache_key(tool_name, input_data)
        self.cache[key] = (result, time.time())
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()


class OptimizedCodeAnalysisAgent:
    """优化版代码分析智能代理"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5:0.5b",
                 enable_cache: bool = True, enable_parallel: bool = True):
        """
        初始化智能代理
        
        Args:
            ollama_url: Ollama 服务地址
            model: 使用的模型名称
            enable_cache: 是否启用缓存
            enable_parallel: 是否启用并行调用
        """
        self.llm = OllamaLLM(base_url=ollama_url, model=model)
        self.enable_cache = enable_cache
        self.enable_parallel = enable_parallel
        
        # 初始化缓存
        if self.enable_cache:
            self.cache = ToolCache(max_size=200, ttl=3600)
        
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=15,  # 增加最大迭代次数
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """创建智能代理可用的工具集（扩展版）"""
        
        tools = [
            # 原有工具
            Tool(
                name="analyze_code_quality",
                func=self._cached_tool(self._analyze_code_quality),
                description="深入分析代码质量，评估代码结构、命名规范、注释完整性、可读性和可维护性。输入：代码字符串。"
            ),
            Tool(
                name="detect_bugs",
                func=self._cached_tool(self._detect_bugs),
                description="检测代码中的潜在 bug、逻辑错误、边界条件问题和空指针风险。输入：代码字符串。"
            ),
            Tool(
                name="suggest_improvements",
                func=self._cached_tool(self._suggest_improvements),
                description="提供代码改进建议，包括重构方案、性能优化、设计模式应用和最佳实践。输入：代码字符串。"
            ),
            Tool(
                name="analyze_security",
                func=self._cached_tool(self._analyze_security),
                description="全面分析代码安全隐患，包括 SQL 注入、XSS、CSRF、敏感信息泄露等。输入：代码字符串。"
            ),
            Tool(
                name="extract_dependencies",
                func=self._cached_tool(self._extract_dependencies),
                description="提取并分析代码的依赖关系、导入的库和外部模块。输入：代码字符串。"
            ),
            Tool(
                name="calculate_complexity",
                func=self._cached_tool(self._calculate_complexity),
                description="计算代码复杂度指标，包括圈复杂度、认知复杂度、代码行数等。输入：代码字符串。"
            ),
            Tool(
                name="generate_summary",
                func=self._cached_tool(self._generate_summary),
                description="生成代码功能摘要和技术文档，描述主要功能和核心逻辑。输入：代码字符串。"
            ),
            
            # 新增工具
            Tool(
                name="analyze_performance",
                func=self._cached_tool(self._analyze_performance),
                description="分析代码性能瓶颈，识别耗时操作、内存使用和优化机会。输入：代码字符串。"
            ),
            Tool(
                name="check_test_coverage",
                func=self._cached_tool(self._check_test_coverage),
                description="评估代码的可测试性，建议测试用例和覆盖策略。输入：代码字符串。"
            ),
            Tool(
                name="analyze_design_patterns",
                func=self._cached_tool(self._analyze_design_patterns),
                description="识别代码中使用的设计模式，建议适用的设计模式。输入：代码字符串。"
            ),
            Tool(
                name="check_code_smells",
                func=self._cached_tool(self._check_code_smells),
                description="检测代码异味，如重复代码、过长方法、过大类等。输入：代码字符串。"
            ),
            Tool(
                name="analyze_error_handling",
                func=self._cached_tool(self._analyze_error_handling),
                description="分析异常处理机制，评估错误处理的完整性和健壮性。输入：代码字符串。"
            ),
        ]
        
        return tools
    
    def _cached_tool(self, func):
        """为工具函数添加缓存装饰器"""
        def wrapper(code: str) -> str:
            if self.enable_cache:
                # 检查缓存
                cached_result = self.cache.get(func.__name__, code[:500])
                if cached_result:
                    return f"[缓存] {cached_result}"
                
                # 执行函数
                result = func(code)
                
                # 保存到缓存
                self.cache.set(func.__name__, code[:500], result)
                return result
            else:
                return func(code)
        
        return wrapper
    
    # ========== 优化的提示词模板 ==========
    
    def _analyze_code_quality(self, code: str) -> str:
        """分析代码质量（优化提示词）"""
        prompt = f"""作为资深代码审查专家，请深入分析以下代码的质量：

代码：
```
{code[:1000]}
```

请从以下维度进行评估（1-10分）：
1. **代码结构** - 模块化、职责分离
2. **命名规范** - 变量、函数、类名的清晰度
3. **注释质量** - 注释的完整性和准确性
4. **可读性** - 代码的易理解程度
5. **可维护性** - 未来修改的难易程度

请给出具体评分和改进建议。"""
        
        return self.llm._call(prompt)
    
    def _detect_bugs(self, code: str) -> str:
        """检测潜在 bug（优化提示词）"""
        prompt = f"""作为 bug 猎手，请仔细检查以下代码中的潜在问题：

代码：
```
{code[:1000]}
```

重点关注：
1. **逻辑错误** - 条件判断、循环逻辑
2. **边界条件** - 数组越界、空值处理
3. **并发问题** - 线程安全、竞态条件
4. **资源泄漏** - 文件、连接未关闭

请列出发现的问题，按严重程度排序。"""
        
        return self.llm._call(prompt)
    
    def _suggest_improvements(self, code: str) -> str:
        """提供改进建议（优化提示词）"""
        prompt = f"""作为架构师，请为以下代码提供专业的改进建议：

代码：
```
{code[:1000]}
```

请提供：
1. **重构建议** - 具体的代码重构方案
2. **性能优化** - 可优化的性能点
3. **设计模式** - 可应用的设计模式
4. **最佳实践** - 行业最佳实践建议

每条建议请给出具体示例。"""
        
        return self.llm._call(prompt)
    
    def _analyze_security(self, code: str) -> str:
        """分析安全隐患（优化提示词）"""
        prompt = f"""作为安全专家，请全面审查以下代码的安全性：

代码：
```
{code[:1000]}
```

安全检查清单：
1. **注入攻击** - SQL注入、命令注入、XSS
2. **认证授权** - 身份验证、权限控制
3. **数据保护** - 敏感信息、加密存储
4. **输入验证** - 用户输入的验证和过滤

请按风险等级（高/中/低）分类列出问题。"""
        
        return self.llm._call(prompt)
    
    def _extract_dependencies(self, code: str) -> str:
        """提取依赖关系（增强版）"""
        dependencies = []
        imports = []
        
        for line in code.split('\n')[:100]:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
            elif 'require(' in line or 'include' in line:
                imports.append(line)
        
        if imports:
            result = "**发现的依赖关系：**\n\n"
            result += "\n".join(f"- {imp}" for imp in imports)
            result += f"\n\n**依赖数量：** {len(imports)}"
            result += "\n\n**建议：** 检查依赖版本，避免使用过时或有安全漏洞的库。"
            return result
        else:
            return "未发现明显的依赖导入语句。"
    
    def _calculate_complexity(self, code: str) -> str:
        """计算代码复杂度（增强版）"""
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        
        # 复杂度指标
        metrics = {
            'if_statements': code.count('if '),
            'for_loops': code.count('for '),
            'while_loops': code.count('while '),
            'try_blocks': code.count('try:'),
            'functions': code.count('def '),
            'classes': code.count('class '),
            'nested_depth': self._estimate_nesting_depth(code),
        }
        
        cyclomatic_complexity = metrics['if_statements'] + metrics['for_loops'] + metrics['while_loops'] + 1
        
        return f"""**代码复杂度分析报告：**

📊 **基本指标：**
- 总行数: {total_lines}
- 代码行数: {code_lines}
- 注释行数: {comment_lines}
- 注释率: {(comment_lines / total_lines * 100):.1f}%

🔄 **控制流复杂度：**
- 条件语句: {metrics['if_statements']}
- For 循环: {metrics['for_loops']}
- While 循环: {metrics['while_loops']}
- 异常处理: {metrics['try_blocks']}
- 圈复杂度: {cyclomatic_complexity}

🏗️ **结构复杂度：**
- 函数数量: {metrics['functions']}
- 类数量: {metrics['classes']}
- 估计嵌套深度: {metrics['nested_depth']}

💡 **评估：**
{self._get_complexity_assessment(cyclomatic_complexity, metrics['nested_depth'])}"""
    
    def _estimate_nesting_depth(self, code: str) -> int:
        """估算嵌套深度"""
        max_depth = 0
        current_depth = 0
        for line in code.split('\n'):
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                current_depth = indent // 4
                max_depth = max(max_depth, current_depth)
        return max_depth
    
    def _get_complexity_assessment(self, cyclomatic: int, nesting: int) -> str:
        """复杂度评估"""
        if cyclomatic <= 10 and nesting <= 3:
            return "✅ 复杂度适中，代码易于理解和维护"
        elif cyclomatic <= 20 and nesting <= 5:
            return "⚠️ 复杂度偏高，建议考虑重构"
        else:
            return "❌ 复杂度过高，强烈建议拆分函数或类"
    
    def _generate_summary(self, code: str) -> str:
        """生成代码摘要（优化提示词）"""
        prompt = f"""请为以下代码生成专业的技术文档摘要：

代码：
```
{code[:1000]}
```

请包含：
1. **功能概述** - 2-3句话描述主要功能
2. **核心逻辑** - 关键算法或业务逻辑
3. **输入输出** - 主要的输入参数和返回值
4. **使用场景** - 典型的使用场景

请用简洁专业的语言描述。"""
        
        return self.llm._call(prompt)
    
    # ========== 新增工具实现 ==========
    
    def _analyze_performance(self, code: str) -> str:
        """分析性能（新增）"""
        prompt = f"""作为性能优化专家，请分析以下代码的性能特征：

代码：
```
{code[:1000]}
```

请分析：
1. **时间复杂度** - 算法的时间复杂度
2. **空间复杂度** - 内存使用情况
3. **性能瓶颈** - 可能的性能瓶颈
4. **优化建议** - 具体的优化方案

请给出量化的分析结果。"""
        
        return self.llm._call(prompt)
    
    def _check_test_coverage(self, code: str) -> str:
        """检查测试覆盖（新增）"""
        prompt = f"""作为测试专家，请评估以下代码的可测试性：

代码：
```
{code[:1000]}
```

请提供：
1. **可测试性评分** - 1-10分
2. **测试建议** - 应该测试的场景
3. **测试用例** - 建议的测试用例示例
4. **Mock 策略** - 需要 mock 的依赖

请给出具体的测试方案。"""
        
        return self.llm._call(prompt)
    
    def _analyze_design_patterns(self, code: str) -> str:
        """分析设计模式（新增）"""
        prompt = f"""作为架构师，请识别以下代码中的设计模式：

代码：
```
{code[:1000]}
```

请分析：
1. **已使用的模式** - 识别出的设计模式
2. **适用的模式** - 可以应用的设计模式
3. **模式优势** - 使用这些模式的好处
4. **实施建议** - 如何应用这些模式

请给出具体的模式名称和应用场景。"""
        
        return self.llm._call(prompt)
    
    def _check_code_smells(self, code: str) -> str:
        """检查代码异味（新增）"""
        smells = []
        
        lines = code.split('\n')
        
        # 检查过长函数
        in_function = False
        function_lines = 0
        for line in lines:
            if 'def ' in line:
                in_function = True
                function_lines = 0
            elif in_function:
                function_lines += 1
                if function_lines > 50:
                    smells.append("⚠️ 过长函数：函数超过50行，建议拆分")
                    in_function = False
        
        # 检查重复代码
        if code.count('for ') > 5:
            smells.append("⚠️ 可能存在重复循环逻辑")
        
        # 检查魔法数字
        import re
        numbers = re.findall(r'\b\d+\b', code)
        if len([n for n in numbers if int(n) > 1]) > 5:
            smells.append("⚠️ 魔法数字：建议使用常量替代硬编码数字")
        
        if smells:
            return "**检测到的代码异味：**\n\n" + "\n".join(smells)
        else:
            return "✅ 未检测到明显的代码异味"
    
    def _analyze_error_handling(self, code: str) -> str:
        """分析错误处理（新增）"""
        prompt = f"""作为可靠性专家，请评估以下代码的错误处理机制：

代码：
```
{code[:1000]}
```

请检查：
1. **异常捕获** - try-catch 的使用
2. **错误传播** - 错误如何向上传递
3. **错误恢复** - 是否有恢复机制
4. **日志记录** - 错误日志是否完善

请给出改进建议。"""
        
        return self.llm._call(prompt)
    
    def _create_agent(self):
        """创建 ReAct 智能代理（优化提示词）"""
        
        template = """你是一位资深的代码审查专家和架构师，拥有多年的软件开发经验。你的任务是帮助用户进行深入的代码分析，提供专业、可执行的建议。

你可以使用以下专业工具：
{tools}

工具名称: {tool_names}

**分析策略：**
1. 先理解代码的整体结构和目的
2. 根据任务选择最合适的工具组合
3. 可以多次使用不同工具进行全面分析
4. 综合所有工具的结果给出最终建议

**回答格式：**

Question: 用户的分析任务
Thought: 我需要分析什么，应该使用哪些工具
Action: 选择的工具名称（必须是 [{tool_names}] 中的一个）
Action Input: 工具的输入（通常是代码内容）
Observation: 工具返回的分析结果
... (可以重复使用多个工具)
Thought: 我已经收集了足够的信息
Final Answer: 综合所有分析结果，给出专业的最终建议

**重要提示：**
- 每次只能使用一个工具
- Action 必须是工具列表中的确切名称
- 充分利用多个工具进行全面分析
- 最终答案要具体、可执行

开始分析！

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
    
    def analyze_parallel(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        并行执行多个分析任务（新增）
        
        Args:
            tasks: 任务列表，每个任务包含 task 和 code
            
        Returns:
            分析结果列表
        """
        if not self.enable_parallel:
            # 串行执行
            return [self.analyze(t['task'], t.get('code')) for t in tasks]
        
        # 并行执行
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_task = {
                executor.submit(self.analyze, t['task'], t.get('code')): t 
                for t in tasks
            }
            
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    task = future_to_task[future]
                    results.append({
                        "status": "error",
                        "task": task['task'],
                        "error": str(e)
                    })
        
        return results
    
    def plan_and_execute(self, objective: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        规划并执行复杂的分析任务
        
        Args:
            objective: 分析目标
            context: 上下文信息（文件路径、语言等）
            
        Returns:
            执行结果
        """
        planning_prompt = f"""
作为代码分析专家，请为以下目标制定详细的分析计划：

目标: {objective}

上下文信息:
{json.dumps(context or {}, indent=2, ensure_ascii=False)}

请列出需要执行的分析步骤，每个步骤使用一个专业工具。
建议的工具包括：代码质量、Bug检测、安全分析、性能分析、设计模式等。
"""
        
        try:
            plan = self.llm._call(planning_prompt)
            
            execution_result = self.analyze(
                task=f"根据以下计划执行全面分析:\n{plan}\n\n目标: {objective}",
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
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.enable_cache:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "size": len(self.cache.cache),
            "max_size": self.cache.max_size,
            "ttl": self.cache.ttl
        }
    
    def clear_cache(self):
        """清空缓存"""
        if self.enable_cache:
            self.cache.clear()


# 为了向后兼容，保留原名称
CodeAnalysisAgent = OptimizedCodeAnalysisAgent


def main():
    """示例用法"""
    print("=" * 80)
    print("优化版 LangChain 智能代理演示")
    print("=" * 80)
    
    # 创建智能代理（启用所有优化）
    agent = OptimizedCodeAnalysisAgent(
        enable_cache=True,
        enable_parallel=True
    )
    
    print(f"\n✓ 智能代理已创建")
    print(f"  工具数量: {len(agent.tools)}")
    print(f"  缓存状态: {'启用' if agent.enable_cache else '禁用'}")
    print(f"  并行调用: {'启用' if agent.enable_parallel else '禁用'}")
    
    # 示例代码
    sample_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
    
    print("\n" + "=" * 80)
    print("示例：并行分析多个任务")
    print("=" * 80)
    
    tasks = [
        {"task": "分析代码质量", "code": sample_code},
        {"task": "检测潜在bug", "code": sample_code},
        {"task": "评估性能", "code": sample_code},
    ]
    
    results = agent.analyze_parallel(tasks)
    
    for i, result in enumerate(results, 1):
        print(f"\n任务 {i}: {result['status']}")
    
    # 显示缓存统计
    print("\n" + "=" * 80)
    print("缓存统计")
    print("=" * 80)
    stats = agent.get_cache_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

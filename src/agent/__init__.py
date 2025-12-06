"""
Agent Module - 智能代理模块
提供基于 LangChain 的智能代码分析能力
"""

from .langchain_agent import CodeAnalysisAgent, OllamaLLM

__all__ = ['CodeAnalysisAgent', 'OllamaLLM']

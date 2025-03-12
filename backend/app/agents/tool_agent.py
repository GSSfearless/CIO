"""
工具选择代理
能够自主选择和使用适当工具的代理
"""
import json
import re
from typing import Dict, List, Optional, Any, Union, Type, Tuple, Set

from app.agents.base_agent import BaseAgent
from app.agents.tools.base_tool import BaseTool
from app.agents.tools import SearchTool, DatabaseTool, WebTool
from app.llm import LLMService, Message
from app.utils import logger


class ToolUsageState:
    """跟踪工具使用状态的类"""
    
    def __init__(self):
        self.used_tools: Dict[str, int] = {}  # 记录已使用的工具及次数
        self.search_queries: List[str] = []  # 记录已执行的搜索查询
        self.visited_urls: List[str] = []  # 记录已访问的网页
        self.information_pieces: List[str] = []  # 收集到的信息片段
        self.confidence_level: float = 0.0  # 当前对回答的信心水平(0-1)
    
    def update_used_tool(self, tool_name: str):
        """更新工具使用记录"""
        if tool_name in self.used_tools:
            self.used_tools[tool_name] += 1
        else:
            self.used_tools[tool_name] = 1
    
    def add_search_query(self, query: str):
        """添加搜索查询"""
        if query not in self.search_queries:
            self.search_queries.append(query)
    
    def add_visited_url(self, url: str):
        """添加已访问URL"""
        if url not in self.visited_urls:
            self.visited_urls.append(url)
    
    def add_information(self, info: str):
        """添加信息片段"""
        self.information_pieces.append(info)
    
    def update_confidence(self, new_info_relevance: float):
        """更新信心水平"""
        # 这里使用一个简单的信心更新算法
        # 当收集到更多相关信息时，信心水平逐渐提高
        current_weight = 0.7  # 当前信心的权重
        new_info_weight = 0.3  # 新信息的权重
        
        self.confidence_level = (
            current_weight * self.confidence_level + 
            new_info_weight * new_info_relevance
        )
        
        # 确保信心水平在0-1之间
        self.confidence_level = max(0.0, min(1.0, self.confidence_level))
    
    def should_continue(self, min_tools_used: int = 1, min_confidence: float = 0.7) -> bool:
        """
        判断是否应该继续使用工具
        
        Args:
            min_tools_used: 最少应使用的工具数量
            min_confidence: 最小信心水平
            
        Returns:
            bool: 是否应该继续使用工具
        """
        # 至少使用了指定数量的工具
        tools_used = len(self.used_tools)
        
        # 如果没有使用足够的工具，继续使用
        if tools_used < min_tools_used:
            return True
        
        # 如果信心水平不够，继续使用
        if self.confidence_level < min_confidence:
            return True
        
        # 如果搜索工具使用次数过多，可以考虑停止
        if self.used_tools.get("search", 0) > 3:
            return False
        
        # 默认继续使用工具
        return True
    
    def get_state_summary(self) -> str:
        """获取状态摘要"""
        summary = []
        
        # 添加已使用工具信息
        if self.used_tools:
            tools_str = ", ".join([f"{tool}({count}次)" for tool, count in self.used_tools.items()])
            summary.append(f"已使用工具: {tools_str}")
        
        # 添加搜索查询信息
        if self.search_queries:
            queries_str = ", ".join([f'"{query}"' for query in self.search_queries])
            summary.append(f"已执行搜索: {queries_str}")
        
        # 添加已访问URL
        if self.visited_urls:
            urls_str = ", ".join([f'"{url}"' for url in self.visited_urls])
            summary.append(f"已访问网页: {urls_str}")
        
        # 添加信心水平
        summary.append(f"当前信心水平: {self.confidence_level:.2f}")
        
        return "\n".join(summary)


class ToolAgent(BaseAgent):
    """能够自主选择和使用工具的代理"""
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        tools: Optional[List[BaseTool]] = None,
        **kwargs
    ):
        """
        初始化工具代理
        
        Args:
            llm_service: LLM服务实例
            tools: 可用工具列表
            **kwargs: 其他参数
        """
        super().__init__(llm_service, **kwargs)
        
        # 初始化工具
        self.tools = tools or self._init_default_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # 构建系统提示词
        self._build_system_prompt()
    
    def _init_default_tools(self) -> List[BaseTool]:
        """
        初始化默认工具
        
        Returns:
            List[BaseTool]: 默认工具列表
        """
        return [
            SearchTool(),
            DatabaseTool(),
            WebTool()
        ]
    
    def _build_system_prompt(self):
        """构建系统提示词"""
        # 基础系统提示词
        self.system_message = """
        你是一个先进的AI助手，能够灵活使用各种工具解决复杂问题。你的目标是提供最准确、最相关的信息。

        在使用工具时，请遵循以下工作流程：
        1. 分析用户问题，理解核心需求
        2. 规划获取信息的策略，决定使用哪些工具
        3. 使用工具获取信息，分析结果
        4. 判断结果是否满足需求:
           - 如果信息不完整或不准确，继续使用工具获取更多信息
           - 如果获得的信息有冲突，使用其他工具交叉验证
           - 如果信息足够，进行总结并回答用户
        5. 在决定退出工具使用循环前，确保你已经：
           - 收集了足够多的相关信息
           - 解答了用户问题的各个方面
           - 验证了关键信息的准确性

        你可以使用以下工具：
        """
        
        # 添加工具说明
        for tool in self.tools:
            self.system_message += f"""
            - {tool.name}: {tool.description}
              参数: {json.dumps(tool.input_schema.schema().get('properties', {}), ensure_ascii=False)}
            """
        
        # 使用工具的指导
        self.system_message += """
        使用工具时，请遵循以下格式：
        
        思考: <在这里分析问题并决定使用哪个工具>
        工具: <工具名称>
        参数: <工具参数的JSON格式>
        
        在回答用户问题时：
        1. 分析用户的问题，判断需要使用哪些工具
        2. 逐步使用工具获取信息
        3. 综合所有信息给出完整回答
        4. 引用信息来源

        如果信息不足，可以主动使用搜索工具获取最新信息。
        如果用户问题涉及系统中已有的数据，优先使用数据库查询工具。
        如果需要获取特定网页的内容，使用网页抓取工具。
        
        在回答中你应该:
        - 保持客观中立
        - 提供来源或引用
        - 当使用工具获取信息时，告诉用户你在查询什么
        - 如果无法找到相关信息，诚实地告诉用户
        
        对于复杂问题，你应该：
        1. 将问题分解为多个子问题
        2. 为每个子问题使用适当的工具收集信息
        3. 整合所有信息，提供全面的答案
        
        当你决定停止使用工具时，请说明"我已收集足够信息，可以回答问题了"，然后给出完整答案。
        """
    
    async def _detect_tool_use(self, text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        检测文本中的工具使用意图
        
        Args:
            text: 要检测的文本
            
        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: 工具名称和参数
        """
        tool_pattern = r"工具:\s*([a-zA-Z_]+)"
        params_pattern = r"参数:\s*(\{[\s\S]*?\})"
        
        # 提取工具名称
        tool_match = re.search(tool_pattern, text)
        if not tool_match:
            return None, None
        
        tool_name = tool_match.group(1).strip()
        
        # 提取参数
        params_match = re.search(params_pattern, text)
        if not params_match:
            return tool_name, {}
        
        params_json = params_match.group(1)
        try:
            params = json.loads(params_json)
            return tool_name, params
        except json.JSONDecodeError:
            logger.error(f"解析工具参数失败: {params_json}")
            return tool_name, {}
    
    async def _run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行指定的工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            Dict[str, Any]: 工具运行结果
        """
        # 获取工具
        tool = self.tool_map.get(tool_name)
        if tool is None:
            return {
                "error": f"未知工具: {tool_name}",
                "success": False
            }
        
        try:
            # 运行工具
            result = await tool.run(params)
            
            # 将结果转换为字典
            if hasattr(result, "dict"):
                return result.dict()
            return result
        except Exception as e:
            logger.error(f"运行工具时出错: {e}")
            return {
                "error": f"运行工具失败: {str(e)}",
                "success": False
            }
    
    async def _generate_plan(self, query: str) -> str:
        """
        生成使用工具的计划
        
        Args:
            query: 用户查询
            
        Returns:
            str: 生成的计划
        """
        planning_prompt = f"""
        请为以下用户查询生成一个使用工具的计划:
        
        用户查询: {query}
        
        你的计划应该包括:
        1. 需要使用哪些工具
        2. 每个工具需要的参数
        3. 如何综合各工具的结果回答用户问题
        
        请只回答执行计划，不要执行工具或回答用户问题。
        """
        
        # 准备消息
        messages = await self._prepare_messages(
            messages=[{"role": "user", "content": planning_prompt}]
        )
        
        # 调用LLM
        return await self.llm_service.chat(
            messages=messages,
            temperature=0.2
        )
    
    async def _execute_with_tools(
        self, 
        messages: List[Message], 
        max_iterations: int = 10,
        show_reasoning: bool = False
    ) -> str:
        """
        使用工具执行和回答，增强版
        
        Args:
            messages: 消息历史
            max_iterations: 最大工具使用迭代次数
            show_reasoning: 是否在回答中显示推理过程
            
        Returns:
            str: 生成的回答
        """
        # 预处理消息以提取最后一条用户消息
        last_user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_message = msg.content
                break
        
        if not last_user_message:
            return "无法识别用户问题"
        
        # 初始化工具使用状态跟踪
        usage_state = ToolUsageState()
        
        # 生成初始回答
        response = await self.llm_service.chat(messages=messages, temperature=0.7)
        
        # 用于存储推理和工具使用过程
        reasoning_steps = []
        
        # 检测工具使用
        iterations = 0
        search_results = []
        
        while iterations < max_iterations:
            # 记录当前推理步骤
            reasoning_steps.append(f"【思考】:\n{response}")
            
            # 检测是否有明确的终止信号
            if "我已收集足够信息" in response or "任务完成" in response or "不需要更多信息" in response:
                # 提取最终答案
                final_answer = re.sub(r'我已收集足够信息.*?回答问题了。?\s*', '', response)
                reasoning_steps.append("【最终答案】:\n" + final_answer)
                
                if show_reasoning:
                    return "\n\n".join(reasoning_steps)
                else:
                    return final_answer
            
            # 检测工具使用意图
            tool_name, params = await self._detect_tool_use(response)
            
            # 如果没有明确的工具使用意图，但暗示需要更多信息
            if tool_name is None and ("需要更多信息" in response or "继续搜索" in response):
                tool_selection_prompt = """
                你需要使用工具获取更多信息。请明确指出要使用的工具和参数。
                使用以下格式：
                
                思考: <在这里分析问题并决定使用哪个工具>
                工具: <工具名称>
                参数: <工具参数的JSON格式>
                """
                messages.append(Message.assistant_message(response))
                messages.append(Message.user_message(tool_selection_prompt))
                
                response = await self.llm_service.chat(messages=messages, temperature=0.5)
                iterations += 1
                continue
            
            # 如果没有工具使用意图，也没有暗示需要更多信息，返回当前回答
            if tool_name is None:
                if show_reasoning:
                    reasoning_steps.append("【最终答案】:\n" + response)
                    return "\n\n".join(reasoning_steps)
                else:
                    return response
            
            # 执行工具，记录工具使用
            usage_state.update_used_tool(tool_name)
            reasoning_steps.append(f"【工具使用】:\n工具: {tool_name}\n参数: {json.dumps(params, ensure_ascii=False)}")
            
            # 针对特定工具进行额外记录
            if tool_name == "search" and "query" in params:
                usage_state.add_search_query(params["query"])
            elif tool_name == "web_scrape" and "url" in params:
                usage_state.add_visited_url(params["url"])
            
            # 运行工具
            result = await self._run_tool(tool_name, params)
            reasoning_steps.append(f"【工具结果】:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 记录搜索结果
            if tool_name == "search" and result.get("success", False):
                search_results.extend(result.get("results", []))
            
            # 更新信心水平（基于工具结果的成功与否）
            relevance = 0.6  # 默认相关性
            if result.get("success", False):
                relevance = 0.8
                # 处理信息片段
                if "content" in result:
                    usage_state.add_information(result["content"])
                elif "results" in result and result["results"]:
                    for item in result["results"]:
                        if isinstance(item, dict) and "content" in item:
                            usage_state.add_information(item["content"])
            
            usage_state.update_confidence(relevance)
            
            # 构建工具结果消息，包含状态信息
            tool_result_message = f"""
            工具执行结果:
            工具: {tool_name}
            参数: {json.dumps(params, ensure_ascii=False)}
            结果: {json.dumps(result, ensure_ascii=False)}
            
            当前状态:
            {usage_state.get_state_summary()}
            
            请分析上述结果，并决定：
            1. 是否需要使用其他工具获取更多信息
            2. 是否已获得足够信息可以回答用户问题
            3. 如果信息足够，请直接给出完整回答，并在回答前说明"我已收集足够信息，可以回答问题了"
            4. 如果信息不足，请说明还需要什么信息，并指定下一个要使用的工具
            """
            
            messages.append(Message.assistant_message(response))
            messages.append(Message.user_message(tool_result_message))
            
            # 生成新的回答
            response = await self.llm_service.chat(messages=messages, temperature=0.7)
            iterations += 1
            
            # 每次迭代后检查是否应该继续使用工具
            if not usage_state.should_continue() and iterations >= 2:
                summary_prompt = """
                你已经收集了足够的信息。请综合所有信息，给出最终完整的回答。
                在回答前，请说明"我已收集足够信息，可以回答问题了"。
                """
                messages.append(Message.user_message(summary_prompt))
                response = await self.llm_service.chat(messages=messages, temperature=0.7)
                break
            
            # 每3次迭代进行一次总结，避免无限循环
            if iterations % 3 == 0 and search_results:
                summary_prompt = f"""
                你已经搜索了多次，请对已获得的信息进行总结，判断是否需要继续搜索。
                
                当前状态:
                {usage_state.get_state_summary()}
                
                请决定是否继续使用工具。如果继续，说明下一步需要什么信息；如果已足够，直接给出完整回答。
                """
                messages.append(Message.user_message(summary_prompt))
                response = await self.llm_service.chat(messages=messages, temperature=0.7)
        
        # 如果达到最大迭代次数还没结束，添加一个最终总结步骤
        if iterations >= max_iterations:
            final_summary_prompt = """
            你已经进行了多次工具调用。请根据已获得的所有信息，给出最终答案。
            不需要使用更多工具，直接给出完整回答。
            """
            messages.append(Message.user_message(final_summary_prompt))
            response = await self.llm_service.chat(messages=messages, temperature=0.7)
            reasoning_steps.append("【强制结束迭代】:\n" + response)
        
        # 返回结果，根据是否显示推理过程决定
        if show_reasoning:
            reasoning_steps.append("【最终答案】:\n" + response)
            return "\n\n".join(reasoning_steps)
        else:
            return response
    
    async def process(
        self, 
        query: str, 
        context: Optional[str] = None, 
        show_reasoning: bool = False,
        **kwargs
    ) -> str:
        """
        处理用户查询
        
        Args:
            query: 用户查询
            context: 上下文信息
            show_reasoning: 是否显示推理过程
            **kwargs: 其他参数
            
        Returns:
            str: 处理结果
        """
        try:
            # 构建提示
            prompt = query
            if context:
                prompt = f"上下文信息:\n{context}\n\n用户查询: {query}"
            
            # 准备消息
            messages = await self._prepare_messages(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 使用工具执行和回答
            return await self._execute_with_tools(messages, show_reasoning=show_reasoning)
            
        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            return f"处理查询时出现错误: {str(e)}"
    
    async def cleanup(self):
        """清理资源"""
        for tool in self.tools:
            if hasattr(tool, "cleanup") and callable(getattr(tool, "cleanup")):
                await tool.cleanup() 
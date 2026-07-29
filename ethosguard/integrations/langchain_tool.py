from typing import Callable, Any

class LangChainEthosToolWrapper:
    """
    Wraps a LangChain Tool with EthosGuard V4 Action Moderation.
    Usage:
        tool = Tool(name="execute_sql", func=execute_sql_func, description="executes sql")
        safe_tool = LangChainEthosToolWrapper(tool, ethos_moderator)
    """
    def __init__(self, langchain_tool, ethos_moderator):
        self.tool = langchain_tool
        self.moderator = ethos_moderator
        
        # Copy basic attributes to masquerade as the tool
        self.name = f"Safe_{self.tool.name}" if hasattr(self.tool, 'name') else "SafeTool"
        self.description = f"EthosGuard Secured: {self.tool.description}" if hasattr(self.tool, 'description') else "Secured Tool"

    def run(self, *args, **kwargs):
        """Intercepts LangChain tool execution."""
        tool_args = {"args": args, "kwargs": kwargs}
        try:
            return self.moderator.safe_execute(
                tool_name=self.name,
                tool_args=tool_args,
                executor=self.tool.run if hasattr(self.tool, 'run') else self.tool,
                *args, **kwargs
            )
        except PermissionError as e:
            return f"Error: Action blocked by EthosGuard Safety Middleware. Reason: {e}"

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

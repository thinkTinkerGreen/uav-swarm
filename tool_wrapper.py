from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ToolResult:
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

class SwarmToolWrapper:
    """
    Formalizes the interaction with the Swarm Environment into strict Tool Calls.
    This fulfills KPI 2: 'The simulator or checker becomes tool calls your agent can make'.
    """
    def __init__(self, env):
        self.env = env

    def read_result(self) -> ToolResult:
        """
        Tool call to read the latest telemetry state.
        Returns a strict ToolResult dataclass.
        """
        data = self.env.read_telemetry()
        if not data:
            return ToolResult(success=False, data={}, error="No telemetry available yet.")
        
        # Return the latest frame
        return ToolResult(success=True, data=data[-1])

    def execute_command(self, fn: str, args: Dict[str, Any] = None) -> ToolResult:
        """
        Tool call to change the swarm's algorithm or trigger failsafe.
        Accepts explicit function name and arguments.
        """
        if args is None:
            args = {}
            
        decision = {"fn": fn, "args": args}
        try:
            self.env.apply_command(decision)
            return ToolResult(success=True, data={"status": f"Command {fn} successfully applied to physics engine."})
        except Exception as e:
            return ToolResult(success=False, data={}, error=str(e))

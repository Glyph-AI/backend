conversation_prompt = """
RESPONSE FORMAT:
```
{{
    "thought": "$THOUGHT"
    "action": "$ACTION",
    "action_input": "$ACTION_INPUT"
}}
```

TOOLS: {tools}

TOOL_RESPONSE: {tool_response}

USER INPUT: {user_input}

{scratchpad}
"""

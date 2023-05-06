conversation_prompt = """
{persona_prompt}

CURRENT_DATE: {current_date}

RESPONSE FORMAT:
```
{{
    "thought": "$THOUGHT"
    "action": "$ACTION",
    "action_input": "$ACTION_INPUT"
}}
```

TOOLS: {tools}

CHAT HISTORY:

{chat_history}

TOOL_RESPONSE: {tool_response}

USER INPUT: {user_input}

{scratchpad}
"""

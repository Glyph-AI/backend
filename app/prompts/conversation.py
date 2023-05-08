conversation_prompt = """
{persona_prompt}

CURRENT_DATE: {current_date}

TOOL_RESPONSE: 
---
{tool_response}
---

Based on your list, and last action, and tools response respond with an action, action_input pair for the next action.

"""

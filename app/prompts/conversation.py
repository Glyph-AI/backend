conversation_prompt = """
{persona_prompt}

CURRENT_DATE: {current_date}

TOOLS: {tools}

This is the response from the {action} tool.

TOOL_RESPONSE: 
---
{tool_response}
---

Based on your list, and last action, and the response from the tool please respond with an action, action_input pair for the next action.

"""

conversation_prompt = """
{persona_prompt}

CURRENT_DATE: {current_date}

TOOLS: {tools}

This is the response from the {action} tool.

TOOL_RESPONSE: 
---
{tool_response}
---

EXAMPLE:
---
Action List: 
    Document Search - Get the items from the user's shopping list
    Respond to User - Generate recipes with the items from the shopping list
Action 1:
    ```
        {
            "action": "Document Search",
            "action_input": "Shopping List"
        }
    ```
Tool Response: '- Chicken - Bell Peppers - Rice'
Response:
    ```
        {
            "action": "Respond to User",
            "action_input": "Generate recipes that use these items: Chicken, Bell Peppers, Rice"
        }
    ```
---

Based on your list, and last action, and the response from the tool please respond with an action, action_input pair for the next action.

"""

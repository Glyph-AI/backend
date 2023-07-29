conversation_prompt = """
{persona_prompt}

CURRENT_DATE: {current_date}

TOOLS: {tools}

Observation: {tool_response}


Based on your observation and last action please respond with a thought, action, action_input for the next action.

"""

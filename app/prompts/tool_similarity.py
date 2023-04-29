tool_prompt = """
TOOLS: {tool_names}

Which of these tools is most similar to {error_tool}? You must give one of the tools in the tools list above. If you don't know, take your best guess.

Respond with only the tool name and nothing else. 
"""
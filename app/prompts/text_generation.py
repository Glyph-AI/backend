text_generation_prompt = """
Based on the responses from tools, and the plan above generate based on the following prompt:

PROMPT: {prompt}

DO NOT FOLLOW action, action_response formatting instructions. Generate whatever text you think is necessary to respond to the user.
"""

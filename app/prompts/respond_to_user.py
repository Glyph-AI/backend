respond_to_user_prompt = """
Based on the responses from tools, and the plan above respond to the user's initial request{tts_tag}:

USER INPUT: {user_input}

DO NOT FOLLOW action, action_response formatting instructions. Generate whatever text you think is necessary to respond to the user, including relevant information that may not have been directly requested. Be thorough in explaining concepts. Cite your source only if requested.

DO NOT INCLUDE ANY URLS TO EXTERNAL SITES.
"""

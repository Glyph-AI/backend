class BaseTool:
    respond_direct = False

    def __init__(self, db, bot_id, chat_id, internal_message_array=[], original_message="", tts=False):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.internal_message_array = internal_message_array
        self.original_message = original_message
        self.tts = False

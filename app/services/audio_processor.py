import openai

openai.api_key = os.environ.get(
    "OPENAI_KEY", "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")

class AudioProcessor():
    def process(self, filepath):
        with open("/temp/output.txt", "w+") as outfile:
            infile = open(filepath, "rb")
            transcript = openai.Audio.transcribe("whisper-1", infile)

            outfile.write(transcript)

        return "/temp/output.txt"


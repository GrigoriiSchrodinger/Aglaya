import whisper
import warnings
from pydub import AudioSegment

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")


class Translator:
    def __init__(self, path_file, model_whisper="large", segment_length=10000):
        self.model_whisper = model_whisper
        self.path_file = path_file
        self.segment_length = segment_length

    def split_audio_into_segments(self):
        audio = AudioSegment.from_file(self.path_file)
        duration = len(audio)
        segments = []

        for start in range(0, duration, self.segment_length):
            end = min(start + self.segment_length, duration)
            segments.append(audio[start:end])

        return segments

    async def transcribe_segments(self, segments):
        model = whisper.load_model(self.model_whisper)

        previous_text = ""

        for segment in segments:
            segment.export("temp_segment.mp3", format="mp3")
            result = model.transcribe("temp_segment.mp3")
            current_text = result["text"]

            if previous_text and (previous_text.endswith(('в', 'и', 'на', 'к'))):
                current_text = previous_text + ' ' + current_text

            yield current_text

            previous_text = current_text

    async def transcribe(self):
        segments = self.split_audio_into_segments()
        async for text in self.transcribe_segments(segments):
            yield text
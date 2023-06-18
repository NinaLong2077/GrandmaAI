import asyncio
import logging
import signal
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.streaming.transcriber import *
from vocode.streaming.agent import *
from vocode.streaming.synthesizer import *
from vocode.streaming.models.transcriber import *
from vocode.streaming.models.agent import *
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig 
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
import vocode
import os

# these can also be set as environment variables
vocode.setenv(
    OPENAI_API_KEY="your key",
    DEEPGRAM_API_KEY="your key",
    ELEVEN_LABS_API_KEY = "your key"
)

'''
transcriber: whisper c++
agent: openai chatgpt
synthesizer: elevenlabs
'''


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    microphone_input, speaker_output = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=False,
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
            )
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello!"),
                prompt_preamble="Have a pleasant conversation about life",
            )
        ),
        synthesizer=ElevenLabsSynthesizer(ElevenLabsSynthesizerConfig.from_output_device(
        
            speaker_output,
            
        ),
        logger=logger,
                                          
                                          
        )
        
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(signal.SIGINT, lambda _0, _1: conversation.terminate()) # kill signal in terminal
    
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())

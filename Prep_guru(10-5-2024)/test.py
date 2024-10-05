import asyncio
import os
import io
import time
import pickle
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
import PyPDF2


# Load environment variables
load_dotenv()

class LanguageModelProcessor:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="mixtral-8x7b-32768", 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        with open('system_prompt2.txt', 'r') as file:
            system_prompt = file.read().strip()
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])
        
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    def process(self, text):
        self.memory.chat_memory.add_user_message(text)
        start_time = time.time()
        response = self.conversation.invoke({"text": text})
        end_time = time.time()
        self.memory.chat_memory.add_ai_message(response['text'])
        elapsed_time = int((end_time - start_time) * 1000)
        print(f"LLM ({elapsed_time}ms): {response['text']}")
        return response['text']

    def load_resume(self, resume_path):
        with open(resume_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text()
        return resume_text.strip()

    def save_memory(self, filepath='conversation_memory.pkl'):
        with open(filepath, 'wb') as f:
            pickle.dump(self.memory, f)
        print(f"Memory saved to {filepath}")

    def load_memory(self, filepath='conversation_memory.pkl'):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.memory = pickle.load(f)
            print(f"Memory loaded from {filepath}")
        else:
            print(f"No memory file found at {filepath}, starting fresh.")

    def save_conversation(self, user_input, ai_response, filepath='conversation_log.txt'):
        try:
            with open(filepath, 'a', encoding='utf-8') as log_file:
                log_file.write(f"User: {user_input}\nAI: {ai_response}\n\n")
        except UnicodeEncodeError as e:
            print(f"UnicodeEncodeError: {e}")

    def load_conversation(self, filepath='conversation_log.txt'):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as log_file:
                previous_conversation = log_file.read()
            print("Previous conversation loaded:\n", previous_conversation)
            return True
        else:
            print("Unable to load conversation_log.txt. I don't have your last information available.")
            return False


def setup_azure_speech(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "en-IN"
    speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, '5000')
    speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, '4000')

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    return speech_recognizer


def setup_azure_tts(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name = 'en-IN-AaravNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    return speech_synthesizer


def text_to_speech(text, speech_synthesizer):
    ssml_text = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-IN'>
        <voice name='en-IN-AaravNeural'>
            <prosody rate='medium'>
                {text}
            </prosody>
        </voice>
    </speak>
    """
    try:
        speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesis complete")
        else:
            print(f"Speech synthesis failed: {speech_synthesis_result.reason}")
    except Exception as e:
        print(f"An error occurred during speech synthesis: {e}")


class ConversationManager:
    def __init__(self):
        self.llm = LanguageModelProcessor()
        self.api_key = os.getenv("AZURE_API_KEY")
        self.region = os.getenv("AZURE_REGION")
        self.speech_recognizer = setup_azure_speech(self.api_key, self.region)
        self.speech_synthesizer = setup_azure_tts(self.api_key, self.region)
        self.is_running = True

    async def listen_for_speech(self):
        print("Listening...")
        result = await self.recognize_speech()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        return None

    async def recognize_speech(self):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def recognized_cb(evt):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, evt.result)

        def canceled_cb(evt):
            if not future.done():
                loop.call_soon_threadsafe(future.set_exception, Exception(f"Speech recognition canceled: {evt.reason}"))

        self.speech_recognizer.recognized.connect(recognized_cb)
        self.speech_recognizer.canceled.connect(canceled_cb)

        await loop.run_in_executor(None, self.speech_recognizer.start_continuous_recognition)

        try:
            result = await asyncio.wait_for(future, timeout=200.0)  # 180 second timeout
        except asyncio.TimeoutError:
            print("Speech recognition timed out")
            result = None
        finally:
            await loop.run_in_executor(None, self.speech_recognizer.stop_continuous_recognition)

        return result
    
    #####################################################################################################
    # async def ask_for_introduction(self):
    #     iteration_count = 0
    #     feedback = ""

    #     while "good" not in feedback.lower() and iteration_count < 2:
    #         # First introduction
    #         intro_prompt = "Please introduce yourself."
    #         print(f"AI: {intro_prompt}")
    #         text_to_speech(intro_prompt, self.speech_synthesizer)

    #         user_intro = await self.listen_for_speech()
    #         if user_intro:
    #             print(f"User: {user_intro}")
    #             feedback = self.llm.process(user_intro)
    #             print(f"AI: {feedback}")
    #             text_to_speech(feedback, self.speech_synthesizer)

    #         iteration_count += 1

    ######################################################################################################

    # async def ask_for_introduction(self):
    #     iteration_count = 0  # To count the number of attempts

    #     while iteration_count < 3:  # Allow for up to 3 attempts
    #         # Step 1: Ask for introduction
    #         intro_prompt = "Please introduce yourself."
    #         print(f"AI: {intro_prompt}")
    #         text_to_speech(intro_prompt, self.speech_synthesizer)

    #         # Capture user's introduction
    #         user_intro = await self.listen_for_speech()
    #         if user_intro:
    #             print(f"User: {user_intro}")

    #             # Step 2: Analyze user's introduction and give feedback
    #             feedback = self.llm.process(f"Here is an introduction: {user_intro}. Give me feedback on the introduction, what is good, and what is missing.")
    #             print(f"AI Feedback: {feedback}")
    #             text_to_speech(feedback, self.speech_synthesizer)

    #             # Step 3: Check if feedback is satisfactory
    #             if "good" in feedback.lower():
    #                 print("Feedback was satisfactory.")
    #                 break  # Exit loop if feedback is satisfactory
    #             else:
    #                 print("Your introduction needs improvement.")
    #                 text_to_speech("Your introduction needs improvement. Please try again.", self.speech_synthesizer)
    #         else:
    #             print("No valid introduction received. Please try again.")
    #             text_to_speech("No valid introduction received. Please try again.", self.speech_synthesizer)

    #         iteration_count += 1  # Increment the attempt count

    #     # After 3 attempts, provide final feedback
    #     if iteration_count == 3:
    #         practice_feedback = "You have made three attempts. Please practice your introduction more."
    #         print(practice_feedback)
    #         text_to_speech(practice_feedback, self.speech_synthesizer)
    #     # Optionally, you could restart asking for introduction or move to the next stage
    #     # Uncomment the following line if you want to ask again after three attempts
    #     # await self.ask_for_introduction()  # Restart the process if needed



    async def ask_for_introduction(self):
        iteration_count = 0  # To count the number of attempts

        while iteration_count < 3:  # Allow for up to 3 attempts
            # Step 1: Ask for introduction
            intro_prompt = "Please introduce yourself."
            print(f"AI: {intro_prompt}")
            text_to_speech(intro_prompt, self.speech_synthesizer)

            # Capture user's introduction
            user_intro = await self.listen_for_speech()
            if user_intro:
                print(f"User: {user_intro}")

                # Step 2: Analyze user's introduction and give feedback
                feedback = self.llm.process(f"Here is an introduction: {user_intro}. Give me feedback on the introduction, what is good, and what is missing.")
                print(f"AI Feedback: {feedback}")
                text_to_speech(feedback, self.speech_synthesizer)

                # Step 3: Check if feedback is satisfactory
                if "good" in feedback.lower():
                    print("Feedback was satisfactory.")
                    return True  # Exit loop and move to the next stage (resume questions)
                else:
                    print("Your introduction needs improvement.")
                    text_to_speech("Your introduction needs improvement. Please try again.", self.speech_synthesizer)
            else:
                print("No valid introduction received. Please try again.")
                text_to_speech("No valid introduction received. Please try again.", self.speech_synthesizer)

            iteration_count += 1  # Increment the attempt count

        # After 3 attempts, provide final feedback
        if iteration_count == 3:
            practice_feedback = "You have made three attempts. Please practice your introduction more."
            print(practice_feedback)
            text_to_speech(practice_feedback, self.speech_synthesizer)

        return False  # Return false if the candidate couldn't provide a satisfactory introduction

###############################################################
        # Optionally, you could restart asking for introduction or move to the next stage
        # Uncomment the following line if you want to ask again after three attempts
        # await self.ask_for_introduction()  # Restart the process if needed



        # After 2 iterations, suggest practice and move on
        # if "good" not in feedback.lower():
        #     text_to_speech("Please practice this introduction more. Let's move on to the next question.", self.speech_synthesizer)


    async def ask_questions_based_on_resume(self, resume_text):
        questions_prompt = f"Based on the following resume, please ask relevant questions: {resume_text}"
        questions = self.llm.process(questions_prompt)
        print(f"AI: {questions}")
        text_to_speech(questions, self.speech_synthesizer)

        while True:
            user_response = await self.listen_for_speech()
            if user_response:
                print(f"User: {user_response}")
                feedback = self.llm.process(user_response)
                print(f"AI: {feedback}")
                text_to_speech(feedback, self.speech_synthesizer)

    async def main(self):
        # Start with the welcome message
        welcome_message = "I am GetScreened PrepGuru. I will guide you step by step to improve your interview skills and help you become a better version of yourself."
        print(f"AI: {welcome_message}")
        text_to_speech(welcome_message, self.speech_synthesizer)

        # Ask for the introduction twice
        await self.ask_for_introduction()

        # Load resume and process it after introductions
        resume_path = r"Resume\Abhinav Anand Resume.pdf"  # Adjust this path to your resume file  
        resume_text = self.llm.load_resume(resume_path)

        # Ask questions based on the resume
        await self.ask_questions_based_on_resume(resume_text)

if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.main())

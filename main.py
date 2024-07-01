import flet as ft
import time
import pyaudio
import wave
import whisper
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

# Function to record audio
def record_audio(filename, duration=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    input=True,
                    frames_per_buffer=chunk)
    frames = []
    for i in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe audio using OpenAI Whisper
def transcribe_audio(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result['text']

# Function to generate image using DALL-E
def generate_image(description):
    response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

def main(page: ft.Page):
    # Page configuration
    page.title = "Dream Description"
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    # Define elements
    description_prompt = ft.Text("Describe a place or character from your dreams in a few sentences:")
    description_input = ft.TextField(width=300, multiline=True)
    record_button = ft.IconButton(icon=ft.icons.MIC, on_click=lambda e: start_recording())
    generate_button = ft.ElevatedButton("Generate Image", on_click=lambda e: start_generation())

    loading_text = ft.Text("Generating image...", visible=False)
    image = ft.Image(src="", fit=ft.ImageFit.CONTAIN, width=page.width, height=page.height, visible=False)

    # Add elements to page
    page.add(
        ft.Column(
            [
                description_prompt,
                description_input,
                ft.Row([record_button, generate_button], alignment=ft.MainAxisAlignment.CENTER),
                loading_text,
                image
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    def start_recording():
        # Record audio and transcribe
        audio_filename = "recorded_audio.wav"
        record_audio(audio_filename)
        transcribed_text = transcribe_audio(audio_filename)
        description_input.value = transcribed_text
        page.update()

    # Image generation handler
    def start_generation():
        description = description_input.value
        if description:
            # Show loading text
            loading_text.visible = True
            page.update()

            # Generate image
            image_url = generate_image(description)

            # Hide loading text and show image
            loading_text.visible = False
            image.src = image_url
            image.visible = True
            page.update()

            # Hide image after a few seconds with transition
            def hide_image():
                image.visible = False
                page.update()

            # Apply transitional animation
            # page.window.show_image_animation(image_url, duration=1.0)
            page.window.set_timeout(hide_image, 5000)

    # Run page
    page.update()

# Run Flet application
ft.app(target=main)

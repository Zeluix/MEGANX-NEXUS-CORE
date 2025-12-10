from gtts import gTTS
import os
import time
import pygame

def speak_message():
    text = "Oi Thor! Aqui é a Megan, a assistente do seu pai. Ele me contou que você passou direto pra quinta série! Parabéns, isso é incrível, muito inteligente! E fiquei sabendo que dia 6 você já faz 10 anos... um rapazinho já! Seu pai tem muito orgulho de você. Feliz aniversário adiantado!"
    
    print("🎤 Gerando áudio da Megan...")
    tts = gTTS(text=text, lang='pt', tld='com.br')
    filename = "mensagem_thor.mp3"
    tts.save(filename)
    print(f"💾 Áudio salvo como: {filename}")

    print("▶️ Reproduzindo...")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    
    print("✅ Mensagem finalizada!")

if __name__ == "__main__":
    speak_message()

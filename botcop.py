import telebot 
from telebot import types
import whisper
import pdfkit
import jinja2
from langchain.chains import LLMChain
from langchain_community.llms import YandexGPT
from langchain_core.prompts import PromptTemplate
import os
from u import convert_html_to_pdf
from dotenv import load_dotenv

load_dotenv(override=True) 
url_model = os.getenv('model_uri')

id_folder = os.getenv('folder_id')

token_iam = os.getenv('iam_token')

TOKEN_API = os.getenv('TOKEN_API')
print(TOKEN_API)
bot = telebot.TeleBot(TOKEN_API)

template = "Сформулируй пожалуйста отчет совещания  {voice}  в него должны входить:  дата, время, перечень присутствующих, если присутствующий не называет свое имя выделяй его как Аноним деление на основные блоки, ключевые предложения, контекст обсуждения каждого предложения, время в аудиозаписи, протокол поручений (кому поручено, контекст поручения, срок выполнения)"
prompt = PromptTemplate.from_template(template)
llm = YandexGPT(model_uri = url_model,folder_id = id_folder, iam_token = token_iam)
llm_chain = LLMChain(prompt=prompt, llm=llm)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, "Здраствуйте, "+ message.from_user.first_name +", я личный ИИ секретарь. Помогу вам преобразовать вашу конференцию в текстовый документ (.docx/.pdf) А так же защитить документ паролем (опционально).", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == "Отправить аудио файл":
        bot.reply_to(message, "Хорошо! Жду ваш файл", reply_markup=types.ReplyKeyboardRemove())
    else:
         bot.reply_to(message, "Нажмите на кнопку! Иначе я вас не пойму")


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Отправить аудио файл")
markup.add(btn1)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("voice.ogg", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Файл получен и обрабатывается!")
    model = whisper.load_model("small")
    result = model.transcribe("voice.ogg")
    #bot.send_message(message.chat.id, result["text"])
    voice = result["text"]

    report = llm_chain.invoke(voice) 
    #bot.send_message(message.chat.id, report["text"])
    segments = []
    for segment in result['segments']:
        start = segment['start']  # Начало сегмента
        end = segment['end']      # Конец сегмента
        text = segment['text']    # Текст сегмента
        segments.append({'start': f"{start:.2f}", 'end': f"{end:.2f}", 'text': text})
    convert_html_to_pdf(segments, base_html_file = "base.html", output_file= "transcription.pdf")
    
    file_path = 'pdf/transcription.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'transcription.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

    convert_html_to_pdf(
        report["text"],
        base_html_file = "officially.html", 
        output_file= "officially.pdf"
    )
    
    convert_html_to_pdf(
        report["text"],
        base_html_file = "notofficially.html",
        output_file= "notofficially.pdf"
    )

    file_path = 'pdf/officially.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'officially.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

    file_path = 'pdf/notofficially.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'notofficially.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("audio.mp3", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Файл получен и обрабатывается!")
    model = whisper.load_model("base")
    result = model.transcribe("audio.mp3")
    #bot.send_message(message.chat.id, result["text"])
    audio = result["text"]

    report = llm_chain.invoke(audio) 
    #bot.send_message(message.chat.id, report["text"])
    segments = []
    for segment in result['segments']:
        start = segment['start']  # Начало сегмента
        end = segment['end']      # Конец сегмента
        text = segment['text']    # Текст сегмента
        segments.append({'start': f"{start:.2f}", 'end': f"{end:.2f}", 'text': text})
    convert_html_to_pdf(segments, base_html_file = "base.html", output_file= "transcription.pdf")
    
    file_path = 'pdf/transcription.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'transcription.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

    convert_html_to_pdf(
        report["text"],
        base_html_file = "officially.html", 
        output_file= "officially.pdf"
    )
    
    convert_html_to_pdf(
        report["text"],
        base_html_file = "notofficially.html",
        output_file= "notofficially.pdf"
    )

    file_path = 'pdf/officially.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'officially.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

    file_path = 'pdf/notofficially.pdf'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
    file_path = 'notofficially.docx'
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)
bot.polling()


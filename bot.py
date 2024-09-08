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

TOKEN_API = os.getenv('TOKEN_API')
print(TOKEN_API)
bot = telebot.TeleBot(TOKEN_API)

template = "Сформируй пожалуйста отчет совещания {voice} в него должны входить: Дата, время, если их не будет в сообщении, то используй дату и время получения. Так же в отчете должны быть спикеры, те кто говорит, спикер может быть один, а можеть быть и несколько, если они(он) не называют своих имен, то называй их Аноним1, Аноним2 и так далее."
prompt = PromptTemplate.from_template(template)
llm = YandexGPT(model_uri='gpt://b1gvmo70ll74cvokevfk/yandexgpt/latest',folder_id='b1gvmo70ll74cvokevfk', iam_token = "t1.9euelZqSls6Uyo_Mi5eKzMnJxsqXx-3rnpWako6Pi8qRy5CQk8zKjY2Jz5jl8_dlYg9J-e8AQ0Q__d3z9yURDUn57wBDRD_9zef1656VmpWTz5OPyZbMy8ubzo-JnZ7O7_zF656VmpWTz5OPyZbMy8ubzo-JnZ7O.cSEDQ94Q-vlSzbCDRekvWrIOcyHVn2ZVmSNFK0rF1czytJktoxOjKazwiTwepUFoy9-hPf00U5TXWpUujV33Aw")
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
    bot.send_message(message.chat.id, result["text"])
    voice = result["text"]

    report = llm_chain.invoke(voice) 
    bot.send_message(message.chat.id, report["text"])
    segments = []
    for segment in result['segments']:
        start = segment['start']  # Начало сегмента
        end = segment['end']      # Конец сегмента
        text = segment['text']    # Текст сегмента
    segments.append({'start': f"{start:.2f}", 'end': f"{end:.2f}", 'text': text})
    convert_html_to_pdf(segments)
    
@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("audio.mp3", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Файл получен и обрабатывается!")
    model = whisper.load_model("base")
    result = model.transcribe("audio.mp3")
    bot.send_message(message.chat.id, result["text"])
    audio = result["text"]

    report = llm_chain.invoke(audio) 
    bot.send_message(message.chat.id, report["text"])
    segments = []
    for segment in result['segments']:
        start = segment['start']  # Начало сегмента
        end = segment['end']      # Конец сегмента
        text = segment['text']    # Текст сегмента
    segments.append({'start': f"{start:.2f}", 'end': f"{end:.2f}", 'text': text})
    convert_html_to_pdf(segments)

    
bot.polling()
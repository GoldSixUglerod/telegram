from aiogram.dispatcher import FSMContext
from aiogram import types
from bot.loader import dp, bot
from bot.config import AUDIO_DIR
from bot.services import convert_and_get_text, send_request
import os
someone_process_audio = False


@dp.message_handler(state="*", commands=["start"])
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Привет!\nЯ помогу тебе быстро разобраться с твоей проблемой. Опиши мне ее или отправь "
                         "голосовое сообщение")


@dp.message_handler(state="*", content_types="voice")
async def get_voice(message: types.Message, state: FSMContext):
    global someone_process_audio
    await state.finish()
    if message.voice['file_id'] is None:
        await message.answer("Произошла ошибка в загрузке голосового сообщения")
        return
    if someone_process_audio:
        await message.answer("Я не могу обрабатывать несоклько сообщений единовременно. Но это можно изправить!")
        return
    someone_process_audio = True
    file_id = str(message.voice['file_id'])
    file = await bot.get_file(file_id)
    file_path = file.file_path

    ogg_path = str(AUDIO_DIR / (file_id + ".ogg"))
    await bot.download_file(file_path, ogg_path)  # Download the file
    await message.answer("Обрабатываю сообщение...")
    text = convert_and_get_text(ogg_path)
    someone_process_audio = False

    # print(f"Тут нужно отправить на api текст. \n{text}")
    api_response = send_request(text)
    await message.answer(api_response)
    os.remove(ogg_path)
    os.remove(ogg_path + ".wav")


@dp.message_handler(state="*")
async def answer_to_text(message: types.Message, state: FSMContext):
    await message.answer("типа обрабатываю сообщение")

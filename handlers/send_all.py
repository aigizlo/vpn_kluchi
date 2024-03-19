from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from keyboards.admin_buutons import *
from keyboards.keyboards import *
from user_data import get_all_users, UserData, get_users_not_trial_and_not_keys
from config import dp, bot
from states import GetuserInfo


@dp.message_handler(commands=['send_all'], state="*")
async def show_rassilka(message: types.Message):
    await message.answer('Введите текст поста:', reply_markup=ReplyKeyboardRemove())
    await GetuserInfo.text.set()


@dp.message_handler(state=GetuserInfo.text)
async def get_posttext(message: types.Message, state: FSMContext):
    textpost = message.text

    await state.update_data(textpost=textpost)
    await message.answer('Выберите то что вам нужно :', reply_markup=adminpanelmenu)
    await GetuserInfo.next_stage.set()


@dp.message_handler(state=GetuserInfo.next_stage, text='С фото 🏞')
async def get_photo(message: types.Message, state: FSMContext):
    await message.answer('Отправьте фото 🏞 :')
    await GetuserInfo.get_img.set()


@dp.message_handler(state=GetuserInfo.get_img, content_types=types.ContentType.PHOTO)
async def get_photo_id(message: types.Message, state: FSMContext):
    fileid = message.photo[0].file_id
    await state.update_data(photoid=fileid)
    await GetuserInfo.finishpost.set()
    await message.answer('✅ Данные получены, нажмите "продолжить"', reply_markup=adminpanelcontinue)


@dp.message_handler(state=GetuserInfo.next_stage, text='С клавиатурой')
async def get_video(message: types.Message, state: FSMContext):
    await message.answer("""У есть 1 клавиатура - '✅ Получить ключ' - 'get10days'""")
    await GetuserInfo.get_keyboard.set()


@dp.message_handler(state=GetuserInfo.get_keyboard)
async def get_video_id(message: types.Message, state: FSMContext):
    keyboard = presenr10()
    await state.update_data(keyboard=keyboard)
    await GetuserInfo.finishpost.set()
    await message.answer('✅ Данные получены, нажмите "продолжить"', reply_markup=adminpanelcontinue)


@dp.message_handler(state=GetuserInfo.next_stage, text='Пропустить ➡️')
@dp.message_handler(state=GetuserInfo.finishpost)
async def get_testpost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_text = data.get('textpost')
    photoid = data.get('photoid')
    keyboard = data.get('keyboard')
    user = message.from_user.id
    try:
        if photoid:
            await bot.send_photo(user, photo=photoid, caption=post_text,
                                 parse_mode='HTML', reply_markup=startposting)
        else:
            await bot.send_message(user, disable_web_page_preview=True, text=post_text, parse_mode='HTML',
                                   reply_markup=startposting)
        await GetuserInfo.publish.set()
    except Exception as e:
        await bot.send_message(user,
                               text=f'Введенный текст не правильно форматирован! Убедитесь что все теги закрыты '
                                    f'правильно.\n Начните всё заново : /send_all')
        await state.finish()
        await state.reset_data()


@dp.callback_query_handler(state=GetuserInfo.publish, text='startposting')
async def sendposts(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_text = data.get('textpost')
    photoid = data.get('photoid')
    keyboard = data.get('keyboard')
    senpostcol = 0
    user_ids = get_all_users()
    # user_ids = get_users_not_trial_and_not_keys()
    for user in user_ids:
        post_text = post_text.format_map({
        })
        try:
            if photoid:
                await bot.send_photo(user, photo=photoid, caption=post_text, reply_markup=presenr10(),
                                     parse_mode='HTML')
            # elif videoid:
            #     await bot.send_video(user, video=videoid, caption=post_text,
            #                          parse_mode='HTML')
            else:
                await bot.send_message(user, disable_web_page_preview=True, text=post_text, parse_mode='HTML', reply_markup=keyboard)
            senpostcol += 1
        except:
            pass
    await call.message.answer(f'✅ Пост успешно отправлен {senpostcol} пользователям \n',
                              reply_markup=main_menu_inline())
    await state.finish()
    await state.reset_data()


@dp.callback_query_handler(state=GetuserInfo.publish, text='cancelposting')
async def cancel_post(call: types.CallbackQuery, state: FSMContext):

    keyboard = main_menu_inline()
    await call.message.answer(f'✅ Данные удалены.\n Начните всё заново : /send_all', reply_markup=keyboard)
    await state.finish()
    await state.reset_data()





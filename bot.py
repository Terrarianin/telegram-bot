import logging
from telegram import Update, BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import sqlite3
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN", "7524215739:AAEhNumq9qtYBDBs8Fx1NYwfaub7MpkSQD0")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1755246768"))


# База данных
def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            message TEXT,
            is_admin BOOLEAN,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_message(user_id, username, first_name, message, is_admin=False):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO messages (user_id, username, first_name, message, is_admin, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, message, is_admin, timestamp))
    conn.commit()
    conn.close()

def get_conversation_history(target_user_id):
    """Получает всю переписку с пользователем без дубликатов"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, first_name, message, is_admin, timestamp 
        FROM messages 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    ''', (target_user_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return messages

def get_all_users():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT user_id, username, first_name 
        FROM messages 
        WHERE is_admin = FALSE 
        ORDER BY timestamp DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    return users

def clear_user_dialog(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def clear_all_dialogs():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM messages WHERE is_admin = FALSE')
    conn.commit()
    conn.close()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Вы владелец бота!\n\n"
            "Вам будут приходить сообщения от пользователей.\n"
            "Чтобы ответить, просто ответьте на сообщение от бота."
        )
    else:
        start_text = (
"⌗︙⸜⸜・꒰🌸꒱\n"
 "Дᴏбᴩᴏ ᴨᴏжᴀᴧᴏʙᴀᴛь ʙ «Tᴏxiᴄ Nᴏvᴀriᴀ sᴇᴄrᴇᴛs» ᴨᴏдᴇᴧиᴛᴇᴄь ᴄʙᴏиʍи ᴄᴇᴋᴩᴇᴛᴀʍи, ᴩᴀᴄᴄᴋᴀɜᴀʍи, ᴏбъяʙᴧᴇнияʍи и инɸᴏᴩʍᴀциᴇй ᴄ нᴀʍи!" 

"Мы нᴇ ᴨᴩиниʍᴀᴇʍ ᴄᴏᴏбщᴇния ᴋᴏᴛᴏᴩыᴇ нᴇ ᴏᴛнᴏᴄяᴛᴄя ʍᴏʙilᴇ lᴇgᴇnds: ʙᴀng ʙᴀng ɸᴧудᴀʍ и ᴩᴨ." 
"Мы нᴇ нᴀʍᴇᴩᴇны ᴨᴩᴇдᴏᴄᴛᴀʙᴧяᴛь ᴧичную инɸᴏᴩʍᴀцию ᴏ ʙᴀᴄ и дᴩуᴦих ᴀᴋᴋᴀунᴛᴀх. Мы ʍᴏжᴇʍ ᴧиɯь ᴨᴩᴇдᴏᴄᴛᴇᴩᴇчь, чᴛᴏ дᴀнный ᴀᴋᴋᴀунᴛ ( юɜ иᴧи ɸᴏᴛᴏ ᴨᴩᴏɸиᴧя) ʍᴏжᴇᴛ быᴛь нᴇ дᴏбᴩᴏжᴇᴧᴀᴛᴇᴧьныʍ."
"Мы нᴇ ᴛᴏᴩᴦуᴇʍ ᴀᴋᴋᴀунᴛᴀʍи, чᴇᴩᴇɜ нᴀᴄ нᴇᴧьɜя ничᴇᴦᴏ ᴨᴩᴏдᴀᴛь, ᴋуᴨиᴛь иᴧи ɜᴀᴋᴀɜᴀᴛь. "
"Вы ʍᴏжᴇᴛᴇ ᴨᴏдᴀᴛь ᴄᴏᴏбщᴇниᴇ ᴏ ᴨᴏиᴄᴋᴇ ɸᴧудᴀ, ᴩᴨ, ɸуᴧᴋи иᴧи дᴩуᴦᴀ, нᴏ ʍы нᴇ ᴦᴀᴩᴀнᴛиᴩуᴇʍ, чᴛᴏ ʙᴀʍ нᴇ нᴀᴨиɯуᴛ ʍᴏɯᴇнниᴋи, ᴨᴏжᴀᴧуйᴄᴛᴀ дᴇᴩжиᴛᴇ ϶ᴛᴏ ʙ ᴋуᴩᴄᴇ. ( дᴧя ᴨᴏиᴄᴋᴀ ʙы ʍᴏжᴇᴛᴇ ᴏᴄᴛᴀʙиᴛь ᴄʙᴏй юɜ иᴧи жᴇ ждᴀᴛь ᴋᴏᴦдᴀ ᴋᴛᴏ-ᴛᴏ ᴏᴛᴋᴧиᴋнᴇᴛᴄя ʙ ᴋᴏʍʍᴇнᴛᴀᴩиях)"
"Мы нᴇ нᴀʍᴇᴩᴇны ʙᴇᴄᴛи ᴋᴏнɸᴧиᴋᴛ ᴄ дᴩуᴦиʍи ᴋᴀнᴀᴧᴀʍи иᴧи ɸᴧудᴀʍи, ʍы ᴧиɯь инɸᴏᴩʍᴀᴛиᴩуᴇʍ ʙᴀᴄ и ᴨᴩᴇдᴏᴄᴛᴀʙᴧяᴇʍ инɸᴏʍᴀцию ᴏᴛ дᴩуᴦих ᴨᴏᴧьɜᴏʙᴀᴛᴇᴧᴇй иᴧи ʙᴧᴀдᴇᴧьцᴇʙ." 

 " ɞ       ꒦          ₊˚          ﹕"
"Вᴀɯᴇ ᴄᴏᴏбщᴇниᴇ будᴇᴛ ᴩᴀᴄᴄʍᴏᴛᴩᴇнᴏ и ᴨᴩиняᴛᴏ ʙ ᴛᴇчᴇнии 12 чᴀᴄᴏʙ. Пᴩᴏᴄиʍ ʙᴀᴄ ᴄᴏбᴧюдᴀᴛь ᴨᴩᴀʙиᴧᴀ ᴋᴀнᴀᴧᴀ и ᴨᴧᴀᴛɸᴏᴩʍы Tᴇlᴇgrᴀʍ"

"‧₊ ๑˚.・🎀"
)
        await update.message.reply_text(start_text)

# Обработка текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "нет username"
    first_name = update.effective_user.first_name or "нет имени"
    text = update.message.text

    # Если сообщение от владельца (ответ через реплай)
    if user_id == ADMIN_ID and update.message.reply_to_message:
        reply_msg = update.message.reply_to_message
        if reply_msg.from_user.id == context.bot.id:
            # Ищем ID пользователя в тексте сообщения
            if "👤 От:" in reply_msg.text:
                lines = reply_msg.text.split('\n')
                for line in lines:
                    if line.startswith("👤 От:"):
                        import re
                        id_match = re.search(r'ID:(\d+)', line)
                        if id_match:
                            target_id = int(id_match.group(1))
                            save_message(target_id, "Владелец", "Владелец", text, True)
                            
                            try:
                                await context.bot.send_message(
                                    chat_id=target_id,
                                    text=f" {text}"
                                )
                                await update.message.reply_text("✅ Ответ отправлен!")
                            except:
                                await update.message.reply_text("❌ Пользователь заблокировал бота")
                            return
        return

    # Если сообщение от обычного пользователя
    if user_id != ADMIN_ID:
        save_message(user_id, username, first_name, text)
        
        sender_info = f"👤 От: {first_name}"
        if username and username != "нет username":
            sender_info += f" (@{username})"
        sender_info += f" | ID:{user_id}"
        
        message_to_admin = (
            f"💬 Новое сообщение\n\n"
            f"{sender_info}\n\n"
            f"📝 {text}\n\n"
            f"💡 Ответьте на это сообщение чтобы ответить"
        )
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
            
            # Новое сообщение после отправки
            confirmation_text = (
               "Благодарим за сообщение! В скором времени вы сможете увидеть пост в канале. Учьтите, если вам бот ответит отказам через некоторое время, значит ваше сообщение отклонено администрацией!"

"\nС любовью Новария 💕"
            )
            await update.message.reply_text(confirmation_text)
        except:
            await update.message.reply_text("❌ Ошибка отправки")

    # Обработка ответа через кнопку "Ответить"
    elif user_id == ADMIN_ID and 'replying_to' in context.user_data:
        target_user_id = context.user_data['replying_to']
        text = update.message.text
        
        save_message(target_user_id, "Владелец", "Владелец", text, True)
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f" {text}"
            )
            await update.message.reply_text("✅ Ответ отправлен!")
            
            # Показываем обновленную историю диалога
            messages = get_conversation_history(target_user_id)
            user_info = ""
            for msg in messages:
                if not msg[4]:  # Сообщение от пользователя
                    first_name = msg[2] or "Пользователь"
                    user_info = f"💬 Диалог с {first_name}"
                    break
            
            # Создаем клавиатуру для возврата
            keyboard = [
                [InlineKeyboardButton("📋 Назад к списку", callback_data="back_to_list")],
                [InlineKeyboardButton("💬 Продолжить общение", callback_data=f"dialog_{target_user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{user_info}\n\n✅ Ваш ответ отправлен!",
                reply_markup=reply_markup
            )
            
        except:
            await update.message.reply_text("❌ Пользователь заблокировал бота")
        
        # Очищаем контекст
        del context.user_data['replying_to']

# Обработка медиа-файлов
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "нет username"
    first_name = update.effective_user.first_name or "нет имени"
    
    if user_id == ADMIN_ID:
        return
    
    media_type = "фото"
    file_id = None
    caption = update.message.caption or ""
    
    if update.message.photo:
        media_type = "фото"
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        media_type = "видео"
        file_id = update.message.video.file_id
    elif update.message.document:
        media_type = "документ"
        file_id = update.message.document.file_id
    elif update.message.audio:
        media_type = "аудио"
        file_id = update.message.audio.file_id
    
    save_message(user_id, username, first_name, f"[{media_type.upper()}] {caption}")
    
    sender_info = f"👤 От: {first_name}"
    if username and username != "нет username":
        sender_info += f" (@{username})"
    sender_info += f" | ID:{user_id}"
    
    message_to_admin = (
        f"📎 Новое {media_type}-сообщение\n\n"
        f"{sender_info}\n\n"
        f"📝 Подпись: {caption if caption else 'нет подписи'}\n\n"
        f"💡 Ответьте текстом чтобы ответить"
    )
    
    try:
        if update.message.photo:
            await context.bot.send_photo(ADMIN_ID, file_id, caption=message_to_admin)
        elif update.message.video:
            await context.bot.send_video(ADMIN_ID, file_id, caption=message_to_admin)
        elif update.message.document:
            await context.bot.send_document(ADMIN_ID, file_id, caption=message_to_admin)
        elif update.message.audio:
            await context.bot.send_audio(ADMIN_ID, file_id, caption=message_to_admin)
        
        # Новое сообщение после отправки медиа
        confirmation_text = (
            "Благодарим за сообщение! В скором времени вы сможете увидеть пост в канале, учитыте если вам бот ответит отказам через некоторое время, значит ваше сообщение отклонено администрацией!\n\n"
            "С любовью Новария 💕"
        )
        await update.message.reply_text(confirmation_text)
    except:
        await update.message.reply_text("❌ Ошибка отправки")

# Просмотр истории конкретного диалога
async def show_dialog_history(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id: int):
    messages = get_conversation_history(target_user_id)
    
    if not messages:
        await update.callback_query.edit_message_text("📭 История диалога пуста")
        return
    
    # Получаем информацию о пользователе
    user_info = ""
    user_messages = [msg for msg in messages if not msg[4]]  # Сообщения от пользователя
    if user_messages:
        first_user_msg = user_messages[0]
        user_id = first_user_msg[0]
        username = first_user_msg[1] or "нет username"
        first_name = first_user_msg[2] or "нет имени"
        
        user_info = f"👤 От: {first_name}"
        if username and username != "нет username":
            user_info += f" (@{username})"
        user_info += f" | ID:{user_id}\n\n"
    
    # Формируем историю сообщений
    history_text = f"💬 История диалога:\n\n{user_info}"
    
    for msg in messages:
        # Безопасное преобразование времени
        timestamp_str = msg[5]
        time_display = "??:??"
        
        if timestamp_str:
            try:
                if 'T' in timestamp_str:  # ISO format
                    dt = datetime.fromisoformat(timestamp_str)
                    time_display = dt.strftime('%H:%M')
                else:
                    try:
                        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                        time_display = dt.strftime('%H:%M')
                    except:
                        time_display = "??:??"
            except:
                time_display = "??:??"
        
        # Правильно определяем отправителя
        is_admin = msg[4]  # Поле is_admin (BOOLEAN)
        if is_admin:
            sender = "👑 Вы"
        else:
            sender = "👤 Пользователь"
        
        message_content = msg[3] or "[медиа-файл]"
        history_text += f"{sender} ({time_display}):\n{message_content}\n\n"
    
    # Обрезаем текст если слишком длинный
    if len(history_text) > 4000:
        history_text = history_text[:4000] + "\n\n... (история обрезана)"
    
    # Создаем клавиатуру для управления диалогом
    keyboard = [
        [InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{target_user_id}")],
        [InlineKeyboardButton("🗑️ Очистить этот диалог", callback_data=f"clear_dialog_{target_user_id}")],
        [InlineKeyboardButton("📋 Назад к списку", callback_data="back_to_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        history_text,
        reply_markup=reply_markup
    )

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    try:
        if data == "back_to_list":
            # Возвращаемся к списку диалогов
            users = get_all_users()
            
            if not users:
                await query.edit_message_text("📭 Нет активных диалогов")
                return
            
            keyboard = []
            for user_id, username, first_name in users:
                btn_text = f"{first_name}"
                if username and username != "нет username":
                    btn_text += f" (@{username})"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"dialog_{user_id}")])
            
            keyboard.append([InlineKeyboardButton("🗑️ Очистить все диалоги", callback_data="clear_all_dialogs")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📋 Выберите диалог для просмотра:",
                reply_markup=reply_markup
            )
        
        elif data.startswith("dialog_"):
            # Просмотр конкретного диалога
            target_user_id = int(data.split("_")[1])
            await show_dialog_history(update, context, target_user_id)
        
        elif data.startswith("clear_dialog_"):
            # Очистка конкретного диалога
            target_user_id = int(data.split("_")[2])
            clear_user_dialog(target_user_id)
            await query.edit_message_text("✅ Диалог очищен!")
        
        elif data == "clear_all_dialogs":
            # Очистка всех диалогов
            clear_all_dialogs()
            await query.edit_message_text("✅ Все диалоги очищены!")
        
        elif data.startswith("reply_"):
            # Подготовка к ответу
            target_user_id = int(data.split("_")[1])
            context.user_data['replying_to'] = target_user_id
            
            # Получаем информацию о пользователе
            messages = get_conversation_history(target_user_id)
            user_info = ""
            for msg in messages:
                if not msg[4]:  # Сообщение от пользователя
                    first_name = msg[2] or "Пользователь"
                    user_info = f"для {first_name}"
                    break
            
            await query.edit_message_text(
                f"💬 Введите ответ {user_info}:\n\n"
                f"Просто напишите сообщение и оно будет отправлено."
            )
    
    except ValueError as e:
        await query.edit_message_text("❌ Ошибка обработки команды")
        print(f"Ошибка обработки callback data: {data}, ошибка: {e}")
    except Exception as e:
        await query.edit_message_text("❌ Произошла ошибка")
        print(f"Неожиданная ошибка: {e}")

# Команда для просмотра диалогов с кнопками
async def dialogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Эта команда только для владельца")
        return
    
    users = get_all_users()
    
    if not users:
        await update.message.reply_text("📭 Нет активных диалогов")
        return
    
    # Создаем клавиатуру с кнопками
    keyboard = []
    for user_id, username, first_name in users:
        btn_text = f"{first_name}"
        if username and username != "нет username":
            btn_text += f" (@{username})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"dialog_{user_id}")])
    
    # Добавляем кнопку очистки всех диалогов
    keyboard.append([InlineKeyboardButton("🗑️ Очистить все диалоги", callback_data="clear_all_dialogs")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 Выберите диалог для просмотра:",
        reply_markup=reply_markup
    )

# Команда помощи
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Эта команда только для владельца")
        return
    
    help_text = (
        "👑 Команды для владельца:\n\n"
        "/start - запуск бота\n"
        "/dialogs - список активных диалогов с кнопками\n"
        "/help - справка по командам\n\n"
        "💡 Функции диалогов:\n"
        "• Просмотр истории переписки\n"
        "• Ответ через кнопку 'Ответить'\n"
        "• Очистка отдельных диалогов\n"
        "• Очистка всех диалогов\n\n"
        "Также можно отвечать на сообщения!"
    )
    
    await update.message.reply_text(help_text)

# Функция для настройки команд меню
async def set_commands(application):
    user_commands = [("start", "Запустить бота")]
    owner_commands = [
        ("start", "Запустить бота"),
        ("dialogs", "Список диалогов"),
        ("help", "Помощь по командам")
    ]
    
    try:
        await application.bot.set_my_commands(user_commands)
        await application.bot.set_my_commands(
            owner_commands,
            scope=BotCommandScopeChat(ADMIN_ID)
        )
        print("✅ Команды меню настроены успешно")
    except Exception as e:
        print(f"⚠️ Ошибка настройки команд меню: {e}")

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dialogs", dialogs))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_media))

    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # Настройка команд меню
    application.post_init = set_commands

    print("✅ Бот запущен и ожидает сообщения...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

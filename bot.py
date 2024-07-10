import emoji
from collections import Counter, defaultdict
import os
import json
import io
import emoji
from emoji import UNICODE_EMOJI
import matplotlib.pyplot as plt  # Matplotlib'ni import qo'shing
from collections import Counter
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import BotCommand
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




JSON_FILES_DIR = os.path.join("Json_files")
"""
TEPADAGI JSON_FILES_DIR GA SIZ OZ JSON FAYLLARNI SAQLASHNI HOHLAGAN FAYLINGIZ NOMINI KIRITASIZ


DIQQAT:::::::::::::::::::::::KIRITLIGAN FAYL KOD YOZILGAN FAYL YONIDA BOLISHI SHART:::::::::::::::::::::::::::

MISOL:
os.path.join("YOUR_JSON_FILE_NAME")


"""
os.makedirs(JSON_FILES_DIR, exist_ok=True)  # Create the directory if it doesn't exist
API_TOKEN = "YOUR_TOKEN"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands="help")
async def Help(message: types.Message):
    inline1=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='How To Use This Bot' ,url="https://telegra.ph/How-to-download-JSON-file-with-Telegram-chat-history-12-15-3")
            ],
            [
                InlineKeyboardButton(text="Delete This Message",callback_data="delet")
            ]

        ]
    )
    await message.answer("Bot Info", reply_markup=inline1)

@dp.callback_query_handler(text="delete")
async def delete_video(callback_query: types.CallbackQuery):
    message = callback_query.message
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)




user_data = {}

async def set_default_commands(dp):
    """
    BOT KOMANDALARINI YASAB BERADI
    :param dp:
    :return:
    """
    await dp.bot.set_my_commands(
        [
            BotCommand(command="start", description="Start interacting with the bot"),
            BotCommand(command="restart", description="Restart the bot"),
            BotCommand(command="analyze", description="Analyze a downloaded JSON file"),
            BotCommand(command="top10messages", description="Get the top 10 most frequently used words"),
            BotCommand(command="totalmessages", description="Get statistics on the time of day messages are sent"),
            BotCommand(command="top10chats", description="Top 10 active chats"),
            BotCommand(command="top10emoji", description="Top 10 used emojis"),
            BotCommand(command="topweekday", description="Top average number of messages per day of the week"),
            BotCommand(command="topmonth", description="Top average number of messages per month"),
            BotCommand(command="top10days", description="Top 10 days with the highest number of messages"),
            BotCommand(command="help", description="Get information about bot commands"),
        ]
    )

async def download_and_save_file(file_path, local_file_path):
    """
    USER JONATGAN FAYLNI YUKLAB OLADI
    :param file_path: BU ARAMETR JSON FAYLNI YUKLASH UCHUN
    :param local_file_path: BU PARAMETR ESA JSON FAYLNI TURGAN JOYI HISOB LANADI BARCHA FUNKSIYALAR SHU PARAMETRDAN FAYLLARNI TOPIB ISHLAYDI!!
    :return: PARAMETR NI BOSHQA FUNKSIYALARGA QAYTARADI
    """
    file_content = await bot.download_file(file_path)
    with open(local_file_path, 'wb') as file:
        file.write(file_content.read())
    return local_file_path
async def analyze_json_file(file_path):
    """
    JSON FAYLNI YUKALASH FUNKSIYASI
    :param file_path: FAYLNI ICHIDAGI MALUMOTLARNI OQIB DATA NOMLI OZGARUVCHIGA SAQLASH
    :return: MALUMOTLARINI QAYTARISH YOLINI QAYTARISH
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
data=analyze_json_file
async def get_top_words(messages):
    """
    JSON DATADAN SOZLARNI AJRATIB OLISH
    :param messages:
    :return:
    """
    all_words = []
    for message in messages:
        if message["type"] == "message":
            text = message.get("text", "")
            if isinstance(text, str):
                text = text.lower()
                words = text.split()
                all_words.extend(words)

    word_counter = Counter(all_words)
    top_words = word_counter.most_common(10)
    return top_words
async def get_top_emojis(messages):
    """
    JSON DATADAN EMOJILARNI AJRATIB OLISH
    :param messages:
    :return:
    """
    emoji_counter = defaultdict(int)

    for message in messages:
        text = message.get("text", "")
        if isinstance(text, str):
            # Extract emojis using emoji library
            emojis = [emoji_info["emoji"] for emoji_info in emoji.emoji_lis(text)]

            # Count occurrences of each emoji
            for emoji in emojis:
                emoji_counter[emoji] += 1

    # Convert the defaultdict to a list of dictionaries
    top_emojis = [{"emoji": emoji, "count": count} for emoji, count in emoji_counter.items()]

    # Sort emojis by count in descending order
    top_emojis.sort(key=lambda x: x["count"], reverse=True)

    return top_emojis

async def create_weekday_chart(top_weekdays):
    days = [weekday['day'] for weekday in top_weekdays]
    averages = [weekday['average'] for weekday in top_weekdays]

    plt.figure(figsize=(10, 6))
    plt.bar(days, averages, color='blue')
    plt.xlabel('Weekday')
    plt.ylabel('Average Messages')
    plt.title('Top Weekdays by Average Messages')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io

@dp.message_handler(commands=["topweekday"])
async def topweekday_command(message: types.Message):
    """
    AGAR /topweekday KOMANDASI BERILSA SHU ASYNC FUNKTION ISHGA TUSHADI VA AGAR FAYL YUBOTILGAN BOLSA VA DASTUR UNI
    DATA OZGARUVCHISIGA SAQLAGAN BOLSA BU FUNKSIYA ISHGA TUSHIB SOG DATADAN OLINGAN MATN VA SOZLARNI TAXLIL QILADI
    VA USERGA DIOGRAMMA BILAN BIRGA YUBORAD BOSHQA FUNKSIYALARHAM SHUNDAY
    :param message: USER YUBORGA XABARNI TEKSHIRADI
    :return:
    """
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)

    await message.answer("Processing the 'topweekday' command...")
    top_weekdays = await get_top_weekdays(data["messages"])

    chart_bytes_io = await create_weekday_chart(top_weekdays)

    response_message = "Top Weekdays:\n"
    for idx, weekday_info in enumerate(top_weekdays, start=1):
        response_message += f"{idx}. {weekday_info['day']} - Average Messages: {weekday_info['average']:.2f}\n"

    await message.reply(response_message)
    await message.answer_photo(types.InputFile(chart_bytes_io, filename="chart.png"))


async def get_top_months(messages):
    month_count = defaultdict(int)
    month_total_messages = defaultdict(int)

    for message in messages:
        date_str = message.get("date", "")
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            month = date.strftime("%B %Y")
            month_count[month] += 1
            month_total_messages[month] += 1

    top_months = []
    for month, count in month_count.items():
        average_messages = month_total_messages[month] / count
        top_months.append({"month": month, "average": average_messages})

    sorted_top_months = sorted(top_months, key=lambda x: x["average"], reverse=True)

    return sorted_top_months


async def create_month_chart(top_months):
    months = [month_info['month'] for month_info in top_months]
    averages = [month_info['average'] for month_info in top_months]

    plt.figure(figsize=(10, 6))
    plt.bar(months, averages, color='blue')
    plt.xlabel('Month')
    plt.ylabel('Average Messages')
    plt.title('Top Months by Average Messages')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io

@dp.message_handler(commands=["topmonth"])
async def topmonth_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'topmonth' command...")

    # Assuming data['messages'] contains messages with a 'date' field
    top_months = await get_top_months(data['messages'])

    response_message = "Top Months with the Most Messages:\n\n"
    for month_info in top_months:
        response_message += f"{month_info['month']} - Average Messages: {month_info['average']:.2f}\n"

    await message.reply(response_message)

    chart_bytes_io = await create_month_chart(top_months)
    await message.reply_photo(types.InputFile(chart_bytes_io, filename="chart.png"))


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def handle_document(message: types.Message):
    file_info = await bot.get_file(message.document.file_id)
    file_path = file_info.file_path
    file_name = file_path.split('/')[-1]
    local_file_path = os.path.join(JSON_FILES_DIR, file_name)

    await message.reply("Downloading your file...")
    local_file_path = await download_and_save_file(file_path, local_file_path)

    user_data[message.from_user.id] = local_file_path

    await message.reply(f"File saved as. You can now use other commands for analysis.")

async def create_word_chart(top_words):
    words = [word for word, count in top_words]
    counts = [count for word, count in top_words]

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='blue')
    plt.xlabel('Word')
    plt.ylabel('Count')
    plt.title('Top 10 Most Frequently Used Words')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io

@dp.message_handler(commands=["top10messages"])
async def top10messages_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return
    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'top10messages' command...")
    top_words = await get_top_words(data['messages'])
    response_message = "Top 10 most frequently used words:\n\n"
    for word, count in top_words:
        response_message += f"{word}: {count}\n"

    await message.reply(response_message)

    chart_bytes_io = await create_word_chart(top_words)
    await message.reply_photo(types.InputFile(chart_bytes_io, filename="word_chart.png"))

@dp.message_handler(commands=["start", "restart"])
async def start(messages: types.Message):
    await messages.answer(f"Hello{messages.from_user.first_name}! you are greeted by the Telegram History Analyzer Bot!🤖📊Get access to fascinating information about your conversations.💬✨")

@dp.message_handler(commands=["top10days"])
async def top10days_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'top10days' command...")

    # Assuming data['messages'] contains messages with a 'date' field
    top_days = await get_top_days(data['messages'])

    response_message = "Top 10 days with the most messages:\n\n"
    for day, count in top_days:
        response_message += f"{day}: {count} messages\n"

    await message.reply(response_message)

    chart_bytes_io = await create_top_days_chart(top_days)
    await message.reply_photo(types.InputFile(chart_bytes_io, filename="top_days_chart.png"))





async def perform_analysis(messages):
    total_messages = len(messages)
    return f"Total Messages: {total_messages}"

async def create_message_statistics_chart(messages, file_path):
    total_messages = len(messages)

    # Count messages for each hour of the day
    hour_counts = [0] * 24
    for message in messages:
        date_str = message.get("date", "")
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            hour = date.hour
            hour_counts[hour] += 1

    # Create a bar chart
    hours = [str(hour) for hour in range(24)]
    plt.figure(figsize=(10, 6))
    plt.bar(hours, hour_counts, color='blue')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Message Count')
    plt.title('Messages by Hour of the Day')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart to the specified file path
    plt.savefig(file_path)
    plt.close()

async def calculate_message_statistics(messages):
    total_messages = len(messages)
    # Calculate other statistics as needed

    return total_messages

@dp.message_handler(commands=["totalmessages"])
async def totalmessages_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]

    try:
        data = await analyze_json_file(local_file_path)
        if 'messages' in data:
            await message.reply("Processing the 'totalmessages' command...")
            statistics_result = await calculate_message_statistics(data['messages'])
            await message.reply(f"Total number of messages: {statistics_result}")

            # Create and send the message statistics chart
            chart_file_path = f"message_statistics_chart_{user_id}.png"
            await create_message_statistics_chart(data['messages'], chart_file_path)
            with open(chart_file_path, 'rb') as chart_file:
                await bot.send_photo(chat_id=message.chat.id, photo=chart_file)

            # Remove the temporary chart file
            os.remove(chart_file_path)
        else:
            await message.reply("Invalid data format. 'messages' key not found.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

async def calculate_message_statistics(messages):
    total_messages = len(messages)
    return f"Total Messages: {total_messages}, Other statistics..."

async def get_top_chats(messages):
    chat_count = defaultdict(int)

    for message in messages:
        chat_name = message.get("name", "")
        if chat_name:
            chat_count[chat_name] += 1

    sorted_chats = sorted(chat_count.items(), key=lambda x: x[1], reverse=True)

    top_chats = [{"name": chat_info[0], "message_count": chat_info[1]} for chat_info in sorted_chats]

    return top_chats



async def create_chat_chart(top_chats):
    chat_names = [chat['name'] for chat in top_chats[:10]]
    message_counts = [chat['message_count'] for chat in top_chats[:10]]

    plt.figure(figsize=(10, 6))
    plt.bar(chat_names, message_counts, color='blue')
    plt.xlabel('Chat')
    plt.ylabel('Message Count')
    plt.title('Top 10 Chats by Message Count')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io


@dp.message_handler(commands=["top10chats"])
async def top10chats_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Please upload a JSON file first using the /start command.")
        return
    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)

    await message.reply("Processing the 'top10chats' command...")
    top_chats = await get_top_chats(data["messages"])
    response_message = "Top 10 Chats:\n"
    for idx, chat in enumerate(top_chats[:10], start=1):
        response_message += f"{idx}. {chat['name']} - Messages: {chat['message_count']}\n"

    await message.reply(response_message)

    chart_bytes_io = await create_chat_chart(top_chats)
    await message.reply_photo(types.InputFile(chart_bytes_io, filename="chat_chart.png"))


async def get_top_emojis(messages):
    emoji_counter = defaultdict(int)

    for message in messages:
        text = message.get("text", "")
        if isinstance(text, str):
            # Extract emojis using emoji library
            emojis_list = [emoji_info["emoji"] for emoji_info in emoji.emoji_lis(text)]

            # Count occurrences of each emoji
            for emoji_char in emojis_list:
                emoji_counter[emoji_char] += 1

    # Convert the defaultdict to a list of dictionaries
    top_emojis = [{"emoji": emoji_char, "count": count} for emoji_char, count in emoji_counter.items()]

    # Sort emojis by count in descending order
    top_emojis.sort(key=lambda x: x["count"], reverse=True)

    return top_emojis


async def create_emoji_chart(top_emojis):
    emojis = [emoji_info['emoji'] for emoji_info in top_emojis[:10]]
    counts = [emoji_info['count'] for emoji_info in top_emojis[:10]]

    plt.figure(figsize=(10, 6))
    plt.bar(emojis, counts, color='blue')
    plt.xlabel('Emoji')
    plt.ylabel('Count')
    plt.title('Top 10 Used Emojis')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io

@dp.message_handler(commands=["top10emoji"])
async def top10emoji_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'top10emoji' command...")

    # Assuming data['messages'] contains messages with a 'text' field
    top_emojis = await get_top_emojis(data['messages'])

    response_message = "Top 10 Emojis:\n"
    for idx, emoji_info in enumerate(top_emojis[:10], start=1):
        response_message += f"{idx}. {emoji_info['emoji']} - Count: {emoji_info['count']}\n"

    await message.reply(response_message)

    chart_bytes_io = await create_emoji_chart(top_emojis)
    await message.reply_photo(types.InputFile(chart_bytes_io, filename="emoji_chart.png"))




async def get_top_weekdays(messages):
    weekdays_count = defaultdict(int)
    weekdays_total_messages = defaultdict(int)

    for message in messages:
        date_str = message.get("date", "")
        if date_str:
            # Updated date format parsing
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

            # Rest of your implementation remains the same
            weekday = date.strftime("%A")
            weekdays_count[weekday] += 1
            weekdays_total_messages[weekday] += 1

    # Calculate average messages per weekday
    top_weekdays = [{"day": day, "average": total / weekdays_count[day]} for day, total in weekdays_total_messages.items()]

    # Sort weekdays by average in descending order
    top_weekdays.sort(key=lambda x: x["average"], reverse=True)

    return top_weekdays

async def topweekday_command(message: types.Message):
    await message.answer("Processing the 'topweekday' command...")
    top_weekdays = await get_top_weekdays(data["messages"])

    response_message = "Top Weekdays:\n"
    for idx, weekday_info in enumerate(top_weekdays, start=1):
        response_message += f"{idx}. {weekday_info['day']} - Average Messages: {weekday_info['average']:.2f}\n"

    await message.reply(response_message)


@dp.message_handler(commands=["topmonth"])
async def topmonth_command(message: types.Message):
    await message.answer("Processing the 'topmonth' command...")
    top_months = await get_top_months(data["messages"])

    response_message = "Top Months:\n"
    for idx, month_info in enumerate(top_months, start=1):
        response_message += f"{idx}. {month_info['month']} - Average Messages: {month_info['average']:.2f}\n"

    await message.answer(response_message)

async def get_top_days(messages):
    day_count = defaultdict(int)

    for message in messages:
        date = message.get("date", "")
        if date:
            # Assuming date is already a string in the format "%Y-%m-%d"
            day_count[date] += 1

    sorted_days = sorted(day_count.items(), key=lambda x: x[1], reverse=True)
    top_days = sorted_days[:10]  # Take the top 10 days

    return top_days

@dp.message_handler(commands=["top10days"])
async def top10days_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'top10days' command...")

    # Assuming data['messages'] contains messages with a 'date' field
    top_days = await get_top_days(data['messages'])

    response_message = "Top 10 days with the most messages:\n\n"
    for day, count in top_days:
        response_message += f"{day}: {count} messages\n"

    await message.reply(response_message)


async def make_t_10_msg_chart(top_days, file_path):
    days, counts = zip(*top_days)
    plt.figure(figsize=(10, 6))
    plt.bar(days, counts, color='blue')
    plt.xlabel('Days')
    plt.ylabel('Message Count')
    plt.title('Top 10 Days with Most Messages')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

async def send_chart_to_user(message, top_days):
    user_id = message.from_user.id
    file_path = f"top10days_chart_{user_id}.png"

    await make_t_10_msg_chart(top_days, file_path)

    with open(file_path, 'rb') as chart_file:
        await bot.send_photo(chat_id=message.chat.id, photo=chart_file)

    os.remove(file_path)

# Bu funksiya top10days buyrug'ini bajaradi

async def create_top_days_chart(top_days):
    days, counts = zip(*top_days)
    plt.figure(figsize=(10, 6))
    plt.bar(days, counts, color='blue')
    plt.xlabel('Days')
    plt.ylabel('Message Count')
    plt.title('Top 10 Days with Most Messages')
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_bytes_io = io.BytesIO()
    plt.savefig(chart_bytes_io, format='png')
    chart_bytes_io.seek(0)  # Fayl o'qish uchun kursor boshiga qaytarish
    plt.close()
    return chart_bytes_io





from aiogram.types import ParseMode
@dp.message_handler(commands=["analyze"])
async def analyze_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply("Please upload a JSON file first using the /start command.")
        return

    local_file_path = user_data[user_id]
    data = await analyze_json_file(local_file_path)
    await message.reply("Processing the 'analyze' command...")
    analysis_result = await perform_analysis(data["messages"])
    await message.answer(f"Analysis Result:\n{analysis_result}", parse_mode=ParseMode.MARKDOWN)

def format_top_words(top_words):
    # Format the top words for display
    formatted_words = [f"{word}: {count}" for word, count in top_words]
    return "\n".join(formatted_words)
async def perform_analysis(messages):
    total_messages = len(messages)
    top_words = await get_top_words(messages)

    analysis_result = (
        f"Total Messages: {total_messages}\n"
        f"Top Words:\n{format_top_words(top_words)}"
    )
    return analysis_result

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=set_default_commands)
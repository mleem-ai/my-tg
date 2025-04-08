import telebot
import os
from dotenv import load_dotenv

# Load configuration
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_CHAT_ID')

# Validate configuration
if not TOKEN:
    raise ValueError("Telegram bot token not found in environment variables")
if not ADMIN_ID:
    raise ValueError("Admin chat ID not found in environment variables")

# Create bot instance
bot = telebot.TeleBot(TOKEN)

# Bot texts
TEXTS = {
    "welcome": """Hello! You're in the Engine of Progress Application Bot.

Before we begin, you need to answer five questions in one message:

1. "What do you do and what do you think of your business?" (if it is)
2. "What are you looking for here and what is your question?"
3. "In which direction you want to work/improve your skills/achieve anything :)"
4. "What life are you in?" (this is what you would call it)
5. "Your name is?"

Please reply with one message containing all answers, numbering each response.""",
    "response": """Thank you! I've forwarded your answers to the manager. They will contact you soon.
(Please don't forget to adjust your privacy settings to allow anyone to send you messages!)""",
    "error": "⚠️ Error processing your request",
    "invalid_format": "Please send your answers in the correct format:\n\n1. Your answer to question 1\n2. Your answer to question 2\n3. Your answer to question 3\n4. Your answer to question 4\n5. Your answer to question 5",
    "received_application": "📝 New Application Received:\n\nUser ID: {user_id}\nUsername: @{username}\nName: {full_name}\n\nAnswers:\n{answers}"
}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, TEXTS["welcome"])
    bot.register_next_step_handler(message, process_answers)

# Process user answers
def process_answers(message):
    try:
        # Validate the message contains all 5 answers
        if not all(f"{i}." in message.text for i in range(1, 6)):
            bot.send_message(message.chat.id, TEXTS["invalid_format"])
            bot.register_next_step_handler(message, process_answers)
            return

        # Prepare user info
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else "no_username"
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()

        # Format the message for admin
        admin_message = TEXTS["received_application"].format(
            user_id=user_id,
            username=username,
            full_name=full_name,
            answers=message.text
        )

        # Send to admin
        bot.send_message(ADMIN_ID, admin_message)
        
        # Send confirmation to user with the new note
        bot.send_message(message.chat.id, TEXTS["response"])

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, TEXTS["error"])

# Start the bot
if __name__ == '__main__':
    print("Bot is running...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot crashed with error: {e}")
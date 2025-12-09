import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import json
import os # An sanya os domin amfani da wajen duba environment

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# File to store user data persistently
USER_DATA_FILE = "user_data.json"

# KA SAKA AINIHIN BOT TOKEN DINKA A NAN
# Lura: Bot Token dinka shine 8487752681:AAEe3mDTnioLmK9dWfsG2HaRxUXCsa2c8H4
API_TOKEN = 'Your_bot_token'

# Load user data
def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        else:
            return {}
    except json.JSONDecodeError:
        logger.error("Error reading JSON from user_data.json. Starting with empty data.")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading data: {e}")
        return {}

# Save user data
def save_user_data(data):
    try:
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")


# Start command handler
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user.first_name}! Welcome to the WhatsApp checker bot. Use /check <phone_number> to get started! (Note: The check is simulated)."
    )

# Check number handler
async def check_number(update: Update, context: CallbackContext):
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text("Please provide a phone number! Use the format: /check <phone_number>")
        return

    number = context.args[0].strip() # Cire fararen wurare
    await update.message.reply_text(f"Checking number {number}...")

    # Kiran function din duba namba
    result = check_whatsapp_number(number)
    
    # Update user data
    user_data = load_user_data()
    user_data[str(user.id)] = {"last_checked_number": number, "result": result}
    save_user_data(user_data)

    await update.message.reply_text(result)

# Function to check WhatsApp number (SIMULATED CHECK)
def check_whatsapp_number(number):
    # An cire Pywhatkit saboda baya aiki a Termux.
    # Wannan hanya tana duba ko lambar wayar ta bi ka'ida ne kawai (misali, tsawonta ya kai 10)
    
    if number.startswith('+'):
        # Cire alamar + domin dubawa mafi sauki
        cleaned_number = number.replace('+', '').strip()
    else:
        cleaned_number = number.strip()

    if cleaned_number.isdigit() and len(cleaned_number) >= 10:
        # Idan lambar tana da tsayi kuma duk lambobi ne
        return f"✅ Number {number} format looks valid (Simulated Check)."
    else:
        return f"❌ Number {number} does not look like a valid phone number."


# Inline keyboard handler
async def inline_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Check Another Number", callback_data='check_another')],
        [InlineKeyboardButton("View Last Checked Number", callback_data='view_last_checked')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose an option:', reply_markup=reply_markup)

# Handle button callback
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer() # Cire ikon loading

    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    if user_id in user_data and "last_checked_number" in user_data[user_id]:
        last_number = user_data[user_id]["last_checked_number"]
        result = user_data[user_id]["result"]
        await query.edit_message_text(f"Last checked number: {last_number}\nResult: {result}")
    else:
        await query.edit_message_text("You haven't checked any number yet.")

# Command handler to show the help message
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("""
    Here are the available commands:
    /start - Start the bot
    /check <phone_number> - Check a phone number (Simulated)
    /help - Get help about the bot
    """)

# Error handling function
async def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

# Main function to set up the Telegram bot
def main():
    # Create Application instance
    application = Application.builder().token(API_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('check', check_number))
    application.add_handler(CommandHandler('help', help_command))

    # Register inline button handler
    application.add_handler(CallbackQueryHandler(button_handler))

    # Register message handler for inline buttons (filters.TEXT & ~filters.COMMAND)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, inline_buttons))

    # Set up error logging
    application.add_error_handler(error)

    # Start the bot
    print("Bot is starting...")
    # run_polling() yana gudana ne kawai kuma baya bukatar asyncio.run() a waje
    application.run_polling()

# Run the bot
if __name__ == '__main__':
    main()

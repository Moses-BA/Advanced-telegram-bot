import json
import telebot
import re
from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, Updater
import requests

class ExtBot(telegram.Bot):
    def set_context(self, **kwargs):
        """Sets the context for the current update."""
        self._context[kwargs['key']] = kwargs['value']
    def get_context(self, update):
        return self._context.get(update.effective_chat.id, {})



TOKEN: Final = '5653667475:AAFPeNKcdQS_BsyoxJHt7DpLwY9x_OsOQpI'
BOT_USERNAME : Final = '@crypto_fatherbot'
MY_PR : Final = 0.00055

bot = ExtBot(TOKEN)

# Create an instance of the Updater class


def get_coin_price(symbol: str) -> float:
    """Gets the price of a coin from CryptoCompare."""
    url = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms=USD'.format(symbol) 
    response = requests.get(url)
    response_json = response.json()
    if 'USD' in response_json and response_json['USD']:
        if symbol == 'BTC':
            return float(response_json['USD']) 
        elif symbol == 'ETH':
            return float(response_json['USD']) 
        else:
            return float(response_json['USD'])
    else:
        return None

#COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!, Welcome to Crypto Father!😊\nUse /prices to get cryptocurrency prices and /rates to view broker rates.'
                                    '\nTo access the full list of commands, click on Menu')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is a list of all available commands.\n\nstart - Starts the bot and shows the user the main menu.'
                                    '\nhelp - Shows the user a list of all the available commands.'
                                    '\ncurrencies - Lists all the available crypto currencies that the bot can sell.'
                                    '\nprices - Get cryptocurrency prices.'
                                    '\nrates -  Views broker rates.'
                                    '\nBuy <currency> <amount> - Buys the specified amount of the specified currency.'
                                    '\nbalance - Shows the user current balance.'
                                    '\nhistory - Shows the user their transaction history.'
                                    '\ncontact support - Opens a chat with the bot support team.')

async def listCurrencies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('We sell:\nBitcoin(BTC)\nEtheruem(ETH)\nTether(USDT)\nBinance coin(BNB)\nLitecoin(LTC)\nPolygon(MATIC)')

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bitcoin_price = get_coin_price('BTC')
    ethereum_price = get_coin_price('ETH')
    litecoin_price = get_coin_price('LTC')
    bnb_price = get_coin_price('BNB')
    matic_price = get_coin_price('MATIC')
    usdt_price = get_coin_price('USDT')
    

    response = f'BTC (0.01): ${bitcoin_price * 0.01}\n\n'
    response += f'ETH (0.1): ${ethereum_price * 0.1}\n\n'
    response += f'LTC: ${litecoin_price}\n\n'
    response += f'BNB: ${bnb_price}\n\n'
    response += f'MATIC: ${matic_price}\n\n'
    response += f'USDT: ${usdt_price}\n\n'

    await update.message.reply_text(response)

async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bitcoin_price = get_coin_price('BTC')
    ethereum_price = get_coin_price('ETH')
    litecoin_price = get_coin_price('LTC')
    bnb_price = get_coin_price('BNB')
    matic_price = get_coin_price('MATIC')
    usdt_price = get_coin_price('USDT')


    response = f'BTC (0.01): ${(bitcoin_price * 0.01) + MY_PR}\n\n'
    response += f'ETH (0.1): ${(ethereum_price * 0.1) + MY_PR}\n\n'
    response += f'LTC: ${litecoin_price + MY_PR}\n\n'
    response += f'BNB: ${bnb_price + MY_PR}\n\n'
    response += f'MATIC: ${matic_price + MY_PR}\n\n'
    response += f'USDT: ${usdt_price + MY_PR}\n\n'

    await update.message.reply_text(response) 

# Define the spinner control.
class SpinnerControl:
  def __init__(self, min_value, max_value, step_size):
    self.min_value = min_value
    self.max_value = max_value
    self.step_size = step_size

# Define the bot.
bot = telebot.TeleBot(TOKEN)

# Define the command handler.

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 

    # Create a list of buttons.
    buy_buttons = [
        [InlineKeyboardButton('BTC', callback_data='BTC')],
        [InlineKeyboardButton('ETH', callback_data='ETH')],
        [InlineKeyboardButton('USDT', callback_data='USDT')],
        [InlineKeyboardButton('BNB', callback_data='BNB')],
        [InlineKeyboardButton('LTC', callback_data='LTC')],
        [InlineKeyboardButton('MATIC', callback_data='MATIC')]
    ]

    # Create an InlineKeyboardMarkup object with the list of buttons.
    reply_markup = InlineKeyboardMarkup(buy_buttons)

    # Send the message with the reply keyboard.
    await update.message.reply_text('What cryptocurrency do you want to buy?', reply_markup=reply_markup)

# Define the callback handler for the button click.
@bot.callback_query_handler(func=lambda query: query.data in ['BTC', 'ETH', 'USDT', 'BNB', 'LTC', 'MATIC'])
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, rates={}):
    query = update.callback_query
    user_choice = query.data
    rates = get_coin_price(user_choice) + MY_PR

    # Prompt the telegram bot to reply with the user's choice.
    await query.message.reply_text(f'You chose {user_choice} at {rates} USD')

    # Create a spinner control for the amount input.
    amount_spinner = SpinnerControl(min_value=0, max_value=100000, step_size=0.01)

    # Serialize the spinner control to JSON.
    spinner_control_json = json.dumps(amount_spinner, default=lambda obj: obj.__dict__)

    # Send a message with the spinner control.
    await query.message.reply_text(f'How much {user_choice} do you want to buy?', reply_markup=spinner_control_json) 


# Define the message handler for the amount input.
@bot.message_handler(func=lambda message: re.match(r'^\d+\.?\d{0,5}$', message.text))
async def amount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, rates, user_choice):
    user_data = context.user_data
    amount = float(update.message.text)

    # Calculate the total amount to be paid.
    total_amount = rates * amount

    # Send a confirmation message to the user.
    await update.message.reply_text(f'Your payment for {amount} {user_choice} has been successful.')




def get_current_naira_to_dollar_rate() -> float:
    """Gets the current Naira to Dollar rate."""
    url = 'https://api.exchangeratesapi.io/latest?base=NGN'
    response = requests.get(url)
    response_json = response.json()
    return response_json['rates']['USD']

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('After each transaction, a receipt and mail was sent to the mail address you provided on paystack, please kindly log into your mail to view past transactions.'
                                    '\nThis is done for security purposes. Thank you for your continuous patronage in our bot😊')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send a mail to moseeb57@gmail.com and our customer care agent will reply you at the soonest!😊, we apologise for any inconveniences')

#RESPONSES
def handle_response(text: str):
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there! send a /start command'
    
    if 'hey' in processed:
        return 'Hi there! send a /start command'
    
    if 'how do i use this bot' in processed:
        return 'press the /help command'
    
    if 'hi' in processed:
        return 'Hello! send a /start command'
    
    if 'help' in processed:
        return 'This bot can help you buy crypto currencies. To get started, send a /start command.'
    
    if 'start' in processed:
        return 'Welcome to the crypto currency bot! What can I help you with today?'
    
    return 'I do not understand what you wrote, please press the /start command.'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id})) in {message_type}: "{text}"')

    if message_type == '<ChatType.SUPERGROUP>':
        if re.search(BOT_USERNAME.lower(), text.lower()):
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return 
    else: 
        new_text: str = text
        response: str = handle_response(new_text)
    
    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot....')
    app = Application.builder().token(TOKEN).build()

    #COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('currencies', listCurrencies_command))
    app.add_handler(CommandHandler('prices', prices_command))
    app.add_handler(CommandHandler('rates', rates_command))
    app.add_handler(CommandHandler('buy', buy_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CallbackQueryHandler(amount_callback))
    app.add_handler(CommandHandler('history', history_command))
    app.add_handler(CommandHandler('contact', contact_command))

    #MESSAGES
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #ERRORS
    app.add_error_handler(error)

    #POLLS THE BOT
    print('Polling.....')
    app.run_polling(poll_interval=3)



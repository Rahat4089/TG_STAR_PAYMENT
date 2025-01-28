import asyncio
import random
import string
import time
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, PreCheckoutQuery, Message, LabeledPrice
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode

# Replace these with your actual values
API_ID = 24720817  # Replace with your API ID
API_HASH = "43669876f7dbd754e157c69c89ebf3eb"  # Replace with your API hash
BOT_TOKEN = "7927514116:AAEJU5UoE4rMFTWj8pA8V7ENVogU91wWRCY"  # Replace with your bot token



# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram Bot Client
bot = Client(
    "donation_bot",  # Session name
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# Command: /donate
@bot.on_message(filters.command("donate") & filters.private)
async def on_donate_handler(client, message: Message):
    await proceed_with_donation(client, message)
      

async def proceed_with_donation(client, message: Message):
    chat_id = message.chat.id
    command = message.text.split()

    if len(command) == 1:
        # Donation options
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("1⭐", callback_data="donate_1"), InlineKeyboardButton("10⭐", callback_data="donate_10")],
                [InlineKeyboardButton("50⭐", callback_data="donate_50"), InlineKeyboardButton("100⭐", callback_data="donate_100")],
                [InlineKeyboardButton("500⭐", callback_data="donate_500"), InlineKeyboardButton("1000⭐", callback_data="donate_1000")]
            ]
        )
        await message.reply("Choose your donation amount:", reply_markup=reply_markup)
    elif len(command) == 2 and command[1].isdigit():
        amount = int(command[1])
        await send_invoice(client, chat_id, amount)
    else:
        await message.reply("Usage: /donate or /donate <amount>")


# Function to Send Invoice
async def send_invoice(client, chat_id, amount):
    dollar_amount = amount * 0.02  # 1⭐ = $0.02
    await client.send_invoice(
        chat_id=chat_id,
        title="Donation",
        description=f"Support our bot with your donation of {amount}⭐! ~${dollar_amount:.2f}",
        payload="donation_payload",
        currency="XTR",  # Use a valid currency code
        prices=[LabeledPrice(label=f"{amount}⭐ Donation", amount=amount)],
        start_parameter="donation"
    )


# Callback Query for Donation Buttons
@bot.on_callback_query(filters.regex(r"^donate_(\d+)$"))
async def on_donate_callback(client, callback_query):
    amount = int(callback_query.data.split("_")[1])
    await send_invoice(client, callback_query.message.chat.id, amount)
    await callback_query.answer("Processing your donation...")


# Pre-checkout Query Handler
@bot.on_pre_checkout_query()
async def process_pre_checkout_query(client, pre_checkout_query: PreCheckoutQuery):
    try:
        # Accept the pre-checkout query
        await client.answer_pre_checkout_query(
            pre_checkout_query.id,
            success=True
        )
    except Exception as e:
        # Reject the pre-checkout query with an error message
        await client.answer_pre_checkout_query(
            pre_checkout_query.id,
            success=False,
            error_message=str(e)
        )


# Successful payment handler
@bot.on_message(filters.successful_payment)
async def process_successful_payment(client, message: Message):
    payment_info = message.successful_payment
    stars = payment_info.total_amount
    currency = payment_info.currency
    transaction_id = payment_info.telegram_payment_charge_id

    # Get the sender's information
    sender_name = message.from_user.first_name
    sender_username = message.from_user.username
    sender_id = message.from_user.id

    # Generate a profile link
    profile_link = f"tg://user?id={sender_id}"

    # Format the date directly
    payment_date = message.date.strftime('%Y-%m-%d %H:%M:%S UTC')

    # Reply to the user
    await message.reply(
        f"🎉 Payment successful!\n"
        f"💲 Amount: {stars}⭐\n"
        f"💵 Currency: {currency}\n"
        f"🆔 Transaction ID: `{transaction_id}`\n"
        f"📅 Payment Date: {payment_date}\n"
        f"👤 Sender: [{sender_name}]({profile_link})",
        parse_mode=ParseMode.MARKDOWN
    )
@bot.on_message(filters.command("refund"))
async def refund_handler(client, message):
    command = message.text.split()

    if len(command) != 2:
        await message.reply(f"Usage: /refund <code>Transaction ID</code>")
        return

    telegram_payment_charge_id = command[1]
    user_id = message.from_user.id
    
    try:
        # Refund using the provided API
        await client.refund_star_payment(user_id, telegram_payment_charge_id)  # Adjust this based on your payment provider
        await message.reply(
            f"<blockquote><b>✅ Refund processed successfully for Transaction ID:</b></blockquote> \n`{telegram_payment_charge_id}`"
        )
    except Exception as e:
        await message.reply(
            f"<blockquote><b>❌ Refund failed:\n`{str(e)}`</b></blockquote>" # Use lowercase "markdown"
        )
        

# Run the bot
if __name__ == '__main__':
    bot.run()

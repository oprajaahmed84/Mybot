import json
import os

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN ="8661427080:AAFBY57EkCY9RkDvTKTuEKjXQOmpyuXG0QM"
ADMIN_ID = 6329123860

DB_FILE = "orders.json"

keyboard = [
    ["🛒 Diamond Price"],
    ["📝 Order Now"],
    ["💳 Payment"],
    ["📞 Contact Admin"],
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True,
)


def load_orders():
    if not os.path.exists(DB_FILE):
        return {}

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_orders(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Welcome to TopUp BD\n\n"
        "একটি অপশন নির্বাচন করুন।",
        reply_markup=reply_markup,
    )
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛒 Diamond Price":
        await update.message.reply_text(
            "👑 VIP DIAMOND SHOP 👑\n\n"
            "💎 25 ➜ ৳25\n"
            "💎 50 ➜ ৳40\n"
            "💎 115 ➜ ৳80\n"
            "💎 240 ➜ ৳160\n"
            "💎 355 ➜ ৳240\n"
            "💎 610 ➜ ৳390\n"
            "💎 1240 ➜ ৳770\n\n"
            "⭐ Weekly Lite ➜ ৳25\n"
            "⭐ Weekly ➜ ৳160\n"
            "⭐ Monthly ➜ ৳780\n"
            "⭐ Level Up Pass ➜ ৳105"
        )

    elif text == "📝 Order Now":
        await update.message.reply_text(
            "অর্ডার এই ফরম্যাটে পাঠান:\n\n"
            "UID: 123456789\n"
            "Diamond: 240"
        )

    elif text == "💳 Payment":
        await update.message.reply_text(
            "💳 PAYMENT\n\n"
            "🟣 bKash: 01893121330\n"
            "🔵 Nagad: 01893121330\n\n"
            "Payment করার পরে UID, Diamond, Transaction ID এবং Screenshot পাঠান।"
        )

    elif text == "📞 Contact Admin":
        await update.message.reply_text(
            "👨‍💼 Admin: @Munnavainet"
        )

    elif "UID:" in text and "Diamond:" in text:
        user = update.effective_user
        uid = text.split("UID:")[1].split("\n")[0].strip()

        orders = load_orders()
        order_id = f"#{1000 + len(orders) + 1}"

        orders[uid] = {
            "chat_id": user.id,
            "order_id": order_id
        }
        save_orders(orders)

        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"done:{uid}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel:{uid}")
            ]
        ]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📦 NEW ORDER\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"👤 {user.full_name}\n\n"
                f"{text}"
            ),
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )

        await update.message.reply_text(
            f"✅ আপনার অর্ডার গ্রহণ করা হয়েছে।\n\n"
            f"🆔 Order ID: {order_id}\n"
            "📋 Status: Pending ⏳"
        )
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=(
            "💳 PAYMENT SCREENSHOT\n\n"
            f"👤 {user.full_name}\n"
            f"🆔 User ID: {user.id}"
        )
    )

    await update.message.reply_text(
        "✅ Payment Screenshot গ্রহণ করা হয়েছে।"
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, uid = query.data.split(":")

    orders = load_orders()

    if uid not in orders:
        await query.edit_message_text("❌ Order পাওয়া যায়নি।")
        return

    order = orders[uid]
    chat_id = order["chat_id"]
    order_id = order["order_id"]

    if action == "done":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"🎉 আপনার অর্ডার সম্পন্ন হয়েছে!\n\n"
                f"🆔 Order ID: {order_id}\n"
                "✅ Diamond সফলভাবে আপনার অ্যাকাউন্টে পাঠানো হয়েছে।"
            )
        )

        await query.edit_message_text(
            f"✅ APPROVED\n🆔 {order_id}"
        )

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"❌ আপনার অর্ডার বাতিল করা হয়েছে।"
            )
        )

        await query.edit_message_text(
            f"❌ CANCELLED\n🆔 {order_id}"
        )

    del orders[uid]
    save_orders(orders)
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text("ব্যবহার: /done UID")
        return

    uid = context.args[0]
    orders = load_orders()

    if uid not in orders:
        await update.message.reply_text("❌ UID পাওয়া যায়নি।")
        return

    order = orders[uid]
    chat_id = order["chat_id"]
    order_id = order["order_id"]

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 আপনার অর্ডার সম্পন্ন হয়েছে!\n\n"
            f"🆔 Order ID: {order_id}\n"
            "✅ Diamond সফলভাবে আপনার অ্যাকাউন্টে পাঠানো হয়েছে।"
        )
    )

    del orders[uid]
    save_orders(orders)

    await update.message.reply_text("✅ Done Message পাঠানো হয়েছে।")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text("ব্যবহার: /cancel UID")
        return

    uid = context.args[0]
    orders = load_orders()

    if uid not in orders:
        await update.message.reply_text("❌ UID পাওয়া যায়নি।")
        return

    chat_id = orders[uid]["chat_id"]

    await context.bot.send_message(
        chat_id=chat_id,
        text="❌ আপনার অর্ডার বাতিল করা হয়েছে।"
    )

    del orders[uid]
    save_orders(orders)

    await update.message.reply_text("✅ Cancel Message পাঠানো হয়েছে।")
app = Application.builder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("cancel", cancel))

# Admin Approve/Cancel Buttons
app.add_handler(CallbackQueryHandler(buttons))

# User Messages
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

print("✅ Bot Running...")
app.run_polling()

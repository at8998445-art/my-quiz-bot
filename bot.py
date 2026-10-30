import sqlite3
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PollAnswerHandler, MessageHandler, filters

import os
TOKEN = os.environ.get("TOKEN")

# ----------------- DATABASE SETUP -----------------
def init_db():
    conn = sqlite3.connect("quiz_results.db")
    cursor = conn.cursor()
    # User တွေရဲ့ ဖြေဆိုမှုများကို မှတ်မယ့် Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_answers (
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            question_index INTEGER,
            selected_option INTEGER,
            is_correct BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------- QUESTIONS DATA -----------------
QUESTIONS = [
    {
        "question": "ရာဇာဓိရာဇ်မင်း၏ ငယ်မည်မှာ မည်သို့ ဖြစ်သနည်း။",
        "options": ["မောင်စောဇံ", "ဗညားနွဲ့", "မင်းရဲကျော်စွာ", "သမိန့်ဗရမ်း"],
        "correct_option_id": 1,
        "explanation": "မှန်ကန်သော အဖြေမှာ ဗညားနွဲ့ ဖြစ်ပါသည်။"
    },
    {
        "question": "ရာဇာဓိရာဇ်နှင့် အဓိက စစ်ခင်းခဲ့ရသော အင်းဝဘုရင် မည်သူနည်း။",
        "options": ["မင်းခေါင်", "သီဟသူ", "ရაზဝင်ကျော်ထင်", "မိုးညှင်းမင်းတရား"],
        "correct_option_id": 0,
        "explanation": "မှန်ကန်သော အဖြေမှာ မင်းခေါင် ဖြစ်ပါသည်။"
    }
]

# ----------------- COMMANDS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ! ရာဇာဓိရာဇ်အရေးတော်ပုံကျမ်း Quiz Bot မှ ကြိုဆိုပါတယ်။\n"
        "မေးခွန်းအသစ်စတင်ရန် /quiz ဟု ရိုက်နှိပ်ပါ။"
    )

async def send_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # ပထမဦးဆုံး မေးခွန်းကို ပို့မည် (Index 0)
    q_data = QUESTIONS[0]
    
    message = await context.bot.send_poll(
        chat_id=chat_id,
        question=q_data["question"],
        options=q_data["options"],
        type=Poll.QUIZ,
        correct_option_id=q_data["correct_option_id"],
        explanation=q_data["explanation"],
        is_anonymous=False  # User ဖြေတာကို Bot က သိနိုင်ရန် False ပေးရပါမည်
    )
    # Poll ID ကို မှတ်ထားမည် (နောက်ပိုင်း အဖြေစစ်ရန်)
    context.bot_data[message.poll.id] = {"question_index": 0, "correct_option": q_data["correct_option_id"]}

# ----------------- HANDLE USER ANSWERS -----------------
async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id
    user = answer.user
    user_id = user.id
    username = user.username or "No Username"
    full_name = user.full_name
    selected_options = answer.option_ids
    
    if not selected_options:
        return
    
    selected_option = selected_options[0]
    poll_info = context.bot_data.get(poll_id)
    
    if poll_info:
        q_index = poll_info["question_index"]
        correct_opt = poll_info["correct_option"]
        is_correct = (selected_option == correct_opt)
        
        # Database ထဲသို့ ထည့်သွင်းခြင်း
        conn = sqlite3.connect("quiz_results.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_answers VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, full_name, q_index, selected_option, is_correct)
        )
        conn.commit()
        conn.close()

# ----------------- STATS COMMAND (ဘယ်သူမှန်/မှား ကြည့်ရန်) -----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("quiz_results.db")
    cursor = conn.cursor()
    
    # စုစုပေါင်း မှန်ကန်သူနှင့် မှားယွင်းသူ အရေအတွက်
    cursor.execute("SELECT is_correct, COUNT(*) FROM user_answers GROUP BY is_correct")
    results = cursor.fetchall()
    
    correct_count = 0
    wrong_count = 0
    for is_corr, count in results:
        if is_corr:
            correct_count = count
        else:
            wrong_count = count

    # အသေးစိတ် စာရင်း
    cursor.execute("SELECT full_name, is_correct FROM user_answers")
    all_users = cursor.fetchall()
    
    conn.close()
    
    report = f"📊 **Quiz ဖြေဆိုမှု စာရင်းဇယား**\n\n"
    report += f"✅ မှန်ကန်သူ - {correct_count} ဦး\n"
    report += f"❌ မှားယွင်းသူ - {wrong_count} ဦး\n\n"
    report += "👤 **ဖြေဆိုခဲ့သူများ:**\n"
    
    for name, is_corr in all_users:
        status = "✅ မှန်" if is_corr else "❌ မှား"
        report += f"- {name} : {status}\n"
        
    await update.message.reply_text(report, parse_mode="Markdown")

# ----------------- MAIN FUNCTION -----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_quiz))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(PollAnswerHandler(receive_poll_answer))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
import os
import json
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

def load_questions():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "questions.json")
        
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found!")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("questions", [])
    except Exception as e:
        print(f"Error loading questions: {e}")
        return []

# /start နှိပ်တဲ့အခါ Quiz ပုံစံဖြင့် မေးခွန်းထုတ်ပေးရန်
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = load_questions()
    if not questions:
        await update.message.reply_text("မေးခွန်းများ ရှာမတွေ့ပါ။ ကျေးဇူးပြု၍ questions.json ဖိုင်ကို စစ်ဆေးပါ။")
        return

    day_of_year = datetime.datetime.now().timetuple().tm_yday
    q_index = (day_of_year - 1) % len(questions)
    q_data = questions[q_index]

    question_text = f"📅 နေ့စဥ် မေးခွန်း\n\n{q_data['question']}"
    
    # Telegram Quiz Poll (သူတို့ရွေးပြီးမှ မှန်/မှား သိရမည်၊ အမည်ဖော်ပြမည်)
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question_text,
        options=q_data['options'],
        type="quiz",
        correct_option_id=q_data['answer'],
        is_anonymous=False  # ဘယ်သူတွေ ဖြေထားတယ်ဆိုတာကို သိနိုင်ရန်
    )

def main():
    if not TOKEN:
        print("Error: TOKEN environment variable not set.")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
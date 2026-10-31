import os
import json
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

# JSON ဖိုင်မှ မေးခွန်းများကို တိကျသော လမ်းကြောင်းဖြင့် ဖတ်ရှုရန်
def load_questions():
    try:
        # လက်ရှိ script ရှိရာ ဖိုင်တွဲထဲမှ questions.json ကို ရှာမည်
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

# /start အမိန့်ပေးသည့်အခါ ယနေ့အတွက် မေးခွန်းကို ထုတ်ပြရန်
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = load_questions()
    if not questions:
        await update.message.reply_text("မေးခွန်းများ ရှာမတွေ့ပါ။ ကျေးဇူးပြု၍ questions.json ဖိုင်ကို စစ်ဆေးပါ။")
        return

    # ယခုနှစ်၏ မည်သည့်ရက်မြောက်ဖြစ်ကြောင်း တွက်ချက်ပြီး မေးခွန်းအညွှန်း (Index) ကို ရှာမည်
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    # မေးခွန်း ၁၀၀ အတွင်း အဝိုင်းလည်နေစေရန်
    q_index = (day_of_year - 1) % len(questions)
    q_data = questions[q_index]

    question_text = f"📅 **ယနေ့အတွက် ရာဇာဓိရာဇ် အရေးတော်ပုံ မေးခွန်း**\n\n{q_data['question']}\n\n"
    for i, option in enumerate(q_data['options']):
        question_text += f"{i+1}. {option}\n"
    
    question_text += f"\n*(အဖြေမှန်မှာ နံပါတ် {q_data['answer'] + 1} ဖြစ်ပါသည်)*"
    
    await update.message.reply_text(question_text)

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
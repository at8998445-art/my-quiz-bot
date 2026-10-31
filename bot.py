import os
import json
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Render က Port တောင်းဆိုမှုကို ဖြေရှင်းရန်အတွက် Dummy Web Server တစ်ခု
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_web_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = load_questions()
    if not questions:
        await update.message.reply_text("မေးခွန်းများ ရှာမတွေ့ပါ။ ကျေးဇူးပြု၍ questions.json ဖိုင်ကို စစ်ဆေးပါ။")
        return

    day_of_year = datetime.datetime.now().timetuple().tm_yday
    q_index = (day_of_year - 1) % len(questions)
    q_data = questions[q_index]

    question_text = f"📅 နေ့စဥ် မေးခွန်း\n\n{q_data['question']}"
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question_text,
        options=q_data['options'],
        type="quiz",
        correct_option_id=q_data['answer'],
        is_anonymous=False
    )

def main():
    if not TOKEN:
        print("Error: TOKEN environment variable not set.")
        return

    # Web server ကို သီးသန့် Thread ဖြင့် စတင် Run မည် (Render Port သတ်မှတ်ချက်အတွက်)
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
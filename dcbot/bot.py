# dcbot/bot.py

import discord
import logging
from discord.ext import commands
from config import DISCORD_TOKEN
from model import get_model_response

# 設置日誌級別為 DEBUG
logging.basicConfig(level=logging.DEBUG)

# 設定機器人的意圖
intents = discord.Intents.default()
intents.message_content = True  # 確保機器人能夠讀取消息內容

# 設定機器人的指令前綴和 @ 機器人時的回應
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

# 當機器人成功啟動時，會觸發這個事件
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

# 定義一個指令，當用戶輸入 !ask 或 @ 機器人時，機器人會將用戶的問題傳送給語言模型並回應
@bot.command()
async def ask(ctx, *, question: str):
    print(f"Received question: {question}")
    response = await get_model_response(question)
    print(f"Generated response: {response}")
    await ctx.send(response)

def run_bot():
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)
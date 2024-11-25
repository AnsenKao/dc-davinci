# dcbot/bot.py

import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from model import get_model_response
import requests
import base64

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

# 下載圖片並轉換為 base64 編碼
async def download_and_encode_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 將圖片內容轉換為 base64
        encoded_image = base64.b64encode(response.content).decode('utf-8')
        return encoded_image
    else:
        raise Exception(f"Failed to download image: {response.status_code}")

# 定義一個指令，當用戶輸入 !ask 時，機器人會將用戶的問題或圖片傳送給語言模型並回應
@bot.command()
async def ask(ctx, *, question: str = None):
    encoded_images = []

    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            # 檢查附件是否為圖片
            if attachment.content_type.startswith('image/'):
                print(f"Image URL: {attachment.url}")
                encoded_image = await download_and_encode_image(attachment.url)
                print(f"Encoded image: {encoded_image}")
                encoded_images.append(encoded_image)

    if question or encoded_images:
        combined_input = question if question else ""
        for encoded_image in encoded_images:
            combined_input += f"\n[IMAGE:{encoded_image}]"
        response = await get_model_response(combined_input)
        print(f"Generated response: {response}")
        await ctx.send(response)
    else:
        await ctx.send("Please provide a question or an image.")

# 監聽訊息事件
@bot.event
async def on_message(message):
    # 確保機器人不會回應自己的訊息
    if message.author == bot.user:
        return

    # 檢查訊息是否來自私訊
    if isinstance(message.channel, discord.DMChannel):
        encoded_images = []
        question = message.content.strip()

        if message.attachments:
            for attachment in message.attachments:
                # 檢查附件是否為圖片
                if attachment.content_type.startswith('image/'):
                    print(f"Image URL: {attachment.url}")
                    encoded_image = await download_and_encode_image(attachment.url)
                    print(f"Encoded image: {encoded_image}")
                    encoded_images.append(encoded_image)

        if question or encoded_images:
            combined_input = question if question else ""
            for encoded_image in encoded_images:
                combined_input += f"\n[IMAGE:{encoded_image}]"
            response = await get_model_response(combined_input)
            print(f"Generated response: {response}")
            await message.channel.send(response)
        else:
            await message.channel.send("Please provide a question or an image.")
    else:
        # 檢查訊息是否提及了機器人
        if bot.user.mentioned_in(message):
            encoded_images = []
            # 移除提及機器人的部分，保留問題內容
            question = message.content.replace(f'<@!{bot.user.id}>', '').strip()

            if message.attachments:
                for attachment in message.attachments:
                    # 檢查附件是否為圖片
                    if attachment.content_type.startswith('image/'):
                        print(f"Image URL: {attachment.url}")
                        encoded_image = await download_and_encode_image(attachment.url)
                        print(f"Encoded image: {encoded_image}")
                        encoded_images.append(encoded_image)

            if question or encoded_images:
                combined_input = question if question else ""
                for encoded_image in encoded_images:
                    combined_input += f"\n[IMAGE:{encoded_image}]"
                response = await get_model_response(combined_input)
                print(f"Generated response: {response}")
                await message.channel.send(response)
            else:
                await message.channel.send("Please provide a question or an image.")

    # 確保其他命令仍然可以正常運行
    await bot.process_commands(message)

def run_bot():
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)
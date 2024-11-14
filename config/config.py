# config/config.py

from dotenv import load_dotenv
import os

# 加載 .env 文件中的環境變量
load_dotenv()

ASSISTANT_API = os.getenv('ASSISTANT_API')
API_KEY = os.getenv('API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


# 確保所有變量都已加載
if not all([ASSISTANT_API, API_KEY, ASSISTANT_ID, DISCORD_TOKEN]):
    raise ValueError("Some environment variables are missing. Please check your .env file.")
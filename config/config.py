# config/config.py

from dotenv import load_dotenv
import os


class Settings:
    def __init__(self):
        # 加載 .env 文件中的環境變量
        load_dotenv()

        # 初始化設定值
        self.assistant_api: str = self._get_env("ASSISTANT_API")
        self.api_key: str = self._get_env("API_KEY")
        self.assistant_id: str = self._get_env("ASSISTANT_ID")
        self.discord_token: str = self._get_env("DISCORD_TOKEN")

        # 驗證所有必要的設定都已加載
        self._validate_settings()

    def _get_env(self, key: str) -> str:
        """從環境變量獲取設定值"""
        value = os.getenv(key)
        return value if value is not None else ""

    def _validate_settings(self) -> None:
        """驗證所有必要的設定是否存在"""
        missing_vars = []

        if not self.assistant_api:
            missing_vars.append("ASSISTANT_API")
        if not self.api_key:
            missing_vars.append("API_KEY")
        if not self.assistant_id:
            missing_vars.append("ASSISTANT_ID")
        if not self.discord_token:
            missing_vars.append("DISCORD_TOKEN")

        if missing_vars:
            raise ValueError(
                f"Missing environment variables: {', '.join(missing_vars)}. Please check your .env file."
            )

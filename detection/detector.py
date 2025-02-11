from typing import Optional, List
from datetime import datetime
import json
from dataclasses import dataclass
import asyncio
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

@dataclass
class DetectionResult:
    """檢測結果的資料類別"""
    timestamp: datetime
    url: str
    items: List[str]
    changed: bool = False
    error: Optional[str] = None

class WebsiteDetector:
    def __init__(self, url: str, item_selector: str, headless: bool = True, wait_time: int = 10):
        self.url = url
        self.item_selector = item_selector
        self.wait_time = wait_time
        self.last_items: List[str] = []
        
        self.edge_options = Options()
        if headless:
            self.edge_options.add_argument("--headless")
        self.edge_options.add_argument("--inprivate")
        self.edge_options.add_argument("--disable-extensions")
        self.edge_options.add_argument("--disable-gpu")
        self.edge_options.add_argument("--no-sandbox")
        self.edge_options.add_argument("--disable-dev-shm-usage")
        
        # 初始化WebDriver
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """設置WebDriver"""
        if self.driver is not None:
            self.driver.quit()
        
        edge_driver_path = EdgeChromiumDriverManager().install()
        
        try:
            service = Service(executable_path=edge_driver_path)
            self.driver = webdriver.Edge(service=service, options=self.edge_options)
        except Exception as e:
            print(f"EdgeDriver 初始化失敗: {str(e)}")
            raise
    
    def _extract_item_data(self, element) -> str:
        """
        從元素中提取文字內容
        """
        return element.text.strip().split("\n")[0]
    
    async def detect_once(self) -> bool:
        """
        執行單次檢測
        Returns:
            bool: 如果內容有變化返回 True，否則返回 False
        """
        try:
            # 使用asyncio.to_thread來非阻塞地執行Selenium操作
            items = await asyncio.to_thread(self._detect_sync)
            
            # 檢查是否有變化
            has_changed = self.last_items and items != self.last_items
            
            # 更新最後檢測的項目
            self.last_items = items
            
            return has_changed
        except Exception as e:
            print(f"Error detecting items: {str(e)}")
            return False
    
    def _detect_sync(self) -> List[str]:
        """同步執行檢測操作"""
        try:
            self.driver.get(self.url)
            
            # 等待元素出現
            wait = WebDriverWait(self.driver, self.wait_time)
            elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, self.item_selector)
                    if self.item_selector.strip()[0] not in ['/', '(']
                    else (By.XPATH, self.item_selector)
                )
            )
            return [self._extract_item_data(element) for element in elements]
        except TimeoutException:
            raise TimeoutException(f"等待元素 '{self.item_selector}' 超時")
    
    async def monitor(self, interval_seconds: int = 60) -> None:
        """
        持續監測網站
        
        Args:
            interval_seconds: 檢測間隔（秒）
        """
        while True:
            has_changed = await self.detect_once()
            if has_changed:
                print(f"Changes detected at {datetime.now()}!")
                print(f"Current items: {json.dumps(self.last_items, indent=2, ensure_ascii=False)}")
                return True
            await asyncio.sleep(interval_seconds)
    
    def close(self):
        """關閉WebDriver"""
        if self.driver is not None:
            self.driver.quit()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    async def main():
        detector = WebsiteDetector(
            url="https://www.twitch.tv/shxtou/videos",
            item_selector=r"//*[@data-a-target='video-carousel-card-0']",
            headless=True,
            wait_time=600
        )
        try:
            has_changed = await detector.detect_once()
            print(f"Has changed: {has_changed}")
            print(f"Current items: {detector.last_items}")
        finally:
            detector.close()

    # 使用 asyncio 運行異步主函數
    asyncio.run(main())

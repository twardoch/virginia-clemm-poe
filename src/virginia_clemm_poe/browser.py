# this_file: src/virginia_clemm_poe/browser.py

"""Browser automation utilities for Virginia Clemm Poe."""

import asyncio
import platform
from pathlib import Path
from typing import List, Optional

import aiohttp
from loguru import logger
from playwright.async_api import Browser, Page, async_playwright

from .config import (
    BROWSER_CONNECT_MAX_ATTEMPTS,
    BROWSER_CONNECT_RETRY_INTERVAL_SECONDS,
    CDP_VERSION_URL,
    DEFAULT_DEBUG_PORT,
)


class BrowserManager:
    """Manages browser lifecycle for web scraping."""
    
    def __init__(self, debug_port: int = DEFAULT_DEBUG_PORT):
        self.debug_port = debug_port
        self.playwright = None
        self.browser = None
        self.context = None
        
    @staticmethod
    def get_chrome_paths() -> List[str]:
        """Get possible Chrome/Chromium paths for different platforms."""
        return [
            # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            # Linux
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome",
            # Windows
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]
    
    @staticmethod
    def find_chrome_path() -> Optional[str]:
        """Find Chrome executable path."""
        paths = BrowserManager.get_chrome_paths()
        return next((path for path in paths if Path(path).exists()), None)
    
    async def check_cdp_connection(self) -> bool:
        """Check if Chrome DevTools Protocol is available."""
        cdp_url = CDP_VERSION_URL.format(port=self.debug_port)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(cdp_url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return "webSocketDebuggerUrl" in data
        except Exception:
            return False
        return False
    
    async def kill_chrome_on_port(self) -> None:
        """Kill any Chrome process using the debug port."""
        try:
            if platform.system() == "Darwin":  # macOS
                proc = await asyncio.create_subprocess_exec(
                    "lsof", "-ti", f":{self.debug_port}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                stdout, _ = await proc.communicate()
                if stdout:
                    pids = stdout.decode().strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                await asyncio.create_subprocess_exec(
                                    "kill", "-9", pid,
                                    stdout=asyncio.subprocess.DEVNULL,
                                    stderr=asyncio.subprocess.DEVNULL,
                                )
                            except Exception:
                                pass
        except Exception as e:
            logger.debug(f"Error killing Chrome processes: {e}")
        await asyncio.sleep(1)
    
    async def launch_chrome(self) -> bool:
        """Launch Chrome with debug mode enabled."""
        chrome_path = self.find_chrome_path()
        if not chrome_path:
            logger.error("Chrome not found. Please install Chrome or Chromium.")
            return False
            
        await self.kill_chrome_on_port()
        
        args = [
            chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--window-size=1280,800",
        ]
        
        logger.info(f"Launching Chrome with debug port {self.debug_port}")
        
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        
        for attempt in range(BROWSER_CONNECT_MAX_ATTEMPTS):
            await asyncio.sleep(BROWSER_CONNECT_RETRY_INTERVAL_SECONDS)
            
            if await self.check_cdp_connection():
                logger.info("Successfully launched Chrome")
                return True
                
            logger.debug(f"Connection attempt {attempt + 1}/{BROWSER_CONNECT_MAX_ATTEMPTS} failed")
        
        logger.error(f"Failed to connect to Chrome after {BROWSER_CONNECT_MAX_ATTEMPTS} attempts")
        
        try:
            process.terminate()
            await asyncio.sleep(1)
            if process.returncode is None:
                process.kill()
        except Exception:
            pass
            
        return False
    
    async def connect(self) -> Browser:
        """Connect to Chrome via CDP."""
        if not await self.check_cdp_connection():
            logger.info("Chrome not running with CDP. Launching Chrome...")
            if not await self.launch_chrome():
                raise RuntimeError("Failed to launch Chrome with CDP")
        
        cdp_url = CDP_VERSION_URL.format(port=self.debug_port)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(cdp_url) as response:
                    info = await response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Chrome CDP: {e}")
        
        ws_url = info["webSocketDebuggerUrl"]
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(ws_url)
        
        if not self.browser.contexts:
            self.context = await self.browser.new_context()
        else:
            self.context = self.browser.contexts[0]
            
        return self.browser
    
    async def new_page(self) -> Page:
        """Create a new page."""
        if not self.context:
            raise RuntimeError("Browser not connected")
        return await self.context.new_page()
    
    async def close(self):
        """Close browser connection."""
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.browser = None
            self.context = None
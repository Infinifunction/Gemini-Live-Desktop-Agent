import requests
import subprocess
import os
import time
import shutil
import glob
import psutil
import pyautogui
import pyperclip
import screen_brightness_control as sbc
from AppOpener import open as app_open
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.genai import types
from google import genai
from newsapi import NewsApiClient
import wikipediaapi
import feedparser
import json
from datetime import datetime, timedelta

# --- Global Variables ---
driver_instance = None

# --- Existing Functions ---

def getWeather(city: str) -> str:
    """
    Gets the current weather for a specific city using weatherapi.com.
    """
    API_KEY = "Your Api Key" # Ensure this environment variable is set
    if not API_KEY:
        return {"error": "WEATHER_API_KEY environment variable not found."}

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "location": data["location"]["name"],
            "country": data["location"]["country"],
            # Extract current weather data
            "temperature_c": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"]
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def runCommand(command: str) -> str:
    """
    Executes a PowerShell command.
    """
    try:
        subprocess.run(["powershell", "-Command", command], capture_output=True)
        return f"Command executed successfully: {command}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

def get_news(category: str, country: str) -> str:
    """
    Fetches top news headlines from NewsAPI.
    """
    try:
        newsapi = NewsApiClient(api_key='Your Api Key')

        # Call the NewsAPI to get top headlines for the specified category and country
        top_headlines = newsapi.get_top_headlines(
            category=category,
            country=country,
        )
        
        if top_headlines.get('status') != 'ok':
            return {"error": top_headlines.get('message', "Unknown error from NewsAPI")}
            
        articles = []
        for article in top_headlines.get('articles', []):
            articles.append({
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "publishedAt": article.get("publishedAt"),
                "description": article.get("description")
            })
            
        return {"articles": articles}
        
    except Exception as e:
        return {"error": str(e)}

def get_local_time(format_type: str = "full") -> dict:
    """
    Returns the local system time.
    format_type: 'time_only', 'date_only', 'full', 'timestamp', 'readable'
    """
    now = datetime.now()
    
    formats = {
        "time_only": now.strftime("%H:%M:%S"),
        "date_only": now.strftime("%Y-%m-%d"),
        "full": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": now.timestamp(),
        "readable": now.strftime("%d %B %Y, %A, %H:%M")
    }
    
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "datetime": formats.get(format_type, formats["full"]),
        "timezone": "local",
        "day_of_week": now.strftime("%A"),
        "day_of_year": now.strftime("%j")
    }

def wikipedia_search_simple(query: str, lang: str = "tr", sentences: int = 3) -> dict:
    """
    Searching Wikipedia using the wikipedia-api library
    """
    try:
        user_agent = "MyAIBot/1.0 (contact@example.com)"
        
        wiki_wiki = wikipediaapi.Wikipedia(
            language=lang,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            # User agent is required by Wikipedia API
            user_agent=user_agent
        )
        
        page = wiki_wiki.page(query)
        
        if not page.exists():
            search_results = wiki_wiki.search(query, results=3)
            
            if search_results:
                return {
                    "status": "search_results",
                    "query": query,
                    "suggestions": [
                        {"title": title, "summary": ""}
                        for title in search_results
                    ]
                }
            return {
                "status": "not_found",
                "query": query,
                "message": "Page not found"
            }
        
        summary = page.summary
        # Split summary into sentences and limit to the requested number
        sentences_list = summary.split('. ')
        if len(sentences_list) > sentences:
            summary = '. '.join(sentences_list[:sentences]) + '.'
        
        return {
            "status": "success",
            "title": page.title,
            "extract": summary,
            "page_url": page.fullurl,
            "language": lang,
            "word_count": len(page.text)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_gaming_news(source: str = "all", limit: int = 5) -> dict:
    """
    It brings game news and announcements.
    """
    sources = {
        "steam": {"name": "Steam", "url": "https://store.steampowered.com/feeds/news.xml", "type": "rss"},
        "ign": {"name": "IGN", "url": "https://feeds.feedburner.com/ign/games-all", "type": "rss"},
        "eurogamer": {"name": "Eurogamer", "url": "https://www.eurogamer.net/feed", "type": "rss"},
        "gamerant": {"name": "Game Rant", "url": "https://gamerant.com/feed", "type": "rss"}
    }
    
    results = []
    
    if source == "all":
        selected_sources = sources.keys()
    else:
        # Default to IGN if source is not found
        selected_sources = [source] if source in sources else ["ign"]
    
    for src in selected_sources:
        src_info = sources[src]
        try:
            feed = feedparser.parse(src_info["url"])
            for entry in feed.entries[:limit]:
                # Filter news to include only those from the last 7 days
                published = entry.get('published_parsed', entry.get('updated_parsed'))
                if published:
                    pub_date = datetime(*published[:6])
                    if datetime.now() - pub_date > timedelta(days=7):
                        continue
                
                results.append({
                    "source": src_info["name"],
                    "title": entry.title,
                    "summary": entry.get('summary', '')[:200],
                    "link": entry.link,
                    "published": entry.get('published', ''),
                    "category": "news"
                })
        except Exception as e:
            continue
    
    results.sort(key=lambda x: x.get('published', ''), reverse=True)
    return {
        "total_news": len(results),
        "sources": list(selected_sources),
        "news": results[:limit*2]
    }

# Out of service(get_company_news)

#def get_company_news(company: str = None, limit: int = 5) -> dict:
#    """
#    Fetches news from specific game companies.
#    """
#    companies = {
#        "ubisoft": {"name": "Ubisoft", "rss": "https://news.ubisoft.com/en-us/feed/", "keywords": ["Ubisoft", "Assassin's Creed", "Far Cry", "Watch Dogs"]},
#        "ea": {"name": "Electronic Arts", "rss": "https://www.ea.com/news.rss", "keywords": ["EA", "EA Sports", "FIFA", "Battlefield", "Apex Legends"]},
#        "activision": {"name": "Activision Blizzard", "rss": "https://news.activision.com/feed", "keywords": ["Call of Duty", "Activision", "Blizzard", "Overwatch", "Diablo"]},
#        "sony": {"name": "Sony Interactive Entertainment", "rss": "https://blog.playstation.com/feed/", "keywords": ["PlayStation", "PS5", "Sony", "God of War", "Spider-Man"]},
#        "microsoft": {"name": "Microsoft Xbox", "rss": "https://news.xbox.com/en-us/feed/", "keywords": ["Xbox", "Game Pass", "Halo", "Forza", "Microsoft"]},
#        "nintendo": {"name": "Nintendo", "rss": "https://www.nintendo.com/whatsnew/feed/", "keywords": ["Nintendo", "Switch", "Mario", "Zelda", "Pokémon"]},
#        "valve": {"name": "Valve", "rss": "https://store.steampowered.com/feeds/news.xml", "keywords": ["Steam", "Valve", "Half-Life", "Counter-Strike", "Dota"]}
#    }
#    
#    if company and company.lower() in companies:
#        selected_companies = [company.lower()]
#    else:
#        selected_companies = list(companies.keys())
#    
#    news_items = []
#    
#    for comp in selected_companies:
#        comp_info = companies[comp]
#        try:
#            feed = feedparser.parse(comp_info["rss"])
#            for entry in feed.entries[:limit]:
#                title = entry.title.lower()
#                if any(keyword.lower() in title for keyword in comp_info["keywords"]):
#                    news_items.append({
#                        "company": comp_info["name"],
#                        "title": entry.title,
#                        "summary": entry.get("summary", "")[:150],
#                        "link": entry.link,
#                        "published": entry.get("published", ""),
#                        "type": "company_news"
#                    })
#        except Exception as e:
#            continue
#    
#    return {
#        "companies": [companies[c]["name"] for c in selected_companies],
#        "news_count": len(news_items),
#        "news": news_items[:limit*2]
#    }

# --- Cat 1: HID Simulation ---

def move_mouse(x: int, y: int) -> str:
    """
    Moves the mouse cursor to the specified X and Y coordinates.
    """
    try:
        pyautogui.moveTo(x, y)
        return f"Mouse moved to ({x}, {y})"
    except Exception as e:
        return f"Error moving mouse: {e}"

def click_mouse(button: str = "left", double_click: bool = False) -> str:
    """
    Clicks a mouse button (left, right, or middle). Can perform double clicks.
    """
    try:
        if double_click:
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)
        return f"{'Double ' if double_click else ''}Clicked {button} button"
    except Exception as e:
        return f"Error clicking mouse: {e}"

def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
    """
    Drags the mouse from a starting position to an ending position.
    """
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, button='left', duration=0.5)
        return f"Dragged mouse from ({start_x}, {start_y}) to ({end_x}, {end_y})"
    except Exception as e:
        return f"Error dragging mouse: {e}"

def scroll(amount: int) -> str:
    """
    Scrolls the mouse wheel up or down.
    """
    try:
        pyautogui.scroll(amount)
        return f"Scrolled {amount}"
    except Exception as e:
        return f"Error scrolling: {e}"

def type_text(text: str, interval: float = 0.0) -> str:
    """
    Types the given text using the keyboard.
    """
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed: {text}"
    except Exception as e:
        return f"Error typing text: {e}"

def press_hotkey(keys: str) -> str:
    """
    Presses a hotkey combination (e.g., 'ctrl+c').
    """
    try:
        # keys format "ctrl+c" or "alt+tab"
        key_list = keys.split('+')
        pyautogui.hotkey(*key_list)
        return f"Pressed hotkey: {keys}"
    except Exception as e:
        return f"Error pressing hotkey: {e}"


# --- Cat 2: Process & App Management ---

def open_application(app_name: str) -> str:
    """
    Opens an application by its name.
    """
    try:
        # AppOpener is easy for common apps
        app_open(app_name, match_closest=True, output=False)
        return f"Opened application: {app_name}"
    except Exception as e:
        return f"Error opening application: {e}"

def close_application(app_name_or_pid: str) -> str:
    """
    Closes an application by its name or Process ID (PID).
    """
    try:
        # Try as PID first
        try:
            pid = int(app_name_or_pid)
            process = psutil.Process(pid)
            process.terminate()
            return f"Terminated process with PID {pid}"
        except ValueError:
            # Try as name
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name_or_pid.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed_count += 1
            if killed_count > 0:
                return f"Terminated {killed_count} processes matching '{app_name_or_pid}'"
            return f"No process found matching '{app_name_or_pid}'"
    except Exception as e:
        return f"Error closing application: {e}"

def list_active_processes() -> str:
    """
    Lists the currently active processes (limited to top 50).
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(f"{proc.info['pid']}: {proc.info['name']}")
        # Limit to the top 50 processes to prevent excessive output that could overflow context window
        return "\n".join(processes[:50])
    except Exception as e:
        return f"Error listing processes: {e}"

def switch_window(window_title: str) -> str:
    """
    Switches focus to a specific window by its title.
    """
    try:
        # PyAutoGUI doesn't direct switch reliably on all clean Windows configs without extra win32 apis,
        # but AppOpener/pygetwindow usage via pyautogui is standard.
        # Let's try to get window first
        import pygetwindow as gw
        window =  gw.getWindowsWithTitle(window_title)
        if window:
            win = window[0]
            if not win.isActive:
                win.activate()
                # Ensure it's not minimized
                if win.isMinimized:
                    win.restore()
                return f"Switched to window: {win.title}"
        return f"Window '{window_title}' not found."
    except Exception as e:
        return f"Error switching window: {e}"


# --- Cat 3: File System Ops ---

def read_file(path: str) -> str:
    """
    Reads and returns the content of a file.
    """
    try:
        if not os.path.exists(path):
            return "File not found."
        # Read the file using utf-8 encoding to support various characters
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_to_file(path: str, content: str, mode: str = "w") -> str:
    """
    Writes content to a file. Supports write ('w') and append ('a') modes.
    """
    try:
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file: {e}"

def manage_files(action: str, path: str, destination: str = None) -> str:
    """
    Manages files: copy, move, delete, or create directories.
    """
    try:
        if action == "copy":
            # Handle recursive copy for directories, simple copy for files
            if os.path.isdir(path):
                shutil.copytree(path, destination)
            else:
                shutil.copy2(path, destination)
            return f"Copied {path} to {destination}"
        elif action == "move":
            # Move files or directories
            shutil.move(path, destination)
            return f"Moved {path} to {destination}"
        elif action == "delete":
            # Handle recursive deletion for directories
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"Deleted {path}"
        elif action == "create_dir":
            os.makedirs(path, exist_ok=True)
            return f"Created directory {path}"
        else:
            return "Unknown action. Use copy, move, delete, or create_dir."
    except Exception as e:
        return f"Error managing files: {e}"

def search_files(query: str, path: str) -> str:
    """
    Searches for files matching a query within a directory.
    """
    try:
        # Simple glob recursive search
        search_pattern = os.path.join(path, f"**/*{query}*")
        files = glob.glob(search_pattern, recursive=True)
        return "\n".join(files[:20]) # Limit to 20
    except Exception as e:
        return f"Error searching files: {e}"


# --- Cat 4: System Control ---

def system_power(action: str) -> str:
    """
    Controls system power: shutdown, restart, sleep, or lock.
    """
    try:
        if action == "shutdown":
            os.system("shutdown /s /t 5")
            return "System shutting down in 5 seconds."
        elif action == "restart":
            os.system("shutdown /r /t 5")
            return "System restarting in 5 seconds."
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "System going to sleep..."
        elif action == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "System locked."
        else:
            return "Unknown action."
    except Exception as e:
        return f"Error in system power: {e}"

def volume_control(action: str, level: int = None) -> str:
    """
    Controls system volume: set level, mute, or unmute.
    """
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        if action == "set":
            if level is not None:
                # Level 0 to 100 mapping to scalar 0.0 to 1.0
                scalar_vol = max(0.0, min(1.0, level / 100.0))
                volume.SetMasterVolumeLevelScalar(scalar_vol, None)
                return f"Volume set to {level}%"
        elif action == "mute":
            volume.SetMute(1, None)
            return "Volume muted."
        elif action == "unmute":
            volume.SetMute(0, None)
            return "Volume unmuted."
        return "Invalid action or level."
    except Exception as e:
        return f"Error in volume control: {e}"

def brightness_control(level: int) -> str:
    """
    Sets the screen brightness level.
    """
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level}%"
    except Exception as e:
        return f"Error setting brightness: {e}"

def get_clipboard() -> str:
    """
    Retrieves the current text from the clipboard.
    """
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error getting clipboard: {e}"

def set_clipboard(text: str) -> str:
    """
    Sets the clipboard text.
    """
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard."
    except Exception as e:
        return f"Error setting clipboard: {e}"


# --- Cat 5: Deep Web Manipulation (Selenium) ---

def _get_driver():
    # Singleton pattern to ensure only one browser instance is active
    global driver_instance
    if driver_instance is None:
        opts = webdriver.ChromeOptions()
        # Add experimental options to keep browser open after script finishes
        opts.add_experimental_option("detach", True)
        # opts.add_argument("--start-maximized")
        driver_instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    return driver_instance

def browser_open(url: str) -> str:
    """
    Opens a URL in the browser using Selenium.
    """
    try:
        driver = _get_driver()
        driver.get(url)
        return f"Opened URL: {url}"
    except Exception as e:
        return f"Error opening browser: {e}"

def browser_type(selector: str, text: str, by_method: str = "css") -> str:
    """
    Types text into a specific browser element (found by selector).
    """
    try:
        driver = _get_driver()
        # Convert string method to Selenium By attribute
        by = getattr(By, by_method.upper(), By.CSS_SELECTOR)
        # Wait until element is present in DOM
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, selector)))
        element.clear()
        element.send_keys(text)
        return f"Typed '{text}' into {selector}"
    except Exception as e:
        return f"Error typing in browser: {e}"

def browser_click(selector: str, by_method: str = "css") -> str:
    """
    Clicks on a specific browser element.
    """
    try:
        driver = _get_driver()
        by = getattr(By, by_method.upper(), By.CSS_SELECTOR)
        # Wait for element to be clickable
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, selector)))
        element.click()
        return f"Clicked element {selector}"
    except Exception as e:
        return f"Error clicking in browser: {e}"

def browser_get_text(selector: str, by_method: str = "css") -> str:
    """
    Retrieves the text content of a specific browser element.
    """
    try:
        driver = _get_driver()
        by = getattr(By, by_method.upper(), By.CSS_SELECTOR)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, selector)))
        return element.text
    except Exception as e:
        return f"Error getting text: {e}"

def browser_scroll(direction: str, amount: int = 500) -> str:
    """
    Scrolls the browser page up or down.
    """
    try:
        driver = _get_driver()
        scroll_amount = amount if direction == "down" else -amount
        driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
        return f"Scrolled {direction} by {amount}"
    except Exception as e:
        return f"Error scrolling browser: {e}"

def browser_capture_full_page() -> str:
    """
    Captures a screenshot of the current browser page (currently viewport).
    """
    try:
        driver = _get_driver()
        # Taking a standard screenshot which is robust across mostly all sites
        # Full page is tricky with Selenium directly, so we take current viewport as base64
        # This acts as the "eyes" of the agent for the current view
        screenshot_b64 = driver.get_screenshot_as_base64()
        
        # We can also attempt to capture the body element for a larger view if possible
        body = driver.find_element(By.TAG_NAME, "body")
        # Ensure temporary directory exists
        if not os.path.exists("temp"):
            os.makedirs("temp")
        path = os.path.abspath("temp/full_page_screenshot.png")
        body.screenshot(path)
        return f"Screenshot saved to {path}"
    except Exception as e:
        return f"Error capturing browser: {e}"


# --- AVAILABLE_FUNCTIONS ---
AVAILABLE_FUNCTIONS = {
    # Existing
    "run_command": runCommand,
    "get_weather": getWeather,
    "get_news": get_news,
    "get_local_time": get_local_time,
    "wikipedia_search": wikipedia_search_simple,
    "get_gaming_news": get_gaming_news,
    #"get_company_news": get_company_news,
    
    # Cat 1
    "move_mouse": move_mouse,
    "click_mouse": click_mouse,
    "drag_mouse": drag_mouse,
    "scroll": scroll,
    "type_text": type_text,
    "press_hotkey": press_hotkey,
    
    # Cat 2
    "open_application": open_application,
    "close_application": close_application,
    "list_active_processes": list_active_processes,
    "switch_window": switch_window,
    
    # Cat 3
    "read_file": read_file,
    "write_to_file": write_to_file,
    "manage_files": manage_files,
    "search_files": search_files,
    
    # Cat 4
    "system_power": system_power,
    "volume_control": volume_control,
    "brightness_control": brightness_control,
    "get_clipboard": get_clipboard,
    "set_clipboard": set_clipboard,
    
    # Cat 5
    "browser_open": browser_open,
    "browser_type": browser_type,
    "browser_click": browser_click,
    "browser_get_text": browser_get_text,
    "browser_scroll": browser_scroll,
    "browser_capture_full_page": browser_capture_full_page,
}


# --- Gemini Tool Schemas ---
tools_gemini = [
    types.Tool(
        function_declarations=[
            # --- Existing Definitions ---
            types.FunctionDeclaration(
                name="get_weather",
                description="gets the weather for a requested city",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "city": genai.types.Schema(type = genai.types.Type.STRING)
                    }
                )
            ),
            types.FunctionDeclaration(
                name="run_command",
                description="run as powershell command",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "command": genai.types.Schema(type = genai.types.Type.STRING)
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_news",
                description="Gets top headlines. Infer country/category.",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "category": genai.types.Schema(type = genai.types.Type.STRING),
                        "country": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_local_time",
                description="Gets the current local time.",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "format_type": genai.types.Schema(type = genai.types.Type.STRING)
                    }
                )
            ),
            types.FunctionDeclaration(
                name="wikipedia_search",
                description="Searches Wikipedia.",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "query": genai.types.Schema(type = genai.types.Type.STRING),
                        "lang": genai.types.Schema(type = genai.types.Type.STRING),
                        "sentences": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_gaming_news",
                description="Gets gaming news.",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "source": genai.types.Schema(type = genai.types.Type.STRING),
                        "limit": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            #types.FunctionDeclaration(
            #    name="get_company_news",
            #    description="Gets company news.",
            #    parameters=genai.types.Schema(
            #        type = genai.types.Type.OBJECT,
            #        properties = {
            #            "company": genai.types.Schema(type = genai.types.Type.STRING),
            #            "limit": genai.types.Schema(type = genai.types.Type.INTEGER),
            #        }
            #    )
            #),
            
            # --- New Definitions ---
            
            # Cat 1: HID
            types.FunctionDeclaration(
                name="move_mouse",
                description="Moves mouse to x, y coordinates",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "x": genai.types.Schema(type = genai.types.Type.INTEGER),
                        "y": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="click_mouse",
                description="Clicks mouse button",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "button": genai.types.Schema(type = genai.types.Type.STRING, description="left, right, or middle"),
                        "double_click": genai.types.Schema(type = genai.types.Type.BOOLEAN),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="drag_mouse",
                description="Drags mouse from start to end coordinates",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "start_x": genai.types.Schema(type = genai.types.Type.INTEGER),
                        "start_y": genai.types.Schema(type = genai.types.Type.INTEGER),
                        "end_x": genai.types.Schema(type = genai.types.Type.INTEGER),
                        "end_y": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="scroll",
                description="Scrolls the mouse wheel",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "amount": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="type_text",
                description="Types text using keyboard",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "text": genai.types.Schema(type = genai.types.Type.STRING),
                        "interval": genai.types.Schema(type = genai.types.Type.NUMBER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="press_hotkey",
                description="Presses a combination of keys (e.g. ctrl+c)",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "keys": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            
            # Cat 2: Processes
            types.FunctionDeclaration(
                name="open_application",
                description="Opens an application by name",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "app_name": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="close_application",
                description="Closes an application by name or PID",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "app_name_or_pid": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="list_active_processes",
                description="Lists active processes",
                parameters=genai.types.Schema(type = genai.types.Type.OBJECT, properties = {})
            ),
            types.FunctionDeclaration(
                name="switch_window",
                description="Switches focus to a window with the given title",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "window_title": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            
            # Cat 3: Files
            types.FunctionDeclaration(
                name="read_file",
                description="Reads content of a file",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "path": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="write_to_file",
                description="Writes content to a file",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "path": genai.types.Schema(type = genai.types.Type.STRING),
                        "content": genai.types.Schema(type = genai.types.Type.STRING),
                        "mode": genai.types.Schema(type = genai.types.Type.STRING, description="w or a"),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="manage_files",
                description="Performs file operations like copy, move, delete",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "action": genai.types.Schema(type = genai.types.Type.STRING, description="copy, move, delete, create_dir"),
                        "path": genai.types.Schema(type = genai.types.Type.STRING),
                        "destination": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="search_files",
                description="Searches for files in a directory",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "query": genai.types.Schema(type = genai.types.Type.STRING),
                        "path": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            
            # Cat 4: System
            types.FunctionDeclaration(
                name="system_power",
                description="Controls system power (shutdown, restart, etc)",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "action": genai.types.Schema(type = genai.types.Type.STRING, description="shutdown, restart, sleep, lock"),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="volume_control",
                description="Controls system volume",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "action": genai.types.Schema(type = genai.types.Type.STRING, description="set, mute, unmute"),
                        "level": genai.types.Schema(type = genai.types.Type.INTEGER, description="0-100"),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="brightness_control",
                description="Controls screen brightness",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "level": genai.types.Schema(type = genai.types.Type.INTEGER, description="0-100"),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_clipboard",
                description="Gets clipboard content",
                parameters=genai.types.Schema(type = genai.types.Type.OBJECT, properties = {})
            ),
            types.FunctionDeclaration(
                name="set_clipboard",
                description="Sets clipboard content",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "text": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            
            # Cat 5: Selenium
            types.FunctionDeclaration(
                name="browser_open",
                description="Opens a browser URL using Selenium",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "url": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="browser_type",
                description="Types text into a browser element",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "selector": genai.types.Schema(type = genai.types.Type.STRING),
                        "text": genai.types.Schema(type = genai.types.Type.STRING),
                        "by_method": genai.types.Schema(type = genai.types.Type.STRING, description="css, xpath, id, etc"),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="browser_click",
                description="Clicks a browser element",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "selector": genai.types.Schema(type = genai.types.Type.STRING),
                        "by_method": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="browser_get_text",
                description="Gets text from a browser element",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "selector": genai.types.Schema(type = genai.types.Type.STRING),
                        "by_method": genai.types.Schema(type = genai.types.Type.STRING),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="browser_scroll",
                description="Scrolls the browser page",
                parameters=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    properties = {
                        "direction": genai.types.Schema(type = genai.types.Type.STRING, description="up or down"),
                        "amount": genai.types.Schema(type = genai.types.Type.INTEGER),
                    }
                )
            ),
            types.FunctionDeclaration(
                name="browser_capture_full_page",
                description="Captures a full page screenshot",
                parameters=genai.types.Schema(type = genai.types.Type.OBJECT, properties = {})
            ),
        ]
    ),
    types.Tool(google_search=types.GoogleSearch()),
]
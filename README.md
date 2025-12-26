# 🤖 Gemini Live Desktop Agent

An advanced, multimodal AI assistant powered by **Google Gemini 2.5 Flash (Live API)**. This agent can see your screen or camera, listen to your voice, speak back, and perform complex actions on your computer including file management, system control, and web browsing via Selenium.

> **⚠️ WARNING:** This software grants an AI model direct control over your mouse, keyboard, file system, and terminal with **System Administrator** privileges. Use with extreme caution.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)
![Selenium](https://img.shields.io/badge/Web-Selenium-green)

---

## ✨ Features

### 🧠 Multimodal Core
*   **Real-time Audio/Video:** Uses Gemini Live API for low-latency voice interaction and video streaming (Screen or Camera).
*   **Context Aware:** The AI understands what is happening on your screen and responds accordingly.

### 🛠️ System Capabilities (Tool Use)
The agent is equipped with a wide range of tools:
*   **HID Control:** Move/Click mouse, scroll, type text, and use hotkeys (Copy/Paste, Alt+Tab, etc.).
*   **System Control:** Manage volume, screen brightness, clipboard, and power options (Shutdown/Restart).
*   **App Management:** Open/Close applications, switch windows, and list active processes.
*   **File System:** Read, write, move, copy, delete, and search files.

### 🌐 Web Automation
*   **Browser Control:** Uses **Selenium** to open URLs, click elements, type in forms, and scroll pages.
*   **Visual Feedback:** Can take screenshots of the browser to "see" the web page.

### 📰 Information Retrieval
*   **Live Info:** Fetch real-time Weather, News (General & Gaming), and Wikipedia articles.

---

## 📋 Prerequisites

Before running the agent, ensure you have the following:

1.  **Operating System:** Windows 10/11 (Required for most system tools like `pycaw`, `ctypes`, etc.).
2.  **Python:** **Version 3.11 or higher** (STRICT REQUIREMENT).
3.  **Google Chrome:** Strictly required for Selenium web automation tools.
4.  **Permissions:** **Administrator Rights** are required. The application will request elevation on startup.
5.  **API Keys:**
    *   **Google GenAI API Key:** Get it from [Google AI Studio](https://aistudio.google.com/).
    *   **WeatherAPI Key:** (Optional) For weather data.
    *   **NewsAPI Key:** (Optional) For news data.

---

## ⚠️ Critical Risks & Limitations

> [!CAUTION]
> **READ CAREFULLY**: This agent runs with elevated privileges.

### 1. Admin Privileges & System Risk
*   **High Risk:** The AI runs as **Administrator**. It has the power to **delete files**, **modify system registries**, and **uninstall software**.
*   **Unintended Actions:** While Gemini is intelligent, it can make mistakes or hallucinate. It might accidentally close the wrong window or delete a file if given vague instructions.

### 2. Browser Automation (Chrome Only)
*   **Chrome Dependency:** This project uses `chromedriver`. It **will not work** with Firefox, Edge, or Safari.
*   **Fragility:** Web automation is sensitive to layout changes. Tools may fail if a website updates its code.

### 3. Tool Stability
*   **Experimental Status:** Some tools (like `AppOpener` or complex HID macros) may fail to launch or hang the system.
*   **Screen Resolution:** Mouse coordinates are mapped to 1920x1080. Using a different resolution may cause clicking accuracy to drift.

---

## 🚀 Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/infinifunction/gemini-live-desktop-agent.git
    cd gemini-live-desktop-agent
    ```

2.  **Install Dependencies**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install `pyaudio` separately using a .whl file if pip install fails on Windows.*

3.  **Configuration**
    Open `main.py` and `tools.py` to insert your API Keys:
    *   `main.py`: Update `api_key="Your API Key"` inside the `client` initialization.
    *   `tools.py`: Update `API_KEY` variables in `getWeather()` and `get_news()` functions.

---

## 🎮 Usage

Run the main script using Python. You will be prompted for Administrator privileges (required for system control).

### Start with Screen Sharing (Default)
The AI will see your primary monitor.
```bash
python main.py --mode screen
```

### Start with Camera
The AI will see through your webcam.
```bash
python main.py --mode camera
```

### Audio Only
```bash
python main.py --mode none
```

**Controls:**
*   Talk to the AI through your microphone.
*   Press `Ctrl+C` in the terminal to stop.
*   The terminal will show tool execution logs and debug info.

---

## 📄 License
MIT License

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



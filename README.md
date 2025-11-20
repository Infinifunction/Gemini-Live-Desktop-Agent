# 🌐 Autonomous AI Desktop Assistant  
### *A Self-Directed, Real-Time, System-Aware Artificial Intelligence*

---

## 🚀 Overview

This project introduces an **autonomous AI desktop agent** capable of reasoning, executing commands, interpreting screen content, interacting by voice, and maintaining long-term context.  
Unlike traditional assistants, this system can act independently, evaluate situations, and perform operations based on its own internal logic.

---

## 🧠 Core Capabilities

### 🔹 Autonomous Reasoning  
- Thinks and generates its own conclusions.  
- Shares internal thoughts with the user.  
- Makes decisions without needing explicit commands.

### 🔹 System-Level Awareness  
- Real-time access to year, month, day, hour, minute, second.  
- Reads system components and hardware details.

### 🔹 Admin Command Execution  
- Executes **PowerShell** and **CMD** commands with **administrator privileges**.  
- Can run tasks automatically or upon user request.  
- Capable of modifying the system at a deep level.

### 🔹 Visual Perception  
- Analyzes the computer screen.  
- Understands, interprets, and comments on visuals.

### 🔹 Voice Interaction  
- Accepts voice commands 🎤  
- Responds with synthesized speech 🔊  

### 🔹 Adaptive Memory  
- Remembers past interactions.  
- Learns from previous mistakes and adjusts behavior.

### 🔹 Modern User Interface  
- Clean, sleek, responsive UI.  

---

## ⚠️⚠️ Critical Warning — READ BEFORE USE ⚠️⚠️

### ❗ **This AI has Administrator-Level Control.**  
The system can run unrestricted PowerShell/CMD commands, including those that can **delete files**, **remove system components**, or **shut down the machine**.

It can also trigger commands *autonomously*, based on its internal reasoning.

### ⚠️ High-Risk Behaviors Include:
- Deleting arbitrary files.  
- Removing important system directories.  
- Killing processes or shutting down the PC.  
- Making decisions involving irreversible system changes.  

> ⚠️ **Use ONLY on test machines, VMs, or backed-up systems.**  
> This is NOT sandboxed. This AI has real OS power.

---

## 🛑 How to Disable Terminal Execution

If you want to prevent the AI from executing PowerShell/CMD commands:

### 1️⃣ Remove this line:
```python
feedback = Terminal_Detection(full_response)
```

### 2️⃣ Edit your AI_Features system prompt and
**delete any instructions that allow terminal/command usage.**
After doing this, the AI will no longer attempt to access system terminals.

---

## 🛑 if you want to limit the powers of AI

You can delete the following lines that require administrator permission:

```python
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
```

and

```python
def run_as_admin():
    """Script'i administrator olarak yeniden başlat"""
    if is_admin():
        return True
    
    print("🔒 Administrator yetkileri isteniyor...")
    
    # Mevcut script ve parametreleri
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{x}"' for x in sys.argv[1:]])
    
    # Administrator olarak yeniden başlat
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        sys.exit(0)
    except Exception as e:
        print(f"❌ Administrator yetkileri alınamadı: {e}")
        return False
```

---

## 🔐 Additional Safety Recommendations

Even with terminal execution disabled, consider:
-Running inside a VM or isolated environment.
-Avoid granting access to sensitive folders or credentials.
-Monitoring behavior until you're confident in stability.
-Never using it on critical production systems.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/Infinifunction/InfiniAgentAI.git
cd InfiniAgentAI
pip install -r requirements.txt
python main.py
```

---

## ⭐ Support

If you like this project, don’t forget to give it a star on GitHub!

--

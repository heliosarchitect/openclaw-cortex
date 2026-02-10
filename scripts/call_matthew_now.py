#!/home/bonsaihorn/Projects/xtts-api-server/venv_xtts/bin/python3
"""
Make a Signal voice call to Matthew via desktop automation
Uses pyautogui directly - no skill dependencies
"""
import sys
import time
import pyautogui

def call_matthew():
    """
    Automate Signal Desktop to call Matthew
    """
    print("🌞 Helios initiating call to Matthew...")
    print("=" * 60)
    
    # Enable failsafe (move mouse to corner to abort)
    pyautogui.FAILSAFE = True
    
    # Step 1: Focus Signal window
    print("🎯 Step 1: Focusing Signal Desktop...")
    
    # Try to find Signal window
    all_windows = pyautogui.getWindowsWithTitle('Signal')
    
    if not all_windows:
        print("❌ Signal Desktop not found!")
        print("   Is Signal running?")
        return False
    
    signal_window = all_windows[0]
    signal_window.activate()
    time.sleep(0.5)
    
    print(f"✅ Found Signal: {signal_window.title}")
    
    # Step 2: Open search
    print("🎯 Step 2: Opening search (Ctrl+F)...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.3)
    
    # Step 3: Search for Matthew
    print("🎯 Step 3: Searching for Matthew...")
    pyautogui.write('Matthew', interval=0.05)
    time.sleep(0.5)
    
    # Step 4: Open conversation
    print("🎯 Step 4: Opening conversation...")
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # Step 5: Initiate voice call
    print("🎯 Step 5: Initiating voice call...")
    # Try keyboard shortcut first
    pyautogui.hotkey('alt', 'shift', 'v')
    time.sleep(0.5)
    
    print("✅ Call automation complete!")
    print("📞 If Signal supports Alt+Shift+V, the call should be ringing now...")
    print("   If not, you may need to click the call button manually.")
    
    return True

if __name__ == "__main__":
    try:
        success = call_matthew()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

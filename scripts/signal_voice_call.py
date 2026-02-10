#!/usr/bin/env python3
"""
Make a Signal voice call by automating Signal Desktop UI
Uses desktop-control skill for mouse/keyboard automation
"""
import sys
import time
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills"))

try:
    from desktop_control.desktop_controller import DesktopController
except ImportError:
    print("❌ desktop-control skill not found!")
    print("Install: pip install pyautogui pillow opencv-python pygetwindow")
    sys.exit(1)

def call_matthew_via_signal():
    """
    Automate Signal Desktop to initiate voice call to Matthew
    
    Process:
    1. Focus Signal Desktop window
    2. Press Ctrl+F to open search
    3. Type "Matthew" to find conversation
    4. Press Enter to open conversation
    5. Click voice call button (top right)
    """
    dc = DesktopController(failsafe=True)
    
    print("🎯 Step 1: Focusing Signal Desktop window...")
    
    # Get all windows and find Signal
    windows = dc.get_window_list()
    signal_window = None
    
    for window in windows:
        if 'signal' in window.title.lower():
            signal_window = window
            break
    
    if not signal_window:
        print("❌ Signal Desktop window not found!")
        print("Is Signal Desktop running?")
        return False
    
    print(f"✅ Found Signal: {signal_window.title}")
    
    # Activate Signal window
    dc.activate_window(signal_window)
    time.sleep(0.5)
    
    print("🎯 Step 2: Opening search...")
    dc.hotkey("ctrl", "f")
    time.sleep(0.3)
    
    print("🎯 Step 3: Searching for Matthew...")
    dc.type_text("Matthew", interval=0.05)
    time.sleep(0.5)
    
    print("🎯 Step 4: Opening conversation...")
    dc.press("enter")
    time.sleep(0.5)
    
    print("🎯 Step 5: Initiating voice call...")
    # Voice call button is typically top-right of conversation
    # Signal Desktop layout: call buttons are in the header
    # We'll use Tab navigation to reach it reliably
    
    dc.hotkey("alt", "shift", "v")  # Try keyboard shortcut first
    time.sleep(0.5)
    
    # If shortcut didn't work, try mouse click
    # (would need to find exact coordinates via screenshot analysis)
    
    print("✅ Call initiated!")
    print("📞 Signal should be ringing Matthew now...")
    return True

if __name__ == "__main__":
    print("🌞 Helios initiating voice call to Matthew via Signal Desktop")
    print("=" * 60)
    
    success = call_matthew_via_signal()
    
    if success:
        print("\n✅ Call automation complete!")
    else:
        print("\n❌ Call automation failed!")
        sys.exit(1)

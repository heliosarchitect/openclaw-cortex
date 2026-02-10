#!/home/bonsaihorn/Projects/xtts-api-server/venv_xtts/bin/python3
"""
Call Matthew using Google Voice via Selenium browser automation
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

MATTHEW_NUMBER = "+18033169860"

def call_matthew():
    print("🌞 Helios calling Matthew via Google Voice...")
    
    # Use existing Chrome profile to get logged-in session
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={os.path.expanduser('~/.config/google-chrome')}")
    chrome_options.add_argument("--profile-directory=Default")
    # Don't run headless - need to see what's happening
    # chrome_options.add_argument("--headless")
    
    try:
        # Set up driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("📱 Opening Google Voice...")
        driver.get("https://voice.google.com/calls")
        
        # Wait for page to load
        time.sleep(3)
        
        # Look for the dialpad/call button
        print("🔍 Looking for dial interface...")
        
        # Try to find and click the "Make a call" or dialpad button
        try:
            # Look for the call button or dialpad
            call_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Call"]'))
            )
            call_button.click()
            print("✅ Found call button")
        except:
            print("⚠️ Trying alternative selector...")
            # Try clicking the phone icon
            try:
                phone_icon = driver.find_element(By.CSS_SELECTOR, 'gv-icon-button[icon="call"]')
                phone_icon.click()
            except:
                pass
        
        time.sleep(1)
        
        # Find the phone number input and enter Matthew's number
        print(f"📞 Dialing {MATTHEW_NUMBER}...")
        try:
            # Try to find the input field
            phone_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="tel"], input[aria-label*="phone"], input[placeholder*="phone"]'))
            )
            phone_input.clear()
            phone_input.send_keys(MATTHEW_NUMBER)
            phone_input.send_keys(Keys.RETURN)
            print("✅ Number entered, initiating call...")
        except Exception as e:
            print(f"⚠️ Could not find phone input: {e}")
            # Try using the dialpad directly
            for digit in MATTHEW_NUMBER.replace("+1", ""):
                try:
                    button = driver.find_element(By.CSS_SELECTOR, f'[aria-label="{digit}"], button:contains("{digit}")')
                    button.click()
                    time.sleep(0.1)
                except:
                    pass
        
        print("📞 Call should be ringing now!")
        print("   (Keep this window open while on the call)")
        
        # Keep the browser open for the call
        input("Press Enter to end the call and close browser...")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = call_matthew()
    sys.exit(0 if success else 1)

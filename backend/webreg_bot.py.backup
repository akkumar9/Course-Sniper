# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import json
from datetime import datetime
import platform
import subprocess

class WebRegBot:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        
        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        
        # Prevent browser from stealing focus
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })
        
        # Set a realistic user agent
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Additional anti-detection via JavaScript
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 30)
    
    def load_cookies(self, cookie_file='cookies.json'):
        try:
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            
            self.driver.get("https://act.ucsd.edu/webreg2/start")
            time.sleep(3)
            
            for cookie in cookies:
                try:
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            print("[OK] Cookies loaded")
            return True
        except:
            print("[INFO] No cookies file found")
            return False
    
    def save_cookies(self, cookie_file='cookies.json'):
        cookies = self.driver.get_cookies()
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=4)
        print(f"[OK] Cookies saved")
    
    def is_logged_in(self):
        """Check if we're on the main WebReg page"""
        try:
            current_url = self.driver.current_url
            
            # Success: on the main page
            if 'webreg2/main' in current_url:
                return True
            
            # Check if we can see the search box (also means logged in)
            try:
                self.driver.find_element(By.ID, 'search-div-t-t1-i1')
                return True
            except:
                pass
            
            return False
        except:
            return False
    
    def is_on_login_page(self):
        """Check if we're stuck on the login/SSO page"""
        try:
            current_url = self.driver.current_url
            
            # These URLs mean we're NOT logged in
            if any(x in current_url for x in [
                'tritON/profile/SAML2',
                'sso.ucsd.edu',
                'login.ucsd.edu',
                'duosecurity.com'
            ]):
                return True
            
            return False
        except:
            return False
    
    def click_go_button_auto(self):
        """Automatically find and click the Go button with proper waiting"""
        try:
            print("[AUTO] Looking for Go button...")
            
            # Wait longer for page to fully load
            time.sleep(5)
            
            # Check if we're already past the Go button
            if self.is_logged_in():
                print("[INFO] Already past Go button - on main page")
                return True
            
            # Method 1: Find by value attribute with explicit wait
            try:
                print("[TRY 1] Looking for Go button by value...")
                go_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@value='Go' or @value='GO']"))
                )
                
                if go_button.is_displayed() and go_button.is_enabled():
                    print("[FOUND] Go button!")
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", go_button)
                    time.sleep(1)
                    
                    # Wait for it to be clickable
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@value='Go' or @value='GO']"))
                    )
                    
                    # Click it
                    try:
                        go_button.click()
                        print("[CLICK] Clicked Go button!")
                    except:
                        # Try JavaScript click
                        self.driver.execute_script("arguments[0].click();", go_button)
                        print("[CLICK] Clicked Go button (JS)!")
                    
                    time.sleep(6)  # Wait longer for navigation
                    return True
                    
            except Exception as e:
                print(f"[INFO] Method 1 failed: {e}")
            
            # Method 2: JavaScript search for any button with "Go"
            try:
                print("[TRY 2] JavaScript search...")
                result = self.driver.execute_script("""
                    var buttons = document.querySelectorAll('input[type="button"], button');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = (buttons[i].value || buttons[i].textContent || '').trim();
                        if (text === 'Go' || text === 'GO') {
                            buttons[i].scrollIntoView({block: 'center'});
                            setTimeout(function() { buttons[i].click(); }, 500);
                            return true;
                        }
                    }
                    return false;
                """)
                
                if result:
                    print("[CLICK] Clicked Go button (JS)!")
                    time.sleep(6)
                    return True
            except Exception as e:
                print(f"[INFO] Method 2 failed: {e}")
            
            print("[INFO] No Go button found")
            return False
            
        except Exception as e:
            print(f"[ERROR] Go button error: {e}")
            return False
    
    def login_manual(self, use_cookies=True):
        print("\n" + "="*60)
        print("LOGIN TO WEBREG")
        print("="*60)
        
        if use_cookies and self.load_cookies():
            print("[NAVIGATE] Going to WebReg...")
            self.driver.get("https://act.ucsd.edu/webreg2/start")
            time.sleep(6)  # Longer initial wait
            
            current_url = self.driver.current_url
            print(f"[INFO] Current URL: {current_url}")
            
            # Check if stuck on login page (cookies expired)
            if self.is_on_login_page():
                print("[ERROR] Cookies expired - stuck on login page")
                print("[INFO] You'll need to log in manually")
                print(f"[BAD URL] {current_url}")
                
                print("\n*** MANUAL LOGIN REQUIRED ***")
                print("1. Complete the login in the browser")
                print("2. Complete Duo authentication")
                print("3. Select 'Winter Quarter 2026'")
                print("4. Click the 'Go' button")
                print("5. Wait for the Course Enrollment page")
                print("********************************\n")
                
                input("Press Enter when you're on the Course Enrollment page...")
                self.save_cookies()
                
                if self.is_logged_in():
                    print("[SUCCESS] Logged in!")
                    return True
                else:
                    print("[ERROR] Still not logged in")
                    return False
            
            # Check if already logged in
            if self.is_logged_in():
                print("[SUCCESS] Already logged in!")
                return True
            
            # Try automatic Go button (with retry)
            print("[AUTO] Attempting automatic Go button click...")
            
            max_retries = 2
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"[RETRY] Attempt {attempt + 1}/{max_retries}...")
                    time.sleep(3)
                
                if self.click_go_button_auto():
                    time.sleep(4)
                    
                    # Check if logged in
                    if self.is_logged_in():
                        print("[SUCCESS] Automatic login worked!")
                        return True
                    
                    # Check for error message
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
                        if 'contact' in body_text or 'error' in body_text or 'problem' in body_text:
                            print(f"[WARNING] Error detected on page")
                            if attempt < max_retries - 1:
                                print("[INFO] Refreshing page and retrying...")
                                self.driver.get("https://act.ucsd.edu/webreg2/start")
                                time.sleep(5)
                                continue
                    except:
                        pass
            
            # All automatic attempts failed - manual intervention
            print("\n" + "="*60)
            print("MANUAL STEP REQUIRED")
            print("="*60)
            print("Automatic Go button failed after retries.")
            print("The browser is open. Please:")
            print("1. Refresh the page if needed")
            print("2. Select 'Winter Quarter 2026'")
            print("3. Click the 'Go' button manually")
            print("4. Wait for the Course Enrollment page")
            print("="*60 + "\n")
            
            input("Press Enter when you're on the Course Enrollment page...")
            
            self.save_cookies()
            
            if self.is_logged_in():
                print("[SUCCESS] You're logged in!")
            else:
                print("[INFO] Continuing anyway...")
            
            return True
            
        else:
            # No cookies - full manual login
            print("[LOGIN] No cookies found - opening login page...")
            self.driver.get("https://act.ucsd.edu/webreg2/start")
            
            print("\n" + "="*60)
            print("FIRST TIME LOGIN")
            print("="*60)
            print("Please:")
            print("1. Enter your credentials and log in")
            print("2. Complete Duo authentication")
            print("3. Select 'Winter Quarter 2026'")
            print("4. Click the 'Go' button")
            print("5. Wait for the Course Enrollment page")
            print("="*60 + "\n")
            
            input("Press Enter when you're on the Course Enrollment page...")
            self.save_cookies()
            print("[SUCCESS] Login complete!")
            return True
    
    def search_course(self, subject, course_num):
        try:
            if not self.is_logged_in():
                print("[ERROR] Not logged in!")
                return None
            
            search_query = f"{subject} {course_num}"
            print(f"\n[SEARCH] Searching for: {search_query}")
            
            # Click search box
            containers = self.driver.find_elements(By.CSS_SELECTOR, '[id^="s2id_search"]')
            for c in containers:
                if c.is_displayed():
                    c.click()
                    break
            time.sleep(0.5)
            
            # Type
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.select2-input'))
            )
            search_input.clear()
            time.sleep(0.2)
            search_input.send_keys(search_query)
            time.sleep(2)
            
            # Select
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)
            
            # Search
            search_btn = self.driver.find_element(By.ID, 'search-div-t-b1')
            search_btn.click()
            time.sleep(1)
            
            # Wait for results
            print("[WAIT] Waiting for results...")
            for i in range(15):
                time.sleep(1)
                rows = self.driver.execute_script("return $('#search-div-b-table .jqgrow').length;")
                if rows > 0:
                    print(f"[SUCCESS] Found {rows} result(s)")
                    time.sleep(2)
                    break
            
            if rows == 0:
                print("[WARNING] No results")
                return None
            
            # EXPAND - click the course header!
            print("\n[EXPAND] Looking for course header to click...")
            
            expanded = False
            
            # Method 1: Click the nested table with the course name
            try:
                course_header = self.driver.find_element(By.ID, 'search-group-header-id')
                print("[EXPAND] Found course header table")
                
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", course_header)
                time.sleep(0.5)
                
                # Click it
                try:
                    course_header.click()
                    print("[OK] Clicked course header!")
                    expanded = True
                except:
                    self.driver.execute_script("arguments[0].click();", course_header)
                    print("[OK] JS clicked course header!")
                    expanded = True
                
                time.sleep(4)
                
            except Exception as e:
                print(f"[TRY 1 FAILED] {e}")
            
            # Method 2: Click the expand icon/button
            if not expanded:
                try:
                    print("[EXPAND] Looking for expand icon...")
                    expand_icon = self.driver.find_element(By.CSS_SELECTOR, '.ui-icon-circlesmall-plus')
                    expand_icon.click()
                    print("[OK] Clicked expand icon!")
                    expanded = True
                    time.sleep(4)
                except Exception as e:
                    print(f"[TRY 2 FAILED] {e}")
            
            # Method 3: Click the row
            if not expanded:
                try:
                    print("[EXPAND] Clicking first row...")
                    rows_elements = self.driver.find_elements(By.CSS_SELECTOR, '#search-div-b-table .jqgrow')
                    if rows_elements:
                        self.driver.execute_script("arguments[0].click();", rows_elements[0])
                        print("[OK] Clicked row!")
                        expanded = True
                        time.sleep(4)
                except Exception as e:
                    print(f"[TRY 3 FAILED] {e}")
            
            if not expanded:
                print("[WARNING] Could not expand course!")
            
            # Save debug
            self.save_debug('results.html')
            self.driver.save_screenshot('results.png')
            
            # Parse using the correct method
            print("\n[PARSE] Parsing seat data...")
            seats_info = self.parse_results_from_table()
            
            return seats_info
                
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_results_from_table(self):
        """
        Parse seat data from table cells with aria-describedby attributes
        """
        try:
            # Find cells with available seats - "AVAIL_SEAT"
            avail_cells = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'td[aria-describedby*="AVAIL_SEAT"]'
            )
            
            # Find cells with total seats - "SCTN_CPCTY_QTY" (Section Capacity Quantity)
            total_cells = self.driver.find_elements(
                By.CSS_SELECTOR,
                'td[aria-describedby*="SCTN_CPCTY_QTY"]'
            )
            
            print(f"[OK] Found {len(avail_cells)} available seat cells")
            print(f"[OK] Found {len(total_cells)} total seat cells")
            
            if len(avail_cells) == 0 or len(total_cells) == 0:
                print("[WARNING] No seat cells found - might not be expanded?")
                return None
            
            # Extract the numbers
            sections = []
            for i in range(min(len(avail_cells), len(total_cells))):
                try:
                    avail_text = avail_cells[i].text.strip()
                    total_text = total_cells[i].text.strip()
                    
                    # Convert to int
                    available = int(avail_text) if avail_text.isdigit() else 0
                    total = int(total_text) if total_text.isdigit() else 0
                    
                    if total > 0:  # Valid section
                        section = {
                            'available': available,
                            'total': total,
                            'full': available == 0
                        }
                        sections.append(section)
                        
                        print(f"  Section {i+1}: {available}/{total} seats")
                        
                except Exception as e:
                    print(f"  [SKIP] Section {i+1}: {e}")
                    continue
            
            if not sections:
                print("[ERROR] No valid sections found")
                return None
            
            # The first section is usually the main lecture
            main = sections[0]
            
            # Check if ANY section has availability (not just main)
            any_available = any(s['available'] > 0 for s in sections)
            total_available = sum(s['available'] for s in sections)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'sections': sections,
                'main_section': main,
                'total_sections': len(sections),
                'total_available': total_available,
                'has_availability': any_available  # True if ANY section has seats
            }
            
            print(f"\n[SUMMARY] Main section: {main['available']}/{main['total']} seats")
            print(f"[SUMMARY] Total available: {total_available} seats across all sections")
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Parse failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_debug(self, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"[SAVE] Saved to {filename}")
        except:
            pass
    
    def play_alert_sound(self):
        """Play a sound alert when seats are found"""
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                # Play system alert sound
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
                subprocess.run(["say", "Seats available!"], check=False)
            elif system == "Linux":
                # Try to play a beep
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], check=False)
            elif system == "Windows":
                # Windows beep
                import winsound
                winsound.Beep(1000, 1000)  # 1000 Hz for 1 second
        except:
            # Fallback: print bell character
            print("\a" * 5)  # Bell sound
    
    def monitor_course(self, subject, course_num, check_interval=30):
        print(f"\n{'='*60}")
        print(f"MONITORING: {subject} {course_num}")
        print(f"Interval: {check_interval} seconds")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*60}\n")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n{'='*60}")
                print(f"Check #{iteration} - {timestamp}")
                print(f"{'='*60}")
                
                result = self.search_course(subject, course_num)
                
                if result:
                    main = result.get('main_section', {})
                    total_avail = result.get('total_available', 0)
                    
                    if result['has_availability']:
                        # Find which sections have seats
                        sections_with_seats = [s for s in result['sections'] if s['available'] > 0]
                        
                        print("\n" + "="*60)
                        print("*** SEATS AVAILABLE! ***")
                        print("="*60)
                        print(f"{subject} {course_num}: {total_avail} total seats available!")
                        print(f"\nSections with openings:")
                        for idx, s in enumerate(sections_with_seats[:10]):  # Show first 10
                            print(f"  - {s['available']}/{s['total']} seats")
                        if len(sections_with_seats) > 10:
                            print(f"  ... and {len(sections_with_seats) - 10} more sections")
                        print("="*60)
                        
                        # Play alert sound!
                        print("[ALERT] Playing sound notification...")
                        self.play_alert_sound()
                        
                        response = input("\nContinue? (y/n): ")
                        if response.lower() != 'y':
                            break
                    else:
                        print(f"[STATUS] No seats available (0 total)")
                else:
                    print("[WARNING] No results")
                
                print(f"\n[SLEEP] Waiting {check_interval}s...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n[STOP] Stopped")
    
    def close(self):
        try:
            self.driver.quit()
            print("\n[CLOSE] Browser closed")
        except:
            pass

if __name__ == "__main__":
    bot = WebRegBot(headless=False)
    
    try:
        print("\n" + "="*60)
        print("UCSD WEBREG MONITOR")
        print("="*60)
        
        bot.login_manual(use_cookies=True)
        
        print("\n" + "="*60)
        print("TEST SEARCH (Optional)")
        print("="*60)
        
        test = input("Run a test search first? (y/n): ")
        
        if test.lower() == 'y':
            test_subject = input("Subject (e.g., CSE): ").strip().upper()
            test_course = input("Course (e.g., 100): ").strip()
            
            result = bot.search_course(test_subject, test_course)
            
            if result:
                print("\n" + "="*60)
                print("RESULTS:")
                print("="*60)
                print(json.dumps(result, indent=2))
        
        print("\n" + "="*60)
        monitor = input("Start monitoring? (y/n): ")
        
        if monitor.lower() == 'y':
            subject = input("Subject (CSE): ").strip().upper() or "CSE"
            course = input("Course (100): ").strip() or "100"
            interval = input("Interval (30): ").strip()
            interval = int(interval) if interval.isdigit() else 30
            
            bot.monitor_course(subject, course, interval)
        
        input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.close()
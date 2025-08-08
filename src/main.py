from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime, timedelta
import argparse
import sys
import ast

def parse_args():
    parser = argparse.ArgumentParser(description='action.yml arguments')
    parser.add_argument('--username', type=str, help='Username (case-insensitive)')
    parser.add_argument('--password', type=str, help='Password (case-insensitive)')
    parser.add_argument('--building_name', type=str, help='Select a Building')
    parser.add_argument('--floor', type=str, help='Floor Acronym Number, ex. JT01')
    parser.add_argument('--workstation', type=str, help='WorkPoint-WorkStation')
    parser.add_argument('--workstation_backup',type=str, default='[]', required=False, help='WorkPoint-WorkStation-Backup')
    parser.add_argument('--advance_reservation',action='store_true', required=False, help='Book 4 weeks and one day ahead')

    return parser.parse_args()

class archibus_scheduler():
    def __init__(self, args):
        # get user input passed by args
        self.username = args.username
        self.password = args.password
        self.building_name = args.building_name.replace("-", " ")
        self.floor = args.floor
        self.workstation = args.workstation
        self.workstation_backup = ast.literal_eval(args.workstation_backup)
        self.advance_reservation = args.advance_reservation

        # Dates
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        # Check if advance_reservation to change from 4 weeks to 4 weeks + 1 day
        if self.advance_reservation:
            self.next_month = str((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=4, days=1)).strftime("%Y-%m-%d"))
            self.next_month_day = str((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=4, days=1)).strftime("%#d")).lstrip("0")
        else:
            self.next_month = str((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=4)).strftime("%Y-%m-%d"))
            self.next_month_day = str((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=4)).strftime("%#d")).lstrip("0")

        # Seat formatted datetime
        self.seat_date = datetime.strptime(self.next_month, '%Y-%m-%d').strftime("Choose %A, %B %d, %Y")
        suffix = "th" if 11 <= int(self.next_month_day) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(int(self.next_month_day) % 10, "th")
        self.seat_date = self.seat_date.replace(f"{int(self.next_month_day):02d}", f"{int(self.next_month_day)}{suffix}",1)

        # validate archnemesis
        if self.workstation == '101' and self.floor == 'JT07' and self.username != 'EVANJUS':
            raise Exception('Workstation is unavailable.')

    ## Setup Webdriver
    def setup(self):

        service = Service(ChromeDriverManager().install())
        chrome_options = webdriver.ChromeOptions() 
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless=new")  # Headless mode
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering
        chrome_options.add_argument("--remote-debugging-port=9222")  # Required for headless mode
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument("--disable-notifications")

        #self.driver = webdriver.Chrome(service=service, options = chrome_options)
        # Establish connection to the Dockerized Selenium Grid
        # Define the Selenium Grid URL (localhost:4444 in your case)
        SELENIUM_GRID_URL = 'http://localhost:4444/wd/hub'
        self.driver = webdriver.Remote(
            command_executor=SELENIUM_GRID_URL,
            options=chrome_options,
            keep_alive=True
        )
        
        # Min Page Load Time
        self.driver.implicitly_wait(15) 

        # Min wait time for element
        self.wait = WebDriverWait(self.driver, 10)

    # Known Popups
    def popups(self):
        try:
            ## Recommended seat assignment
            reassignment = self.driver.find_element(By.CSS_SELECTOR, '[class*="DontShowButton"]') 
            reassignment.click()
        except NoSuchElementException:
            pass
        try:
            # Time slot of today's booking has passed
            reassignment = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
            reassignment.click()
        except NoSuchElementException:
            pass
        try:
            # A seat has already been booked, do you want to rebook
            reassignment = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Yes')]")
            reassignment.click()
        except NoSuchElementException:
            pass

    # Selenium Custom Seat Selection
    def seat_selection(self):
        seat_options = [self.workstation]
        seat_options.extend(self.workstation_backup)
        seat_found = False # flag to break if found a seat

        # Search all combinations
        for seat in seat_options:
            if seat_found:
                break

            workstation_formats = [
                f"//p[text() = '{seat} - Primary Individual Open/Primaire, individuel et ouvert']",
                f"//p[text() = '{self.floor}-{int(seat):02} - Secondary Individual/Secondaire et individuel']"
                ]
            for format in workstation_formats:
                try:
                    input_selected_seat = self.driver.find_element(By.XPATH, format)
                    print(f"Seat Selected: {input_selected_seat.text}")
                    seat_found = True
                    break
                except:
                    print(f"Seat Unavailable: {seat}")
        # Select seat
        try:
            input_selected_seat.click()
        except:
            raise NoSuchElementException("No available seat found")  # Raise an exception if neither seat is available

    # Selenium Actions to Walk Webpage
    def actions(self):

        # Setup
        self.setup()

        # Archibus Webpage
        self.driver.get("https://pathfinder.horizantsolutions.com/archibus/schema/ab-products/essential/workplace/index.html")

        # Wait for full page load
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        ## Login Page
        input_username = self.wait.until(EC.presence_of_element_located((By.ID, 'logon-user-input')))
        input_username.send_keys(self.username)

        input_password = self.wait.until(EC.presence_of_element_located((By.ID, 'logon-password-input')))
        input_password.send_keys(self.password)

        input_log_in = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="logon-sign-in-btn"]') # 'logon-sign-in-btn'
        input_log_in.click()
        print(f"User Logged In")

        # Menu Selection - Create Workspace Booking
        # workspace-path-1 : this pops up in some paths depending on user-login 
        try:
            input_workspace_booking = self.driver.find_element(By.XPATH, f"//div[contains(text(), 'CREATE WORKSPACE BOOKING')]")
            input_workspace_booking.click()
            print(f'Loading Create Workspace Booking')
            time.sleep(10)
        except NoSuchElementException:
            print("Pre-loaded into Create Workstation Booking")

        # Building Selection
        input_building = self.driver.find_element(By.XPATH, f"//div[contains(text(), {self.building_name})]")
        input_building.click()
        print(f'Selected Building')
        time.sleep(2)

        ## Workspace Menu
        # workspace-path-2 : this pops up in some paths depending on user-login 
        try:
            input_workspace_booking = self.driver.find_element(By.XPATH, f"//h3[contains(text(), 'Workspaces')]")
            input_workspace_booking.click()
            print(f'Loading Create Workspace Booking')  
            time.sleep(2)
            self.popups() # pop-up indicating previous day no longer available
        except NoSuchElementException:
            print("Pre-loaded into Building Booking")
            time.sleep(2)

        # Alternative Building Selection Path
        # even though building is selected in prior step sometimes the building appears empty, try search menu for building
        try:
            input_building_search = self.driver.find_element(By.XPATH, f"//div[contains(text(), 'Buildings')]")
            input_building_search.click()
            print(f'Searching for Building in Dropdown')
            time.sleep(30) # longer load on dropdown search
            self.popups()       

            print('Waiting for overlay to dissappear')
            def wait_for_overlay_to_disappear(driver, timeout=20):
                WebDriverWait(driver, timeout).until(
                    lambda d: all(not el.is_displayed() for el in d.find_elements(By.CLASS_NAME, "ReactModal__Overlay"))
                )
            wait_for_overlay_to_disappear(self.driver)

            input_building = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{self.building_name}')]")
            self.driver.execute_script("arguments[0].click();", input_building)
            print(f'Selected Building')
            time.sleep(2)

        except NoSuchElementException as e:
            print(f'Exception: {e}')
            print("Building Already Selected")

        ### Workspace Booking
        # Manual time delays added as selenium able to find/click elements but fails on final booking button
        # WebDriverWait, ActionChains considered but did not resolve the issue

        # Known stop for popups
        self.popups()

        ## StartDate
        calendar = self.driver.find_element(By.ID, 'startData_icon')
        calendar.click()

        input_next_month = self.driver.find_element(By.XPATH, "//button[@aria-label = 'Select next month']")
        input_next_month.click()

        # Look for a class with the day value of 1 month from today
        # ActionChains used to simulate click of date, more specific aria-label used 
        date = self.driver.find_element(By.XPATH, f"//div[@aria-label='{self.seat_date}']")
        actions = ActionChains(self.driver)
        actions.move_to_element(date).click().perform()
        print(f'Date Selected: {self.next_month}')
        time.sleep(2)

        # Select Floor
        input_floor = self.driver.find_element(By.XPATH, f"//div[text() = '{self.floor}']")
        input_floor.click()
        print(f'Floor Selected: {self.floor}')
        time.sleep(2)

        # Search Parameters
        input_search = self.driver.find_element(By.XPATH, "//button[text() = 'Search']")
        input_search.click()
        time.sleep(2)

        ## Select Seat
        self.seat_selection()
        time.sleep(2)

        # Book Seat
        input_book_seat = self.driver.find_element(By.XPATH, "//button[text() = 'Book']")
        input_book_seat.click()
        time.sleep(2)
        print('Select Book Seat')

        # Book for 'Myself'
        input_book_myself = self.driver.find_element(By.XPATH, "//span[text() = 'Myself']")
        input_book_myself.click()
        time.sleep(2)
        print("Booking for 'Myself'")

        # Booking Seat
        input_book_seat = self.driver.find_element(By.XPATH, "//button[text() = 'BOOK']")
        input_book_seat.click()
        time.sleep(2)

        # Confirmation page
        # Confirmation page
        self.popups()
        input_confirmation = self.driver.find_element(By.XPATH, "//button[contains(text(),'GO TO MAIN')]") # 'logon-sign-in-btn'
        input_confirmation.click()
        print("Confirmation seat is booked")

        self.driver.close()


if __name__ == "__main__":

    # simulated args for testing
    # sys.argv = [ 'main.py',
    #              '--username', 'LASTFIRST',
    #              '--building_name', 'BUILDING',
    #              '--floor', 'ACRONYMNUMBER',    
    #              '--workstation', 'NUMBER',
    #              '--password', 'PASSWORD'
    #              ]

    args = parse_args()
    scheduler = archibus_scheduler(args)
    scheduler.actions()

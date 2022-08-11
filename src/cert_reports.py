import time
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tkinter import messagebox
import sys
import os


def error_message(string):
    messagebox.showerror("Error", string)


def message(string):
    messagebox.showinfo("Info", string)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class Browser:
    def __init__(self, username, password, lea_codes, term_input, year, file_location, file_type, window, curr_school, curr_link):
        self.username = username
        self.password = password
        self.lea_codes = lea_codes
        self.term_input = term_input
        self.year = year
        self.file_location = file_location.replace("/", "\\")
        self.file_type = file_type
        self.window = window
        self.curr_link = curr_link
        self.curr_school = curr_school

    def close_browser(self):
        self.driver.quit()

    def run_browser(self, dry_run):
        try:
            if self.curr_school is not None:
                index = self.lea_codes.index(self.curr_school)
                self.lea_codes = self.lea_codes[index:]
            counter = 0
            total_links = 0
            for school in self.lea_codes:
                lea_code = school[-7:]
                options = webdriver.ChromeOptions()
                if not dry_run:
                    school_dir = os.path.join(self.file_location, school[:-10])
                    if not os.path.exists(school_dir):
                        os.mkdir(school_dir)
                    prefs = {'download.default_directory': school_dir}
                    options.add_experimental_option('prefs', prefs)
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1000")
                self.driver = webdriver.Chrome(resource_path('./driver/chromedriver.exe'), options=options)
                with self.driver as driver:
                    driver.get(
                        "https://identity.calpads.org/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id"
                        "%3DCALPADSWebClient%26redirect_uri%3Dhttps%253A%252F%252Fwww.calpads.org%252Fsignin-oidc%26response_type"
                        "%3Dcode%2520id_token%26scope%3Dopenid%2520profile%26max_age%3D14400%26response_mode%3Dform_post%26nonce"
                        "%3D637932857194244885"
                        ".ZmJmYTQwODctZTA2OS00YjFkLWIzNjUtMDAwZGE1ZDVhYmFhNzU5ZjJlNzQtZTU2YS00ZTBkLWI0N2QtMWY5ZWQyYjQ0NzNl"
                        "%26state%3DCfDJ8MAX9CfV_fxHksEmX8cRo1gaNmYPrDIm0NoCebdA9"
                        "-jHUPz0YNNjeol3Oxt1oOi11cpt3aABtNa_ktJ09_rneGhJ20hwSkY763s"
                        "--xWUNwYFQZhrEPIhX9fOV1Bin6fzjBMrAD371qhM9oJbKX12bdafltDL_Zz4rmgDTPktC"
                        "-U8hpuAE9czfpqbWuEMAotVLvaP9kja1fbhIOUF8fQd4rLwta5g0vdCU0DpnvoWCN7SbHjWkVyNsx7DO3xHmQR_YBj50f"
                        "-xW5SXuOlTs_xUXmNDCeJbwAGergTVZNdzKW-i%26x-client-SKU%3DID_NETSTANDARD2_0%26x-client-ver%3D5.5.0.0")
                    assert "CALPADS" in driver.title
                    driver.find_element(By.ID, 'Username').send_keys(self.username)
                    driver.find_element(By.ID, 'Password').send_keys(self.password)
                    terms_and_conditions = driver.find_element(By.CLASS_NAME, 'custom-control-label').click()
                    submit = driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()
                    try:
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'dd__logOut')))
                        print('Successful login')
                    except TimeoutException:
                        error_message("Incorrect login/password")
                        self.window.enable_button()
                        driver.quit()
                    time.sleep(2)
                    try:
                        driver.get('https://www.calpads.org/StateReporting/Certification')
                        self.switch_lea(lea_code)
                        self.curr_school = school
                        year_selector = Select(driver.find_element(By.XPATH, '//*[@id="AcademicYear"]'))
                        year_selector.select_by_value(self.year)
                    except:
                        print("Switching to the term and year failed")
                        return

                    row = driver.find_element(By.XPATH, '//*[@id="CertStatusGrid"]/table/tbody')
                    row_list = row.find_elements(By.TAG_NAME, 'tr')

                    term_list = {}
                    for r in row_list:
                        link = r.find_element(By.XPATH,'.//*[1]/a').get_attribute('href')
                        term = r.find_element(By.XPATH, './/*[3]').text
                        cert_status = r.find_element(By.XPATH, './/*[6]').text
                        string = term + " - " + cert_status
                        term_list[string] = link

                    if dry_run:
                        self.window.update_term(term_list)
                        driver.close()
                        message("Please enter which report period you want now")
                        return
                    terms = list(term_list.keys())
                    for t_input in self.term_input:
                        for t in terms:
                            if t_input == t:
                                driver.get(term_list[t])
                        link_list = []
                        cert_reports = driver.find_element(By.XPATH, '//*[@id="certReports"]')
                        cert_reports = cert_reports.find_elements(By.TAG_NAME, "a")
                        for c in cert_reports:
                            link_list.append(c.get_attribute('href'))
                        if len(self.term_input) > 1:
                            total_links = len(link_list)

                        if total_links == 0:
                            total_links = len(self.lea_codes) * len(link_list)
                        if self.curr_link is not None:
                            index = link_list.index(self.curr_link)
                            link_list = link_list[index:]
                            total_links -= index
                        for curr_link in link_list:
                            self.curr_link = curr_link
                            driver.get(curr_link)
                            try:
                                WebDriverWait(driver, 30).until(
                                    EC.frame_to_be_available_and_switch_to_it(
                                        (By.XPATH, '//*[@id="reports"]/div/div/div/iframe')))
                            except TimeoutError:
                                error_message("The page took too long to load")
                                self.window.get_browser_info(self.curr_school, self.curr_link)
                                driver.quit()
                                return
                            time.sleep(2)
                            try:
                                status = Select(driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl08_ctl07_ddValue"]'))
                                status.select_by_index(1)
                            except:
                                pass
                            time.sleep(2)
                            try:
                                submit = driver.find_element(By.ID, 'ReportViewer1_ctl08_ctl00')
                                webdriver.ActionChains(driver).move_to_element(submit).click(submit).perform()
                            except:
                                pass
                            try:
                                print("Waiting for document " + curr_link)
                                WebDriverWait(driver, 900).until(EC.text_to_be_present_in_element_attribute(
                                    (By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_ButtonLink"]'), 'aria-disabled',
                                    'false'))
                            except:
                                error_message("The report took too long to load!")
                                self.window.get_browser_info(self.curr_school, self.curr_link)
                                driver.quit()
                                return

                            time.sleep(1)
                            save = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_ButtonLink"]')
                            driver.execute_script("arguments[0].click();", save)
                            time.sleep(1)

                            file = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_Menu"]')
                            if self.file_type == 'PDF':
                                pdf = file.find_element(By.XPATH, "//*[text()='PDF']")
                                webdriver.ActionChains(driver).move_to_element(pdf).click(pdf).perform()
                            elif self.file_type == 'CSV':
                                csv = file.find_element(By.XPATH, "//*[text()='CSV']")
                                webdriver.ActionChains(driver).move_to_element(csv).click(csv).perform()
                            elif self.file_type == 'EXCEL':
                                excel = file.find_element(By.XPATH, "//*[text()='EXCEL']")
                                webdriver.ActionChains(driver).move_to_element(excel).click(excel).perform()
                            else:
                                error_message("The file type specified does not exist")
                            counter += 1
                            if len(self.term_input) > 1:
                                print("Downloaded " + str(counter) + "/" + str(total_links) + " reports in " + t_input + " for " + school)
                            else:
                                print("Downloaded " + str(counter) + "/" + str(total_links) + " reports.")
                        self.curr_link = None
                        if len(self.term_input) > 1:
                            counter = 0
                    time.sleep(2)
                    driver.close()
            message("The process has finished")
            self.window.enable_button()
            self.window.hide_resubmit()
            driver.quit()

        except:
            if dry_run:
                error_message("Something went wrong when trying to generate the terms")
            else:
                error_message("Something went wrong. You can resume your download with the resume button")
            self.window.get_browser_info(self.curr_school, self.curr_link)

    def switch_lea(self, lea):
        lea_select = Select(self.driver.find_element(By.XPATH, '//*[@id="org-select"]'))
        time.sleep(2)
        for option in lea_select.options:
            if option.text.find(lea) != -1:
                op_value = option.get_attribute("value")

        try:
            lea_select.select_by_value(op_value)
        except NameError:
            error_message("LEA code could not be found")
            self.window.get_browser_info(self.curr_school, self.curr_link)
            self.driver.quit()
        time.sleep(2)


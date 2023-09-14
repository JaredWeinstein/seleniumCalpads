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
import glob


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
    def __init__(self, username, password, lea_codes, year, file_location,  window, curr_data, report_list, report_count):
        self.username = username
        self.password = password
        self.lea_codes = lea_codes
        self.year = year
        self.file_location = file_location.replace("/", "\\")
        self.window = window
        self.curr_data = curr_data
        # report_list is in the format of term (key) -> tuple with [name, file type] (value)
        self.report_list = report_list
        self.download_location = ""
        self.report_count = report_count

    def close_browser(self):
        self.driver.quit()

    def run_browser(self, dry_run):
        """
        Creates the headless Chrome browsers necessary to download the reports from CALPADS
        :param dry_run: Boolean value for if the request is to generate report periods or download the reports
        """
        try:
            # If the download failed, the curr_school lets the user resume where the program stopped
            if self.curr_data[0] is not None:
                index = self.lea_codes.index(self.curr_data[0])
                self.lea_codes = self.lea_codes[index:]

            counter = 0
            total_links = self.report_count
            rerun_flag = False
            # Creates a new chrome webdriver for each school to change the download location of each
            for school in self.lea_codes:
                lea_code = school[-7:]
                options = webdriver.ChromeOptions()

                # Makes a folder with the school name and changes the download location to that directory
                if not dry_run:
                    school_dir = os.path.join(self.file_location, school[:-10])
                    self.download_location = school_dir
                    if not os.path.exists(school_dir):
                        os.mkdir(school_dir)
                    prefs = {'download.default_directory': school_dir}
                    options.add_experimental_option('prefs', prefs)

                # options.add_argument("--headless")
                # options.add_argument("--no-sandbox")
                # options.add_argument("--disable-gpu")

                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
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

                    # Code to find the login boxes and input the user data into them
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

                    # Tries to switch to the year that was selected by the user
                    try:
                        driver.get('https://www.calpads.org/StateReporting/Certification')
                        self.switch_lea(lea_code)
                        self.curr_data[0] = school
                        year_selector = Select(driver.find_element(By.XPATH, '//*[@id="AcademicYear"]'))
                        year_selector.select_by_value(self.year)
                    except Exception as error:
                        print(error)
                        print("Switching to the term and year failed")
                        self.window.enable_button()
                        return

                    row = driver.find_element(By.XPATH, '//*[@id="CertStatusGrid"]/table/tbody')
                    row_list = row.find_elements(By.TAG_NAME, 'tr')

                    # Creates a dictionary mapping the report period to the link that leads to it
                    term_list = {}
                    for r in row_list:
                        link = r.find_element(By.XPATH,'.//*[1]/a').get_attribute('href')
                        term = r.find_element(By.XPATH, './/*[3]').text
                        cert_status = r.find_element(By.XPATH, './/*[6]').text
                        string = term + " - " + cert_status
                        term_list[string] = link

                    # Returns the information from the period list to update the GUI if it is a dry run
                    if dry_run:
                        reports = {}
                        key_list = list(term_list.keys())
                        value_list = list(term_list.values())
                        counter = 0

                        # Gets the name for the certification reports
                        for link in value_list:
                            driver.get(link)
                            cert_reports = driver.find_element(By.XPATH, '//*[@id="certReports"]')
                            cert_reports = cert_reports.find_elements(By.TAG_NAME, "a")
                            cert_report_names = []
                            for c in cert_reports:
                                cert_report_names.append(c.text)
                            reports[key_list[counter]] = cert_report_names
                            counter += 1
                        self.window.update_term(term_list, reports)
                        driver.close()
                        message("Please enter which report period you want now")
                        return

                    terms = list(term_list.keys())
                    if self.curr_data[2] is not None:
                        rerun_flag = True
                    for t_input in self.report_list.keys():
                        if rerun_flag == True:
                            if t_input != self.curr_data[2]:
                                continue
                            else:
                                rerun_flag = False
                        # Matches the user input with the list and goes to the link corresponding to the term
                        for t in terms:
                            if t.find(t_input) != -1:
                                driver.get(term_list[t])
                                break
                        self.curr_data[2] = t_input
                        link_list = []
                        cert_reports = driver.find_element(By.XPATH, '//*[@id="certReports"]')
                        # Finds all the links under the header designated 'certReports' and adds them to a list
                        for reports in self.report_list[t_input]:

                            # Needs to be put in a try block because some schools don't have reports
                            # that other schools have for some reason
                            try:
                                link_list.append((cert_reports.find_element(By.XPATH, "//a[contains(text(), '" + reports[0] + "')]").get_attribute('href'), reports[1]))
                            except Exception as e:
                                print("The report (" + reports[0] + ") was not found in school (" + school + ")!")
                                total_links -= 1
                                pass

                        # If the program crashed and the current link exists, start from that link in the list
                        if self.curr_data[1] is not None:
                            index = 0
                            for links in link_list:
                                if links[0] == self.curr_data[1]:
                                    link_list = link_list[index:]
                                    break
                                index += 1
                        # Iterates through every link in the list
                        for curr_link in link_list:
                            self.curr_data[1] = curr_link[0]
                            driver.get(curr_link[0])

                            # Microsoft ReportViewer exists within a different frame so the program must switch to
                            # looking within that frame otherwise selenium will be looking in the wrong place.
                            try:
                                WebDriverWait(driver, 30).until(
                                    EC.frame_to_be_available_and_switch_to_it(
                                        (By.XPATH, '//*[@id="reports"]/div/div/div/iframe')))
                            except TimeoutError:
                                error_message("The page took too long to load")
                                self.window.get_browser_info(self.curr_data, self.report_count)
                                driver.quit()
                                return
                            time.sleep(2)

                            # Some reports do not generate automatically upon page load requiring that you must
                            # try to select the status by the first index (usually the default) and click on the
                            # "View Report" button just in case.
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

                            # Waits for the download symbol to become enabled, signaling that the report has generated
                            try:
                                print("Waiting for document " + curr_link[0])
                                WebDriverWait(driver, 900).until(EC.text_to_be_present_in_element_attribute(
                                    (By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_ButtonLink"]'), 'aria-disabled',
                                    'false'))
                            except Exception as e:
                                print(e)
                                error_message("The report took too long to load!")
                                self.window.get_browser_info(self.curr_data, self.report_count)
                                driver.quit()
                                return

                            time.sleep(1)
                            save = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_ButtonLink"]')
                            driver.execute_script("arguments[0].click();", save)
                            time.sleep(1)

                            # Program is set to only recognize these 3 file types
                            file = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_Menu"]')
                            if curr_link[1] == 'pdf':
                                pdf = file.find_element(By.XPATH, "//*[text()='PDF']")
                                webdriver.ActionChains(driver).move_to_element(pdf).click(pdf).perform()
                            elif curr_link[1] == 'csv':
                                csv = file.find_element(By.XPATH, "//*[text()='CSV (comma delimited)']")
                                webdriver.ActionChains(driver).move_to_element(csv).click(csv).perform()
                            elif curr_link[1] == 'excel':
                                excel = file.find_element(By.XPATH, "//*[text()='Excel']")
                                webdriver.ActionChains(driver).move_to_element(excel).click(excel).perform()
                            else:
                                error_message("The file type specified does not exist")
                            time.sleep(4)
                            if curr_link[1] == 'excel':
                                type = r"\*" + "xlsx"
                            else:
                                type = r"\*" + curr_link[1]
                            list_of_files = glob.glob(self.download_location + type)  # * means all if need specific format then *.csv
                            latest_file = max(list_of_files, key=os.path.getmtime)
                            base_name = os.path.basename(os.path.normpath(latest_file))
                            new_name = self.download_location + "/"  + t_input + " - " + base_name
                            if not os.path.exists(new_name):
                                os.rename(self.download_location + "/" + base_name, new_name)

                            # Prints how many reports are left
                            counter += 1
                            self.report_count -= 1
                            print("Downloaded " + str(counter) + "/" + str(total_links) + " reports")

                    time.sleep(2)
                    driver.close()
                    self.curr_data[1] = None
                    self.curr_data[2] = None
            message("The process has finished")
            self.window.enable_button()
            self.window.hide_resubmit()
            self.window.reset_process()
            driver.quit()

        except Exception as e:
            print(e)
            if dry_run:
                self.curr_data[0] = None
                error_message("Something went wrong when trying to generate the terms")
            else:
                error_message("Something went wrong. You can resume your download with the resume button")
            self.window.get_browser_info(self.curr_data,self.report_count)

    def switch_lea(self, lea):
        """
        Switches which school is selected in CALPADS
        :param lea: The 7 digit lea code that corresponds to the school
        """
        lea_select = Select(self.driver.find_element(By.XPATH, '//*[@id="org-select"]'))
        time.sleep(2)
        for option in lea_select.options:
            if option.text.find(lea) != -1:
                op_value = option.get_attribute("value")

        try:
            lea_select.select_by_value(op_value)
        except NameError:
            error_message("LEA code could not be found")
            self.window.get_browser_info(self.curr_data,self.report_count)
            self.driver.quit()
        time.sleep(2)
    #
    # def get_all_reports(self):

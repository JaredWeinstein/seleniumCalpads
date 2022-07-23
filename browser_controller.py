import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class BrowserController:
    def __init__(self, username, password, lea_code, term_input, year, file_location):
        self.username = username
        self.password = password
        self.lea_code = lea_code
        self.term_input = term_input
        self.year = year
        self.file_location = file_location

        self.run_browser()


    def run_browser(self):
        options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': self.file_location}
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(options=options)
        driver.get(
            "https://identity.calpads.org/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3DCALPADSWebClient%26redirect_uri%3Dhttps%253A%252F%252Fwww.calpads.org%252Fsignin-oidc%26response_type%3Dcode%2520id_token%26scope%3Dopenid%2520profile%26max_age%3D14400%26response_mode%3Dform_post%26nonce%3D637932857194244885.ZmJmYTQwODctZTA2OS00YjFkLWIzNjUtMDAwZGE1ZDVhYmFhNzU5ZjJlNzQtZTU2YS00ZTBkLWI0N2QtMWY5ZWQyYjQ0NzNl%26state%3DCfDJ8MAX9CfV_fxHksEmX8cRo1gaNmYPrDIm0NoCebdA9-jHUPz0YNNjeol3Oxt1oOi11cpt3aABtNa_ktJ09_rneGhJ20hwSkY763s--xWUNwYFQZhrEPIhX9fOV1Bin6fzjBMrAD371qhM9oJbKX12bdafltDL_Zz4rmgDTPktC-U8hpuAE9czfpqbWuEMAotVLvaP9kja1fbhIOUF8fQd4rLwta5g0vdCU0DpnvoWCN7SbHjWkVyNsx7DO3xHmQR_YBj50f-xW5SXuOlTs_xUXmNDCeJbwAGergTVZNdzKW-i%26x-client-SKU%3DID_NETSTANDARD2_0%26x-client-ver%3D5.5.0.0")
        assert "CALPADS" in driver.title
        driver.find_element(By.ID, 'Username').send_keys(self.username)
        driver.find_element(By.ID, 'Password').send_keys(self.password)
        terms_and_conditions = driver.find_element(By.CLASS_NAME, 'custom-control-label').click()
        submit = driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'dd__logOut')))
            print('Successful login')
        except NoSuchElementException:
            print('Incorrect login/password')
            driver.quit()
        lea_select = Select(driver.find_element(By.XPATH, '//*[@id="org-select"]'))

        time.sleep(2)
        for option in lea_select.options:
            if option.text.find(self.lea_code) != -1:
                op_value = option.get_attribute("value")

        try:
            lea_select.select_by_value(op_value)
            print(op_value)
            print("School switch successful")
        except NameError:
            print("LEA code could not be found")
            driver.quit()
        time.sleep(2)

        driver.get('https://www.calpads.org/Report/Snapshot')

        if (self.term_input == 'FALL1'):
            term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[2]/ul')
            term_list = term.find_elements(By.TAG_NAME, "a")
            term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[3]/ul')
            term_list.extend(term.find_elements(By.TAG_NAME, "a"))
        else:
            if self.term_input == 'FALL2':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[4]/ul')
            elif self.term_input == 'SPRING':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[5]/ul')
            elif self.term_input == 'EOY1':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[6]/ul')
            elif self.term_input == 'EOY2':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[7]/ul')
            elif self.term_input == 'EOY3':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[8]/ul')
            elif self.term_input == 'EOY4':
                term = driver.find_element(By.XPATH, '//*[@id="divsnapshotreportsunavmsg1"]/div[9]/ul')

            term_list = term.find_elements(By.TAG_NAME, "a")

        link_list = []
        for t in term_list:
            link_list.append(t.get_attribute('href'))
        print(link_list)

        for link in link_list:
            driver.get(link)

            try:
                WebDriverWait(driver, 30).until(
                    EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="reports"]/div/div/div/iframe')))
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ReportViewer1_ctl08_ctl03"]'))
                )
            except TimeoutError:
                print("The page took too long to load")
                driver.quit()

            year_select = Select(driver.find_element(By.ID, 'ReportViewer1_ctl08_ctl03_ddValue'))
            try:
                year_select.select_by_visible_text(self.year)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'ReportViewer1_ctl08_ctl07_ddValue'))
                )
            except NoSuchElementException:
                print("This year doesn't exist for report " + link + ". This report will be skipped.")
                print()
                continue
            except TimeoutError:
                print("The page took too long to load")

            time.sleep(2)
            status = Select(driver.find_element(By.ID, 'ReportViewer1_ctl08_ctl07_ddValue'))
            try:
                counter = 0
                for option in status.options:
                    if option.text == 'SELPA Approved' or option.text == 'Certified' or option.text == 'LEA Approved':
                        status_string = option.text
                status.select_by_visible_text(status_string)

            except:
                print("Only non-certified reports exist for " + link + ". This report will be skipped.")
                continue
            time.sleep(2)

            view_report = driver.find_element(By.CSS_SELECTOR, "#ReportViewer1_ctl08_ctl00").click()

            try:
                WebDriverWait(driver, 450).until(EC.text_to_be_present_in_element_attribute(
                    (By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_ButtonLink"]'), 'aria-disabled', 'false'))
            except TimeoutError:
                print("The report took too long to load!")
                driver.quit()
            save = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00"]').click()
            time.sleep(1)
            pdf = driver.find_element(By.XPATH, '//*[@id="ReportViewer1_ctl09_ctl04_ctl00_Menu"]/div[4]').click()

        driver.quit()

    def close_browser(self):
        self.driver.quit()

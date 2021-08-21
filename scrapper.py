import os
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pickle
import pandas as pd
from pandas import ExcelWriter


class LinkedInScrapper:
    def save_cookie(self, path="cookie.txt"):
        with open(path, "wb") as filehandler:
            pickle.dump(self.driver.get_cookies(), filehandler)

    def load_cookie(self, path="cookie.txt"):
        with open(path, "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def __init__(self, email, password):
        self.driver = webdriver.Opera(executable_path="./operadriver")
        self.email = email
        self.password = password
        self.data = []

    def vpn_setup(self):
        self.driver.get("https://addons.opera.com/ru/extensions/details/opera-vpn/")
        self.driver.find_element_by_class_name("btn-enable").click()

        time.sleep(5)

    def login(self):
        """Opening LinkedIn"""
        self.driver.maximize_window()
        self.driver.get("https://www.linkedin.com/")
        time.sleep(3)

        """ Logging in LinkedIn """
        self.driver.find_element_by_id("session_key").send_keys(self.email)
        self.driver.find_element_by_id("session_password").send_keys(self.password)
        self.driver.find_element_by_class_name("sign-in-form__submit-button").click()
        time.sleep(15)

    def recruit_search(self):
        self.driver.get(
            'https://www.linkedin.com/search/results/people/?geoUrn=%5B"103644278"%5D&keywords=university%20recruiter&origin=FACETED_SEARCH&sid=Ph('
        )
        counter = 0
        for _ in range(0, 100):
            try:
                main = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "main"))
                )
                persons = main.find_elements_by_class_name(
                    "reusable-search__result-container"
                )
                for person in persons:
                    link = person.find_element_by_class_name(
                        "app-aware-link"
                    ).get_attribute("href")
                    name = person.find_element_by_class_name(
                        "visually-hidden"
                    ).text.split(" ")
                    fname = name[1]
                    lname = name[-2][0:-2]
                    job = person.find_element_by_class_name(
                        "entity-result__primary-subtitle"
                    ).text.split(" at ", maxsplit=1)
                    specialization = job[0]
                    company = job[1] if len(job) > 1 else "-0"
                    location = person.find_element_by_class_name(
                        "entity-result__secondary-subtitle"
                    ).text.split(",")
                    state = location[1] if len(location) > 1 else "-0"
                    city = location[0]

                    self.data.append(
                        [
                            counter,
                            fname,
                            lname,
                            company,
                            city,
                            state,
                            "-0",
                            "-0",
                            link,
                            specialization,
                        ]
                    )
                    counter += 1
            except Exception as e:
                print("An error occured")
                print(e)

            time.sleep(2)

            next_button = self.driver.find_element_by_class_name(
                "artdeco-pagination__button--next"
            )
            next_button.click()

            time.sleep(2)

        self.to_excel()

    def to_excel(self):
        df = pd.DataFrame(
            self.data,
            columns=[
                "№",
                "First Name",
                "Last Name",
                "Company",
                "City",
                "State",
                "Phone Number",
                "Email",
                "Link",
                "Specialization",
            ],
        )

        with ExcelWriter("recruiters.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer)

    def run(self):
        self.vpn_setup()

        if os.path.exists("cookies.txt"):
            self.driver.get("https://www.linkedin.com/")
            self.load_cookie("cookies.txt")
            self.driver.get("https://www.linkedin.com/")
        else:
            self.login()
            self.save_cookie("cookies.txt")

        self.recruit_search()


def main():
    email = input("Email: ")
    password = input("Password: ")
    scrapper = LinkedInScrapper(email, password)
    scrapper.run()


if __name__ == "__main__":
    main()

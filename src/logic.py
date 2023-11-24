from tqdm import tqdm
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from config_setup import read_config, check_selenium_install, create_config
from sys import exit
from lpt_lms import print_term_lines

check_selenium_install()


wait_period = 10
tmp_file_path = "/tmp/lpt"


def read_text_file(os) -> list:
    directory = tmp_file_path
    filenames = [file.path for file in os.scandir(directory) if file.is_file()]
    arr_dic = []
    print("Getting review details..\n")
    for file in filenames:
        if ".sample" in file:
            with open(file, "r") as f:
                textfile = f.readlines()
                arr_text = [line.strip()
                            for line in textfile]
                arr_text[0] = arr_text[0].split("@")[0]

            username = arr_text.pop(0)
            dic = {username: arr_text}
            arr_dic.append(dic)

    return arr_dic


def user() -> tuple[str, str]:
    global options, browser

    try:
        username, password = read_config()
    except FileNotFoundError:
        create_config()
        username, password = read_config()

    try:
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.add_argument("--headless")
        browser = webdriver.Firefox(options=firefox_options)
    except InvalidArgumentException:
        print("Failed to connect to browser")
        exit()
    return username, password


def open_browser():
    slack_url = "https://wethinkcode-community.slack.com/sign_in_with_password?redir=%2Fgantry%2Fclient"
    browser.get(slack_url)
    return browser


def login_to_slack(username, password) -> None:
    print("Logging in to slack...")
    browser = open_browser()
    gmail_account = '//*[@id="email"]'
    browser.find_element(By.XPATH, gmail_account).send_keys(username)

    gmail_password = '//*[@id="password"]'
    browser.find_element(By.XPATH, gmail_password).send_keys(password)

    login_next_btn = '//*[@id="signin_btn"]'
    browser.find_element(By.XPATH, login_next_btn).click()


def open_slack_link() -> None:
    print("Opening slack...")
    slack_link = '/html/body/div[1]/div/div/div[2]/p/a'
    try:
        slack_link_element = WebDriverWait(browser, wait_period/2).until(
            EC.presence_of_element_located((By.XPATH, slack_link))
        )
        slack_link_element.click()
    except:
        incorrect_details_class = "c-inline_alert__text"
        print_term_lines()
        try:
            find_err = WebDriverWait(browser, 0).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, incorrect_details_class))
            )
            print("Sorry, you entered an incorrect email address or password.\n\nPlease do the following in Terminal:\n\t rm -rf ~/.config/lpt")
            browser.quit()
            exit()

        except Exception:
            print(
                "Failed to load Slack link page contents. It may be a connection issue, please try again.")
            browser.quit()
            exit()


def get_review_usernames(read_text_file, os) -> list:
    names = read_text_file(os)
    return names


def username_search_bar() -> None:
    campus_general_link = '//*[@id="C0182HEG02C"]'

    # slack_users = 'html body.p-ia4_body.gecko.use-slack-font div.p-client_container div.p-ia4_client_container div.p-ia4_client.p-ia4_client--with-search-in-top-nav.p-ia4_client--workspace-switcher-prototype-on.p-ia4_client--browser.p-ia4_client--theming div.p-client_workspace--including_tab_rail div.p-client_workspace div.p-client_workspace__layout div.active-managed-focus-container div div.p-view_contents.p-view_contents--primary.p-view_contents--channel-list-pry div div.p-view_header.p-view_header--tiles.p-view_header--with-bookmarks-bar div.p-view_header__actions div.p-autoclog__hook button.c-button-unstyled.p-avatar_stack--details'

    # slack_users_xpath = "/html/body/div[2]/div/div/div[4]/div[2]/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/button"

    slack_users_class = "p-avatar_stack--details"

    try:
        slack_page_element = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.XPATH, campus_general_link))
        )
        slack_page_element.click()

    except:
        print("Failed to load Campus general, please try again.")
        browser.quit()
        exit()

    try:
        # print("Trying to find btn")
        slack_users_element = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.CLASS_NAME, slack_users_class))
        )
        # print("Arrived, about to click")
        slack_users_element.click()

    except:
        print("Failed to load the Slack Users page contents, please try again.")
        browser.quit()
        exit()


def search_username(name) -> None:
    search_user = '/html/body/div[11]/div/div/div[2]/div[2]/div/div[1]/div/div[1]/input'
    try:
        slack_link_element = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.XPATH, search_user))
        )
        slack_link_element.clear()
        slack_link_element.send_keys(name)

    except:
        print("Failed to load username search bar, please try again.")
        browser.quit()
        exit()

    users_in_channel_list = 'p-ia_details_popover__members_list_item_member'
    users_not_in_channel_list = 'p-ia_details_popover__members_list_item_member--non-channel'

    try:
        names_ele = WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, users_not_in_channel_list)))

        enter_user_btn = '/html/body/div[11]/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/div[1]/div/div/div[6]/button[1]'
        try:
            enter_user_details_btn = WebDriverWait(browser, wait_period).until(
                EC.presence_of_element_located((By.XPATH, enter_user_btn)))
            enter_user_details_btn.click()
        except:
            pass

    except:
        try:
            names_ele = WebDriverWait(browser, wait_period).until(
                EC.presence_of_element_located((By.CLASS_NAME, users_in_channel_list)))

            enter_user_btn = '/html/body/div[11]/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/div[1]/div/div/div[4]/button'
            try:
                enter_into_user = WebDriverWait(browser, wait_period).until(
                    EC.presence_of_element_located((By.XPATH, enter_user_btn)))
                enter_into_user.click()

            except:
                print("Username not found, Please enter a valid username.")
                browser.quit()
                exit()
        except:
            print("Username not found, Please enter a valid username.")
            browser.quit()
            exit()


def go_to_message_user() -> None:
    user_name = get_user_name()

    message_btn = 'html body.p-ia4_body.gecko.use-slack-font div.p-client_container div.p-ia4_client_container div.p-ia4_client.p-ia4_client--with-search-in-top-nav.p-ia4_client--workspace-switcher-prototype-on.p-ia4_client--browser.p-ia4_client--theming div.p-client_workspace--including_tab_rail div.p-client_workspace div.p-client_workspace__layout div.active-managed-focus-container div div.p-view_contents.p-view_contents--secondary.p-view_contents--channel-list-pry div.p-flexpane.p-flexpane--iap1.p-flexpane--ia_details_popover div div.p-flexpane__body.p-flexpane__body--light div div.c-scrollbar.c-scrollbar--fade div.c-scrollbar__hider div.c-scrollbar__child div.p-autoclog__hook div.p-r_member_profile__container div.p-r_member_profile_section div.p-r_member_profile_section_content div.margin_top_75 div.p-r_member_profile__buttons.p-member_profile_buttons button.c-button.c-button--outline.c-button--medium.p-member_profile_buttons__button'

    try:
        go_to_message = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, message_btn))
        )
        go_to_message.click()

    except:
        print("Failed to load the page, please try again.")
        browser.quit()
        exit()

    return user_name


def get_user_name() -> str:

    user_name_class = "p-r_member_profile__name__text"
    try:
        sleep(2)
        get_username = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.CLASS_NAME, user_name_class))
        )
        user_name = get_username.text
        return user_name

    except:
        print("Failed to get username, please try again.")
        browser.quit()
        exit()


def message_user(names, os) -> None:
    print(f"Now sending messages to {len(names)} person(s)")
    for user_data in tqdm(names):

        try:
            for name, data in user_data.items():
                username_search_bar()
                search_username(name)
                user_name = go_to_message_user()

                module = data[0]
                topic = data[1]
                problem = data[2]
                uuid = data[3]
                arr_message = [f"Hi {user_name.title()}, I am reviewing your project.", " ",
                               "Project Details:", module, topic, problem, uuid, " ", "When are you available for a Google meets so we can discuss your project further?", "Thank you."]

                sleep(1)
                type_message = ActionChains(browser)

                for line in arr_message:
                    type_message.send_keys(line)
                    type_message.key_down(Keys.SHIFT).send_keys(
                        Keys.RETURN).key_up(Keys.SHIFT)
                    type_message.perform()

                send_message_btn_xpath = '/html/body/div[2]/div/div/div[4]/div[2]/div[1]/div[3]/div[2]/div/div/div[3]/div[2]/div/div/div[2]/div/div/div/div[3]/div[3]/span/button[1]'

                send_message_btn_class = 'c-wysiwyg_container__button--send'

                try:
                    send_message = WebDriverWait(browser, wait_period).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, send_message_btn_class))
                    )
                    send_message.click()
                except:
                    send_message = WebDriverWait(browser, wait_period).until(
                        EC.presence_of_element_located(
                            (By.XPATH, send_message_btn_xpath))
                    )
                    send_message.click()
                delete_tmp_file(os, uuid)
                sleep(3)
        except:
            user = str(user_data.keys())
            print("Skipping", user.split('\'')[1])
            sleep(3)
            continue


def sending_message():
    print()
    print_term_lines()
    print("Now Sending message(s) via Slack")
    print_term_lines()


def delete_tmp_file(os, uuid):
    try:
        file_path = os.path.join(
            tmp_file_path, f'.sample-{uuid.split()[1]}.txt')
        if os.path.isfile(file_path):
            os.remove(file_path)
    except FileNotFoundError:
        print("File was not found")
        pass


def delete_tmp_files(os):
    files = os.listdir(tmp_file_path)
    for file in files:
        file_path = os.path.join(tmp_file_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def run_script(os) -> None:
    try:
        username, password = user()
        sending_message()
        login_to_slack(username, password)
        open_slack_link()
        names = get_review_usernames(read_text_file, os)

        message_user(names, os)

        print("\nAll messages have been sent.")

        browser.quit()
    except KeyboardInterrupt:
        print()
        exit()

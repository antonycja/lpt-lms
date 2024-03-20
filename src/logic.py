from tqdm import tqdm
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from config_setup import read_config, check_selenium_install
from sys import exit
from lpt_lms import print_term_lines
import os

check_selenium_install()


wait_period = 10
tmp_file_path = "/tmp/lpt"
# tmp_file = "./sample_files (copy)" DEBUGGING

# TODO: Hide firefox


def read_text_file(os) -> list:
    """Open each text file and read its contents. The textfile contains the data needed by the script to send messages to the correct users. Extract the username from the email and create a dictionary with the username being the key.

    Args:
        os (Module): The os module passed from the main file to read file paths.

    Returns:
        list: Returns a list of dictionaries and each dictionary item containing a list of details.
    """
    # directory = "./sample_files"
    directory = tmp_file_path
    # arr of the file names in the directory
    filenames = [file.path for file in os.scandir(directory) if file.is_file()]
    arr_dic = []
    print("Getting review details..\n")
    for file in filenames:  # Create an arr of dictionaries
        with open(file, "r") as f:  # Read the text files
            textfile = f.readlines()
            arr_text = [line.strip()
                        for line in textfile]  # Remove newline from line
            arr_text[0] = arr_text[0].split("@")[0]  # Get username from email
            # username = arr_text[0]

        username = arr_text.pop(0)  # Remove username fr
        dic = {username: arr_text}
        arr_dic.append(dic)

    return arr_dic

# TODO: Add headerless


def user() -> tuple[str, str]:
    """Get the users login information from the config file and choose the browser to be used.

    Returns:
        tuple[str, str]: Returns the slack login username(email) and the password as a tuple in str format.
    """
    global options, browser
    username, password = read_config()  # Read from the config file
    # Choose which browser to use.
    # if browser == "Edge":
    #     edge_options = webdriver.EdgeOptions()
    #     # edge_options.add_argument("--headless")
    #     browser = webdriver.Edge(options=edge_options)

    # elif browser == "Chrome":
    #     chrome_options = webdriver.ChromeOptions()
    #     # chrome_options.add_argument("--headless")
    #     browser = webdriver.Chrome(options=chrome_options)
    # else:
    #     firefox_options = webdriver.FirefoxOptions()
    #     # firefox_options.add_argument("--headless")
    #     browser = webdriver.Firefox(options=firefox_options)

    # firefox_options = webdriver.FirefoxOptions()
    # firefox_options.add_argument("--headless")
    # browser = webdriver.Firefox(options=firefox_options)
    try:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")
        browser = webdriver.Firefox(options=firefox_options)
    except:
        try:
            safari_options = webdriver.SafariOptions()
            safari_options.add_argument("--headless")
            browser = webdriver.Safari(options=safari_options)
        except:
            print("Failed to connect to Firefox and Safari browser")
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")
                browser = webdriver.Chrome(options=chrome_options)
            except:
                print("Failed to connect to all browsers")
                exit()
    return username, password


def open_browser():
    """Open slack login url 

    Returns:
        browser: the selenium browser driver to be used when opening slack
    """
    slack_url = "https://wethinkcode-community.slack.com/sign_in_with_password?redir=%2Fgantry%2Fclient"
    browser.get(slack_url)
    return browser


def login_to_slack(username, password) -> None:
    """Login to slack using your slack details

    Args:
        username (str): the slack login email
        password (str): the slack login password
    """
    print("Logging in to slack...")
    browser = open_browser()  # open the browser
    gmail_account = '//*[@id="email"]'  # Email field
    browser.find_element(By.XPATH, gmail_account).send_keys(username)

    gmail_password = '//*[@id="password"]'  # Password field
    browser.find_element(By.XPATH, gmail_password).send_keys(password)

    login_next_btn = '//*[@id="signin_btn"]'  # Login Button
    browser.find_element(By.XPATH, login_next_btn).click()


def open_slack_link() -> None:
    """Open the slack link.
    """
    print("Opening slack...")
    slack_link = '/html/body/div[1]/div/div/div[2]/p/a'  # Slack link
    try:  # waiting period from 10 to 5
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
    """Getting the usernames from the text files.

    Args:
        read_text_file (function): Read from the textfile
        os (Module): Module used to access os specific tasks

    Returns:
        list: Return the list of names
    """
    # Get Usernames from textfile
    names = read_text_file(os)
    return names


def username_search_bar() -> None:
    """Go to Campus general workspace and go to the search bar
    """
    campus_general_link = '//*[@id="C0182HEG02C"]'
    slack_users = 'html body.p-ia4_body.gecko.use-slack-font div.p-client_container div.p-ia4_client_container div.p-ia4_client.p-ia4_client--with-search-in-top-nav.p-ia4_client--workspace-switcher-prototype-on.p-ia4_client--browser.p-ia4_client--theming div.p-client_workspace--including_tab_rail div.p-client_workspace div.p-client_workspace__layout div.active-managed-focus-container div div.p-view_contents.p-view_contents--primary.p-view_contents--channel-list-pry div div.p-view_header.p-view_header--tiles.p-view_header--with-bookmarks-bar div.p-view_header__actions div.p-autoclog__hook button.c-button-unstyled.p-avatar_stack--details'

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
        slack_users_element = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, slack_users))
        )
        slack_users_element.click()

    except:
        print("Failed to load the Slack Users page contents, please try again.")
        browser.quit()
        exit()


def search_username(name) -> None:
    """Search the name in the search bar.

    Args:
        name (string): The student name extracted from the student email to search for.

    Returns:
        string: The user name of the person receiving the message.
    """
    search_user = '/html/body/div[11]/div/div/div[2]/div[2]/div/div[1]/div/div[1]/input'  # user search bar
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
    enter_user_btn = 'html body.p-ia4_body.gecko.use-slack-font.underline-all-links.ReactModal__Body--open div.c-sk-modal_portal div.ReactModal__Overlay.ReactModal__Overlay--after-open.c-sk-overlay div.ReactModal__Content.ReactModal__Content--after-open.c-sk-modal.c-sk-modal--fixed.c-sk-modal--responsive.p-about_modal div.p-about_modal__tabs div.p-about_modal__tab_panel.c-tabs__tab_panel.c-tabs__tab_panel--active div.p-ia_details_popover__members.p-ia_details_popover__members--non-channel-results.p-ia_details_popover__members--in-channel-empty div.p-ia_details_popover__members_list div div div.c-virtual_list.c-virtual_list--scrollbar.c-scrollbar.c-scrollbar--hidden div.c-scrollbar__hider div.c-scrollbar__child div.c-virtual_list__scroll_container div#U05S19T5D9T.p-ia_details_popover__members_list_item.p-ia_details_popover__members_list_item_member.p-ia_details_popover__members_list_item_member--non-channel.c-virtual_list__item button.c-button-unstyled'

    try:
        names_ele = WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, users_not_in_channel_list)))

        browser.find_element(By.CSS_SELECTOR, enter_user_btn).click()

    except:
        try:
            names_ele = WebDriverWait(browser, wait_period).until(
                EC.presence_of_element_located((By.CLASS_NAME, users_in_channel_list)))
            enter_user_btn = '/html/body/div[11]/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/div[1]/div/div/div[4]/button'
            browser.find_element(By.XPATH, enter_user_btn).click()

        except:
            print("Username not found, Please enter a valid username.")
            browser.quit()
            exit()


def go_to_message_user() -> None:
    """Go to the users message page.
    """
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
    """get the users username

    Returns:
        str: Returns the username of the current user.
    """

    user_name_class = "p-r_member_profile__name__text"
    try:
        get_user_name = WebDriverWait(browser, wait_period).until(
            EC.presence_of_element_located((By.CLASS_NAME, user_name_class))
        )
        user_name = get_user_name.text
        return user_name

    except:
        print("Failed to get username, please try again.")
        browser.quit()
        exit()


def message_user(names) -> None:
    """Type the message and send it to each student, do this for every student being reviewed.

    Args:
        names (str): An arr of the names being reviewed
    """

    print(f"Now sending messages to {len(names)} person(s)")
    for user_data in tqdm(names):  # Loop through the list of dictionaries
        for name, data in user_data.items():  # Loop through each dictionary
            username_search_bar()  # Go to username search bar
            search_username(name)  # Search the username
            user_name = go_to_message_user()  # Go to the users message profile

            module = data[0]  # Get the module
            topic = data[1]  # Get the topic
            problem = data[2]  # Get the problem
            uuid = data[3]  # Get the uuid

            # The message to be sent
            arr_message = [f"Hi {user_name.title()}, I am reviewing your project.", " ",
                           "Project Details:", module, topic, problem, uuid, " ", "When are you available for a Google meets so we can discuss your project further?", "Thank you."]

            sleep(1)
            type_message = ActionChains(browser)

            # print(f"Typing message to {user_name}...")
            for line in arr_message:
                type_message.send_keys(line)
                type_message.key_down(Keys.SHIFT).send_keys(
                    Keys.RETURN).key_up(Keys.SHIFT)
                type_message.perform()

            send_message_btn = 'html body.p-ia4_body.gecko.use-slack-font div.p-client_container div.p-ia4_client_container div.p-ia4_client.p-ia4_client--with-search-in-top-nav.p-ia4_client--workspace-switcher-prototype-on.p-ia4_client--browser.p-ia4_client--theming div.p-client_workspace--including_tab_rail div.p-client_workspace div.p-client_workspace__layout div.active-managed-focus-container div div.p-view_contents.p-view_contents--primary.p-view_contents--channel-list-pry div div.p-file_drag_drop__container div.workspace__primary_view_footer.p-workspace__primary_view_footer--float div.p-message_pane_input div.p-message_pane_input_inner div.p-message_pane_input_inner_main div.p-workspace__input.p-message_input_unstyled div.p-message_input__input_container_unstyled.c-wysiwyg_container.c-wysiwyg_container--theme_light.c-wysiwyg_container--with_footer.c-wysiwyg_container--theme_light_bordered.c-basic_container.c-basic_container--size_medium div.c-basic_container__body div.c-wysiwyg_container__footer.c-wysiwyg_container__footer--with_formatting div.c-wysiwyg_container__suffix span.c-wysiwyg_container__send_button--with_options button.c-button-unstyled.c-icon_button.c-icon_button--size_small.c-wysiwyg_container__button.c-wysiwyg_container__button--send.c-icon_button--default'
            browser.find_element(By.CSS_SELECTOR, send_message_btn).click()


def sending_message():
    print()
    print_term_lines()
    print("Now Sending message(s) via Slack")
    print_term_lines()


def delete_tmp_files(os):
    files = os.listdir(tmp_file_path)

    # Iterate through the files and delete each one
    for file in files:
        file_path = os.path.join(tmp_file_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def run_script(os) -> None:
    """Run the slack bot to message the students you are reviewing and let them know that you are reviewing them

    Args:
        os (Module): Module to control the computer
    """
    username, password = user()
    sending_message()
    login_to_slack(username, password)
    open_slack_link()
    names = get_review_usernames(read_text_file, os)

    message_user(names)

    print("\nAll messages have been sent.")

    browser.quit()


if __name__ == "__main__":
    run_script(os)

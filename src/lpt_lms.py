import subprocess
import os
from time import sleep
# rewriting the parameter_generator.sh in python

# technically we still using bash but I am scripting it as a .py file for better compatibility


def print_term_lines():
    column, lines = os.get_terminal_size()
    print("-" * column)


def login_lms():
    """
    The start of the review process \n
    Accepts the review and generates the sample file
    """
    # logging into lms
    subprocess.run(f"wtc-lms login", shell=True)
    print_term_lines()
    print(f"\nloading available reviews...\n\n")
    subprocess.run(f"wtc-lms reviews", shell=True)

    return


def get_UUID():
    """
    Gets user input

    Returns:
        list: Returns a list of the selected UUID(S)
    """

    # saving user input into a variable
    user_input = input("\n\nEnter the UUID(S): ").lower().strip()
    ls_of_sel_UUID = user_input.split(" ")
    subprocess.run(f'echo', shell=True)

    return ls_of_sel_UUID


def accept_reviews(student_UUIDS: list):
    """
    Accepting student reviews, cloning the relevant work and storing the student information

    Args:
        student_UUIDS (list): a list of the student uuid
    """
    failed = []
    successful = []
    # accepting reviews
    for uuid in student_UUIDS:
        print_term_lines()
        print(f"For {uuid}: ")
        print_term_lines()
        if os.path.exists(f"{uuid}.txt"):
            pass
        else:
            with open(f"{uuid}.txt", "w") as save_file:
                subprocess.run(
                    f"wtc-lms accept {uuid}", shell=True, stdout=save_file, text=True)
                subprocess.run(
                    f"wtc-lms review_details {uuid}", shell=True, stdout=save_file, text=True)
                save_file.close()

        var = subprocess.run(
            f'git clone $(cat "{uuid}.txt" | grep -w "git clone" | cut -f3 -d " ")', shell=True, capture_output=True, text=True)

        if ("fatal: You must specify a repository to clone.") in var.stderr:
            var = subprocess.run(
                f'git clone $(cat "{uuid}.txt" | grep -w "Git Url:" | cut -f3 -d " ")', shell=True, capture_output=True, text=True)

        if "Failed" in var.stderr or "failed" in var.stderr:
            print(var.stderr.strip())
            failed.append(uuid)
            os.remove(f'{uuid}.txt')
        else:
            print(var.stderr)
            successful.append(uuid)
        print_term_lines()

        sleep(5)
        subprocess.run(f"wtc-lms reviews", shell=True, capture_output=True)

    return failed, successful


def failed(failed):

    print()
    print_term_lines()
    print("Failed to clone the following: ")
    print_term_lines()
    for index, fail in enumerate(failed):
        print(f'{index+1}) {fail}')
    print_term_lines()


def parameter_generation(student_UUID: list):
    """
    Generates the files that is needed for selenium's message automation

    Args:
        student_UUIDS (list): a list of the student uuid
    """
    # making the lpt folder
    try:
        os.mkdir("/tmp/lpt")
    except FileExistsError:
        pass

    # we suppose to get the par from uuid.txt
    UUID_sample = []
    for uuid in student_UUID:
        UUID_sample.append((f"sample-{uuid}"))

    # the index of the first
    uuid_index = 0
    for uuid in UUID_sample:

        # we opening and writing to a file the file sample-name:
        with open(f".{uuid}.txt", "w") as f:
            subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Submission" | cut -f3 -d " ")', shell=True, stdout=f, text=True)
            subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Module")', shell=True, stdout=f, text=True)
            subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Topic")', shell=True, stdout=f, text=True)
            subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Problem")', shell=True, stdout=f, text=True)
            ID = subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "add_comment" | cut -f3 -d " ")', shell=True, stdout=subprocess.PIPE, text=True)
            f.write(f"UUID: {ID.stdout}")
        # once we done writing, we move on the next index
        uuid_index += 1

    message = reminder(UUID_sample)
    subprocess.run(f"mv .s* /tmp/lpt", shell=True, capture_output=True)

    return message


def reminder(UUID_sample: list):
    """
    Generates a message for the user as a reminder to text the students
    Args:
        UUID_sample (list):
    """

    reminder_info = []
    for uuid in UUID_sample:
        with open(f".{uuid}.txt", "r") as saved_files:
            info = saved_files.readlines()
            reminder_info.append(tuple(info))
        pass

    message_line = []
    for student in reminder_info:
        tmp = []
        tmp.append(student[0].replace(
            "@student.wethinkcode.co.za\n", ""))
        tmp.append(" regarding ")
        tmp.append(student[3][9:].strip("\n"))
        message_line.append(tmp)
        del tmp

    return message_line


def messenger(message):
    """
    Reminds the user to follow up on the personals
    """

    print()
    print_term_lines()
    print("Please follow-up on the following individuals via slack.")
    print_term_lines()
    for index, reminder in enumerate(message):
        print(f'\t{index+1}) {"".join(reminder)}')
    print_term_lines()


def run():
    login_lms()
    UUID_list = get_UUID()
    fail, success = accept_reviews(UUID_list)
    message = parameter_generation(success)

    if len(fail) > 0:
        failed(fail)
    if len(success) > 0:
        return message

    # exit()


def return_message():

    file_in_dir = os.listdir(os.getcwd())
    files = [file for file in file_in_dir
             if ".txt" in file]

    UUID_list = []
    for file in files:
        txt_file_name = file.split(".")[0]
        UUID_list.append(txt_file_name)
    message = parameter_generation(UUID_list)

    return message

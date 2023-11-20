import subprocess
import os
from time import sleep
from sys import exit


def print_term_lines():
    column, lines = os.get_terminal_size()
    print("-" * column)


def login_lms():

    try:
        print_term_lines()
        print("Logging into WTC-LMS")

        try:
            out = subprocess.run(f"wtc-lms login", shell=True,
                                 stdout=subprocess.PIPE, text=True)
        except KeyboardInterrupt:
            exit()

        if "login failed" in out.stdout:
            print_term_lines()
            print(out.stdout)
            print("Error response: Incorrect Password")
            exit()

        # sleep(4)
        print()
        print_term_lines()
        print(f"\nloading available reviews...\n\n")
        subprocess.run(f"wtc-lms reviews", shell=True)
    except KeyboardInterrupt:
        exit()


def get_UUID():
    print("Please enter the UUID(s) you would like to review separated by spaces (spicey-chick-set spare-ton-fix)")
    user_input = input("\n\nEnter the UUID(S): ").lower(
    ).strip().strip("(").strip(")")


    ls_of_sel_UUID = user_input.split(" ")
    subprocess.run(f'echo', shell=True)

    return ls_of_sel_UUID


def accept_reviews(student_UUIDS: list):
    failed = []
    successful = []

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
            sleep(5)
            continue

        if "Failed" in var.stderr or "failed" in var.stderr:
            print(var.stderr.strip())
            failed.append(uuid)
            os.remove(f'{uuid}.txt')
            sleep(5)
            continue
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
    try:
        os.mkdir("/tmp/lpt")
    except FileExistsError:
        pass

    UUID_sample = []
    for uuid in student_UUID:
        if ".sample-" in uuid:
            continue
        else:
            UUID_sample.append((f"sample-{uuid}"))

    uuid_index = 0
    for uuid in UUID_sample:

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

            # Renaming the folder with student name
            name = subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Submission" | cut -f3 -d " ")', shell=True, capture_output=True, text=True)
            file_name = subprocess.run(
                f'(cat "{student_UUID[uuid_index]}.txt" | grep -w "Git Url:" | cut -f2 -d "/")', shell=True, capture_output=True, text=True)

            folder_name = file_name.stdout
            new_name = folder_name.replace(".git", "").strip()
            rename = name.stdout
            rename = rename.strip("@student.wethinkcode.co.za\n")

            sleep(1)
            subprocess.run(f'mv {new_name} {rename}',
                           shell=True, capture_output=True, text=True)
            sleep(1)
            subprocess.run(f'mv {student_UUID[uuid_index]} {rename}',
                           shell=True, capture_output=True, text=True)

        uuid_index += 1

    message = reminder(UUID_sample)
    subprocess.run(f"mv .sample* /tmp/lpt", shell=True, capture_output=True)

    return message


def reminder(UUID_sample: list):
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

    print()
    print_term_lines()
    print("Please follow-up on the following individuals via slack.")
    print_term_lines()
    for index, reminder in enumerate(message):
        print(f'\t{index+1}) {"".join(reminder)}')
    print_term_lines()


def run():
    try:
        login_lms()
        UUID_list = get_UUID()
        fail, success = accept_reviews(UUID_list)
        message = parameter_generation(success)

        if len(fail) > 0:
            failed(fail)
        if len(success) > 0:
            return message
    except KeyboardInterrupt:
        print()
        exit()


def return_message():

    # subprocess.run(f"cd /tmp/lpt",shell=True)
    os.chdir("/tmp/lpt")

    try:

        file_in_dir = os.listdir(os.getcwd())

        files = [file for file in file_in_dir
                 if ".txt" in file]

        UUID_list = []
        for file in files:
            txt_file_name = file.replace(".txt", "").replace(".s","s")
            UUID_list.append(txt_file_name)
        message = reminder(UUID_list)
    except FileNotFoundError:
        print("Your message box is clean.")

    return message

# slovnik kde budou predpripraveny firmy, ktere se mi vyplni
# do slozky podklady nechat vytvaret .txt soubory s výsledky
# vysledky = výpočet bariéry, full info o zakazce

import os
import re
import shutil
import sys
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep

import jinja2
import templates

from load_info import (
    fire_protection_options,
    order_keys,
    translate_device,
    translate_protection,
    documentation_folders,
)

# change start folder, program dont start where is a script saved.
os.chdir("/Users/stroch/Documents/RSBP/Zakazky")
# dictionary which contains variable which we are using in Tex documentation
ORDER_FULL_INFO = {}


def over_weekend(date_for_check):
    """
    Function check if date is weekend or not
    if day is weekend move date to date which is week
    """
    if date_for_check.weekday() > 4:
        return date_for_check + timedelta(2)
    else:
        return date_for_check


def convert_dateformat(*dates, separator="-"):
    """
    Function convert_dateformat convert one or more date
    string format and format dd. mm. yyyy
    """
    dates = list(dates)
    for i, a_date in enumerate(dates):
        a_date = over_weekend(a_date)
        a_date = str(a_date)
        a_date = a_date.split(" ")[0]
        a_date = reversed(a_date.split(separator))
        dates[i] = ". ".join(a_date)

    return dates


def check_input(str_input, dict_key):
    """
    Function for checking input from user. If user make some mistake,
    he can change it, by this function.
    """
    str_input = str_input.strip()
    while True:
        print("You typed " + '"' + str_input + '"' + " as " + dict_key)
        #  option for if you like to change or not
        option = input("\nDo you want to re-type your input (y\\n): ")
        option = option.lower().strip()

        if not option or option == "n":
            return str_input
        elif option == "y":
            str_input = input("Type a new " + dict_key + " : ").strip()
        else:
            print("Wrong answer. Try again !")


def choose_language():
    """
    Our documentation and templates are diff in language. It is
    necessary to make choice of language of documentation. This
    funciton return string of language - "cz", "en" etc.
    """
    while True:
        answer = input("Choose language of documentation: ").lower().strip()

        for language in "cz", "en":
            if answer == language:
                return answer

        print("I do not understand your asnwer. Language is 'cz' or 'en'.")


def input_index_lst(list_choices):
    """
    Function check if your choice for choices in list are available.
    If your input is correct, than function return element from list you were
    choosing. So function have one necessary parametr - list.
    """
    while True:
        try:
            index_lst = int(input("Your choice: "))
            if index_lst < 0:
                print("Negative number is not allowed.")
                continue
            # return exactly elemtn form list which you are choosing
            return list_choices[index_lst]

        except ValueError:
            print("You don't type a number.")
        except IndexError:
            print("Number is not available in choices.")


def input_number(text):
    while True:
        try:
            num = int(input("\nInsert amount of {}:".format(text)))
            if num < 0:
                print("\nNegative number is not allowed.")
                continue
            # return exactly elemtn form list which you are choosing
            return num
        except ValueError:
            print("\nYou don't type a number.")


def choose_protection(language):
    """
    Function choose from pre-define file with type of protected space and
    type of protection what we want to applicate to protected space.
    """
    types_machinery = fire_protection_options[language]
    machinery_options = list(types_machinery.keys())

    print("\nChoose type of protected machine:")
    for i, device in enumerate(machinery_options):
        print(i, device)

    machine_selection = input_index_lst(machinery_options)

    print("\nChoose a type of protection:")
    protection_options = types_machinery[machine_selection]
    for i, protection in enumerate(protection_options):
        pattern = re.compile(r"[$_]")
        protection = pattern.sub("", protection)
        print(i, protection)

    protection_selection = input_index_lst(protection_options)

    ORDER_FULL_INFO["protect_machine"] = machine_selection
    ORDER_FULL_INFO["type_protection"] = protection_selection


def create_document_folders(order_folder):
    lst_created_folders = []
    for i, folder in enumerate(documentation_folders):
        os.makedirs("{}/Dokumentace/{}_{}/".format(order_folder, i, folder))
        lst_created_folders.append("{}_{}".format(i, folder))

    for i, folder in enumerate(documentation_folders):
        if folder != "electronic_version":
            os.mkdir(
                "{}/Dokumentace/6_electronic_version/{}_{}".format(
                    order_folder, i, folder
                )
            )
    sleep(0.4)
    print("\nFolder 'Documentation' was created.")

    for folder in ("Material", "Podklady", "Realizace"):
        shutil.copytree(
            os.path.join("Sablony", folder), os.path.join(order_folder, folder)
        )
        print("Folder '{}' was created.".format(folder))
        sleep(0.4)
    print()

    return lst_created_folders


def create_order_folder(order_number, customer_name, installation_company):
    order_folder = []
    pattern_company = re.compile(
        r"\s+(a\.?\s*s\.?|(spol\.?\s*)?(s\.?\s*r\.?\s*o\.?)?)?$", re.IGNORECASE
    )
    for info in (order_number, customer_name, installation_company):
        info = pattern_company.sub("", info).replace(" ", "_")
        order_folder.append(info)

    order_folder = "_".join(order_folder)
    print("\nDocumentation for '{}' is creating:\n".format(order_number))
    sleep(0.4)

    if not os.path.exists(order_folder):
        os.mkdir(order_folder)
        print("\nFolder '{}' was created.".format(order_folder))
    else:
        raise Exception("Folder with name {} is already exist.".format(order_folder))

    return order_folder


def nahraj_komponenty_pro_titulku():
    pass


def create_LaTeX_documentation(language, protect_machine, type_protection):
    order_number = ORDER_FULL_INFO["order_number"]
    order_folder = create_order_folder(
        ORDER_FULL_INFO["order_number"],
        ORDER_FULL_INFO["customer_name"],
        ORDER_FULL_INFO["installation_company"],
    )
    for language_set in translate_device:
        for word in language_set:
            if "_" in word:
                word = word[: word.index("_")]
            if word in protect_machine:
                protected_space = language_set[0]

    path_report_template = os.path.join(
        os.getcwd(), "tex_templates/{}/{}/".format(protected_space, language)
    )

    for language_set in translate_protection:
        for word in language_set:
            if word in type_protection:
                result = language_set[0].lower().replace("_", "")
                result = result.replace(" ", "_") + "_{}.tex".format(language)
                report_template_file = result

    LaTeX_JINJA_ENV = jinja2.Environment(
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        # loader - odkud budou nacitany template soubory .tex
        # os.path.abs(".") - hledej soubor ve slozce v kter je spusten script
        loader=jinja2.FileSystemLoader(
            [
                path_report_template,
                os.path.join(
                    os.getcwd(), os.path.join("tex_templates", "title_page", language)
                ),
            ]
        ),
    )

    lst_created_folders = create_document_folders(order_folder)

    while lst_created_folders:
        folder = lst_created_folders.pop()

        if "title" in folder:
            path = "{}/Dokumentace/{}/{}_title_page.tex".format(
                order_folder, folder, order_number
            )
            # write info to title page of order
            title_template_file = "title_page_template_{}.tex".format(language)
            with open(path, encoding="utf-8", mode="w") as result_file:
                template = LaTeX_JINJA_ENV.get_template(title_template_file)
                result_file.write(template.render(**ORDER_FULL_INFO))

        # write info to technical report
        # with open("result.tex", encoding="utf-8", mode="w") as result_file:
        #     template = LaTeX_JINJA_ENV.get_template(report_template_file)
        #     result_file.write(template.render(**ORDER_FULL_INFO))


def create_txt_files():
    pass


def calculate_CO2barrier():
    pass


# napsat zvlast soubor


def main():
    for item in order_keys:
        print("Type " + item.replace("_", " ") + ":")
        ORDER_FULL_INFO[item] = check_input(input(), item.replace("_", " "))
        if item == "customer_name" or item == "installation_company":
            ORDER_FULL_INFO[item] = ORDER_FULL_INFO[item].capitalize()

    date_start = datetime.today()
    date_end = date_start + timedelta(25)
    date_start, date_end = convert_dateformat(date_start, date_end)
    ORDER_FULL_INFO["date_end"] = date_end

    language_documentation = choose_language()

    choose_protection(language_documentation)

    pprint(ORDER_FULL_INFO, width=1)

    create_LaTeX_documentation(
        language_documentation,
        ORDER_FULL_INFO["protect_machine"],
        ORDER_FULL_INFO["type_protection"],
    )


if __name__ == "__main__":
    main()

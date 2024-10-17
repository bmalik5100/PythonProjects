""" Hashcrack utility functions """
import os
import random

def confirmation(question):
    """ Simple bool prompt to confirm an action """
    print(question + ' [Y/n]')
    try:
        confirm = str(input('$ ')).lower()
        if confirm[0] == 'y':
            return True
        elif confirm[0] == 'n':
            return False
        else:
            print('Try again.')
            confirmation(question)
    except ValueError or NameError or AttributeError:
        print('Try again.')
        confirmation(question)
    except KeyboardInterrupt:
        print("Shutting down.")
        exit()

def parse_rules(rule):
    """ gets additional information for specific rules """

    if rule == 1: ### RULE 1 - NUMBERS
        while True:
            print('$ Enter number to append to each password.')
            print('$ Leave blank for random 0-9:')
            xrule = str(input('$ '))
            if xrule == '':
                xrule = str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
                print('$ Appending ' + xrule + ' to all passwords.')
                break
            elif  xrule.isdigit() and int(xrule) >= 0:
                break
            else:
                print('$ ERROR: Try again.')

    elif rule == 6: ### RULE 6 - CUSTOM
        while True:
            print('$ Enter minimum length of word (Default 4, 0 for no minimum): ')
            minim = input("$ ")
            if minim == '':
                minim = 4
                break
            elif minim == '0':
                minim = 0
                break
            elif len(str(minim)) > 0 and minim.isdigit() and int(minim) > 0:
                break
        while True:
            print('$ Enter maximum length of word (Default 8, 0 for no maximum):')
            maxim = str(input("$ "))
            if maxim == '':
                maxim = 8
                break
            elif maxim == "0":
                maxim = 1000
                break
            elif len(maxim) > 0 and maxim.isdigit() and int(maxim) > int(minim):
                break
        while True:
            print('$ Enter characters to prepend to word (leave blank if N/A):')
            prep = str(input("$ "))
            if prep == '':
                break
            elif len(prep) < 5:
                break
        while True:
            print('$ Enter characters to append to word (leave blank if N/A):')
            app = str(input("$ "))
            if app == '':
                break
            elif len(app) < 5:
                break

        if confirmation("$ Capitalize first letter?"):
            xrule = [minim, maxim, prep, app, True]
        else:
            xrule = [minim, maxim, prep, app, False]
    else: ### CATCH ALL
        xrule = ''

    return xrule

    """
    elif rule == 2: ### RULE 2 - SPECIAL CHARACTERS
        while True:
            print('$ Enter special character to prepend to each password.')
            print('$ Leave blank for random (* / ~ #) :')
            xrule = input('$ ')
            if xrule == '':
                xrule = random.choice(['*', '/', '~', '#'])
                print('$ Prepending ' + xrule + ' to all passwords.')
                break
            elif xrule and (not xrule.isanum()):
                break
            else:
                print('$ ERROR: Try again.')
    """


def print_help_screen():
    """ gives help screen for command line syntax """
    print("$ Usage: hashcrack <PATH_TO_TARGET> <PATH_TO_PASS_FILE> -r <INT> [options]")
    print('$ \t-h - help: display this message')
    print('$ \t-v - Enable verbose mode.')
    print('$ \t-o <PATH_TO_OUTPUT> - outputs successfully found passwords to file.')
    print("$ \t-r <INT> - choose rule for wordlist")
    print("$ \t\t-r 1 - 7 characters long with 1st letter capitalized and 1 digit appended")
    print("$ \t\t-r 2 - 8 characters long with *, /, ~, or # prepended")
    print("$ \t\t-r 3 - 5 chars with a's and l's replaced with @'s and 1's")
    print("$ \t\t-r 4 - only numbers up to 6 digits long")
    print("$ \t\t-r 5 - all words in wordlist file")
    print("$ \t\t-r 6 - custom")
    exit()

def verify_args(args):
    """ this would be a whole lot easier if I made a GUI with drop down menus """

    # checking for help message
    if '-h' in args or '--help' in args:
        print_help_screen()

    # Checking minimum args
    elif len(args) < 3:
        print('$ ERROR: Not enough arguments.')
        print_help_screen()

    # Checking file existance
    elif not os.path.isfile(args[1]):
        print('$ ERROR: Could not find file ' + args[1])
        print_help_screen()
    elif not os.path.isfile(args[2]):
        print('$ ERROR: Could not find file ' + args[2])
        print_help_screen()

    # checking output file
    elif '-o' in args:
        try:
            open(args[args.index('-o') + 1], 'a').write('$$$ HASHCRACK OUTPUT FILE $$$\n')
        except IndexError:
            print("$ ERROR: please enter a valid output file.")
            print_help_screen()
        except PermissionError:
            print("$ ERROR: Cannot create/access output file.")
            print_help_screen()
    # Checking file existance and read access
    try:
        open(args[1], 'r')
        open(args[2], 'r')
    except FileNotFoundError as err_msg:
        print('$ ERROR: Could not find one or more files: ' + str(err_msg))
        print_help_screen()
    except PermissionError as err_msg:
        print('$ ERROR: Could not access one or more files: ' + str(err_msg))
        print_help_screen()

    # checking rule boundries
    if '-r' in args:

        try:
            rule = str(args[args.index('-r') + 1])
        except IndexError or UnboundLocalError:
            print("$ Error: No rule set.")
            print_help_screen()

        if not rule.isdigit():
            print("$ ERROR: Invalid rule number.")
            print_help_screen()
        elif rule not in ["1","2","3","4","5","6"]:
            print('$ ERROR: Rule out of bounds.')
            print_help_screen()
    else:
        print("$ ERROR: Please choose a rule.")
        print_help_screen()

    # all good
    return True

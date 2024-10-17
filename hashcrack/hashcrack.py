"""
Hashcrack SHA-256 password bruteforce progranm
Written by Benjamin Malik
"""
import hashlib
import time
import sys
import re
import utilities
from tqdm import tqdm


ARGS = sys.argv
VERBOSE = '-v' in ARGS
ENABLE_LOG = '-o' in ARGS

def generate_viable_passwords(pfile, mode, extra):
    """ creates and returns an array of passwords filtered by rules """
    viables = []

    def a_or_l(char):
        """ quick check if char is an a or an l """
        if char in 'Aa':
            return '@'
        elif char in 'Ll':
            return '1'

    if mode == 1: # 7 chars with 1st letter capitalized and 1 digit appended
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                if len(passwd) == 8:
                    passwd = passwd[:7] + extra
                    passwd = re.sub(r'[A-Za-z]',lambda m:m.group(0).upper(),passwd,1)
                    viables.append(passwd)

    elif mode == 2: # 8 chars with * / ~ or # at the beginning
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                if len(passwd) == 9 and passwd[0] in '*/~#':
                    passwd = passwd[:8]
                    viables.append(passwd)

    elif mode == 3: # 5 chars with with a's, l's replaced with @'s, 1's
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                if len(passwd) == 6:
                    passwd = passwd[:5]
                    ### come back to this, possibly remove capitals ###
                    passwd = passwd.replace('a','@').replace('l','1')
                    viables.append(passwd)

    elif mode == 4: # only numbers up to 6 digits
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                passwd = passwd[:len(passwd) - 1]
                if passwd.isdigit() and len(passwd) < 7:
                    viables.append(passwd)

    elif mode == 5: # any
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                passwd = passwd[:len(passwd) - 1]
                viables.append(passwd)

    elif mode == 6: # custom
        with open(pfile, 'r') as wordlist:
            for passwd in wordlist:
                plen = len(passwd)
                if plen >= int(extra[0]) and plen <= int(extra[1]):
                    passwd = extra[2] + passwd[:len(passwd)] + extra[3]
                    if extra[4]:
                        passwd = re.sub(r'[A-Za-z]',lambda m:m.group(0).upper(),passwd,1)
                    viables.append(passwd)


    return viables

def convert_to_hash(arr, hashtype):
    """ Iterates through array, converting through hashlib sha algorythm """

    global VERBOSE
    failures = 0
    new_arr = []

    if VERBOSE:
        print("$ Converting each to SHA-256 hash...")
        for string in arr:
            try:
                new_arr.append([string, hashlib.sha256(string.encode('utf-8')).hexdigest()])
            except Exception as err_msg:
                print("$ Could not convert " + string + ':' + str(err_msg))
                failures += 1
        print('$ done.')

    else: # not verbose
        for string in tqdm(arr, "$ Converting each to SHA-256 hash..."):
            try:
                new_arr.append([string, hashlib.sha256(string.encode('utf-8')).hexdigest()])
            except:
                failures += 1

    return new_arr, failures

def try_crack(pass_arr, target):
    """ tries matching unknown hashes with those in hashlist """
    global VERBOSE, ENABLE_LOG

    with open(target, 'r') as targetfile:
        for line in targetfile: # begin loop
            cracked = False
            try: # make sure file is readable
                try:
                    userinfo = line.split(':')
                    tuser = userinfo[0]
                    thash = userinfo[1]
                except:
                    print(
                    '$ ERROR: Target file in incorrect format (user:pass) or (user:pass:extra).'
                    )
                    exit()
            except Exception as err_msg:
                print("$ Error: " + str(err_msg))
            print("$ Trying hashlist on user " + tuser + '...', end='')
            for h in pass_arr:
                if VERBOSE:
                    print("\n$ Trying pass " + h[0] + " on user " + tuser + '...')

                if h[1] == thash:
                    cracked = True
                    print('Success!\n')
                    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                    print("$ FOUND MATCH FOR USER " + tuser)
                    print('$ PASSWORD: ' + h[0] + '\n$ HASH: ' + h[1])
                    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')

                    if ENABLE_LOG:
                        open(ARGS[ARGS.index('-o') + 1] ,'a').write( tuser + ':' + h[0] + '\n')

                    while True:
                        if utilities.confirmation('$ Continue?'):
                            break
                        else:
                            print('Shutting down.')
                            exit()
                    break
            if not cracked:
                print("failure.")

def main(passfile, targetfile, rule):
    """ Performs eachs step in bruteforce attack """

    # STEP 1 - CREATE WORDLIST ARRAY FROM FILE AND RULES
    try:
        xrule = utilities.parse_rules(rule)
        start = time.perf_counter()
        print("$ Generating custom wordlist...", end='')
        passlist = generate_viable_passwords(passfile, rule, xrule)
        print('done.')
        print('$ Created ' + str(len(passlist)) + ' words.')
    except Exception as err_msg:
        print('\n$ Error: ' + str(err_msg))
        exit()

    # STEP 2 - CONVERT WORDS IN WORDLIST ARRAY TO RESPECTIVE SHA-256 HASHES
    try:
        hashpairs, fails = convert_to_hash(passlist, None)
        print('$ Created ' + str(len(passlist) - fails) + ' hashes.')
        if fails > 0:
            print('$ Could not convert ' + str(fails) + ' words.')
    except Exception as err_msg:
        print('\n$ ERROR: ' + str(err_msg))

    # STEP 3 - TESTING GENERATED HASHES ON PASSLIST
    try_crack(hashpairs, targetfile)
    end = time.perf_counter()
    print("$ Bruteforce completed in " + str(round(end - start, 2)) + " seconds.")


if utilities.verify_args(ARGS):
    main(ARGS[2], ARGS[1], int(ARGS[ARGS.index('-r') + 1]))

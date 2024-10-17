index = 0
numbers = []
areacodes = open('area_codes.txt', 'r').read().split(', ')

with open('all210Phones.txt', 'w') as wlist:
    for code in areacodes:
        while index < 10000000:
            numstr = str(index)
            while len(numstr) != 7:
                numstr = '0' + numstr
            numstr = '210' + numstr
            wlist.write(numstr + '\n')
            index += 1

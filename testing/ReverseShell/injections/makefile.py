""" makes a file """
from datetime import datetime

dtt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open("file.txt", "wb") as file_w:
    file_w.write(str.encode("File written successfully at " + dtt + "\n"))

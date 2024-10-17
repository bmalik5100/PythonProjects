import io

with open("file.txt", "wb") as file_w:
    file_w.write(str.encode("File written successfully!"))

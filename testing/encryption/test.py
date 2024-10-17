import os
from getpass import getuser
from pwd import getpwuid
# entire_directory = []


# for root, dirs, files in os.walk("."):
#     for f in files:
#         entire_directory.append(os.path.join(root, f))

# for files in entire_directory:
#     print(files)

file_name = __file__

#try:
#    file_owner = getpwuid(os.stat(file_name).st_uid).pw_name
#except:
file_owner = os.stat(file_name).st_uid
print(file_owner)
if file_owner == os.getlogin():
    print(True)
else:
    print(False)

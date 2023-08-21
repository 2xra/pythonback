import os

dirlist = os.listdir()
for element in dirlist:
    if ".tex" in element:
        pass
    elif ".pdf" in element:
        pass
    else:
        os.remove(element)
import os
import time

def watch_new_file(file_path):
    return os.listdir(file_path)


path = r"C:\Users\juankroos\PycharmProjects\AgentIA\Agent"
dirr = os.getcwd()
dir = watch_new_file(path)
print(dir)
for d in dir:
    print(dirr + "\\" + d)
    current_file1 = (dirr + "\\" + d)
    print(current_file1)
    while True:
        pass


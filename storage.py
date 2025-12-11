import os_getter
import os
import sys
import sqlite3

def find_or_create_data_folder():
    if os_getter.os_name == "Windows":
        folder_name = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\ZerolfieWeb" # Windows
    else:
        folder_name = f"{os.getcwd()}/.zerolfie-web" # Linux

    os.makedirs(folder_name)

    return folder_name

class Profile:
    def __init__(self, name):
        self.datafolder=find_or_create_data_folder()+f"/profile_{name}/"
        self.mydb = sqlite3.connect()

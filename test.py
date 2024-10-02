import os

def check_file_exists(file_path):
    if os.path.isfile(file_path):
        print("Tệp tồn tại.")
    else:
        print("Tệp không tồn tại.")

file_path = r"E:\Code\serverkma-sec\server\.docker\data\files\models\64b42eda7d41ef8ebdb4909b\model.h5"
check_file_exists(file_path)

import os
from util.abs_path import abs_path

def verify_folder(folder,debug=False):
    if not os.path.exists(folder):
        if(debug): print('creating folder '+ folder)
        os.makedirs(folder)
    elif os.path.isfile(folder):
        if(debug): print('there exists folder of same name')

def verify_file(file_path,debug=False):
    if not os.path.exists(file_path):
        if(debug): print('creating file '+ file_path)
        file_ = open(file_path, 'w')
        file_.close()
    elif os.path.isdir(file_path):
        if(debug): print('there exists file of same name')

def get_files_in_dir(folder):
    folder = abs_path(folder)
    verify_folder(folder)
    return os.listdir(folder)

def clean_folder(folder):
    folder = abs_path(folder)
    verify_folder(folder)
    list_files = get_files_in_dir(folder)
    for file_name in list_files:
        os.remove(folder + "/" + file_name)

def del_folder(folder):
    folder = abs_path(folder)
    verify_folder(folder)
    os.rmdir(folder)

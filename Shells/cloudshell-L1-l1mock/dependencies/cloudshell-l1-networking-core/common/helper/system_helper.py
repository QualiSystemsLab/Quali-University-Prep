#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys


def get_file_path(root_path, relative_path):
    return os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(root_path)), relative_path)


def get_file_folder(file_path):
    index = file_path.rfind('\\')
    file_folder = ''
    if index != -1:
        file_folder = file_path[:index + 1]
    else:
        index = file_path.rfind('/')
        if index != -1:
            file_folder = file_path[:index + 1]

    return file_folder

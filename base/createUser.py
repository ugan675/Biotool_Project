import os
import re
import subprocess


class userFiles:
    def __init__(self, id):
        self.id = id
        self.add_directory(id)
        self.add_init_file(id)

    def add_directory(self, id):
        if id:
            path = './documents/' + id
            os.mkdir(path)

    def add_init_file(self, id):
        if id:
            file = "./directories/" + id + '.txt'
            open(file, "w")
            file_opened = open(file, 'a')
            file_opened.write(self.get_path('./documents/' + id))
            file_opened.close()

    def get_path(self, dir):
        new_cmd = '(cd ' + dir + ' && pwd)'
        process = subprocess.Popen(
            new_cmd, shell=True, stdout=subprocess.PIPE)
        return process.communicate()[0].decode('utf-8')

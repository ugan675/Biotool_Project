import subprocess
from subprocess import check_output, STDOUT, CalledProcessError, PIPE
from fs import open_fs
import os
from os import scandir, walk
from scandir import scandir, walk
import re


class command:
    def __init__(self, id):
        self.id = id
        self.root = '/django/documents/' + id
        self.initial_root = '/django/documents/' + id
        self.permmisions = '/django/directories/' + id + '.txt'
        self.COMMANDS = {'ls': self.ls, 'mkdir': self.mkdir,
                         'cd': self.cd, 'pwd': self.pwd, 'rmdir': self.rmdir, 'diff': self.diff, 'cmp': self.cmp, 'wc': self.wc, 'rm': self.rm,
                         'cat': self.cat, 'tail': self.tail, 'head': self.head, 'sort': self.sort, 'grep': self.grep, 'sed': self.sed, 'needle': self.needle,
                         'water': self.water, 'esearch': self.tools, 'efetch': self.tools, 'epost': self.tools, 'esummary': self.tools,
                         'elink': self.tools, 'einfo': self.tools, 'equery': self.tools, 'blastp': self.tools, 'blastn': self.tools,
                         'blastx': self.tools, 'tblastn': self.tools, 'tblastx': self.tools, 'makeblastdb': self.tools, 'makeprofiledb': self.tools,
                         'blastdbcmd': self.tools, 'dustmaker': self.tools, 'segmasker': self.tools, 'windowmasker': self.tools, 'convert2blastmask': self.tools,
                         'rpsblast': self.tools, 'rpstblastn': self.tools}

    def check_if_valid(self, splitted_cmd):
        if '' in splitted_cmd:
            return False
        else:
            return True

    def check_if_name_valid(self, dir_name):
        isIllegal = re.search('["`#%@&*:<>=!?\\{|}\s]+', dir_name)
        if isIllegal == None:
            return True
        else:
            return False

    def check_if_file_valid(self, file_name):
        isIllegal = re.search('["`#%@&*:<>=!?/\\{|}\s]+', file_name)
        if isIllegal == None:
            return True
        else:
            return False

    def add_perm_to_dir(self, dir):
        file = open(self.permmisions, 'a')
        file.write(self.get_path(dir))
        file.close()

    def delete_perm_from_dir(self, dir):
        with open(self.permmisions, "r") as f:
            lines = f.readlines()
        with open(self.permmisions, "w") as f:
            for line in lines:
                if line != dir:
                    f.write(line)

    def get_path(self, dir):
        new_cmd = '(cd ' + dir + ' && pwd)'
        process = subprocess.Popen(
            new_cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE)
        return process.communicate()[0].decode('utf-8')

    def get_legal_path(self, dir):
        if self.check_for_permmision(dir):
            return self.get_path(dir)
        else:
            return None

    def get_initial_path(self):
        new_cmd = '(cd . && pwd)'
        process = subprocess.Popen(
            new_cmd, shell=True, cwd=self.initial_root, stdout=subprocess.PIPE)
        return process.communicate()[0].decode('utf-8')

    def check_for_permmision(self, arg):
        test_cmd = '(cd ' + arg + ' && pwd)'
        with subprocess.Popen(test_cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=STDOUT) as process:
            try:
                test_directory = process.communicate()[0].decode('utf-8')
            except CalledProcessError as exc:
                return False
        return self.check_in_file(test_directory)

    def check_for_file_permmision(self, arg):
        arg = arg.split('/')
        dir_name = arg.pop()
        arg = '/'.join(arg)
        test_cmd = '(cd ./' + arg + ' && pwd)'
        with subprocess.Popen(test_cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=STDOUT) as process:
            try:
                test_directory = process.communicate()[0].decode('utf-8')
            except CalledProcessError as exc:
                return False
        return self.check_in_file(test_directory)

    def check_in_file(self, test_dir):
        with open(self.permmisions) as f:
            lines = [line for line in f]
        if test_dir in lines:
            return True

        return False

    ###########################################################################################
    # cd - returns only error messages, no parameters
    # can not be used in pipe
    def cd(self, cmd,  args, passed_input):
        if not args:
            self.root = self.initial_root
        elif len(args) == 1:
            path = self.correct_path(args[0])
            if path and self.check_for_permmision(path):
                self.root = self.get_path(path).rstrip()
            else:
                return "No such directory: " + args[0], None
        else:
            return "cd: too many arguments", None
        return None, None

    ###########################################################################################
    # ls - returns error messages and process, no parameters
    # can not be used in a pipe
    def ls(self, cmd, args, passed_input):
        msg = str()
        process = None
        valid_args = []

        if len(args) == 0:
            process = subprocess.Popen(
                [cmd], cwd=self.root, stdout=subprocess.PIPE)
            return msg, process

        for arg in args:
            fixed_arg = self.get_correct_path(arg)
            if self.check_for_permmision(fixed_arg):
                valid_args.append(fixed_arg)
            else:
                msg += "No such directory: " + fixed_arg + "\n"

        if valid_args:
            cmd = "ls " + ' '.join(valid_args)
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # mkdir - returns only error messages, no parameters
    # can not be used in a pipe
    def mkdir(self, cmd, args, passed_input):
        msg = str()
        if not args:
            return cmd + ": missing operand\n", None
        for arg in args:
            dir = arg.split('/')
            dir_name = dir.pop()
            dir = '/'.join(dir)
            if not self.check_if_name_valid(dir_name):
                msg += "Directory name: " + dir + " is illegal\n"
            elif not dir or self.check_for_permmision(dir):
                process = subprocess.Popen(
                    [cmd, arg], cwd=self.root, stderr=subprocess.PIPE)
                out, error = process.communicate()
                if error:
                    msg += error.decode('utf-8')
                else:
                    self.add_perm_to_dir(arg)
            else:
                msg += "No such directory: " + dir + "\n"
        return msg, None

    ###########################################################################################
    # rmdir - returns only error messages, no parameters
    # can not be used in a pipe
    def rmdir(self, cmd, args, passed_input):
        msg = str()
        if not args:
            return cmd + ": missing operand\n", None
        for arg in args:
            dir = arg
            if self.check_for_permmision(dir):
                dir_deleted = self.get_path(dir)
                process = subprocess.Popen(
                    [cmd, arg], cwd=self.root, stderr=subprocess.PIPE)
                out, error = process.communicate()
                if process.returncode != 0:
                    msg += error.decode('utf-8')
                else:
                    self.delete_perm_from_dir(dir_deleted)
            else:
                msg += "No such directory: " + dir + "\n"
        return msg, None

    ###########################################################################################
    # pwd - returns only path, no parameters
    def pwd(self, cmd, args, passed_input):
        if self.root == self.initial_root:
            return "~", None
        else:
            return "~" + self.get_modified_dir(), None

    ###########################################################################################
    # diff - returns error messages and process, parameters
    def diff(self, command, args, passed_input):
        param = str()
        msg = str()
        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if not args:
            return command + ": missing operand\n", None

        if len(args) == 2:
            arg1 = args[0]
            if_file1 = self.check_for_file_permmision(arg1)
            arg2 = args[1]
            if passed_input == None:
                if_file2 = self.check_for_file_permmision(arg2)
                if if_file1 and if_file2:
                    cmd = command + " " + param + ' '.join(args)
                    process = subprocess.Popen(
                        cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if not if_file1:
                    msg += command + ": " + arg1 + " No such file or directory\n"
                if not if_file2:
                    msg += command + ": " + arg2 + " No such file or directory\n"
                return msg, process
            elif passed_input and arg2 == '-':
                if not if_file1:
                    return command + ": " + arg1 + " No such file or directory\n", None
                else:
                    cmd = command + " " + param + ' '.join(args)
                    process = subprocess.Popen(
                        cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return msg, process

        elif len(args) == 1:
            return command + ": missing operand after '" + str(args[0]) + "'\n", None

        return command + ": extra operand: " + ' '.join(map(str, args[2:])) + "\n", None

    ###########################################################################################
    # wc - returns error messages and process, parameters
    def wc(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if passed_input == None and not args:
            return "wc: missing operand\n", process
        elif passed_input and not args:
            cmd = "wc " + param
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            valid_args = []
            for arg in args:
                if not self.check_for_file_permmision(arg):
                    msg += "No such directory: " + arg + "\n"
                else:
                    valid_args.append(arg)

            if valid_args:
                cmd = "wc " + param + ' '.join(valid_args)
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # cmp - returns error messages and process, parameters
    def cmp(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if not args:
            return "cmp: missing operand\n", None

        if len(args) == 2:
            arg1 = args[0]
            if_file1 = self.check_for_file_permmision(arg1)
            arg2 = args[1]
            if passed_input == None:
                if_file2 = self.check_for_file_permmision(arg2)
                if if_file1 and if_file2:
                    cmd = "cmp " + param + ' '.join(args)
                    process = subprocess.Popen(
                        cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if not if_file1:
                    msg += "cmp: " + arg1 + " No such file or directory\n"
                if not if_file2:
                    msg += "cmp: " + arg2 + " No such file or directory\n"
                return msg, process
            elif passed_input and arg2 == '-':
                if not if_file1:
                    return "cmp: " + arg1 + " No such file or directory\n", None
                else:
                    cmd = "cmp " + param + ' '.join(args)
                    process = subprocess.Popen(
                        cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return msg, process

        elif len(args) == 1:
            return "cmp: missing operand after '" + str(args[0]) + "'\n", None

        return "cmp: extra operand: " + ' '.join(map(str, args[2:])) + "\n", None

    ###########################################################################################
    # sort - returns error messages and process, parameters
    def sort(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if passed_input == None and not args:
            msg += "sort: missing operand\n"
        elif passed_input and not args:
            cmd = "sort " + param
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            for arg in args:
                if not self.check_for_file_permmision(arg):
                    msg += "No such directory: " + arg + "\n"
                else:
                    valid_args.append(arg)

            cmd = "sort " + param + ' '.join(valid_args)

            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # cat - returns error messages and process, parameters
    def cat(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if passed_input == None and not args:
            msg += "cat: missing operand\n"
        elif passed_input and not args:
            cmd = "cat " + param
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            for arg in args:
                if not self.check_for_file_permmision(arg):
                    msg += "No such directory: " + arg + "\n"
                else:
                    valid_args.append(arg)

            cmd = "cat " + param + ' '.join(valid_args)

            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # tail - returns error messages and process, parameters
    def tail(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if passed_input == None and not args:
            msg += "tail: missing operand\n"
        elif passed_input and not args:
            cmd = "tail " + param
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            for arg in args:
                if not self.check_for_file_permmision(arg):
                    msg += "No such directory: " + arg + "\n"
                else:
                    valid_args.append(arg)

            cmd = "tail " + param + ' '.join(valid_args)

            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # head - returns error messages and process, parameters
    def head(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if passed_input == None and not args:
            msg += "head: missing operand\n"
        elif passed_input and not args:
            cmd = "head " + param
            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            for arg in args:
                if not self.check_for_file_permmision(arg):
                    msg += "No such directory: " + arg + "\n"
                else:
                    valid_args.append(arg)

            cmd = "head " + param + ' '.join(valid_args)

            process = subprocess.Popen(
                cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # rm - returns only error messages
    # can not be used in a pipe
    def rm(self, cmd, args, passed_input):
        msg = ''
        deleted_files = []
        if not args:
            return "rm: missing operand\n", None
        for arg in args:
            dir = arg
            if self.check_for_file_permmision(dir):
                process = subprocess.Popen(
                    ['rm', arg], cwd=self.root, stderr=subprocess.PIPE)
                output, error = process.communicate()
                if error:
                    msg += error.decode('utf-8')
                else:
                    deleted_files.append(arg)
            else:
                msg += "No such directory: " + dir + "\n"
        return msg, None

    ###########################################################################################
    # grep - returns error messages and process, parameters
    def grep(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if not args or len(args) == 1:
            return "grep: missing operand\n", None

        regex = args[0]
        args = args[1:]

        for arg in args:
            if self.check_for_file_permmision(arg):
                valid_args.append(arg)
            else:
                msg += "No such directory: " + arg + "\n"

        if valid_args:
            cmd = "grep " + param + regex + " " + ' '.join(valid_args)
            if passed_input:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # sed - returns error messages and process, parameters
    def sed(self, cmd2, args, passed_input):
        param = str()
        msg = str()
        valid_args = []
        process = None

        while args and args[0][0] == '-':
            param += args[0] + " "
            args = args[1:]

        if not args or len(args) == 1:
            return "sed: missing operand\n", None

        regex = args[0]
        args = args[1:]

        for arg in args:
            if self.check_for_file_permmision(arg):
                valid_args.append(arg)
            else:
                msg += "No such directory: " + arg + "\n"

        if valid_args:
            cmd = "sed " + param + regex + " " + ' '.join(valid_args)
            if passed_input:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # needle - returns message
    def needle(self, cmd2, args, passed_input):
        options = {'asequence': '', 'bsequence': '',
                   'gapopen': '10.0', 'gapextend': '0.5', 'outfile': '', 'datafile': '', 'endweight': '', 'endopen': '', 'endextend': ''}
        parameters = []
        msg = str()
        process = None

        if not args or len(args) == 1:
            return "needle: missing operand\n", None

        while args and len(args) % 2 == 0 and args[0][0] == '-':
            param = args[0][1:]
            if param in options:
                if self.check_for_file_permmision(args[1]):
                    parameters.append(param)
                    options[param] = args[1]
                else:
                    return "No such directory: " + args[1] + "\n", None
            else:
                return "needle: option: " + param + " is not valid\n", None
            args = args[2:]

        if not self.check_if_file_valid(options['outfile']):
            return "File name: " + options['outfile'] + " is illegal\n", None

        cmd = 'needle'
        for param in parameters:
            if param in options:
                cmd += " -" + param + " " + options[param]

        cmd += " -gapopen " + options['gapopen']
        cmd += " -gapextend " + options['gapextend']

        process = subprocess.Popen(
            cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # water - returns message
    def water(self, cmd2, args, passed_input):
        options = {'asequence': '', 'bsequence': '',
                   'gapopen': '10.0', 'gapextend': '0.5', 'outfile': '', 'datafile': ''}
        parameters = []
        msg = str()
        process = None

        if not args or len(args) == 1:
            return "water: missing operand\n", None

        while args and len(args) % 2 == 0 and args[0][0] == '-':
            param = args[0][1:]
            if param in options:
                if self.check_for_file_permmision(args[1]):
                    parameters.append(param)
                    options[param] = args[1]
                else:
                    return "No such directory: " + args[1] + "\n", None
            else:
                return "water: option: " + param + " is not valid\n", None
            args = args[2:]

        if (options['outfile']):
            new_dir = options['outfile']
            dir = new_dir.split('/')
            dir_name = dir.pop()
            if not self.check_if_file_valid(dir_name):
                return "File name: " + dir_name + " is illegal\n", None

        cmd = 'water'
        for param in parameters:
            if param in options:
                cmd += " -" + param + " " + options[param]

        cmd += " -gapopen " + options['gapopen']
        cmd += " -gapextend " + options['gapextend']

        process = subprocess.Popen(
            cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return msg, process

    ###########################################################################################
    # esearch - returns message
    def tools(self, command, args, passed_input):
        msg = str()
        process = None
        valid_args = [
            valid_arg for valid_arg in args if self.is_argument_valid(valid_arg)]

        print(valid_args)
        # print(args)

        if len(valid_args) == len(args):
            cmd = command + " " + " ".join(args)
            if passed_input:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdin=passed_input.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    cmd, shell=True, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            msg = command + ": invalid parameters are given\n"

        return msg, process

    ###########################################################################################
    def is_argument_valid(self, arg):
        if self.check_if_option_tag(arg):
            return True
        elif self.check_if_path(arg):
            fixed_path = self.get_correct_path(arg)
            if self.check_for_permmision(fixed_path):
                return True
            else:
                return False
        elif not self.check_if_no_illegal_symbols(arg):
            return True

        return False

    def check_if_option_tag(self, arg):
        return bool(re.search("^-{1,2}[a-zA-Z]+$", arg))

    def check_if_no_illegal_symbols(self, arg):
        return bool(re.search('[#%@&*:=!?\\{|}\s-]+', arg))

    def check_if_path(self, arg):
        return bool(re.search('^~{0,1}(\/|(\/[a-zA-Z0-9_]+))+$', arg))

    def fast_scandir(self, dirname):
        subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
        for dirname in list(subfolders):
            subfolders.extend(self.fast_scandir(dirname))
        return subfolders

    def correct_path(self, path):
        dirs = path.split('/')
        if dirs[0] == '~':
            dirs = dirs[1:]
            self.root = self.initial_root
        return '/'.join(dirs)

    def get_correct_path(self, path):
        dirs = path.split('/')
        if dirs[0] == '~':
            dirs = dirs[1:]
            return self.initial_root + '/' + '/'.join(dirs)
        else:
            return path

    def split_into_args(self, splitted_cmd):
        splitted = splitted_cmd.split()
        return splitted

    def get_file_dir(self):
        return self.get_path('.').rstrip()

    def get_commands(self):
        return list(self.COMMANDS.keys())

    def get_initial_dir(self):
        return self.get_initial_path().rstrip()

    def get_modified_dir(self):
        dir = self.get_file_dir()
        initial = self.get_initial_dir()
        dir = dir.replace(initial, '')
        return dir

    def get_files(self):
        # path = self.get_file_dir()
        path = self.root
        return os.listdir(path)

    def remove_new_line(self, path):
        return path.replace('\n', '')

    def get_all_files_recursively(self, path):
        search_path = self.root if path == "" else path
        all_files = []
        for root, d_names, f_names in os.walk(search_path):
            for f in f_names:
                all_files.append(os.path.join(root, f))
            for d in d_names:
                all_files.append(os.path.join(root, d))
        root_part = re.sub(r'^/django/', '', self.root)
        pattern = r'^.*' + root_part + r'/'
        pattern_for_initial_root = r'^' + self.initial_root + r'/*'
        valid_files = [re.sub(pattern, '', line) for line in all_files]
        valid_files_without_root = [
            re.sub(pattern_for_initial_root, '', line) for line in valid_files]
        return valid_files_without_root

    def execute(self, cmd):
        parts_of_pipe = cmd.split('|')
        passed_input = None
        all_msg = str()
        process = ''
        # Checking if there are no empty commands
        if self.check_if_valid(parts_of_pipe):
            for one_pipe_part in parts_of_pipe:  # Returns None if contains commands not allowed in the pipe
                args = self.split_into_args(one_pipe_part)
                # cmd_name = args[0] if args != None else str()
                if args != None:
                    cmd_name = args[0]
                else:
                    cmd_name = str()
                if cmd_name in self.COMMANDS:
                    msg, process = self.COMMANDS[cmd_name](
                        cmd_name, args[1:], passed_input)
                    if process:
                        passed_input = process
                        if process.stderr:
                            for line in process.stderr:
                                all_msg += line.decode('utf-8')
                    if msg:
                        all_msg += msg
                    # if process != None:
                    # out, error = process.communicate()
                    # if out:
                    #   msg += out.decode('utf-8')
                    # if error:
                    #   msg += error.decode('utf-8')
                # command not found -> error
                elif cmd_name:
                    all_msg = cmd_name + ": command not found\n"
            if process:
                out, error = process.communicate()
                if out:
                    all_msg += out.decode('utf-8')
                if error:
                    all_msg += error.decode('utf-8')
            if all_msg:
                return all_msg.rstrip()
            # else:
            #    output = self.COMMANDS[cmd_name](args[1:])
            #    if output == "\n":
            #        return None
            #    elif output:
            #        return output.rstrip()

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

from .forms import FileForm, RegisterForm
from .models import File, History
from .createUser import userFiles
from .userCommand import command

from subprocess import check_output, STDOUT, CalledProcessError
from subprocess import Popen, PIPE, TimeoutExpired
from time import monotonic as timer

from os import walk
import json
import re

user_loc = userFiles('')
user_cmd = command('')
history_count = 0
COMMANDS = [
    'ls', 'mkdir', 'cd', 'pwd', 'rmdir', 'diff', 'cmp', 'wc', 'rm', 'cat', 'tail',
    'head', 'sort', 'grep', 'sed', 'needle', 'water', 'esearch', 'efetch', 'epost',
    'esummary', 'elink', 'einfo', 'equery', 'blastp', 'blastn', 'blastx', 'tblastn',
    'tblastx', 'makeblastdb', 'makeprofiledb', 'blastdbcmd', 'dustmaker', 'segmasker',
    'windowmasker', 'convert2blastmask', 'rpsblast', 'rpstblastn', 'upload'
]


def home(request):
    global user_cmd
    global history_count
    global user_loc
    form = FileForm()
    if request.user.is_authenticated:
        if request.method == 'POST' and request.is_ajax():
            if 'cmd' in request.POST:
                cmd = request.POST.get("cmd")
                if cmd == '38' or cmd == '40':
                    return getCurrentHistoryCmd(request, cmd)
                elif cmd == 'path':
                    path = request.POST.get('path')
                    return getPossiblePaths(path)
                else:
                    globalresult = current_command(cmd)
                    History.objects.create(user=request.user, command=cmd)
                    command_history = list(History.objects.filter(
                        user=request.user).values('command'))
                    history_count = len(command_history)
                    path = user_cmd.get_modified_dir()
                    files = user_cmd.get_files()
                    command_names = user_cmd.get_commands()
                    user_files_and_dirs = user_cmd.get_all_files_recursively(
                        "")
                    context = {
                        'globalresult': globalresult,
                        'command_history': command_history,
                        'files': files,
                        'path': path,
                        'command_names': command_names,
                        'user_files_and_dirs': user_files_and_dirs
                    }
                    return JsonResponse(context)
            else:
                try:
                    id_form = request.POST.get("id")
                    post_id = json.loads(id_form).get('id')
                except:
                    post_id = json.loads(request.body).get('id')
                if 'search-field' == post_id:
                    return searchForFile(request)
                elif 'search-field-tools' == post_id:
                    return searchForTool(request)
                elif 'upload' == post_id:
                    return upload(request)
    """
        if request.method == 'GET':
            id = request.user.id
            if 'cmd' in request.GET:
                cmd = request.GET['cmd']
                if cmd == '38' or cmd == '40':
                    return getCurrentHistoryCmd(request, cmd)
                elif cmd == 'path':
                    # print("kkkk")
                    path = request.GET['path']
                    # print(path)
                    return getPossiblePaths(path)
                else:
                    globalresult = current_command(cmd)
                    History.objects.create(user=request.user, command=cmd)
                    command_history = list(History.objects.filter(
                        user=request.user).values('command'))
                    history_count = len(command_history)
                    path = user_cmd.get_modified_dir()
                    files = user_cmd.get_files()
                    command_names = user_cmd.get_commands()
                    # user_files_and_dirs = user_loc.get_all_legal_paths(
                    #    request.user.username)
                    user_files_and_dirs = user_cmd.get_all_files_recursively(
                        "")
                    context = {
                        'globalresult': globalresult,
                        'command_history': command_history,
                        'files': files,
                        'path': path,
                        'command_names': command_names,
                        'user_files_and_dirs': user_files_and_dirs
                    }
                    return JsonResponse(context)
    """
    context = getContextForUser(request, form)
    return render(request, 'base/home.html', context)


def getPossiblePaths(path):
    global user_cmd
    if path:
        current_path = user_cmd.get_correct_path(path)
        current_path = user_cmd.get_legal_path(current_path)
        if current_path:
            current_path = user_cmd.remove_new_line(current_path)
            return JsonResponse({'Possible_path': user_cmd.get_all_files_recursively(current_path)})
        else:
            return JsonResponse({'Possible_path': current_path})
    else:
        Possible_path = user_cmd.get_all_files_recursively(path)
        return JsonResponse({'Possible_path': Possible_path})


def searchForFile(request):
    search_str = json.loads(request.body).get('searchText')
    files = [file for file in user_cmd.get_files() if search_str in file]
    return JsonResponse({'files': files})


def searchForTool(request):
    search_str = json.loads(request.body).get('searchText')
    tools = [tool for tool in user_cmd.get_commands() if search_str in tool]
    return JsonResponse({'tools': tools})


def filterHistoryByUser(user):
    command_history = list(History.objects.filter(user=user).values('command'))
    return command_history


def getContextForUser(request, form):
    global history_count
    global user_loc
    global user_cmd
    if request.user.is_authenticated:
        cmd_history = History.objects.filter(user=request.user)
        user_cmd = command(request.user.username)
        command_history = filterHistoryByUser(request.user)
        history_count = len(command_history)
        files = user_cmd.get_files()
        command_names = user_cmd.get_commands()
        user_files_and_dirs = user_cmd.get_all_files_recursively("")
        context = {
            'form': form,
            'files': files,
            'cmd_history': cmd_history,
            'command_names': command_names,
            'user_files_and_dirs': user_files_and_dirs
        }
    else:
        context = {'form': form, 'command_names': COMMANDS}
    return context


def getCurrentHistoryCmd(request, cmd):
    global history_count
    command_history = filterHistoryByUser(request.user)
    command_from_history = ""
    if cmd == '38' and history_count > 0:
        history_count -= 1
        command_from_history = command_history[history_count]['command']
    elif cmd == '40' and history_count < len(command_history) - 1:
        history_count += 1
        command_from_history = command_history[history_count]['command']
    return JsonResponse({'command_from_history': command_from_history})


def loginPage(request):
    global user_cmd
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            user_cmd = command(user.username)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exists.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    global user_loc
    global user_cmd
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            user_loc = userFiles(user.username)
            user_cmd = command(user.username)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration!')

    return render(request, 'base/login_register.html', {'form': form})


def upload(request):
    uploaded_file = request.FILES.get("file")
    path = user_cmd.get_file_dir()
    full_file_name = path + '/' + uploaded_file.name

    files_exist = File.objects.filter(
        name=full_file_name, user=request.user)

    line = 'upload ' + uploaded_file.name
    History.objects.create(user=request.user, command=line)
    command_history = list(History.objects.filter(
        user=request.user).values('command'))

    isIllegal = re.search('[~"`#%@&*:<>=!?/\\{|}\s-]+', uploaded_file.name)
    if isIllegal != None:
        error_msg = ""'File name - ' + uploaded_file.name + " is illegal."
        return JsonResponse({'error': error_msg, 'command_history': command_history})

    if (files_exist):
        error_msg = 'File - ' + uploaded_file.name + " already exists."
        return JsonResponse({'error': error_msg, 'command_history': command_history})
    else:
        fss = FileSystemStorage(location=path)
        filename = fss.save(uploaded_file.name, uploaded_file)
        url = fss.url(filename)
        File.objects.create(
            file=url, user=request.user, name=full_file_name)
        return JsonResponse({'file_name': uploaded_file.name, 'command_history': command_history})


def current_command(command):
    output = user_cmd.execute(command)
    return output

from django import template
import subprocess
import os

register = template.Library()

@register.simple_tag
def current_command(username, comm):
    path = '/home/ubuntu/kursinis/documents/' + username + '/'
    globalresult = subprocess.check_output(comm, shell=True, cwd=path)
    return globalresult 

@register.simple_tag
def cat():
    #globalresult = subprocess.check_output(['cat', '/home/ubuntu/kursinis/documents/ugne123/failas1.txt'], shell=True)
    #path = '/home/ubuntu/kursinis/documents/' + 'ugne123' + '/'
    globalresult = subprocess.check_output("cat /home/ubuntu/kursinis/documents/ugne123/random_sequence.txt", shell=True)
    return globalresult 

@register.filter
def filename(value):
    return os.path.basename(value.file.name)
import argparse
import datetime
import os
import shutil
import stat
import subprocess
import sys


def CleanDir(buildDir):
    if not buildDir or not os.path.isdir(buildDir):
        return

    print('Deleting contents of directory %s' % buildDir)
    for entry in os.listdir(buildDir):
        path = os.path.join(buildDir, entry)
        if os.path.isfile(path):
            try:
                os.chmod(path, stat.S_IWRITE)
                os.remove(path)
            except OSError:
                pass
        elif os.path.isdir(path):
            def del_rw(action, name, exc):
                try:
                    os.chmod(name, stat.S_IWRITE)
                    os.remove(name)
                except OSError:
                    pass
            shutil.rmtree(path, onerror=del_rw)


def RunCommand(command, out):
    print('Running command: %s' % ' '.join(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=sys.stderr, cwd=os.getcwd())
    for c in iter(lambda: process.stdout.read(1).decode('utf-8'), ''):
        out.write(c)
    code = process.wait()
    if code != 0:
        out.write('Child process exited with nonzero return code: %d\n' % code)
        exit(1)


def ModifySomeFiles():
    files = [
        os.path.join(os.getcwd(), 'bora', 'public', 'vm_basic_types.h'),
    ]
    for file in files:
        if not os.access(file, os.W_OK):
            command = ['p4.exe' if os.name == 'nt' else 'p4', 'edit', file]
            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError:
                print('Failed command to check out read-only file: %s' %
                      ' '.join(command))
                exit(1)
        with open(file, 'a') as myfile:
            myfile.write('// a comment')

parser = argparse.ArgumentParser(description='Repeat builds')
parser.add_argument('--type',
                    help='Run type. '
                         'full: deletes bora/build inbetween runs. '
                         'incremental: touches some source files. '
                         'none: just repeats the command')
parser.add_argument('--number', help='Number of builds to run')
parser.add_argument('--log', help='Log to output the current build command to '
                                  '(starts over with each build)')
parser.add_argument('command', help='Command to run', nargs=argparse.REMAINDER)
args = vars(parser.parse_args())

type = args['type'] or 'none'
number = int(args['number']) if args['number'] else None
command = args['command']
log = args['log']

if type not in ['incremental', 'full', 'none']:
    print('Unsupported type: %s' % type)
    exit(1)

if not command:
    print('You need to provide a command to run')
    exit(1)

dirs = []
buildDir = os.path.join(os.getcwd(), 'bora', 'build')

if os.name == 'nt':
    executable = command[0]
    _, ext = os.path.splitext(executable)
    # Windows needs to autocomplete an extension.
    if not ext:
        for extension in ['.exe', '.bat', '.cmd', '.lnk']:
            candidate = executable + extension
            if os.path.isfile(candidate):
                command[0] = candidate
                break

totalSeconds = 0
results = []
while not number or len(results) < number:
    # Clean up after our test run.
    if type == 'incremental':
        ModifySomeFiles()
    elif type == 'full':
        CleanDir(buildDir)

    out = logFile = open(log, 'wb') if log else sys.stdout

    before = datetime.datetime.now()
    RunCommand(command, out)
    delta = datetime.datetime.now() - before
    seconds = delta.total_seconds()
    totalSeconds = totalSeconds + seconds
    results.append(seconds)

    print('Finished %d runs' % len(results))
    average = totalSeconds / len(results)
    print('Average run: %d minutes %d seconds' % (average / 60, average % 60))
    print('Raw results: %s' % results)

    if log:
        out.close()

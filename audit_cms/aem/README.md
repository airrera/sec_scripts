# aem
Scripts used for pentesting AEM.

Based on the following papers and tools: 

- https://speakerdeck.com/0ang3el/securing-aem-webapps-by-hacking-them
- https://speakerdeck.com/0ang3el/hunting-for-security-bugs-in-aem-webapps
- https://speakerdeck.com/0ang3el/aem-hacker-approaching-adobe-experience-manager-webapps-in-bug-bounty-programs
- https://labs.withsecure.com/publications/securing-aem-with-dispatcher
- https://github.com/0ang3el/aem-hacker


## aemleaks.py
Script created for crawling JCR endpoints (not filtered by the dispatchers) searching at the same time for potentially sensitive information such as passwords and secrets. The script also search for usernames and emails addresses that could be used in SE attacks.

Note: This script was build for Python3.

Note2: Search patterns used needs to be improved to obtain better results and rule out false positives

### Usage

```
$> python3 aemleaks.py -h
usage: aemleaks.py [-h] --url URL [-d] [-p PROXY] [-l LEVEL] [-H HEADERS]

Script for crawling endpoints on AEM environments - Detecting users content, PII and secrets. 

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL of the target along with the vulnerable path. Consider using a endpoint ending with '.1.json'
                        or equal
  -d, --debug           debug output
  -p PROXY, --proxy PROXY
                        Https and http proxies.
  -l LEVEL, --level LEVEL
                        Depth level.
  -H HEADERS, --Headers HEADERS
                        Adding HTTP headers. Could be useful for bypass Akamai's rules
```

### Sample
TODO

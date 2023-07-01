import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
import http.server,ssl,socketserver

from io import BytesIO

login_page=b'''
<html>
<H2>Login</H2>
<form action="/" method="post">
  <div class="container">
    <label for="uname"><b>Username</b></label>
    <input type="text" placeholder="Enter Username" name="uname" required>

    <label for="psw"><b>Password</b></label>
    <input type="password" placeholder="Enter Password" name="psw" required>

    <button type="submit">Login</button>
  </div>
</form>
</html>
'''

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/profile"):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                output = ""
                output += '<html><body>Hello!'
                output += '<form method="POST" enctype="text/plain" action="/profile"><h2> What would you like me to say?</h2><input name="message" type="text" /><input type="submit" value="Submit" /></form>'
                output += '</body></html>'
                self.wfile.write(output.encode())
                print(output)
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                #self.send_header('Set-Cookie', 'monster=1')
                self.end_headers()
                self.wfile.write(login_page)
        
        except IOError:
            self.send_error(404, "File not found %s" % self.path)        

    def do_POST(self):
        
        try:
            if self.path.endswith("/profile"):
                #cheking the cookie
                mycookies = SimpleCookie(self.headers.get('Cookie'))
                print(mycookies)
                if 'SESSION_COOKIE' in mycookies:
                    session = mycookies['SESSION_COOKIE'].value
                else:
                    session = ""
             
                if session=='1111!!!':
                    msg=b'Cookie found, you are authenticated :> '
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    self.send_response(200)
                    self.end_headers()
                    response = BytesIO()
                    response.write(msg)
                    response.write(b'Received: ')
                    response.write(body)
                    self.wfile.write(response.getvalue())
                else:
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    self.send_response(401)
                    self.end_headers()
                    response = BytesIO()
                    response.write(b'Cookie not found')
                    self.wfile.write(response.getvalue())

            else:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                p_1 = '(?<=uname=)([^&]*)'
                p_2 = '(?<=psw=)([^&]*)'

                #print(str(body))
                user = re.findall(p_1, str(body)) 
                user = str(user[0]) 
                pwd = re.findall(p_2, str(body))
                pwd = str(pwd[0][:-1])

                print(user) 
                print(pwd)
        
                if user == 'admin':
                    print('User found')
                    if pwd == '1234':
                        self.send_response(200)
                        #self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!; SameSite=None; Secure;')
                        #self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!; SameSite=None; Secure; Domain=tas.org; path=/; HTTPOnly;')
                        self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!; SameSite=None; Secure;')
                        #self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!; SameSite=Strict; Secure;')
                        #self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!; SameSite=None; Secure; Domain=192.168.179.1:8000;')
                        #self.send_header('Set-Cookie', 'SESSION_COOKIE=1111!!!;')
                        self.end_headers()
                        output = ""
                        output += '<html><body><h2>Admin Dashboard</h2>'
                        output += '<p>User:'+user+'</p>'
                        output += '<p><a href="/profile">Profile</a></p>'
                        output += '</body></html>'
                        self.wfile.write(output.encode())
                    else:
                        self.send_response(200)
                        self.end_headers()
                        response = BytesIO()
                        response.write(b'Login Failed')
                        self.wfile.write(response.getvalue())
                else:
                    self.send_response(200)
                    self.end_headers()
                    response = BytesIO()
                    response.write(b'Login Failed')
                    self.wfile.write(response.getvalue())
        except IOError:
            self.send_error(404, "File not found %s" % self.path)        


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem") # PUT YOUR cert.pem HERE
server_address = ("127.0.0.1", 4443)  # CHANGE THIS IP & PORT

with socketserver.TCPServer(server_address, SimpleHTTPRequestHandler) as httpd:
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()

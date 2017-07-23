from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi
import queries as q


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path.endswith('/kneegrow')):
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            out = "<html><body><h1>Working</h1></body></html>"
            self.wfile.write(out)
            return

def main():
    try:
        port = 8080
        server = HTTPServer(('',port),Handler)
        print('Server running at port %s' % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print(' Entered.Shutting down server at port %s' %port)
        server.socket.close()

if(__name__ == '__main__'):
    main()

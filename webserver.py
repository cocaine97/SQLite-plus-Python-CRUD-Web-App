from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi
import re
import queries as q


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path.endswith('/restaurants')):
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()

            data = q.res_data()
            name_list=""
            for x in data:
                edit = "<a href='/{}/edit'>Edit</a>".format(x.id)
                delete = "<a href='/{}/delete'>Delete</a>".format(x.id)
                name_list+="<h3>{}</h3><h4>{} {}</h4><br>".format(x.name,edit,delete)

            out = "<html><body><a href='/restaurants/new'>Create a new Restaurant</a>{}</body></html>".format(name_list)
            self.wfile.write(out)
            return

        if(self.path.endswith('/restaurants/new')):
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()

            out = "<html><body><h1>Working</h1><h3><form action='#' enctype='multipart/form-data' method='POST'>Name of your restaurant:<input type='text' name='res_name'><input type='Submit' value='Create'></h3></form></body></html>"
            self.wfile.write(out)
            return

        if(self.path.endswith('/edit')):
            #using regex to get the id of edit req, not very well executed
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            temp = re.split(r'/*/',self.path)
            edit_id = temp
            edit_name = q.res_name(edit_id[1])
            edit_out = "<html><body>"
            edit_out +="<h1>Edit {}</h1>".format(edit_name)
            edit_out +="<form action='#' enctype='multipart/form-data' method='POST'><input type='text' name='new_name' placeholder='Enter new name here'><input type='Submit' value='Change'></form>"
            self.wfile.write(edit_out)






    def do_POST(self):
        if(self.path.endswith("/restaurants/new")):
            ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
            if(ctype == 'multipart/form-data'):
                fields = cgi.parse_multipart(self.rfile,pdict)
                x =  fields.get('res_name')
                q.res_add(str(x[0]))

                self.send_response(301)
                self.send_header('Location','/restaurants')
                self.end_headers()
                return

        if(self.path.endswith("/edit")):
            ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
            if(ctype == 'multipart/form-data'):
                fields = cgi.parse_multipart(self.rfile,pdict)
                new_name = fields.get('new_name')[0]
                temp= re.split('/*/',self.path)
                temp_id = temp[1]
                print(new_name)
                q.res_edit_name(temp_id,new_name)

                self.send_response(301)
                self.send_header('Location','/restaurants')
                self.end_headers()
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

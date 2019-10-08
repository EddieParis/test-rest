import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler

from collections import namedtuple

import json

class BaseRestServer(BaseHTTPRequestHandler):
    """This is the base rest server. It handles get and post method. The URL syntax is v{x}/{method}/{whatever you want}.
    The action method get the url, extract version and method name, pre-pends get_ or post_ and call this name.
    The end of url is given as a list as first argument, json_parsed body as second argument if POST or None if GET.

    It also implements a help method that is able to get all get_ and post_ methods to display them, and shows the docstring
    when detailed help is required, see help() method

    This is an example.

    from BaseHTTPServer import HTTPServer

    class MyRest(BaseRestServer):
        def get_v1_my_method(self, params, json_body)
            \""" This would be displayed as detailed doc
            \"""
            ...
            if error:
                return 400, "Something bad happened"
            else:
                return 200, json.dumps({"value":the_thing})

    def run_on(port):
        print("Starting a server on port %i" % port)
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, MyRest)
        httpd.serve_forever()

    server = threading.Thread(target=run_on, args=args.rest)
    server.daemon = True # Do not make us wait for you to exit
    server.start()

    """

    class ParamChecker(object):
        """This class is used to wrap a parameter description with name type and default value, and
           a static method that does check for input against the given parameter list.
           A parameter is considered mandatory if it has no default value.
        """
        Parameter = namedtuple("Parameter", ["name", "type", "default"])

        @staticmethod
        def check(input_dict, parameters):
            """ @input_dict : the input dict to check
                @parameters : list of Parameter instances
            """
            for parameter in parameters:
                if parameter.name not in input_dict and parameter.default == None:
                    return "Missing parameter {}".format(parameter.name)
                elif parameter.name not in input_dict:
                    input_dict[parameter.name] = parameter.default
                elif type(input_dict[parameter.name]) != parameter.type:
                    return "Wrong type for {}, expected {}".format(parameter.name, parameter.type)
            return None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        pass

    def do_GET(self):
        self.action("get")

    def do_POST(self):
        self.action("post")

    def do_DELETE(self):
        self.action("delete")

    def do_PUT(self):
        self.action("put")

    def action(self, kind):
        parsed_url = urlparse.urlparse(self.path)
        cmd_line = parsed_url.path.split("/")
        if cmd_line[0] == '':
            cmd_line = cmd_line[1:]
        query_params = urlparse.parse_qs(parsed_url.query)


        if "Content-Length" in self.headers and int(self.headers["Content-Length"]) > 0:
            body = self.rfile.read(int(self.headers["Content-Length"]))

            try:
                json_body = json.loads(body)
            except ValueError as excp:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Body parsing error: {}".format(excp))
                return
        else:
            json_body = {}

        code = 404
        content = "Unknown command"

        if cmd_line[0] == 'help':
            code, content = self.help(cmd_line[1:], query_params,  None)
        else:
            if not cmd_line[0].startswith("v"):
                code = 400
                content = "path shall start by version"
            else:
                func = getattr(self, kind+"_"+cmd_line[0]+"_"+cmd_line[1], None)
                if func:
                    code, content = func(cmd_line[2:], query_params, json_body)

        self.reply(code, content)


    def reply(self, code, content):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(content)
        self.wfile.write("\n")

    def help(self, params, query_params, json_body):

        url_doc = "help/{method}/{version}/{command} where method is post or get, version starts with a 'v'"

        if len(params) == 0:
            get_methods = [name[4:].replace("_", "/",1) for name in dir(self) if callable(getattr(self, name)) and name.startswith("get_")]
            get_methods.sort()
            post_methods = [name[5:].replace("_", "/",1) for name in dir(self) if callable(getattr(self, name)) and name.startswith("post_")]
            post_methods.sort()
            delete_methods = [name[7:].replace("_", "/",1) for name in dir(self) if callable(getattr(self, name)) and name.startswith("delete_")]
            delete_methods.sort()
            return 200, json.dumps({"get_methods":get_methods, "post_methods":post_methods, "delete_methods":delete_methods, "help":"more help with "+url_doc })
        else:
            if len(params) < 3:
                return 400, "malformed url, should be " + url_doc
            meth_name = params[0]+"_"+params[1]+"_"+params[2]
            method = getattr(self, meth_name, None)
            if method:
                doc = method.__doc__
                return 200, doc
            else:
                return 404, "No command {}/{} for http method {}".format(params[1], params[2], params[0])

import os
import sqlite3
import argparse
import json
import threading
import signal

from BaseHTTPServer import HTTPServer


from rest_implem import RestServer


schema_filename = 'schema.sql'

class DBManager(object):

    def __init__(self, db_filename):
        db_exists = os.path.exists(db_filename)

        self.conn = sqlite3.connect(db_filename)

        self.conn.row_factory = sqlite3.Row

        if not db_exists:
            #the file does not exist, create the DB

            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            self.conn.executescript(schema)

            print('Inserting initial data')
        else:
            print("Running with existing DB")

    def close(self):
        self.conn.close()


class MyHttpServer(threading.Thread):
    def __init__(self, port, dbfile):
        super(MyHttpServer, self).__init__()
        self.port= port
        self.db_file = dbfile

    def run(self):
        self.db_manager = DBManager(self.db_file)
        # poor trick to make db_manager accessible from RestServer, we do not manage RestServer instances lifecycle
        RestServer.db_manager = self.db_manager
        server_address = ('', self.port)
        httpd = HTTPServer(server_address, RestServer)
        print 'Starting httpd...'
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add an event through the frontend.')

    #positional
    parser.add_argument('dbfile', metavar='DBFILE', type=str, nargs=1,
                    help='database file name')
    parser.add_argument('port', metavar='port', type=int, nargs=1, help='sets port for HTTP REST server')

    args = parser.parse_args()
    db_filename = args.dbfile[0]

    threaded_server = MyHttpServer(args.port[0], args.dbfile[0])

    def signal_handler(signal, frame):
        threaded_server.db_manager.close()


    threaded_server.daemon = True # Do not make us wait for you to exit
    threaded_server.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()


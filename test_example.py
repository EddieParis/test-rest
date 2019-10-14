import unirest
import pytest
import sqlite3
import json

PORT = 1234
VERSION = 1

rest_header = { "Accept": "application/json", "Content-Type": "application/json" }


class TestRest(object):


    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_get_project(self):
        base_url = "http://127.0.0.1:{}/v{}/".format(PORT, VERSION)
        res = unirest.get(base_url + "projects")
        if (res.code == 200):
            print res.body
            print("Test1 ok")

    def test_make_project(self):
        base_url = "http://127.0.0.1:{}/v{}/".format(PORT, VERSION)
        proj_params = { "project":"project_42", "description":"This is a project about everything" }
        res = unirest.post(base_url + "project/project_42", headers = rest_header, params=json.dumps(proj_params))
        print res.code

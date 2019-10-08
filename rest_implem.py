from base_rest_server import BaseRestServer
from model import *
import json

class RestServer(BaseRestServer):

    def get_v1_projects(self, params, query_params, json_body):
        """v1/projects : Get all available projects, returns json
        """
        pk = None
        return 200, self.generic_get_object(Project, pk)

    def get_v1_project(self, params, query_params, json_body):
        """v1/project/{project_name} : Get specified project, returns json
        """
        pk = ["name", [params[0]]]
        return 200, self.generic_get_object(Project, pk)

    def get_v1_tasks(self, params, query_params, json_body):
        """v1/tasks : Get all available tasks, returns json
        """
        pk = None
        return 200, self.generic_get_object(Task, pk)

    def get_v1_task(self, params, query_params, json_body):
        """v1/task/{project_name} : Get specified task, returns json
        """
        pk = ["id", [int(params[0])]]
        return 200, self.generic_get_object(Task, pk)

    def generic_get_object(self, obj_type, pk):
        obj = obj_type()
        result = obj.get_from_db(self.__class__.db_manager.conn, pk)
        res_list = []
        for row in result.fetchall():
            print row
            new_obj = obj_type()
            new_obj.from_db(row)
            res_list.append(json.dumps(new_obj.to_json()))
        return res_list

    def get_v1_task_by_project_by_status(self, params, query_params, json_body):
        """v1/task_by_project_by_status/{project_id}/{status} get the specified projects tasks that are in the specified status, returns json"""

        try:
            query = 'select * from task where project = ? and status = ?'
            cursor = self.__class__.db_manager.conn.execute(query, [params[0], params[1]])
        except Exception as excp:
            return 409, str(excp)

        result = cursor.fetchall()

        return 200, str(len(result))


    def post_v1_project(self, params, query_params, json_body):
        """ v1/project/{project_name} creates or updates a project, request body is json, fields are:
        name: (string, mandatory) name of the project
        description: (string, optional) description of the project
        deadline: (date, optional) deadline of the project (must be a valid date in format YYYY-MM-DD:HH:MM:SS
        """
        path_name = params[0]
        return self.delete_object(Project, "name", path_name, params, query_params, json_body)

    def post_v1_task(self, params, query_params, json_body):
        """ v1/project/{task_id} creates or updates a project, request body is json, fields are:
        id: (integer, mandatory) unique id of the task
        priority: (integer, mandatory) priority of the task
        details: (string, mandatory) details of the task
        status: (string, mandatory) status of the task (may be todo, done, in_progress, rejected)
        deadline: (date, optional) deadline of the task (must be a valid date in format YYYY-MM-DD:HH:MM:SS
        completed_on: (date, optional) completion date of the task (must be a valid date in format YYYY-MM-DD:HH:MM:SS
        project: (string, mandatory) project which the task refers to
        """

        try:
            path_id = int(params[0])
        except ValueError:
            return 409, "Id on the path must be integer"
        return self.insert_object(Task, "id", path_id, params, query_params, json_body)

    def insert_object(self, obj_type, id_field, path_value, params, query_params, json_body):

        obj = obj_type()

        get_cursor = obj.get_from_db(self.__class__.db_manager.conn, [ id_field, [path_value] ])
        get_res = get_cursor.fetchall()
        if len(get_res)>1:
            return 500, "Internal error, query returned several objects"

        print (len(get_res))

        if len(get_res) == 1:
            obj.from_db(get_res[0])

        try:
            obj.from_json(json_body, len(get_res) == 1)#.decode("utf-8"))
        except ModelException as excp:
            return 409, str(excp)

        id_value = getattr(obj, id_field)

        if id_value != path_value:
            return 409, "Body {} {} and path {} {} do not match".format(id_field, id_value, id_field, path_value)

        try:
            obj.save_to_db(self.__class__.db_manager.conn, len(get_res) == 1)
        except Exception as excp:
            return 409, str(excp)

        return 201, ""

    def delete_v1_project(self, params, query_params, json_body):
        """ v1/project/{project_name} no json body:
        """
        project_name = params[0]
        return self.del_from_pk("project", "name", project_name)


    def delete_v1_task(self, params, query_params, json_body):
        """ v1/project/{project_name} no json body:
        """
        try:
            path_id = int(params[0])
        except ValueError:
            return 409, "Id on the path must be integer"
        return self.del_from_pk("task", "id", path_id)

    def del_from_pk(self, table_name, pk_name, pk_value):
        query = "delete from {} where {} = :{}".format(table_name, pk_name, pk_name)
        print query
        self.__class__.db_manager.conn.execute(query, {pk_name:pk_value})
        self.__class__.db_manager.conn.commit()
        return 204, ""

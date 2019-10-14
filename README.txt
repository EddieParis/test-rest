Do a get on http://{address}:{port}/help to get help summarized below.

sqlite browser can be used to see what's inside the DB

Goal is to test the REST api for consistency and reliability in black box mode.
Sql schema and insights on the code should not be used to achieve tests.

Then do a performance for task get and post with 1000 then 10000 entries (total) on 20 then 100 projects.


The application is a todo manager, there are projects in which there are tasks.

run main.py to have a server.

Available REST calls:

GET
    v1/projects : Get all available projects, returns json
    v1/project/{project_name} : Get specified project, returns json
    v1/tasks : Get all available tasks, returns json
    v1/task/{project_name} : Get specified task, returns json
    v1/task_by_project_by_status/{project_id}/{status} get the specified projects tasks that are in the specified status, returns json

POST

    v1/project/{project_name} creates or updates a project, request body is json, fields are:
        name: (string, mandatory) name of the project
        description: (string, optional) description of the project
        deadline: (date, optional) deadline of the project (must be a valid date in format YYYY-MM-DD:HH:MM:SS

    v1/project/{task_id} creates or updates a project, request body is json, fields are:
        id: (integer, mandatory) unique id of the task
        priority: (integer, mandatory) priority of the task
        details: (string, mandatory) details of the task
        status: (string, mandatory) status of the task (may be todo, done, in_progress, rejected)
        deadline: (date, optional) deadline of the task (must be a valid date in format YYYY-MM-DD:HH:MM:SS
        completed_on: (date, optional) completion date of the task (must be a valid date in format YYYY-MM-DD:HH:MM:SS
        project: (string, mandatory) project which the task refers to

DELETE
    v1/project/{project_name} no json body
    v1/project/{project_name} no json body

from datetime import datetime
from collections import OrderedDict

class ModelException(Exception):
    pass

class ModelObject(object):

    insert_query = None

    def __init__(self):
        self.values = {}
        if not self.__class__.insert_query:
            query = "insert into {} (".format(self.__class__.__name__.lower())
            query2 = "update {} set ".format(self.__class__.__name__.lower())
            params = ""
            for index, field_name in enumerate(self.__class__.fields.keys()):
                query += field_name +  ", "
                params += ":"+field_name+", "
                if index == 0:
                    #never update the PK
                    pk_name = field_name
                else:
                    query2 += field_name + "= :" + field_name + ", "

            query = query[:-2] + ") values("+params[:-2]+")"
            self.__class__.insert_query = query
            self.__class__.update_query = query2[:-2] + " where {0} = :{0}".format(pk_name)

    def __getattr__(self, name):
        if name in self.__class__.fields:
            return self.values[name]
        else:
            return super.__getattr__(name)

    def __setattr__(self, name, value):
        if name in self.__class__.fields:
            self.values[name] = value
        else:
            super.__setattr__(self, name, value)

    def from_json(self, json_dict, update=False):
        fields = self.__class__.fields
        # ~ json_dict = json.loads(json_data)
        for field_name in fields.keys():
            field_type, field_mandatory = fields[field_name]
            value = json_dict.get(field_name, None)
            if value == None and field_mandatory:
                if update:
                    continue
                else:
                    raise ModelException("Missing mandatory data when building object: {}".format(field_name))
            if value != None and type(value) != field_type:
                raise ModelException("Wrong type for field {}, expected {}, got {}".format(field_name, field_type, type(value)))
            self.values[field_name] = value

    def to_json(self):
        return self.values

    def from_db(self, row):
        self.values = {}
        for index, field_name in enumerate(self.__class__.fields.keys()):
            self.values[field_name] = row[index]

    def save_to_db(self, conn, update = False):
        data = {}
        for field_name in self.__class__.fields.keys():
            data[field_name] = getattr(self, field_name)

        if update:
            query = self.__class__.update_query
        else:
            query = self.__class__.insert_query

        print(query)
        print(data)
        conn.execute(query, data)
        conn.commit()

    def get_from_db(self, conn, pk):
        if pk == None:
            query = 'select * from '+self.__class__.__name__.lower()
            return conn.execute(query)
        else:
            query = 'select * from {} where {} = ?'.format(self.__class__.__name__.lower(), pk[0])
            return conn.execute(query, pk[1])

class Project(ModelObject):
    fields = OrderedDict( [ ("name", (unicode, True)), ("description", (unicode, True)), ("deadline", (unicode, False))])


class Task(ModelObject):
    fields = OrderedDict( [ ("id", (int, True)), ("priority", (int, True)), ("details", (unicode, True)), ("status", (unicode, True)), ("deadline", (datetime, False)), ("completed_on", (datetime, False)), ("project", (unicode, True)) ])


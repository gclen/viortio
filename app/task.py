import datetime
from dateutil import parser


class Task(object):

    def __init__(self, name, due_date=None, start_date=None, project=None):

        self.name = name
        self.due_date = due_date
        self.start_date = start_date
        self.project = project

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            raise ValueError("Task name must be specified!")
        self._name = value

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        if value is not None:
            dt = parser.parse(value)
            self._due_date = dt.strftime('%Y-%m-%d')

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if value is not None:
            dt = parser.parse(value)
            self._start_date = dt.strftime('%Y-%m-%d')
        else:
            self._start_date = datetime.datetime.now().strftime('%Y-%m-%d')

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value


"""
Utilities for interfacing with ProgSnap2 data files, both in SQL format and
in Zipped-CSV format.

Filters can be: Exact string match, regex, or function
    TODO: So far only really support exact string match

    TODO: No support for link_context

progsnap = SqlProgSnap2("test/datafiles/progsnap2_3.db")
fun_student_edits = progsnap.get_events(
    event_filter={'EventType': 'File.Edit'},
    link_filters={
        'Subject': {
            'X-IsStaff': "False",
        },
        'Assignment': {
            'X-Name': "Fun%"
        },
    },
    link_selections={
        'Subject': {
            'X-Email': 'student_email',
            'X-Name.First': 'student_first'
            'X-Name.Last': 'student_last',
        },
        'Assignment': {
            'X-Name': 'assignment_name',
            'X-URL': 'assignment_url',
            'X-Code.OnRun': 'on_run'
        }
    }
)
"""
import sqlite3
import re

class BaseProgSnap2:
    def __init__(self, path: str):
        self.path = path

    def get_events(self, event_filter=None, link_filters=None,
                   link_selections=None, with_code=True):
        raise NotImplemented("Cannot execute get_events on base ProgSnap2 Format")

    def close(self):
        pass

class SqlProgSnap2(BaseProgSnap2):
    def __init__(self, path: str):
        super().__init__(path)
        self._connection = sqlite3.connect(self.path)
        self._cursor = self._connection.cursor()

    def close(self):
        self._connection.close()

    def get_events(self, event_filter=None, link_filters=None,
                   link_selections=None, with_code=True):
        # Setup data
        tables = ['MainTable']
        filters = [] #"MainTable.EventType=?"
        selections = ['MainTable.EventID']
        fields = ['event_id']
        data = []
        # Add in event filters
        for column, value_filter in event_filter.items():
            if isinstance(value_filter, str):
                filters.append(f"MainTable.`{column}`=?")
                data.append(value_filter)
        # Add in code
        if with_code:
            tables.append("CodeState")
            filters.append(f"MainTable.CodeStateID=CodeState.ID")
            selections.append("CodeState.Contents as submission_code")
            fields.append("submission_code")
        # Add in all needed link tables
        for table in (link_filters.keys() | link_selections.keys()):
            tables.append('Link' + table)
            filters.append(f"MainTable.`{table}ID`=Link{table}.`{table}Id`")
        # Add in link table filters
        for table, table_filters in link_filters.items():
            for column, value_filter in table_filters.items():
                if isinstance(value_filter, str):
                    # TODO: Make this more robust
                    if "%" in value_filter:
                        filters.append(f"Link{table}.`{column}` LIKE ?")
                    else:
                        filters.append(f"Link{table}.`{column}`=?")
                    data.append(value_filter)
        # Add in Contextual tables
        for table, table_selections in link_selections.items():
            for column, alias in table_selections.items():
                selections.append(f"Link{table}.`{column}` AS {alias}")
                fields.append(alias)
        # Prepare actual filter query string
        if filters:
            filters = "WHERE " + " AND ".join(filters)
        else:
            filters = ""
        # And execute
        query = f"""
        SELECT {', '.join(selections)}
        FROM {', '.join(tables)}
        {filters}
        """
        print(query)
        result = self._cursor.execute(query, data)
        # Process result
        return [dict(zip(fields, row)) for row in result.fetchall()]

class ZipProgSnap2(BaseProgSnap2):
    pass
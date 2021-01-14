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
import hashlib
import os
import pickle
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SqlProgSnap2(BaseProgSnap2):
    PROFILES = {
        'blockpy': dict(link_filters={
            'Subject': {
                'X-IsStaff': "False",
            },
        },
            link_selections={
                'Subject': {
                    'X-Email': 'student_email',
                    'X-Name.First': 'student_first',
                    'X-Name.Last': 'student_last',
                },
                'Assignment': {
                    'X-Name': 'assignment_name',
                    'X-URL': 'assignment_url',
                    'X-Code.OnRun': 'on_run'
                }
            })
    }

    def set_profile(self, profile):
        if profile not in self.PROFILES:
            raise ValueError(f"Unknown ProgSnap Profile specified: {profile}")
        self.profile = profile

    def __init__(self, path: str, cache=False, status_update=None):
        super().__init__(path)
        self._connection = sqlite3.connect(self.path)
        self._cursor = self._connection.cursor()
        self.profile = None
        self.cache = cache
        # To see executed queries:
        # self._connection.set_trace_callback(print)
        if status_update:
            self._connection.set_progress_handler(status_update, 1000)

    def close(self):
        self._connection.close()

    def _merge(self, key, overrides):
        result = {}
        for k, v in self.PROFILES.get(self.profile, {}).get(key, {}).items():
            result[k] = v
        if overrides is not None:
            for k, v in overrides.items():
                result[k] = v
        return result

    def get_code(self, query):
        #flat_filters = {k + k2: v
        #                for k, vs in link_filters.items()
        #                for k2, v in vs
        #                }
        #codes = tuple(sorted(event_filter.items() | flat_filters))
        encoded = "pedal_cache_"+hashlib.md5(query.encode('utf-8')).hexdigest()+".pickle"
        return encoded

    def get_events(self, event_filter=None, link_filters=None,
                   link_selections=None, with_code=True, limit=None):
        # Load in profile defaults
        link_selections = self._merge('link_selections', link_selections)
        link_filters = self._merge('link_filters', link_filters)
        # Setup data
        tables = ['MainTable']
        filters = []  # "MainTable.EventType=?"
        selections = ['MainTable.EventID', 'MainTable.ClientTimestamp']
        fields = ['event_id', 'client_timestamp']
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
        # And a limit for testing purposes
        query_limit = ""
        if limit:
            query_limit = f"LIMIT {limit}"
        # And execute
        query = f"""
            SELECT {', '.join(selections)}
            FROM {', '.join(tables)}
            {filters}
            {query_limit}
        """
        # Is it is in our cache?
        if isinstance(self.cache, str):
            key = self.get_code(query)
            cache_path = os.path.join(self.cache, key)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as cache_file:
                    return pickle.load(cache_file)
        result = self._cursor.execute(query, data)
        result = [dict(zip(fields, row)) for row in result.fetchall()]
        # Store it in our cache for the future
        if isinstance(self.cache, str):
            key = self.get_code(query)
            cache_path = os.path.join(self.cache, key)
            with open(cache_path, 'wb') as cache_file:
                pickle.dump(result, cache_file)
        # Process result
        return result


class ZipProgSnap2(BaseProgSnap2):
    pass

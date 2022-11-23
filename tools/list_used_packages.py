import ast
import os
import glob
import collections
from pathlib import Path
from pprint import pprint

IGNORE_LIST = {"pedal"}
ROOT_PATH = Path(r"../pedal")


class ModuleFinder(ast.NodeVisitor):
    def __init__(self, current_file):
        super().__init__()
        self.modules = collections.defaultdict(dict)
        self.aliases = {}
        self._current_file = current_file

    @property
    def current_file(self):
        return str(Path(self._current_file).relative_to(ROOT_PATH))

    def track_module(self, name, alias=None):
        top_level_import = name.split(".")[0]
        if top_level_import in IGNORE_LIST:
            return
        self.modules[top_level_import][self.current_file] = set()
        if alias:
            self.aliases[alias] = top_level_import
        return top_level_import

    def track_member(self, module_name, member):
        self.modules[module_name][self.current_file].add(member)

    def visit_Import(self, node):
        for name in node.names:
            self.track_module(name.name, name.asname)

    def visit_ImportFrom(self, node):
        # if node.module is missing it's a "from . import ..." statement
        # if level > 0 it's a "from .submodule import ..." statement
        if node.module is not None and node.level == 0:
            top_level_module = self.track_module(node.module)
            if top_level_module:
                for name in node.names:
                    self.track_member(top_level_module, name.name)

    def visit_Attribute(self, node):
        super().visit(node.value)
        if not isinstance(node.value, ast.Name):
            return
        actual_module = None
        if node.value.id in self.modules:
            actual_module = node.value.id
        elif node.value.id in self.aliases:
            actual_module = self.aliases[node.value.id]
        if not actual_module:
            return
        self.track_member(actual_module, node.attr)


all_modules = collections.defaultdict(lambda: collections.defaultdict(set))
for path in glob.glob(str(ROOT_PATH) + "\**\*", recursive=True):
    if path.endswith('.py'):
        with open(path, encoding='utf-8') as python_file:
            code = python_file.read()
        node_iter = ModuleFinder(path)
        node_iter.visit(ast.parse(code))
        modules = node_iter.modules
        for module_name, paths_members in modules.items():
            for path, members in paths_members.items():
                all_modules[module_name][path].update(members)


for module, paths_members in all_modules.items():
    print(module)
    for path, members in paths_members.items():
        print("    ", path)
        for member in members:
            print("    "*2, member)
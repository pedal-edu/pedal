from ct_map import *
from easy_node import *


class AstSymbol:
	def __init__(self, _id="", _node=None):
		self.id = _id
		self.astNode = _node

	def __str__(self):
		return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])

	def __repr__(self):
		return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])


class AstMap:
	def __init__(self):
		self.mappings = CtMap()
		self.symbol_table = CtMap()
		self.exp_table = CtMap()
		self.conflict_keys = []

	'''
	Adds ins_node.id to the symbol table if it doesn't already exist,
	mapping it to a set of ins_node.
	Updates a second dictionary that maps ins_node to an std_node, and overwrites
	the current std_node since there should only be one mapping.
	'''
	def add_var_to_sym_table(self, ins_node, std_node):
		if type(ins_node) == str:
			key = ins_node
		else:
			key = ins_node.astNode.id
		value = AstSymbol(std_node.astNode.id, std_node.astNode)
		if self.symbol_table.has(key):
			new_list = self.symbol_table.get(key)
			new_list.append(value)
			if not (key in self.conflict_keys):
				for other in new_list:
					if value.id != other.id:
						self.conflict_keys.append(key)
						break
		else:
			new_list = [value]
		
		self.symbol_table.set(key, new_list)
		return len(self.conflict_keys)

	def add_exp_to_sym_table(self, ins_node, std_node):
		self.exp_table.set(ins_node.astNode.id, std_node.astNode)

	def add_node_pairing(self, ins_node, std_node):
		self.mappings.set(ins_node.astNode, std_node.astNode)

	def has_conflicts(self, ):
		return len(self.conflict_keys) > 0

	'''
	Returns a newly merged map consisting of this and other
	without modifying self.
	@param :AstMap other - the other AstMap to be merged with
	@return this modified by adding the contents of other
	'''
	def new_merged_map(self, other):
		new_map = AstMap()
		new_map.merge_map_with(self)
		new_map.merge_map_with(other)
		return new_map

	'''
	Returns a newly merged map consisting of this and other
	by modifying this
	@param :AstMap other - the other AstMap to be merged with
	@return this modified by adding the contents of other
	'''
	def merge_map_with(self, other):
		# TODO: check if other is also an AstMap.
		# merge all mappings
		other_map = other.mappings
		for other_map_key, other_map_value in zip(other_map.keys, other_map.values):
			self.mappings.set(other_map_key, other_map_value)
		# merge all expressions
		other_exp = other.exp_table
		for other_expKey, other_expValue in zip(other_exp.keys, other_exp.values):
			self.exp_table.set(other_expKey, other_expValue)
		# merge all symbols
		other_sym = other.symbol_table
		for key, value in zip(other_sym.keys, other_sym.values):
			for sub_value in value:
				self.add_var_to_sym_table(key, EasyNode(sub_value.astNode))

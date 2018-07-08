import ast
import ast_helpers as ast_str


class EasyNode:
	"""
	A wrapper class for AST nodes. Linearizes access to the children of the ast node and saves the field this AST node
	originated from
	"""
	def __init__(self, ast_node, my_field=''):
		"""
		:param ast_node: The AST node to be wrapped
		:param my_field: the field of the parent node that produced this child.
		"""
		self.children = []
		self.astNode = ast_node
		self.field = my_field
		my_field_generator = ast.iter_fields(self.astNode)
		for item in my_field_generator:

			field, value = item
			# if the field doesn't have a value, no child exists
			if value is None:
				continue
			
			# If the children are not in an array, wrap it in an array for consistency in the code the follows
			if type(value) != list:
				value = [value]
			
			# Reference ast_node_visitor.js for the original behavior and keep note of it for the purposes of handling
			# the children noting the special case when the nodes of the array are actually parameters of the node
			# (e.g. a load function) instead of a child node
			for sub_value in value:
				if isinstance(sub_value, ast.AST):
					self.children.append(EasyNode(sub_value, field))

	def __str__(self):
		return ''.join([self.field, "\n", ast_str.dump(self.astNode)])

def load_ipython_extension(ip):
    from IPython.core.magic import Magics, magics_class, cell_magic
    from IPython.core import magic_arguments
    
    @magics_class
    class AstMagics(Magics):
        
        @magic_arguments.magic_arguments()
        @magic_arguments.argument(
            '-m', '--mode', default='exec',
            help="The mode in which to parse the code. Can be exec (the default), "
                 "eval or single."
        )    
        @cell_magic
        def dump_ast(self, line, cell):
            """Parse the code in the cell, and pretty-print the AST."""
            args = magic_arguments.parse_argstring(self.dump_ast, line)
            parseprint(cell, mode=args.mode)
    
    ip.register_magics(AstMagics)

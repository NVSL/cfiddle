import contextlib
import io
from elftools.elf.elffile import ELFFile
from elftools.dwarf.die import DIE
from elftools.dwarf.die import AttributeValue
from elftools.dwarf.descriptions import    describe_DWARF_expr, set_global_machine_arch
from elftools.dwarf.locationlists import     LocationEntry, LocationExpr, LocationParser

class DebugInfo:

    def debug_info(self, show=None, **kwargs):
        """Print a summary of the debugging info for the compiled code.
        
        This is the data that debuggers use to make debugging a program
        comprehensible.  It includes variable and function names, types, file
        names, line numbers, etc.

        Currently only `DWARF4 <https://dwarfstd.org/doc/DWARF4.pdf>`_ is
        supported, which is the standard on Linux systems.

        In order for debugging information to present, the code must be
        compiled with :code:`-g`.

        Args:
          show: What to show -- a function name.  Defaults to ``None`` which will display all the debugging info.
        Returns:
          :code:`str`: String rendering the DWARF data for the file or function.  This can be very long.

        """
        self.show = show

        with self.DWARFInfo() as dwarfinfo:
            if dwarfinfo is None:
                return f"No debugging data in {self.lib}"
            for CU in dwarfinfo.iter_CUs():
                 top_DIE = CU.get_top_DIE()
                 return DebugInfo.DWARFRenderer(top_DIE, show).render()

        return f"No Compilation units in {self.lib}."


    def stack_frame(self, show, **kwargs):
        """Print the stack frame layout for a function.

        This returns a description of where each variable and argument
        resides on the stack or in registers.

        For instance:

        .. doctest::
        
            >>> from cfiddle import * 
            >>> sample = code(r''' 
            ... extern "C"
            ... int foo(int a) {
            ...    register int sum = 0;
            ...    for(int i = 0; i < 10; i++) {
            ...       sum += i;
            ...    }
            ...    return sum;
            ... }
            ... ''')
            >>> stack_frame = build(sample)[0].stack_frame("foo")
            >>> print(stack_frame) # doctest: +SKIP
            function foo
                a: (DW_OP_fbreg: -44) 
                sum: (DW_OP_reg3 (rbx))
                i: (DW_OP_fbreg: -28) 

        The format is potentially complicated (the DWARF format is Turing
        complelete!), but most entries are easy to understand.
        
        The example above shows that :code:`a` is store at -44 bytes relative
        to the frame base register and :code:`sum` is a register. 

        This is a work in progress.  Here's the `Dwarf4 spec
        <https://dwarfstd.org/doc/DWARF4.pdf>`_ and the source code for
        `pyelftools <https://github.com/eliben/pyelftools>`_, which is reasonably well documented.

        Pull requests welcome :-).

        Args:
          show: Function to extract the frame layout from.
        Returns:
          :code:`str`: A description of the layout

        """
        output = io.StringIO()
        
        with self.ELFFile() as elffile:    # This is required for the descriptions module to correctly decode
            # register names contained in DWARF expressions.
            set_global_machine_arch(elffile.get_machine_arch())

        with self.DWARFInfo() as dwarfinfo:
            location_lists = dwarfinfo.location_lists()

            loc_parser = LocationParser(location_lists)

            for CU in dwarfinfo.iter_CUs():

                # A CU provides a simple API to iterate over all the DIEs in it.
                for DIE in CU.iter_DIEs():
                    if DIE.tag == "DW_TAG_subprogram":
                        if "DW_AT_name" in DIE.attributes:
                            output.write(f"function {DIE.attributes['DW_AT_name'].value.decode()}\n")
                        else:
                            output.write(f"function <anon>\n")
                            
                    if DIE.tag in ["DW_TAG_formal_parameter", "DW_TAG_variable"]:
                        if "DW_AT_location" not in DIE.attributes:
                            if "DW_AT_name" in DIE.attributes:
                                 output.write(f"{DIE.attributes['DW_AT_name'].value.decode()} has no location\n")
                            continue
                        loc = loc_parser.parse_from_attribute(DIE.attributes["DW_AT_location"], CU['version'])
                        if isinstance(loc, LocationExpr):
                            offset = describe_DWARF_expr(loc.loc_expr, dwarfinfo.structs, CU.cu_offset)
                            if "DW_AT_name" in DIE.attributes:
                                output.write(f"    {DIE.attributes['DW_AT_name'].value.decode()}: {offset}\n")
                            else:
                                output.write(f"    <unamed> is at {offset} ({CU.cu_offset})\n")
        return output.getvalue()

    @contextlib.contextmanager
    def DWARFInfo(self):

        """Context manager for the raw :code:`DWARFInfo` object for the  compiled code.

        Returns:
           :code:`DWARFInfo`: :code:`DWARFInfo` object created by `pyelftools <https://github.com/eliben/pyelftools>`_.
        """
        try:
            with self.ELFFile() as elffile:
                if not elffile.has_dwarf_info():
                    yield None
                else:
                    # we need to yield because the elftools hasn't finished parsing yet
                    yield elffile.get_dwarf_info()
        finally:
            pass

        
    @contextlib.contextmanager
    def ELFFile(self):
        """Context manager for the raw :code:`ELFFile` object for the compiled code.
        
        Returns:
           :code:`ELFFile`: :code:`ELFFile` object created by `pyelftools <https://github.com/eliben/pyelftools>`_.
        """
        try:
            with open(self.lib, 'rb') as f:
                yield ELFFile(f)
        finally:
            pass

        
    class DWARFRenderer:
        def __init__(self, die, show):
            self.root = die
            self.show = show

            if self.show is  None:
                self.printing = 1
            else:
                self.printing = 0
                
            self.output = io.StringIO()
            self.indent = 0
            
        def render(self):
            self._die_info_rec(self.root)
            return self.output.getvalue()

        def _die_info_rec(self, die):

            printing_increment = 0

            if die.tag == "DW_TAG_subprogram":
                
                if self.show == self._get_die_name(die):
                    printing_increment = 1
            self.printing += printing_increment
                    
            self._output_element(die)

            self._push_indent()
            for key, attribute in die.attributes.items():
                self._output_element(attribute)

            for child in die.iter_children():
                self._die_info_rec(child)

            self._pop_indent()
            
            self.printing -= printing_increment

        def _get_die_name(self, die):
            if "DW_AT_name" in die.attributes:
                return die.attributes["DW_AT_name"].value.decode()
            else:
                return "<unknown name>"
            
        def _push_indent(self):
            self.indent += 1
        def _pop_indent(self):
            self.indent -= 1
            
        def _output_element(self, e):
            if self.printing > 0:
                indent =  "  " * self.indent
                self.output.write(f"[{e.offset:4}] {indent}{self._render_element(e)}\n")

        def _render_element(self, e):
            if isinstance(e, AttributeValue) :
                return f"{e.name} = {e.value}"
            elif  isinstance(e, DIE) :
                return f"{e.tag}"

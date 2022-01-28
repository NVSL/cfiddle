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
                 return DWARFRenderer(top_DIE, show).render()

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
        current_function = None
        self._set_machine_architecture()

        def emit(s):
            if current_function == show:
                output.write(s)
                
        with self.DWARFInfo() as dwarfinfo:
            loc_parser = self._build_location_parser(dwarfinfo)

            for CU in dwarfinfo.iter_CUs():
                for DIE in CU.iter_DIEs():
                    if DIE.tag == "DW_TAG_subprogram":
                        current_function = self._extract_name(DIE)
                        emit(self._render_function_name(DIE))
                    elif DIE.tag in ["DW_TAG_formal_parameter", "DW_TAG_variable"]:
                        if current_function == show:
                            emit(self._render_variable_location(DIE, CU, dwarfinfo, loc_parser))
                        
        return output.getvalue()
    
    def _render_variable_location(self, DIE, CU, dwarfinfo, loc_parser):
        if "DW_AT_name" in DIE.attributes:
            name = DIE.attributes['DW_AT_name'].value.decode()
        else:
            name = "<unnamed>"
        
        if "DW_AT_location" not in DIE.attributes:
            return f"{name} has no location\n"
        else:
            loc = loc_parser.parse_from_attribute(DIE.attributes["DW_AT_location"], CU['version'])
            if isinstance(loc, LocationExpr):
                offset = describe_DWARF_expr(loc.loc_expr, dwarfinfo.structs, CU.cu_offset)
                return f"    {name}: {offset}\n"
            else:
                return f"    {name}: <not a location>\n"
            

    def _set_machine_architecture(self):
        with self.ELFFile() as elffile:    # This is required for the descriptions module to correctly decode
            # register names contained in DWARF expressions.
            set_global_machine_arch(elffile.get_machine_arch())


    def _render_function_name(self, DIE):
        n = self._extract_name(DIE)
        if n is None:
            return f"function <anon>\n"
        else:
            return f"function {n}\n"


    def _extract_name(self, DIE):
        if "DW_AT_name" in DIE.attributes:
            return DIE.attributes['DW_AT_name'].value.decode()
        else:
            return None

    def _build_location_parser(self, dwarfinfo):
        location_lists = dwarfinfo.location_lists()
        return LocationParser(location_lists)

        
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

import contextlib
import io
from elftools.elf.elffile import ELFFile
from elftools.dwarf.die import DIE
from elftools.dwarf.die import AttributeValue

class DebugInfo:

    def debug_info(self, show=None, **kwargs):
        """Print a summary of the debugging info for the compiled code.
        
        This is the data that debuggers use to make debugging a program
        comprehensible.  It includes variable and function names, types, file
        names, line numbers, etc.

        Currently only `Dwarf4 <https://dwarfstd.org/doc/DWARF4.pdf>`_ is
        supported, which is the standard on Linux systems.

        In order for debugging information to present, the code must be
        compiled with :code:`-g`.

        Args:
          show: What to show -- a function name.  Defaults to ``None`` which will display all the debugging info.
        Returns:
          :code:`str`: String rendering the Dwarf data for the file or function.

        """
        self.show = show

        with self.DWARFInfo() as dwarfinfo:
            if dwarfinfo is None:
                return f"No debugging data in {self.lib}"
            for CU in dwarfinfo.iter_CUs():
                 top_DIE = CU.get_top_DIE()
                 return DebugInfo.DWARFRenderer(top_DIE, show).render()

        return f"No Compilation units in {self.lib}."

    @contextlib.contextmanager
    def DWARFInfo(self):
        """Get the raw :code:`DWARFInfo` object for the the compiled code.

        Returns:
           The raw :code:`DWARFInfo` object for the compiled code as created by `pyelftools <https://github.com/eliben/pyelftools>`_.
        """
        try:
            with self.ELFFile() as elffile:
                if not elffile.has_dwarf_info():
                    yield None
                else:
                    # we need to yield because the elftools hasn't finished parsing yet
                    yield elffile.get_dwarf_info()
        except:
            pass

    @contextlib.contextmanager
    def ELFFile(self):
        """Get the raw :code:`ELFFile` object for the the compiled code.

        Returns:
           The raw :code:`ELFFile` object for the compiled code as created by `pyelftools <https://github.com/eliben/pyelftools>`_.
        """
        try:
            with open(self.lib, 'rb') as f:
                yield ELFFile(f)
        except:
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
                if self.show == die.attributes["DW_AT_name"].value.decode():
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

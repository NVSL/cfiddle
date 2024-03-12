from ..Builder import BuildFailure
from ..Exceptions import CFiddleInternalError, OutermostCallExceptionHandler
from ..Runner import RunnerExecutionMethodException
import re
import click
import traceback
import sys

class CFiddleUserException(Exception):
    def _render_traceback_(self):
        etype, evalue, tb = sys.exc_info()
        #tb.tb_next = tb.tb_next.tb_next
        tb.tb_next.tb_next = None
        stb = traceback.format_exception(etype, evalue, tb.tb_next)
        return [click.style(stb[-2].strip(), fg="green"),
                click.style(stb[-1].strip(), fg="red")]    

def error_style(s):
    return click.style(s, fg="red")

def plain_style(s):
    return click.style(s, fg="black")
def show_error(s):
    click.echo(error_style(s))

class PrettyExceptionHandler(OutermostCallExceptionHandler):

    def handle_exception(self, e):
        from ..config import in_debug, get_config
 
        breakpoint()
        if not self.is_outermost_call() or in_debug():
            return None



        if isinstance(e, BuildFailure):
            return CFiddleUserException(f"""
{plain_style(f'Build parameters = {e.executable_description.build_parameters}')}
{plain_style(f'Source file = {e.executable_description.source_file}')}
{plain_style(f'''Build command = 
{e.command}''')}

{error_style(e.output)}

{plain_style('Your code failed to build.  The compilations errors are in red.')}""")


        if isinstance(e, FileNotFoundError):
            if ".pickle" in str(e):
                return CFiddleUserException(f"""
{error_style(f"It is likely that your code crashed.")}
{e}""")
            
        if isinstance(e, RunnerExecutionMethodException):
            cleanedup = e.output
            if not "_invoke_function" in cleanedup:
                return None # It appears the problems is not with the user's code.
            cleanedup = re.sub(r"\s*Current thread.*", "\n", cleanedup, flags=re.MULTILINE|re.DOTALL)
            cleanedup = re.sub(r".*Fatal Python error: ", "", cleanedup, flags=re.MULTILINE|re.DOTALL)
            return CFiddleUserException(f"""
{plain_style('The following error occured in your code')}
{error_style(cleanedup.strip())}
{plain_style(f'The output prior to "Fatal Python Error: {cleanedup.strip()}" is your output.  You can ignore what comes after')}.""")

        return None
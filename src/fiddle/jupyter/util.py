import time
from IPython.display import clear_output

def html_parameters(parameter_set):
    return "<br/>".join([f"{p} = {v}" for p,v in parameter_set.items()])

def changes_in(filename):
    old_last_change = None
    while True:
        try:
            current_last_change = os.path.getmtime(filename)
            if current_last_change != old_last_change:
                old_last_change = current_last_change
                clear_output(wait=True)
                yield None
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            return
            

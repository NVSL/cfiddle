import nbformat
import click
import re
from pathlib import Path
from shutil import copyfile

def process_cell(cells, cell_index):
    cell = cells[cell_index]
    
    if "outputs" in cell:
        cell.outputs= []

    if "scrolled" in cell.metadata:
        del cell.metadata['scrolled']

    if cell['cell_type'] == "code":
        cell['execution_count'] = None
        

@click.command()
@click.argument("notebooks", nargs=-1, type=str)
def nbclean(notebooks=None, out=None):

    for notebook in notebooks:
        copyfile(notebook, f"{notebook}.bak")

        with click.open_file(notebook) as infile:
            nb = nbformat.read(infile, as_version=nbformat.NO_CONVERT)

        for cell_index, cell in enumerate(nb.cells):
            process_cell(nb.cells, cell_index)

        with click.open_file(notebook, mode="w", atomic=True) as outfile:
            nbformat.write(nb, outfile, version=nbformat.NO_CONVERT)


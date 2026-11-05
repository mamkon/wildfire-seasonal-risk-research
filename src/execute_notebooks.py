"""Execute each notebook in a fresh IPython interpreter and capture rich outputs."""

import os
import subprocess
import sys

from src.config import ROOT

R = ROOT
execution = r"""
import os,sys
from pathlib import Path
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
p=Path(sys.argv[1])
book=nbformat.read(p,as_version=4)
os.chdir(p.parent)
shell=InteractiveShell.instance()
count=0
for cell in book.cells:
    if cell.cell_type!='code': continue
    count+=1
    with capture_output() as output:
        result=shell.run_cell(cell.source,store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f'Cell {count} failed: {result.error_before_exec or result.error_in_exec}')
    cell.execution_count=count
    cell.outputs=[]
    for name in ['stdout','stderr']:
        value=getattr(output,name)
        if value:cell.outputs.append(nbformat.v4.new_output('stream',name=name,text=value))
    for display in output.outputs:
        cell.outputs.append(nbformat.v4.new_output('display_data',data=display.data,metadata=display.metadata))
book.metadata['execution_note']='Executed in cell order in a fresh Python process with IPython rich-display capture.'
nbformat.validate(book)
nbformat.write(book,p)
print(p.name+': '+str(count)+' code cells executed with saved outputs.')
"""
for p in sorted((R / "notebooks").glob("*.ipynb")):
    subprocess.run([sys.executable, "-c", execution, str(p)], check=True, env=os.environ.copy())

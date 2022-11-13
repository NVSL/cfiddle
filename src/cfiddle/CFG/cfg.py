import enum
import pydot
import click
import r2pipe
import tempfile
import subprocess
import networkx as nx
import re
import sys
import time
import os

"""
CLI for x86 CFGs using radare2
"""
def in_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules


def dst_dominates_src(dst=None, src=None, immed_doms=None):
    """
    Returns whether or not the destination node dominates the source node. 
    Dst and src nodes must be distinct. 
    """
    curr_dominator = immed_doms[src] if src in immed_doms.keys() else None

    if curr_dominator is None or curr_dominator == src: # Base case
        return False

    if curr_dominator == dst:
        return True

    return dst_dominates_src(dst=dst, src=curr_dominator, immed_doms=immed_doms)


def is_self_loop(dst=None, src=None):
    """
    Returns whether or not dst and src are the same and thus a self loop
    """
    return dst == src 


def get_back_edges(cfg):
    """
    Returns list of back edges in given cfg
    """
    # NOTE: Usually first node is start node...
    start_node = list(cfg.nodes)[0]
    back_edges = []
    immed_doms = nx.immediate_dominators(cfg, start_node)
    for e in cfg.edges():
        is_back_edge = False
        src_node = e[0]
        dst_node = e[1]
        if is_self_loop(dst_node, src_node) \
        or dst_dominates_src(dst_node, src_node, immed_doms):
            is_back_edge = True 
        if is_back_edge:
            back_edges.append(e)
    
    return back_edges


def prettify_back_edges(pydot_cfg, back_edges):
    """
    Make back edges go from bottom 
    of source node to top of destination node
    """
    for b in back_edges:
        src = b[0]
        dst = b[1]
        pydot_cfg.del_edge(f'"{src}"', f'"{dst}"')
        compass_edge = pydot.Edge(f'"{src}":s',f'"{dst}":n')
        pydot_cfg.add_edge(compass_edge)
    return pydot_cfg


def identify_loops(cfg, back_edges):
    """
    Identify the loops in the cfg by the following definition:
    Given header node h and back edge source node n, all nodes reachable from
    h that also reach n without going through h are in the loop.
    Return a list of the identified loops
    """
    loops = []
    
    for e in back_edges:
        stack = []
        curr_loop = []
        visted_nodes = set()

        n = e[0]
        header = e[1]
        curr_loop.append(n)
        curr_loop.append(header)
        # DFS
        stack.append(header)
        while stack:
            v = stack.pop()
            if v not in visted_nodes:
                visted_nodes.add(v)
                # Is v reachable from header?
                header_reachable = nx.has_path(cfg, source=header, target=v)
                if header_reachable:
                    # Find path from v to n that does not go through header
                    paths = nx.all_simple_paths(cfg, v, n)
                    valid_paths = [p for p in paths if header not in p]
                    if valid_paths:
                        curr_loop.append(v)    
                for w in cfg.out_edges(v):
                    stack.append(w[1])
        loops.append(sorted(curr_loop))

    return loops


def create_loop_subgraphs(cfg, loops):
    """
    Group loops into subgraphs. NOTE: This did not help aesthetics. 
    """
    # cfg.set_clusterrank("global") # If we don't have this with clusters, the loops look whack
    for i, loop in enumerate(loops):
        sub_g = pydot.Subgraph(f'loop{i}')
        # sub_g = pydot.Cluster(f'cluster_loop{i}')
        # sub_g.set_color('blue')
        for node in loop:
            n = cfg.get_node(f'"{node}"')[0]
            sub_g.add_node(n)
        cfg.add_subgraph(sub_g)
    return cfg


def add_rank_subgraph(pydot_cfg, rank, cfg_node):
    subg = pydot.Subgraph(rank="same", rankdir="LR")
    rank_node = pydot.Node(rank, style="invis")
    pydot_cfg.add_node(rank_node)
    rank_edge = pydot.Edge(f'{rank}', f'"{cfg_node}"', style="invis")
    subg.add_edge(rank_edge)
    pydot_cfg.add_subgraph(subg)

    return pydot_cfg


def sequentialize_loops(nx_cfg, pydot_cfg, loops):
    # Create invisible nodes to define node ordering: https://newbedev.com/how-can-i-control-within-level-node-order-in-graphviz-s-dot
    # Loops should be sorted
    rank_nodes = []
    rank_counter = 0
    for l in loops:
        header = l[0]
        back_edge_src_node = l[-1]
        src_succ = nx_cfg.successors(header)
        # Identify loop exit node
        exit_node = None
        for s in src_succ:
            if s not in l:
                exit_node = s
                break
        rank = f'rank{rank_counter}'
        rank_nodes.append(rank)
        pydot_cfg = add_rank_subgraph(pydot_cfg, rank, back_edge_src_node)
        rank_counter += 1
        # Currently adding duplicate rank nodes but it doesn't seem to make a difference
        rank = f'rank{rank_counter}'
        rank_nodes.append(rank)
        pydot_cfg = add_rank_subgraph(pydot_cfg, rank, exit_node)
        rank_counter += 1
    # Link up rank nodes in order
    for i in range(1, len(rank_nodes)):
        rank_edge = pydot.Edge(f'rank{i - 1}', f'rank{i}', color="white")
        pydot_cfg.add_edge(rank_edge)
    return pydot_cfg
    


def remove_basic_block_assembly(pydot_cfg):
    """
    Remove assembly text from the CFG's basic blocks
    """

    # Avoid graph and edge nodes, which are the 1st and 2nd nodes
    nodes = pydot_cfg.get_nodes()[2:]
    for n in nodes: 
        n.set_label("")
    return pydot_cfg

def do_number_nodes(pydot_cfg):

    # Avoid graph and edge nodes, which are the 1st and 2nd nodes
    nodes = pydot_cfg.get_nodes()[2:]
    i = 0;
    for n in nodes:
        l = n.get_label()
        if l is None:
            l = ""
        l = l.replace(r"\"@\"","")
        lines = l.split(r"\l")
        lines = [f"; n{i}"] + lines;
        n.set_label(r"\l".join(lines))
        i+=1;
    return pydot_cfg


def do_trim_addresses(pydot_cfg):
    """
    Remove addresses from assembly
    """
    # Avoid graph and edge nodes, which are the 1st and 2nd nodes
    nodes = pydot_cfg.get_nodes()[2:]
    for n in nodes:
        l = n.get_label()
        if not l:
            continue
        lines = l.split(r"\l")
        for i in range(len(lines)):
            lines[i] = re.sub("^0x[0-9A-Fa-f]{8}", "", lines[i])
            lines[i] = re.sub("^\"0x[0-9A-Fa-f]{8}", "\"", lines[i])
        n.set_label(r"\l".join(lines))
    return pydot_cfg

def do_inst_counts(pydot_cfg):
    """
    Remove addresses from assembly
    """
    # Avoid graph and edge nodes, which are the 1st and 2nd nodes
    nodes = pydot_cfg.get_nodes()[2:]
    for n in nodes:
        l = n.get_label()
        if not l:
            continue
        lines = l.split(r"\l")
        c = 0 
        for i in range(len(lines)):
            if re.search("^0x[0-9A-Fa-f]{8}", lines[i]) \
            or re.search("^\"0x[0-9A-Fa-f]{8}", lines[i]): # If an instr is at the beginning of the lines, it will start with double quotes
                c+=1
        n.set_label(str(c))
    return pydot_cfg

def do_trim_comments(pydot_cfg):
    """
    Remove assembly comments
    """
    # Avoid graph and edge nodes, which are the 1st and 2nd nodes
    nodes = pydot_cfg.get_nodes()[2:]

    for n in nodes:
        c = []
        l = n.get_label()
        if not l:
            continue
        lines = l.split(r"\l")
        for i in range(len(lines)):
            lines[i] = re.sub(";.*", "", lines[i])
            if not re.match(r"^\s*$", lines[i]):
                c.append(lines[i])

        if len(c) == 0:
            n.set_label("")
        else:
            n.set_label(r"\l".join(c))
            
    return pydot_cfg


@click.command()
@click.argument('file', nargs=1)
@click.option('-o', '--output', default="out.png", type=str, help='Output PNG file name')
@click.option('--remove-assembly', is_flag=True, default=False, help="Remove assembly from basic blocks")
@click.option('--trim-addresses/--no-trim-addresses', default=True, help="Remove addresses from assembly")
@click.option('--trim-comments', is_flag=True, default=False, help="Remove comments from assembly")
@click.option('--number-nodes', is_flag=True, default=False, help="Number the nodes")
@click.option('--inst-counts', is_flag=True, default=False, help="Just show instructions per basic block")
@click.option('--pretty-loops', is_flag=True, default=False, help="Make loops visually more sequential")
@click.option('--spacing', type=float, default=1, help="Spacing between nodes")
@click.option('--symbol', help="Function to draw")
@click.option('--filter','filt', help="string to search for symbols to show.")
@click.option('--list', '-l', 'just_list', is_flag=True, help="just list symbols")
def cfg(*args, **kwargs):
    return do_cfg(*args, **kwargs)
    
def do_cfg(file,  symbol, output=None,
           spacing=1, trim_comments=False, remove_assembly=False,
           trim_addresses=True, number_nodes=False, jupyter=False,
           inst_counts=False, pretty_loops=True, filt=None,
           just_list=None):
    r2 = r2pipe.open(f'{file}', flags="-e bin.cache=true".split())
    listing = r2.cmd('aab; fs symbols; f')
    if not symbol or just_list:
        symbols = [l.split(r" ")[2] for l in listing.split(r"\n") if len(l) > 0]
        filtered_symbols = filter(lambda x: x.startswith("sym."), symbols)
        if filt:
            filtered_symbols = filter(lambda x: filt in x , filtered_symbols)
        click.echo("\n".join(filtered_symbols))
        if just_list:
            return
        symbol = click.prompt('Enter a function symbol name from one of the above', type=str)

    if not symbol.startswith("sym."):
        fcn_name = f"sym.{symbol}"
    else:
        fcn_name = symbol


    with tempfile.TemporaryDirectory() as temp_dir:

        r2.cmd('e asm.syntax=att')
        finished = False
        r2.cmd(f's {fcn_name}; agfd > {temp_dir}/tmp.dot')
        time.sleep(0.5)
        nx_cfg = nx.drawing.nx_pydot.read_dot(f'{temp_dir}/tmp.dot')

        back_edges = get_back_edges(nx_cfg)
        loops = identify_loops(nx_cfg, back_edges)


        # Try fiddling with the dot file itself to see if it's better
        # Try heuristic where the node going out of a loop is of lower rank
        # than the rest of the loop
        # Try drawing boxes around loop bodies - This is bad!
        # Make last return block have lowest rank
        # Create invisible nodes to define node ordering: https://newbedev.com/how-can-i-control-within-level-node-order-in-graphviz-s-dot

        nx.nx_pydot.write_dot(nx_cfg, f'{temp_dir}/nx_tmp.dot')

        pydot_cfg = nx.nx_pydot.to_pydot(nx_cfg)
        pydot_cfg = prettify_back_edges(pydot_cfg, back_edges)

        if pretty_loops:
            pydot_cfg = sequentialize_loops(nx_cfg, pydot_cfg, loops)
        if trim_addresses:
            pydot_cfg = do_trim_addresses(pydot_cfg)
        if trim_comments:
            pydot_cfg = do_trim_comments(pydot_cfg)
        if remove_assembly:
            pydot_cfg = remove_basic_block_assembly(pydot_cfg)
        if number_nodes:
            pydot_cfg = do_number_nodes(pydot_cfg)
        if inst_counts:
            pydot_cfg = do_inst_counts(pydot_cfg)

        pydot_cfg.set_ranksep(spacing) # Increase spacing between ranks and thus the nodes

        if output is None:
            if in_notebook() or jupyter:
                output = f"{file}-{symbol}.svg"
            else:
                output = f"{file}-{symbol}.png"

        ext = os.path.splitext(output)[1]

        pydot_cfg.write_raw(f'{temp_dir}/pretty_tmp.dot')
        if ext == ".png":
            pydot_cfg.write_png(f'{output}')
        elif ext == ".svg":
            pydot_cfg.write_svg(f'{output}')

        return output

if __name__ == '__main__':
    cfg()


class CFG:
    def cfg(self, function, output, **kwargs):
        """Return a image of the control flow graph for a function.

        This extracts the CFG from the compiled object file using the `Redare2
        <https://rada.re/n/>`_ toolkit.  Redare will sometimes fail to create a
        coherent CFG.

        Args:
           function: function to show.
           output: filename in which to put the resulting ``png`` file or ``None``, which an anonymous file will be created.
        Returns:
           ``str`` : The filename containing the file.

        """
        return do_cfg(self.lib, function,  output=output, **kwargs)

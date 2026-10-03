"""Compile Agent-authored semantic JSON. Does not perform scientific understanding."""
import argparse
import copy
from contracts import read, write
from validate_ir import validate

def compile_ir(agent, snapshot):
    ir=copy.deepcopy(agent)
    ir['schema_version']='scientific-framework/ir/v1'
    # Author must explicitly set status and source registry; no automatic approval.
    qa=validate(ir,snapshot)
    if not qa['valid']: raise ValueError('\n'.join(qa['errors']))
    return ir,qa

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('agent_understanding'); p.add_argument('--sources',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args(); ir,qa=compile_ir(read(a.agent_understanding),read(a.sources))
    write(a.output,ir)
    print('Compiled Agent understanding; approval_eligible=',qa['approval_eligible'])

if __name__=='__main__': main()

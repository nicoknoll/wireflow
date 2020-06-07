try:
    from graphviz import Digraph
except ImportError:
    raise ImportError('To use the debug diagram you need to install `graphviz`.')

import os.path

from . import config
from .module import ModuleStatus
from .util import flatten

STATUS_COLOR = {
    ModuleStatus.PENDING: 'white',
    ModuleStatus.READY: 'lightgray',
    ModuleStatus.RUNNING: 'green',
    ModuleStatus.DONE: 'palegreen1',
    ModuleStatus.ERROR: 'lightred',
}


def draw_runner_state(runner):
    filename = os.path.join(config.FILE_STORAGE_ROOT, '_debug.gv')
    f = Digraph('flow', filename=filename, graph_attr={'nodesep': '1', 'ranksep': '1'})
    f.attr(rankdir='LR', size='8,8')

    for module_id, state in runner.states.items():
        module = runner.flow.modules[module_id]
        f.attr('node', shape='record', fillcolor=STATUS_COLOR.get(state.status), style='filled,solid')
        params_in = '({})'.format(', '.join(module.get_params_in()))
        params_out = '({})'.format(', '.join(module.get_params_out()))
        f.node(module_id, label=module.label + ' ' + params_in + '|' + params_out)

    for connection in flatten(runner.flow.connections.values()):
        for k, v in connection.mapping.items():
            f.edge(connection.module_from_id, connection.module_to_id, label=f'{k} → {v}')

    f.view()

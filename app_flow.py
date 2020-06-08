from os.path import join, dirname, abspath

from wireflow import config as global_config
from wireflow.flow import Flow
from wireflow.module import Module, module_registry
from wireflow.runner import Runner

global_config.STORAGE = 'wireflow.storage.backends.memory.MemoryStorage'
global_config.FILE_STORAGE_ROOT = join(dirname(abspath(__file__)), '_tmp')


@module_registry.register
class RandomTextModule(Module):
    params_in = []
    params_out = ['text']

    @classmethod
    def run(cls, config=None):
        return {'text': 'Random string'}


@module_registry.register
class CaseModule(Module):
    params_in = ['text']
    params_out = ['upper', 'lower']

    @classmethod
    def run(cls, config=None, text=''):
        return {'upper': text.upper(), 'lower': text.lower()}


@module_registry.register
class PrintModule(Module):
    params_in = ['text']
    params_out = []

    default_config = {}

    @classmethod
    def run(cls, config=None, text=''):
        print(config['prefix'] + text)


@module_registry.register
class ConcatModule(Module):
    params_in = ['text1', 'text2']
    params_out = ['text']

    @classmethod
    def run(cls, config=None, text1='', text2=''):
        return {
            'text': text1 + text2
        }


@module_registry.register
class AsyncModule(Module):
    params_in = ['text']
    params_out = ['text']
    is_async = True

    @classmethod
    def run(cls, config=None, text=''):
        # send request with data to external server
        print('Please enter data at: http://127.0.0.1:5000/tasks/data-entry')


flow = Flow()
flow.store()

start = flow.add(RandomTextModule)
m1 = flow.add(CaseModule)
m2 = flow.add(PrintModule)
m3 = flow.add(PrintModule)

async_module = flow.add(AsyncModule)
m5 = flow.add(PrintModule)

flow.connect(start, m1, {'text': 'text'})
flow.connect(m1, m2, {'upper': 'text'})
flow.connect(m1, m3, {'lower': 'text'})

flow.connect(start, async_module, {'text': 'text'})
flow.connect(async_module, m5, {'text': 'text'})

runner = Runner(flow_id=flow.id)
runner.store()

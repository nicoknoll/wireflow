from functools import partial

from .exception import FlowRuntimeError
from .flow import Flow
from .module import ModuleStatus, ANY_PARAMS
from .util import cached_property, Storable, get_reverse_relation


class ModuleState(Storable):
	prefix = 'ms'
	state_keys = Storable.state_keys + [
		'module_id', 'runner_id', 'status', 'kwargs', 'error'
	]

	def __init__(self, module_id, runner_id, status, kwargs=None):
		super().__init__()
		self.module_id = getattr(module_id, 'id', module_id)
		self.runner_id = getattr(runner_id, 'id', runner_id)
		self.status = status
		self.kwargs = kwargs or {}
		self.error = ''

	def get_store_key(self):
		return f'{self.runner_id}:{self.id}'

	@cached_property
	def runner(self):
		return Runner.load(f'{self.runner_id}:{self.runner_id}')


class Runner(Storable):
	prefix = 'run'
	state_keys = Storable.state_keys + ['flow_id']

	def __init__(self, flow_id):
		super().__init__()
		self.flow_id = getattr(flow_id, 'id', flow_id)
		self.init_states()

	def get_store_key(self):
		return f'{self.id}:{self.id}'

	def init_states(self):
		for module_id, module in self.flow.modules.items():
			ms = ModuleState(
				runner_id=self.id,
				module_id=module_id,
				status=ModuleStatus.PENDING,
			)
			ms.store()

	@cached_property
	def flow(self):
		return Flow.load(f'{self.flow_id}:{self.flow_id}')

	@cached_property
	def states(self):
		states = get_reverse_relation(self.id, ModuleState)
		return {s.module_id: s for s in states}

	def run(self, module_id):
		module_id = getattr(module_id, 'id', module_id)

		module = self.flow.modules[module_id]
		state = self.states[module_id]
		state.status = ModuleStatus.RUNNING
		state.store()

		try:
			callback = partial(self.complete, module_id)
			module.module_class._run(
				callback,
				config=module.config,
				**state.kwargs
			)

		except Exception as e:
			state.status = ModuleStatus.ERROR
			state.error = str(e)
			state.store()
			raise e  # TODO: only debug

	def _validate_params_out(self, module_id, params_out):
		module = self.flow.modules[module_id]
		module_params_out = set(module.get_params_out())
		params_out = set(params_out)

		if ANY_PARAMS not in module_params_out and module_params_out != params_out: 
			msg = 'Wrong output parameters. Expected: {}, got: {}'
			raise FlowRuntimeError(msg.format(module_params_out, params_out))

	def complete(self, module_id, **kwargs):
		self._validate_params_out(module_id, kwargs.keys())

		# Initiate connected modules with output parameters
		for connection in self.flow.connections[module_id]:
			params_in = {v: kwargs.get(k) for k, v in connection.mapping.items()}
			next_state = self.states[connection.module_to_id]
			next_module = self.flow.modules[connection.module_to_id]

			if next_state.status in [ModuleStatus.DONE, ModuleStatus.ERROR]:
				raise FlowRuntimeError('Circles are not supported yet.')

			# Prevent existing kwargs from overwrite
			existing_keys = set(params_in.keys()) & set(next_state.kwargs.keys())
			if existing_keys:
				raise FlowRuntimeError('Cannot overwrite existing kwargs: {}'.format(existing_keys))

			next_state.kwargs.update(params_in)

			can_run = next_module.module_class.can_run(**next_state.kwargs)
			next_state.status = ModuleStatus.READY if can_run else ModuleStatus.PENDING
			next_state.store()
			
		# Move status to done
		self.states[module_id].status = ModuleStatus.DONE
		self.states[module_id].store()

	def step(self):
		ready_modules = [m for m, s in self.states.items() if s.status == ModuleStatus.READY]
		for module_id in ready_modules:
			self.run(module_id)

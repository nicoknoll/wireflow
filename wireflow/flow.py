from .exception import FlowConfigurationError
from .module import ANY_PARAMS, module_registry
from .util import format_class_name, cached_property, Storable


def _validate_mapping(module_from, module_to, mapping):
	params_out = set(mapping.keys())
	params_in = set(mapping.values())

	module_params_out = set(module_from.get_params_out())
	module_params_in = set(module_to.get_params_in())

	# module.params_out >= mappping.params_out
	if ANY_PARAMS not in module_params_out and not params_out.issubset(module_params_out):
		raise FlowConfigurationError('Cannot connect: {} is not subset of {}'.format(
			params_out, module_params_out
		))

	# module.params_in >= mappping.params_in
	if ANY_PARAMS not in module_params_in and not params_in.issubset(set(module_params_in)):
		raise FlowConfigurationError('Cannot connect: {} is not subset of {}'.format(
			params_in, module_params_in
		))


class FlowModule(Storable):
	prefix = 'mod'
	state_keys = Storable.state_keys + [
		'class_name', 'flow_id', 'label', 'config'
	]

	def __init__(self, class_name, flow_id, label=None, config=None):
		super().__init__()
		self.flow_id = getattr(flow_id, 'id', flow_id)

		self.class_name = class_name
		self.label = label or format_class_name(class_name)

		config = config or {}
		self.config = (self.module_class.default_config or {}).copy()
		self.config.update({k: config[k] for k in config if k in self.config})

	def get_store_key(self):
		return f'{self.flow_id}:{self.id}'

	@cached_property
	def flow(self):
		return Flow.load(f'{self.flow_id}:{self.flow_id}')

	@cached_property
	def module_class(self):
		return module_registry[self.class_name]

	def get_params_in(self):
		return self.module_class.params_in

	def get_params_out(self):
		return self.module_class.params_out

	def get_config(self):
		return self.config


class Connection(Storable):
	prefix = 'con'
	state_keys = Storable.state_keys + [
		'flow_id', 'module_from_id', 'module_to_id', 'mapping'
	]

	def __init__(self, flow_id, module_from_id, module_to_id, mapping):
		super().__init__()
		self.flow_id = getattr(flow_id, 'id', flow_id)
		self.module_from_id = getattr(module_from_id, 'id', module_from_id)
		self.module_to_id = getattr(module_to_id, 'id', module_to_id)
		self.mapping = mapping

	def get_store_key(self):
		return f'{self.flow_id}:{self.id}'

	@cached_property
	def flow(self):
		return Flow.load(f'{self.flow_id}:{self.flow_id}')

	@cached_property
	def module_from(self):
		return FlowModule.load(f'{self.flow_id}:{self.module_from_id}')

	@cached_property
	def module_to(self):
		return FlowModule.load(f'{self.flow_id}:{self.module_to_id}')


class Flow(Storable):
	prefix = 'flow'

	def get_store_key(self):
		return f'{self.id}:{self.id}'

	def add(self, class_name, label=None, config=None):
		class_name = getattr(class_name, '__name__', class_name)
		flow_module = FlowModule(
			class_name,
			flow_id=self.id,
			label=label,
			config=config
		)
		flow_module.store()

		# invalidate cache
		if 'modules' in self.__dict__:
			del self.__dict__['modules']

		return flow_module

	def connect(self, module_from_id, module_to_id, mapping):
		module_from_id = getattr(module_from_id, 'id', module_from_id)
		module_to_id = getattr(module_to_id, 'id', module_to_id)

		module_from = self.modules[module_from_id]
		module_to = self.modules[module_to_id]
		_validate_mapping(module_from, module_to, mapping)

		connection = Connection(self.id, module_from_id, module_to_id, mapping)
		connection.store()

		# invalidate cache
		if 'connections' in self.__dict__:
			del self.__dict__['connections']

		return connection

	@cached_property
	def modules(self):
		keys = self.storage.get_reverse_keys(self.id)
		keys = [k for k in keys if k.split(':')[1].startswith(FlowModule.prefix)]
		modules = [FlowModule.load(k) for k in keys]
		return {m.id: m for m in modules}

	@cached_property
	def connections(self):
		keys = self.storage.get_reverse_keys(self.id)
		keys = [k for k in keys if k.split(':')[1].startswith(Connection.prefix)]

		connections = {k: [] for k in self.modules.keys()}
		for k in keys:
			connection = Connection.load(k)
			connections[connection.module_from_id].append(connection)

		return connections

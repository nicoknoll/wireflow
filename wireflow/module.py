from .exception import FlowRuntimeError

ANY_PARAMS = '__any__'


class ModuleStatus:
	PENDING = 'PENDING'  # before reached
	READY = 'READY'  # reached
	RUNNING = 'RUNNING'  # after start, before done
	DONE = 'DONE'  # after completion
	ERROR = 'ERROR'  # if error


class Module:
	params_in = [ANY_PARAMS]
	params_out = [ANY_PARAMS]
	is_async = False  # e.g. external services

	identifier = 'is.nico.Module'
	default_config = None

	@classmethod
	def can_run(cls, **kwargs):
		return set(cls.params_in).issubset(set(kwargs.keys()))

	@classmethod
	def run(cls, config=None, **kwargs):
		raise NotImplementedError

	@classmethod
	def _run(cls, complete, **kwargs):
		if not cls.can_run(**kwargs):
			raise FlowRuntimeError('Cannot run "{}"'.format('self.id'))

		result = cls.run(**kwargs) or {}
		
		if not cls.is_async:
			return complete(**result)


class ModuleRegistry(dict):
	def register(self, cls):
		self[cls.__name__] = cls
		return cls


module_registry = ModuleRegistry()

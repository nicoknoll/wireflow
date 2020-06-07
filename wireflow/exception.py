class WireflowException(Exception):
    pass


class FlowConfigurationError(WireflowException):
    pass


class FlowRuntimeError(WireflowException):
    pass

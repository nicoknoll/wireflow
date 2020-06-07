import requests

from flask import Flask
from flask import request
from flask import render_template

from wireflow.debug import draw_runner_state
from wireflow.exception import FlowRuntimeError
from wireflow.module import ModuleStatus
from wireflow.runner import Runner

from app_flow import runner as flow_runner, start, async_module

flow_runner.run(start)
flow_runner.step()
flow_runner.step()
flow_runner.step()

# Web interface / delay

"""
POST http://api.wireflow.io/v1/runs/:run/modules/:module/complete
-> load runner for :run
-> trigger complete with :module and {payload}
-> store new state
"""


app = Flask(__name__)


@app.route('/v1/runs/<runner_id>/modules/<module_id>/complete', methods=['POST'])
def complete_module(runner_id, module_id):
	payload = dict(request.form)
	runner = Runner.load(f'{runner_id}:{runner_id}')
	status = runner.states[module_id].status

	if not status == ModuleStatus.RUNNING:
		msg = '{} needs to be in status "RUNNING" to be completed, not in status "{}".'
		raise FlowRuntimeError(msg.format(module_id, status))

	runner.complete(module_id, **payload)
	runner.step()

	draw_runner_state(runner)

	return ''


@app.route('/tasks/data-entry', methods=['GET', 'POST'])
def async_form():
	if request.method == 'POST':
		payload = dict(request.form)
		requests.post(f'http://127.0.0.1:5000/v1/runs/{flow_runner.id}/modules/{async_module.id}/complete', data=payload)

	return render_template('form.html', params_out=async_module.module_class.params_out)




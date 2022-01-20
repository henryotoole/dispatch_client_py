# dispatch_client_py/dispatch_client.py
# Josh Reed
#
# A dispatch foreign client which is built in python using the popular requests module.

# Our code
from dispatch_client_py.exceptions import DispatchResponseErrorException, DispatchResponseTimeoutException
from dispatch_client_py.exceptions import DispatchClientException, DispatchServerException

# Other libraries
import requests

# Base python
import time
import random
import string
import urllib
import json

class DispatchClient:

	def __init__(self, server_domain, dispatch_route='/_dispatch', client_name='py', verbose=True):
		"""Initialize a dispatch client which can communicate with a central dispatch server. This client will be assigned
		a unique session id and all requests to the server will have this ID associated with it.
		This client adheres to the JSONRPC 2.0 standard for communication.


		Args:
			server_domain (str): The absolute URL that points to the domain of this dispatch server (e.g. https://www.theroot.tech)
			dispatch_route (str, optional): The route to the dispatch request handler. Default "/_dispatch"
			client_name (str, optional): The name given to this client. This name can be used to designate
				a series of clients under one project namespace. Default is 'py'
			verbose (bool, optional): Whether or not to print log messages. Default is True
		"""		

		# Main variables
		self.dispatch_url = server_domain + dispatch_route
		self.base_url = server_domain
		self.verbose = verbose
		self.logger = None
		self.session_id = self.gen_session_id()

		# The foreign type indicates to the backend from what client comes a poll request (js, python, etc)
		self.client_name = client_name
		
		# This is a key/value pair set that will be sent along with every request.
		self.base_data = {} 
		self.headers = {}
		
		# Frontend functions bound with client.bind(fn) will be stored here by key: function_name
		self.client_functions = {}

		# These cookies will be sent with every request.
		self._cookies = {}

		# Polling variables
		self.polling_fast = 1		# Polling interval for fast polling
		self.polling_slow = 5		# Polling interval for slow polling
		self.polling_stop_flag = None
		self.request_timeout = 10	# How long it takes for a request to time out

		self.log_debug("Initialized to point at " + self.dispatch_url)

	def call_server_function(self, function_name, *args):
		"""Call a function on the running dispatch backend associated with this client. This function call will be provided
		with all given arguments.

		WARNING: This function will block until the request completes.

		Args:
			function_name (str): The name of the function on the backend to call
			...args (*): Any number of arguments to provide to the backend function. Keyword arguments are not supported.

		Raises:
			DispatchResponseErrorException if the server responds with a JSONRPC 2.0 error
			DispatchResponseTimeoutException if the request times out
			DispatchClientException if the client has not been configured correctly (400's)
			DispatchServerException if the server had an issue (500 error, etc.)
			ValueError for unhandled codes.

		Returns:
			*:	This will be the JSONRPC 'result' object, which can be anything
		"""

		# Pack all arguments into a JSON string
		params = urllib.parse.quote(json.dumps(args))
		permanent_data = urllib.parse.quote(json.dumps(self.base_data))

		# Base-format data block
		data = {
			'jsonrpc': "2.0",
			'method': function_name,
			'params': params,
			'id': self.session_id,
			'__dispatch__permanent_data': permanent_data
		}

		# Debug info
		debug_datastring = json.dumps(data)
		mlen = min(len(debug_datastring), 256) # The length of the datastring or 256, whichever is smaller.
		self.log_debug("Calling " + str(function_name) + " with " + debug_datastring[:mlen])

		# Use requests module to send request.
		r_code, r_data = self.get_json(self.dispatch_url, self.prep_data(data))

		if r_code == 200:
			if r_data is None:
				raise ValueError("Server responded with code 200, but with no data.")
			result = r_data.get('result')
			error = r_data.get('error')
			if result is not None:
				return result
			if error is not None:
				raise DispatchResponseErrorException(error)
		elif r_code == None:
			raise DispatchResponseTimeoutException()
		elif r_code >= 300 and r_code < 500:
			raise DispatchClientException(r_code)
		elif r_code >= 500 and r_code < 600:
			raise DispatchServerException(r_code)
		else:
			raise ValueError("Unhandled server response code: " + str(r_code))

	def get_json(self, url, data, files={}):
		"""Use the requests module to send a request to Dispatch. This will block until either the timeout
		is reached or the request returns. In the future I'd like to upgrade this to be more of a promise
		using python's await features.

		Args:
			url (String): The absolute url at which to place this request
			data (Dict): A dictionary of key/value pairs to be sent to the server. All keys and values
				will be stringified before being sent.
			files (dict, optional): Files to be sent with the request. Defaults to {}.
		Returns:
			Tuple: status_code, response_data e.g. 
				404, "File not found" or perhaps
				200, {'json_key', 1} <--- note that this is an actual dict, not a string.
			If the request times out, the tuple (None, None) is returned.
		"""
		try:
			r = requests.post(
				url, data=data,
				files=files,
				timeout=self.request_timeout,
				cookies=self._cookies,
				allow_redirects=False,
				verify=False,
				headers=self.headers)
			self._last_request = r
			if(r.status_code != 200):
				self.log_debug("Dispatch request returns non-200 code <" + str(r.status_code) + "> - Debug Info: '" + r.text + "'")
				return r.status_code, None # Return the status code and None to signify it wasn't a 200
			try:
				return 200, r.json() # Return the JSON and the 200 code
			except ValueError as e:
				return 200, None # No JSON parseable, but we still got a 200
		except (requests.exceptions.ConnectTimeout):
			self.log_debug('Dispatch request has timed out (or had a ConnectionError) after ' + str(self.request_timeout) + ' seconds.')
		return None, None # Connection timed out, so no code or JSON

	def polling_set_frequency(self, interval):
		"""Set the the frequency at which polls will be made.

		Args:
			interval (Number): Number of seconds between polls
		"""
		self._polling_enable(interval)
	
	def polling_set_fast(self):
		"""Set polling to the faster rate.
		"""
		self.polling_set_frequency(self.pollint_fast)

	def polling_set_slow(self):
		"""Set polling to the slower rate.
		"""
		self.polling_set_frequency(self.pollint_slow)

	def _polling_enable(self, poll_interval):
		"""Enable polling as a mechanism to check every so often if the server has some calls it would
		like to make to this client. This will send a request every so often, so use with caution.

		Args:
			poll_interval (int): Number of seconds between polls
		"""

		# Clear the old interval, if it exists
		self._polling_disable()

		# Setup a new polling interval.
		# This function should preserve the 'self' context.
		def wrapped():
			return self._polling_function()
			
		# This will start a timer
		#TODO use Process to do this with multithreading.
		raise ValueError("This functionality is not yet implemented : (")

	def _polling_disable(self):
		"""Disables polling and does cleanup. Safe to call even if polling is not happening.
		"""

		# Clear the old interval, if it exists
		if(self.polling_stop_flag):
			self.polling_stop_flag.set() # Will kill the interval thread
			self.polling_stop_flag = None
	
	def _polling_function(self):
		"""Call the general polling function on the dispatch server to see if this session has any
		new info for us.
		"""

		result = self.call_server_function('__dispatch__client_poll', self.session_id, self.client_name)

		function_blocks = result.get('queued_functions', [])

		# Function blocks is a list of form: 'queued_functions': [{
		#	'fname': fname,
		#	'args': args,
		#	}, {...}, ...],

		for function_block in function_blocks:
			self.client_call_bound_function(function_block.get('fname'), function_block.get('args'))
	
	def client_call_bound_function(self, function_name, args):
		"""Call a function which has been bound using client_bind_function(). This is generally called by
		polling when the server instigates a function call.

		Args:
			function_name (str): The name of the function to call
			args (list): A list of arguments to be provided to the function when we call it 
		"""	
		fn = self.client_functions.get(function_name)

		if(fn is None):
			self.log("Warning: Server attempted to call unbound frontend function '" + function_name + "'")
			return

		print_args = str(args)
		if(len(print_args) > 256): print_args = print_args[0:256] + "..."

		self.log_debug("Calling frontend function: " + function_name + " with " + print_args)

		fn(*args) # Call the function with the args.

		# TODO In the future I'd like to add some sort of callback mechanism, but that will require some
		# extra hoops on the server.
		
	def client_bind_function(self, frontend_fn, function_name=None):
		"""Bind a function to this client so the server can call it. For now, the return value of this
		function is entirely ignored.

		Args:
			frontend_fn (function): The function to be called, with some sort of 'self' context bound
			function_name (str, optional): function_name: Can be provided to set a specific name for a function.
				This must be provided for anon functions. Default is to use the given name of the provided function.
		"""
	
		if(function_name is None): function_name = frontend_fn.func_name
		
		# If the function was anonymous or did not have a name, use the optional one provided by user
		if(function_name is None or function_name == ""):
			raise ValueError("Provided function had no base name (possible anonymous function?). Use the kwarg 'function_name'.")
			
		self.log_debug("Binding dispatch callable function '" + str(function_name))

		# Can't bind if it's already bound...
		if(self.client_functions.get(function_name)):
			raise ValueError("A function has already been bound to name " + str(function_name))
		
		self.client_functions[function_name] = frontend_fn
		
	def prep_data(self, request_data, prevent_caching=True):
		"""Modify a post request data block to have any base_data and perhaps to prevent caching.

		Args:
			request_data (dict): The key-value dict that is sent to the server in the POST request
			prevent_caching (bool, optional): If true, add a special param to prevent caching. Defaults to True.

		Returns:
			dict: The request_data object with terms added.
		"""
		if(prevent_caching):
			request_data['__dispatch__cache_bust'] = str(time.time())

		return request_data

	def gen_session_id(self):
		"""Return a random string 64 characters long to be used as a session id.
		Returns:
			String: Random hash string
		"""
		N = 64
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

	def logger_set(self, logger):
		"""Provide a python 'logger' instance to this client. If a logger is set, then debug output will be routed
		to the logger rather than print() when verbose is True.

		Args:
			logger (Logger): Python logging module logger
		"""
		self.logger = logger

	def log_debug(self, message):
		"""Log a message, but only if verbose is true

		Args:
			message (*): Anything capable of being converted to string.
		"""
		if self.verbose:
			self.log(message)

	def log(self, message):
		"""Log a message for this client. If there's a logger for this client use it, otherwise print
		the message.

		Args:
			message (*): Anything capable of being converted to string.
		"""
		message = "Dispatch >> " + str(message)
		if(self.logger):
			self.logger.debug(message)
		else:
			print(message)

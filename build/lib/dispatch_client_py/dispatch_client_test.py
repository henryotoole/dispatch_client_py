# dispatch_client_py/dispatch_client_test.py
# Josh Reed 2021
#
# This is an extension of the base client which can be used to test the dispatch server.

# Our code
from dispatch_client_py.dispatch_client import DispatchClient

# Base python
from urllib.parse import urlsplit
import traceback

class DispatchClientTest(DispatchClient):

	def __init__(self, server_domain):
		"""Initialize a dispatch client for use in testing. See base class for more info.

		Args:
			server_domain (str): The absolute url to point this client at (e.g. https://www.theroot.tech).
		"""

		super().__init__(server_domain, verbose=True)

	def login_user(self, login_route, user_email, user_pass):
		""" Calling this function will log in a user with user_email and user_password at the
		indicated server route. This assumes that flask_login or something similar has been
		used for this server.

		Calling this function will add the cookies returned by the login request to this
		client. Those cookies will be sent along with subsequent requests, simulating a logged
		in user in a browser or something.

		Args:
			login_route (str): The login route for this server e.g. "/login"
			user_email (str): The email of the user to log in with
			user_pass (str): The password of the user to log in with
		"""
		
		ret, data = self.get_json(self.base_url + login_route, {'email': user_email, 'password': user_pass})
		
		# Save the cookies off the login request so that we appear logged in every time.
		self._cookies = self._last_request.cookies

	def assert_block(self, block):
		"""Assert that a dispatch request block actually evaluates correctly when fired at a server.
		
		Raises:
			AssertionError if it does not.

		Args:
			block (DispatchClientTestBlock): The block to test
		"""

		# Send the block request
		try:
			result = self.call_server_function(block.function_name, *block.args)

			# Make sure it was supposed to succeed
			if block.desired_result is None:
				raise AssertionError(
					"Dispatch test block for fn '" + str(block.function_name) + "' succeeded when it should have failed."
				)
			else:
				# Make sure the success had the right data.
				if block.desired_result == result:
					return
				else:
					raise AssertionError(
						"Wrong result data for fn '" + str(block.function_name) + "': wants (" + str(block.desired_result) + "), got (" + str(result) + ")"
					)
		except Exception as e:
			# Make sure it was supposed to fail
			if block.desired_error is None:
				print("############ Original Exception ##############")
				traceback.print_exc()
				print("##############################################")
				raise AssertionError(
					"Dispatch test block for fn '" + str(block.function_name) + "' failed when it should have succeeded with error: " + str(e)
				)
			if not isinstance(e, block.desired_error):
				print("############ Original Exception ##############")
				traceback.print_exc()
				print("##############################################")
				raise AssertionError(
					"Wrong failure type for fn '" + str(block.function_name) + "': wants (" + str(block.desired_error) + "), got (" + str(e) + ")"
				)

class DispatchClientTestBlock:

	def __init__(self, function_name, args, desired_result=None, desired_error=None):
		"""Create a block of info which can be fired at a dispatch server with DispatchTestClient.assert_block()
		to see if the server returns the response we want.

		Args:
			function_name (str): The name of the dispatch server function
			args (list): A list of args. Can be anything that can be converted to json.
			desired_result (*, optional): If provided, this block will need to get a successful response. This will be
				the data that we expect to get as the result from the request. Defaults to None.
			desired_error (ExceptionDef, optional): If provided, we expect this block to trip an error of
				the type provided here. Defaults to None.
		"""
		self.function_name = function_name
		self.args = args
		self.desired_result = desired_result
		self.desired_error = desired_error
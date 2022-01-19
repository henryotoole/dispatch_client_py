# dispatch_client_py/exceptions.py
# Josh Reed 2020
# 
# Exceptions used by the dispatch client module.

class DispatchResponseErrorException(Exception):

	def __init__(self, error_object):
		"""Raised when the dispatch server returns a 200 response with a JSONRPC formatted
		error object.

		Args:
			error_object (dict): The JSONRPC format error object with keys:
				code, message, data
		"""
		self.error_code = error_object['code']
		self.error_message = error_object['message']
		self.error_data = error_object.get('data')
		super().__init__(self.error_message)

class DispatchResponseTimeoutException(Exception):
	"""Raised when a dispatch server request times out.
	"""

	def __init__(self):
		
		super().__init__("Dispatch request timed out.")

class DispatchClientException(Exception):
	"""Raised when a dispatch server request returns a 400 response, indicating
	that the client has the wrong url or does not have access.
	"""

	def __init__(self, error_code):
		
		msg = "Server returns code " + str(error_code) + " when attempting to send dispatch request. Check that client is configured correctly."

		super().__init__(msg)

class DispatchServerException(Exception):
	"""Raised when a dispatch server request returns a 500 response, indicating
	that the server is having some sort of trouble.
	"""

	def __init__(self, error_code):
		
		msg = "Server returns code " + str(error_code) + " when attempting to send dispatch request. Check that server is configured correctly."

		super().__init__(msg)
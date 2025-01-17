#!/usr/bin/env python3
import weakref
import asyncio
import asab
import aiohttp

import asab.web
import asab.web.rest
import asab.web.session
import asab.api


class MyApplication(asab.Application):

	'''
	Run by:  
	`$ PYTHONPATH=.. ./webserver-advanced.py`
	
	The application will be available at http://localhost:8080/   
	Visit also the documentation at http://localhost:8080/doc
	'''

	async def initialize(self):
		# Loading the web service module
		self.add_module(asab.web.Module)

		# Locate web service
		websvc = self.get_service("asab.WebService")

		# Create a dedicated web container
		container = asab.web.WebContainer(websvc, 'web')

		# Add a web session service
		asab.web.session.ServiceWebSession(self, "asab.ServiceWebSession", container.WebApp, session_class=MySession)

		# Enable exception to JSON exception middleware
		container.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		# Add a route
		container.WebApp.router.add_get('/', self.index)
		print("Test with curl:\n\t$ curl http://localhost:8080/")

		container.WebApp.router.add_get('/api/login', self.login)
		container.WebApp.router.add_get('/error', self.error)

		# Add a web app
		asab.web.StaticDirProvider(container.WebApp, '/', "webapp")

		# Add a websocket handler
		container.WebApp.router.add_get('/subscribe', MyWebSocketFactory(self))

		# Also use API Service
		svc = asab.api.ApiService(self)
		svc.initialize_web(container)


	async def index(self, request):
		'''
		Returns "Hello, world!"
		'''
		return aiohttp.web.Response(text="Hello, world!\n")


	async def login(self, request):
		'''
		Greets in the session.
		'''

		session = request.get('Session')
		return aiohttp.web.Response(text='Hello {}!\n'.format(session))


	async def error(self, request):
		'''
		Raises the error.
		'''
		raise RuntimeError("Error!!")


class MyWebSocketFactory(asab.web.WebSocketFactory):

	def __init__(self, app):
		super().__init__(app)

		app.PubSub.subscribe("Application.tick/10!", self.on_tick)


	async def on_request(self, request):
		session = request.get('Session')
		ws = await super().on_request(request)
		session.WebSockets.add(ws)
		return ws


	async def on_message(self, request, websocket, message):
		print("WebSocket message", message)


	def on_tick(self, event_name):
		message = {'event_name': event_name, 'type': 'factory'}

		wsc = list()
		for ws in self.WebSockets:
			wsc.append(ws.send_json(message))

		self.send_parallely(wsc)


class MySession(asab.web.session.Session):

	def __init__(self, storage, id, new, max_age=None):
		super().__init__(storage, id, new, max_age)
		storage.App.PubSub.subscribe("Application.tick!", self.on_tick)

		self.Loop = storage.App.Loop
		self.WebSockets = weakref.WeakSet()



	def on_tick(self, event_name):
		message = {'event_name': event_name, 'type': 'session'}

		wsc = list()
		for ws in self.WebSockets:
			wsc.append(ws.send_json(message))

		asyncio.gather(*wsc)


if __name__ == '__main__':
	app = MyApplication()
	app.run()

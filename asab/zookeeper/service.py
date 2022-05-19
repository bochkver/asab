from ..abc.service import Service
from ..config import Config

from .container import ZooKeeperContainer


class ZooKeeperService(Service):
	"""
	ZooKeeperService connects to Zookeeper via aiozk client:
	https://zookeeper.apache.org/
	https://pypi.org/project/aiozk/
	"""

	Config.add_defaults({
		"asab:zookeeper": {
			# Server list to which ZooKeeper Client tries connecting.
			# Specify a comma (,) separated server list.
			# A server is defined as address:port format.
			# "servers": "zookeeper:12181",
			"servers": "zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181",
			"path": "/asab",
		}
	})

	def __init__(self, app, service_name):
		super().__init__(app, service_name)
		self.App = app
		self.Containers = {}


	async def finalize(self, app):
		for containers in self.Containers.values():
			await containers.finalize(app)


	@property
	def DefaultContainer(self):
		'''
		This is here to maintain backward compatibility.
		'''
		config_section = 'asab:zookeeper'

		try:
			return self.Containers[config_section]
		except KeyError:
			return self.build_container(config_section)


	def build_container(self, config_section_name):
		container = ZooKeeperContainer(self.App, config_section_name)
		self.Containers[container.ConfigSectionName] = container
		container.ZooKeeper.ProactorService.schedule(container._start, self.App)
		return container


	async def advertise(self, data, path, encoding="utf-8", container=None):
		if container is None:
			container = self.DefaultContainer
		if container is None:
			raise RuntimeError("The container must be specified.")
		return await container.advertise(data, path, encoding)


	async def get_children(self, container=None):
		if container is None:
			container = self.DefaultContainer
		if container is None:
			raise RuntimeError("The container must be specified.")
		return await container.get_children()

	async def get_data(self, child, encoding="utf-8", container=None):
		if container is None:
			container = self.DefaultContainer
		if container is None:
			raise RuntimeError("The container must be specified.")
		return await container.get_data(child, encoding)

	async def get_raw_data(self, child, container=None):
		if container is None:
			container = self.DefaultContainer
		if container is None:
			raise RuntimeError("The container must be specified.")
		return await container.get_raw_data(child)

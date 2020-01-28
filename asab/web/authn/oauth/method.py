import abc

from ....config import ConfigObject


class ABCOAuthMethod(abc.ABC, ConfigObject):

	# Configuration for KeyCloak
	# "token_url": "http://localhost:8080/auth/realms/teskalabs/protocol/openid-connect/token",
	# "userinfo_url": "http://localhost:8080/auth/realms/teskalabs/protocol/openid-connect/userinfo",

	# Configuration for SeaCat Auth
	# "token_url": "http://localhost:8080/oidc/token",
	# "userinfo_url": "http://localhost:8080/oidc/userinfo",

	ConfigDefaults = {
		#TODO: Is "asab-oauth" really needed?
		"oauth_server_id": "asab-oauth",

		# URL of "Access Token Request" endpoint, see https://tools.ietf.org/html/rfc6749#section-4.1.3
		"token_url": "http://localhost:8080/auth/realms/teskalabs/protocol/openid-connect/token",  

		# URL of "UserInfo Request" endpoint, see https://connect2id.com/products/server/docs/api/userinfo
		"userinfo_url": "http://localhost:8080/auth/realms/teskalabs/protocol/openid-connect/userinfo", 

		# URL of "Revocation Request" endpoint, see https://tools.ietf.org/html/rfc7009#page-4
		"invalidate_url": "",  

		# Refreshes access token, see https://auth0.com/docs/tokens/refresh-token/current#use-a-refresh-token
		"refresh_url": "",
		
		"client_id": "",  # Client ID of the current application, see https://tools.ietf.org/html/rfc6749#section-4.1.1
		"client_secret": "",  # Client secret of the current application, see https://tools.ietf.org/html/rfc6749#section-4.1.1
		"oauth_server_public_key": "",  # To decode token from token id: https://www.oauth.com/oauth2-servers/access-tokens/self-encoded-access-tokens/
	}

	def __init__(self, config_section_name=None, config=None):
		config_section_name = config_section_name if config_section_name is not None else self.__class__.__name__
		super().__init__(config_section_name=config_section_name, config=config)

	@abc.abstractmethod
	def extract_identity(self, oauth_user_info):
		pass


class GitHubOAuthMethod(ABCOAuthMethod):

	def __init__(self, config_section_name=None):
		super().__init__(config_section_name, {
			"oauth_server_id": "github.com",
			"token_url": "https://github.com/login/oauth/access_token",
			"userinfo_url": "https://api.github.com/user",
		})

	def extract_identity(self, oauth_user_info):
		return oauth_user_info["email"]


class OpenIDConnectMethod(ABCOAuthMethod):

	def extract_identity(self, oauth_user_info):
		return str(oauth_user_info["sub"])

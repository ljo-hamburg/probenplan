from urllib.parse import urljoin

from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session

from . import config


class MSGraphSession(OAuth2Session):
    def __init__(
        self,
        api_version: str = "v1.0",
        tenant: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        *args,
        **kwargs,
    ):
        self.api_version = api_version
        self.tenant = tenant
        self.client_secret = client_secret
        super().__init__(
            client=BackendApplicationClient(client_id=client_id), *args, **kwargs
        )

    def fetch_token(self, scope=None, **kwargs):
        if not scope:
            scope = ".default"
        return super().fetch_token(
            f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token",
            scope=scope,
            client_secret=self.client_secret,
        )

    def request(self, method, url, *args, **kwargs):
        if not url.startswith("https://"):
            url = urljoin(f"https://graph.microsoft.com/{self.api_version}/", url)
        try:
            return super().request(method, url, *args, **kwargs)
        except TokenExpiredError:
            self.fetch_token()
            return super().request(method, url, *args, **kwargs)

    def get_list(self, url, **kwargs):
        page = self.get(url, **kwargs).json()
        while True:
            for value in page["value"]:
                yield value
            next_link = page.get("@odata.nextLink", None)
            if next_link is None:
                break
            page = self.get(next_link).json()


session = MSGraphSession(
    tenant=config.tenant,
    client_id=config.client_id,
    client_secret=config.client_secret,
)

session.fetch_token()

# SYS
import json

# Google
from google_auth_oauthlib.flow import Flow

# setup google authen
client_secrets_file = "config/client_secrets.json"
ClientDataFile = open(client_secrets_file)
ClientData = json.load(ClientDataFile)

GOOGLE_CLIENT_ID = ClientData['web']['client_id']
redirect_uri = ClientData['web']['redirect_uris'][0]
secret_key = ClientData['web']['client_secret']

ClientDataFile.close()

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=redirect_uri
)
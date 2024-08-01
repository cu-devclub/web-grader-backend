
# web-grader-backend

in config folder

make .env file

    JWT_SECRET_KEY= (string)
    PORT= (number)
    HOST= (0.0.0.0)
    dev= (boolean)
    DBHOST= (url)
    DBUSER= (string)
    DBPASS= (string)
    DBNAME= (string)
    DOMAIN= (url with prefix)
    PUBKEY= (string with "")
    PRIKEY= (string with "")

and client_secrets.json (Generate from google api)

    {
        "web": {
            "client_id": "",
            "project_id": "",
            "auth_uri": "",
            "token_uri": "",
            "auth_provider_x509_cert_url": "",
            "client_secret": "",
            "redirect_uris": [""]
        }
    }

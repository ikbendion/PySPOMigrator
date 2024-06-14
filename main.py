import sys
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import msal
import requests
import json
from OpenSSL import crypto
import os
# Configuration
client_id = 'ee62634a-259'
tenant_id = ''
client_secret = 'mA'
authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["https://ikbendion.sharepoint.com/.default"]
# Path to your certificate file
certificate_path = 'MyCompanyName.pfx'
certificate_password = 'h23'

def get_access_token():
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential={
            "thumbprint": get_certificate_thumbprint(certificate_path, certificate_password),
            "private_key": get_certificate_private_key(certificate_path, certificate_password)
        }
    )

    result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        print("Error acquiring token: ", result.get("error_description"))
        sys.exit(1)

def get_certificate_thumbprint(cert_path, cert_password):
    with open(cert_path, 'rb') as cert_file:
        cert_data = cert_file.read()
    pfx = crypto.load_pkcs12(cert_data, cert_password)
    cert = pfx.get_certificate()
    return cert.digest('sha1').decode('utf-8').replace(':', '')

def get_certificate_private_key(cert_path, cert_password):
    with open(cert_path, 'rb') as cert_file:
        cert_data = cert_file.read()
    pfx = crypto.load_pkcs12(cert_data, cert_password)
    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())
    return private_key.decode('utf-8')

def create_copy_job(source_url, destination_url, access_token):
    url = "https://ikbendion.sharepoint.com/sites/ExterneBestanden/_api/site/CreateCopyJobs"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json;odata=verbose",
        "Content-Type": "application/json"
    }
    body = {
        "exportObjectUris": [source_url],
        "destinationUri": destination_url,
        "options": {
            "IgnoreVersionHistory": True,
            "IsMoveMode": True
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        print("Copy job created successfully.")
        print(response.json())
    else:
        print(f"Failed to create copy job. Status code: {response.status_code}")
        print(response.text)

def main():
    access_token = get_access_token()
    print("Access token acquired.")
    print(access_token)
    create_copy_job(
        source_url='https://ikbendion.sharepoint.com/sites/ExterneBestanden/Shared%20Documents/Folder2',
        destination_url='https://ikbendion.sharepoint.com/sites/Bestanden/Shared%20Documents',
        access_token=access_token
    )

if __name__ == "__main__":
    main()

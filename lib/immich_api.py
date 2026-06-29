#!/usr/bin/env python3

import requests
import logging
import sys
import datetime
from lib.models import Album, ItemAsset

class Immich_API():
    def __init__(self, RAW_SERVER_URL, APIKey):
        self.url    = RAW_SERVER_URL
        self.APIKey = APIKey

    #---------------------------------------------------------
    @staticmethod
    def _user_agent():
        try:
            import xbmc
            return xbmc.getUserAgent()
        except ModuleNotFoundError:
            return "Immich-API 0.1"
        
    #---------------------------------------------------------
    def _api_call(self, action, path, payload=None):
        url = f"{self.url}/api/{path}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.APIKey,
            "User-agent": self._user_agent(),
            }

        resp = requests.request(action, url, headers=headers, json=payload)

        if resp.status_code == 401:
            return false

        elif resp.status_code != 200:
            return false
            
        response = resp.json()
        return response

    #---------------------------------------------------------
    def get_version(self):
        return self._api_call("GET", "server/version")

    #---------------------------------------------------------
    def list_albums(self):
        resp = self._api_call("GET", "albums")
        return [Album.from_api_response(d) for d in resp ]
        
    #---------------------------------------------------------
    def getThumbUrl(self, id):
        return f"{self.url}/api/assets/{id}/thumbnail|x-api-key={self.APIKey}"    

    def getAssetUrl(self, id):
        return f"{self.url}/api/assets/{id}/original|x-api-key={self.APIKey}"
    #---------------------------------------------------------
    def get_album(self, id):
        resp = self._api_call("GET", f"albums/{id}")
        
        resp["assets"] = [ItemAsset.from_api_response(d) for d in resp["assets"] ]
        return resp
    
# ======================================================================================
# ======================================================================================
if __name__ == '__main__':


    IMMICH = Immich_API(
        "https://********",
        "********")

#    print(IMMICH.get_version())  
#    print(IMMICH.list_albums())

#    print(IMMICH.get_album('lkjhj7'))

# ======================================================================================
# ======================================================================================
else:
    import xbmcplugin
    HANDLE = int(sys.argv[1])

    RAW_SERVER_URL = xbmcplugin.getSetting(HANDLE, "immich_url")
    API_KEY = xbmcplugin.getSetting(HANDLE, "api_key")

    IMMICH = Immich_API(RAW_SERVER_URL,API_KEY)
    

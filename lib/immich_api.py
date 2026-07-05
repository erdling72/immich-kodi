#!/usr/bin/env python3

import requests
import logging
import sys
import datetime
from models import Album, ItemAsset

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
   
        resp = self._api_call("POST", "search/metadata", {
            "albumIds": [id],
            "visibility": "timeline",
            "withExif": True
            })
            
        data = {"assets": [ItemAsset.from_api_response(d) for d in resp["assets"]["items"]]}
        return data
    
# ======================================================================================
# ======================================================================================
if __name__ == '__main__':


    IMMICH = Immich_API(
        "https://immich.siedler.xyz",
        "e1fDGydhXQTtaya3vCE0JUzn3KcGD1T7kzVCbGY")

    print(IMMICH.get_version())  
#    print(IMMICH.list_albums()[0])

    print(IMMICH.get_album('d8bf768b-5096-4cfe-94a3-964a933bd5d2')["assets"][3].exifInfo.to_kodi_info())

# ======================================================================================
# ======================================================================================
else:
    import xbmcplugin
    HANDLE = int(sys.argv[1])

    RAW_SERVER_URL = xbmcplugin.getSetting(HANDLE, "immich_url")
    API_KEY = xbmcplugin.getSetting(HANDLE, "api_key")

    IMMICH = Immich_API(RAW_SERVER_URL,API_KEY)
    

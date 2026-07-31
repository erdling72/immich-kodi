#!/usr/bin/env python3

import xbmc
#import requests
import http.client
from urllib.parse import urlparse
import json
import logging
import sys
from lib.models import Album, ItemAsset, TimelineBucket

class Immich_API():
    def __init__(self, RAW_SERVER_URL, APIKey):

        xbmc.log("Immich_API CTOR: " + RAW_SERVER_URL, xbmc.LOGINFO)

        self.url    = RAW_SERVER_URL
        self.url_parsed = urlparse(RAW_SERVER_URL)
        self.APIKey = APIKey
        self.global_filter = {}

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

#        xbmc.log("START", xbmc.LOGINFO)

        host = self.url_parsed.hostname
        port = self.url_parsed.port

        conn = (
            http.client.HTTPSConnection(host, port)
            if self.url.startswith("https")
            else http.client.HTTPConnection(host, port)
        )

#        xbmc.log(str(conn.__dict__), xbmc.LOGINFO)
#        xbmc.log("END", xbmc.LOGINFO)

        try:
            #api_path = f"{self.url}/api/{path}"
            api_path = f"/api/{path}"

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": self.APIKey,
                "User-Agent": self._user_agent(),
            }

            body = json.dumps(payload) if payload is not None else None

            conn.request(action, api_path, body=body, headers=headers)
            resp = conn.getresponse()

            status = resp.status
            text = resp.read().decode("utf-8")

            if status == 403:
                print(text)
                raise PermissionError
            elif status == 401:
                print(text)
                raise ConnectionError
            elif status != 200:
                print(status, text)
                raise ConnectionError

            return json.loads(text) if text else None

        except Exception as e:
            xbmc.log("Fehler", xbmc.LOGINFO)
            xbmc.log(str(e.__dict__), xbmc.LOGINFO)
            raise

        finally:
            conn.close()

    #---------------------------------------------------------
    def get_version(self):
        return self._api_call("GET", "server/version")

    #---------------------------------------------------------
    def getAllAlbums(self):
        resp = self._api_call("GET", "albums")
        return [Album.from_api_response(d) for d in resp ]
        
    #---------------------------------------------------------
    def getTimeBuckets(self):
        resp = self._api_call("GET", "timeline/buckets")
        return [TimelineBucket.from_api_response(d) for d in resp ]

    #---------------------------------------------------------
    def getThumbUrl(self, uuid):
        return self.getAssetUrl(uuid, size="thumbnail")

    #---------------------------------------------------------
    def getAssetUrl(self, uuid, size="original"):
        if size=="original":
            return f"{self.url}/api/assets/{uuid}/original|x-api-key={self.APIKey}"
            
        elif size in ["original", "fullsize", "preview", "thumbnail"]:
            return f"{self.url}/api/assets/{uuid}/thumbnail?size={size}|x-api-key={self.APIKey}"

        elif size == "video": # Transcoded video
            return f"{self.url}/api/assets/{uuid}/video/playback|x-api-key={self.APIKey}"
        else:
            raise ValueError
    #---------------------------------------------------------
    def get_album(self, id):
   
        resp = self._api_call("POST", "search/metadata", {
            "albumIds": [id],
            "visibility": "timeline",
            "withExif": True
            })
            
        data = {"assets": [ItemAsset.from_api_response(d) for d in resp["assets"]["items"]]}
        return data

    #---------------------------------------------------------
    def getTimeBucket(self, startdate, enddate):
        
        resp = self._api_call("POST", "search/metadata", {
            "visibility": "timeline",
            "withExif": True,
            "takenAfter": startdate.isoformat(), 
            "takenBefore": enddate.isoformat()
            })
        
        data = {"assets": [ItemAsset.from_api_response(d) for d in resp["assets"]["items"]]}
        return data

    #---------------------------------------------------------
    def get_random_Asset(self, filter={"size": 1}):    
        # Just get one random picture

        d = self.global_filter.copy()
        d.update(filter)

        response = self._api_call("POST", "search/random", d)
        return response
        
    #---------------------------------------------------------
    def getAssetInfo(self, assetId):
	    return self._api_call("GET", f"assets/{assetId}")

    #---------------------------------------------------------
    def getParrentAlbums(self, assetId):
	    response = self._api_call("GET", f"albums?assetId={assetId}")
	    
	    blacklist = ['Bilderrahmen']
	    	    
	    data = [x for x in response if x['albumName'] not in blacklist]
	    return data
	    
            
# ======================================================================================
# ======================================================================================
    

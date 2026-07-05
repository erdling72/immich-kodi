#!/usr/bin/env python3

import xbmcgui
import xbmcplugin
import sys
HANDLE = int(sys.argv[1])

RAW_SERVER_URL = xbmcplugin.getSetting(HANDLE, "immich_url")
API_KEY = xbmcplugin.getSetting(HANDLE, "api_key")

from lib.immich_api import Immich_API

IMMICH = Immich_API(RAW_SERVER_URL,API_KEY)


#--------------------------------------------------------------------
def KodiContent(HANDLE, assets, t="timeline"):

    items = []
    
    for asset in assets:
        item = xbmcgui.ListItem(asset.originalFileName)

        item.setArt({"thumb": IMMICH.getThumbUrl(asset.id)})
        item.setProperty("MimeType", asset.originalMimeType)
        item.setDateTime(asset.fileCreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

        if asset.exifInfo.rating:
            item.setRating('immich', asset.exifInfo.rating)

        if asset.exifInfo.description and asset.type==  'VIDEO':
            item.setInfo(
                type='video', 
                infoLabels={
                    'title': asset.originalFileName,
                    'plot':  asset.exifInfo.description
                    }
	        )

        elif asset.exifInfo.description and asset.type=='IMAGE':
            item.setInfo(
                type='pictures', 
                infoLabels={
                    'title': asset.originalFileName,
                    **asset.exifInfo.to_kodi_info(),
                    }
	        )
	        
        items.append((
            IMMICH.getAssetUrl(asset.id), 
            item,
            False))


    xbmcplugin.setContent(HANDLE, "images")
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    if t == "album":
        xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

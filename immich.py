#!/usr/bin/env python3

import xbmcgui
import xbmcplugin
import sys
import xbmcaddon

HANDLE = int(sys.argv[1])

addon = xbmcaddon.Addon()

from lib.immich_api import Immich_API


IMMICH = Immich_API(
	addon.getSettingString("immich_url"),
	addon.getSettingString("api_key")
	)
#--------------------------------------------------------------------
def KodiContent(HANDLE, assets, t="timeline"):

    items = []
    
    for asset in assets:
        item = xbmcgui.ListItem(asset.originalFileName)

        item.setArt({"thumb": IMMICH.getThumbUrl(asset.id)})
        item.setProperty("MimeType", asset.originalMimeType)
        item.setDateTime(asset.fileCreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

        # item.setLabel(asset.exifInfo.description) # Titel überschreben
        item.setLabel2(asset.exifInfo.description)

	        
        if asset.exifInfo.description and asset.type==  'VIDEO':
        
            tag = item.getVideoInfoTag()
            tag.setTitle(asset.originalFileName)
            
            if asset.exifInfo.description:
                tag.setPlot(asset.exifInfo.description)

            if asset.exifInfo.rating:
                tag.setUserRating(asset.exifInfo.rating)
        
#            item.setInfo(
#                type='video', 
#                infoLabels={
#                    'title': asset.originalFileName,
#                    'plot':  asset.exifInfo.description
#                    }
#	        )

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
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_USER_RATING)
    if t == "album":
        xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

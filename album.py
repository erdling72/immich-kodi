
import sys
import xbmcgui
import xbmcplugin

from lib.immich_api import IMMICH

HANDLE = int(sys.argv[1])


from utils import (
    get_url
)

def list_albums():
    albums = IMMICH.list_albums()
    
    items = []
    for album in albums:
        if album.assetCount == 0:   # skip empty albums
            continue
            
        item = xbmcgui.ListItem(album.albumName)
        
        if album.albumThumbnailAssetId:
            item.setArt({"thumb": IMMICH.getThumbUrl(album.albumThumbnailAssetId)})

        if album.startDate:
            item.setDateTime(album.startDate.strftime("%Y-%m-%dT%H:%M:%SZ"))

        if album.description: 
            item.setInfo(
                type='video', 
                infoLabels={
                    'title': album.albumName,
                    'plot':  album.description
                    }
	        )
            
        items.append((
            get_url(action="album", id=album.id), 
            item,
            True))
            

    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)

    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))      
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
     
     
#--------------------------------------       
def album(id):
    xbmcplugin.setContent(HANDLE, "images")

    album = IMMICH.get_album(id)
    
    items = []
    for asset in album["assets"]:
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
                    **{f"exif:{k}": str(v) for k, v in asset.exifInfo},
                    }
	        )
	        
        items.append((
            IMMICH.getAssetUrl(asset.id), 
            item,
            False))


    xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_DATE)
     
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
    

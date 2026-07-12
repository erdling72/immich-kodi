import socket

import sys
import datetime
from urllib.parse import parse_qsl

import xbmcaddon
import xbmcgui
import xbmcplugin

from album import list_albums, album
from timeline import timeline, time
from utils import get_url, set_locale

from immich import IMMICH

DEBUG = False
if DEBUG:
    import debug

URL = sys.argv[0]
HANDLE = int(sys.argv[1])
addon = xbmcaddon.Addon()


if __name__ == '__main__':
    set_locale()
    params = dict(parse_qsl(sys.argv[2][1:]))


    if not IMMICH.url:
        addon.openSettings()

    try:
        IMMICH.get_version()
    except Exception as e:
        raise Exception('Can\'t connect to Immich')

    if not params.get('action'):
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action='timeline'),
                                    xbmcgui.ListItem(addon.getLocalizedString(30002)), True)

        xbmcplugin.addDirectoryItem(HANDLE, get_url(action='albums'),
                                    xbmcgui.ListItem(addon.getLocalizedString(30003)), True)

        xbmcplugin.endOfDirectory(HANDLE)
        
        
    elif params['action'] == 'settings':
        addon.openSettings()

    elif params['action'] == 'timeline':
        timeline('video' in params)
    elif params['action'] == 'albums':
        list_albums()
    elif params['action'] == 'album':
        album(params['id'])
    elif params['action'] == 'time':
        time(params['id'], 'video' in params)

if DEBUG:
    import pydevd
    pydevd.stoptrace()


from os import getlogin,  environ
from enum import Enum
import sys

class Platform(Enum):
    UNKNOWN = 1
    LINUX = 2
    WINDOWS = 3

PLATFORM = Platform.UNKNOWN
APOD_DIRECTORY = None
wallManager = None

if sys.platform.startswith('linux'):
    PLATFORM = Platform.LINUX
elif sys.platform.startswith('win'):
    PLATFORM = Platform.WINDOWS
else:
    raise Exception("Unknown Operating System")

if PLATFORM == Platform.LINUX:
    username = getlogin()
    APOD_DIRECTORY = f'/var/home/{username}/Pictures/apod/'
elif PLATFORM == Platform.WINDOWS:
    username = environ["USERNAME"]
    APOD_DIRECTORY = rf'C:\Users\{username}\Pictures\apod'

if PLATFORM == Platform.LINUX:
    from wallpapermanager_kde import WallpaperManagerKde
    wallManager = WallpaperManagerKde()
elif PLATFORM == Platform.WINDOWS:
    from wallpapermanager_win import WallpaperManagerWin
    wallMager = WallpaperManagerWin()
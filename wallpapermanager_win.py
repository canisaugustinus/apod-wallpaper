from ctypes import HRESULT, POINTER, pointer
from ctypes.wintypes import LPCWSTR, UINT, LPWSTR, RECT
import comtypes


class IDesktopWallpaper(comtypes.IUnknown):
    """
    Credit to Xdynix on stackoverflow for this class: https://stackoverflow.com/a/74203777
    Ref: https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-idesktopwallpaper
    """

    # "B92B56A9-8B55-4E14-9A89-0199BBB6F93B" obtained by searching "IDesktopWallpaper" in "\HKEY_CLASSES_ROOT\Interface"
    _iid_ = comtypes.GUID('{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}')

    @classmethod
    def coCreateInstance(cls):
        # "C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD" obtained by searching "Desktop Wallpaper" in "\HKEY_CLASSES_ROOT\CLSID"
        class_id = comtypes.GUID('{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}')
        return comtypes.CoCreateInstance(class_id, interface=cls)

    _methods_ = [
        comtypes.COMMETHOD(
            [], HRESULT, 'SetWallpaper',
            (['in'], LPCWSTR, 'monitorID'),
            (['in'], LPCWSTR, 'wallpaper'),
        ),
        comtypes.COMMETHOD(
            [], HRESULT, 'GetWallpaper',
            (['in'], LPCWSTR, 'monitorID'),
            (['out'], POINTER(LPWSTR), 'wallpaper'),
        ),
        comtypes.COMMETHOD(
            [], HRESULT, 'GetMonitorDevicePathAt',
            (['in'], UINT, 'monitorIndex'),
            (['out'], POINTER(LPWSTR), 'monitorID'),
        ),
        comtypes.COMMETHOD(
            [], HRESULT, 'GetMonitorDevicePathCount',
            (['out'], POINTER(UINT), 'count'),
        ),
        comtypes.COMMETHOD(
            [], HRESULT, 'GetMonitorRECT',
            (['in'], LPWSTR, 'monitorID'),
            (['out'], POINTER(RECT), 'displayRect'),
        ),
    ]

    def setWallpaper(self, monitorId: str, wallpaper: str):
        self.__com_SetWallpaper(LPCWSTR(monitorId), LPCWSTR(wallpaper))

    def getMonitorDevicePathAt(self, monitorIndex: int) -> str:
        monitorId = LPWSTR()
        self.__com_GetMonitorDevicePathAt(UINT(monitorIndex), pointer(monitorId))
        return monitorId.value

    def getMonitorDevicePathCount(self) -> int:
        count = UINT()
        self.__com_GetMonitorDevicePathCount(pointer(count))
        return count.value

    def getMonitorRECT(self, monitorID: str) -> RECT:
        displayRect = RECT()
        self.__com_GetMonitorRECT(LPCWSTR(monitorID), pointer(displayRect))
        return displayRect

    def findAllowedIDs(self) -> dict[str, RECT]:
        allowed_ids = {}
        count = self.getMonitorDevicePathCount()
        for i in range(count):
            monitorID = self.getMonitorDevicePathAt(i)
            try:
                displayRect = self.getMonitorRECT(monitorID)
                allowed_ids[monitorID] = displayRect
            except comtypes.COMError:
                pass
        return allowed_ids


class WallpaperManagerWin:
    def __init__(self):
        self._inst = IDesktopWallpaper.coCreateInstance()

        # monitor ID indexing is from left to right
        monitor_id_dict = self._inst.findAllowedIDs()
        monitor_id_lef_dict = {}
        for monitor_id in monitor_id_dict:
            display_rect = monitor_id_dict[monitor_id]
            monitor_id_lef_dict[monitor_id] = display_rect.left,
        self._monitor_id_list = sorted(monitor_id_lef_dict, key=monitor_id_lef_dict.get)

    def get_number_of_monitors(self) -> int:
        return len(self._monitor_id_list)

    def change_wallpaper(
            self,
            i: int,
            image_path: str):
        self._inst.setWallpaper(self._monitor_id_list[i], image_path)
from datetime import datetime
from apod_wallpaper import random_retry, MAX_ATTEMPTS
from wallpapermanager import IDesktopWallpaper


def main():
    # use the COM wallpaper manager
    desk_wall = IDesktopWallpaper.coCreateInstance()
    monitor_id_dict = desk_wall.findAllowedIDs()
    monitor_id_list = list(monitor_id_dict.keys())

    # random APODs for all monitors
    today = datetime.today()
    wallpaper_list = []
    for i_monitor in range(len(monitor_id_list)):
        image_random = random_retry(today)
        if image_random is not None:
            wallpaper_list.append(image_random)
        else:
            break

    # check if we have an image for all monitors
    if len(wallpaper_list) != len(monitor_id_list):
        raise Exception(f"Unable to find APODs for all monitors after {MAX_ATTEMPTS} attempts.")

    # assign wallpapers to each monitor
    for monitor_id, wallpaper in zip(monitor_id_list, wallpaper_list):
        desk_wall.setWallpaper(monitor_id, wallpaper)


if __name__ == '__main__':
    main()

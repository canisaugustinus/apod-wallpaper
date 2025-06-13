from datetime import datetime
from apod_wallpaper import random_retry, MAX_ATTEMPTS, wallManager


def main():
    # get the number of monitors to see how many wallpapers we need
    num_monitors = wallManager.get_number_of_monitors()

    # random APODs for all monitors
    today = datetime.today()
    wallpaper_list = []
    for i_monitor in range(num_monitors):
        image_random = random_retry(today)
        if image_random is not None:
            wallpaper_list.append(image_random)
        else:
            break

    # check if we have an image for all monitors
    if len(wallpaper_list) != num_monitors:
        raise Exception(f"Unable to find APODs for all monitors after {MAX_ATTEMPTS} attempts.")

    # assign wallpapers to each monitor
    for i, wallpaper in enumerate(wallpaper_list):
        wallManager.change_wallpaper(i, wallpaper)


if __name__ == '__main__':
    main()

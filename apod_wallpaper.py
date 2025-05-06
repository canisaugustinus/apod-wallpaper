from os import listdir, environ
from os.path import isfile, join
import pathlib
import json
import requests
from datetime import datetime, timedelta
import ctypes
from PIL import Image
import random
from typing import Optional
from wallpapermanager import IDesktopWallpaper
from ctypes.wintypes import RECT

MAX_ATTEMPTS = 10
MAIN_MONITOR_TOP_LEFT = {'top': 0, 'left': 0}  # https://learn.microsoft.com/en-us/windows/win32/api/windef/ns-windef-rect
USERNAME = environ["USERNAME"]
DIRECTORY = pathlib.Path(__file__).parent.resolve()
with open(join(DIRECTORY, 'apod_api_key.json'), 'r') as api_key_file:
    APOD_API_KEY = json.load(api_key_file)['APOD_API_KEY']
APOD_DIRECTORY = rf'C:\Users\{USERNAME}\Pictures\apod'
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
START_DATE = datetime(1995, 6, 16)  # first day of APOD


def pick_random_date(today: datetime) -> datetime:
    delta = today - START_DATE
    days = random.randint(0, delta.days)
    date = START_DATE + timedelta(days=days)
    return date


def random_retry(date: datetime) -> str | None:
    for i in range(MAX_ATTEMPTS):
        image_random, is_success = download_apod(pick_random_date(date))
        if image_random is not None:
            return image_random
    return None


def find_saved_image(date: datetime) -> Optional[str]:
    date_str = date.strftime("%Y-%m-%d")
    f_start = f'{date_str}.'
    files = [f for f in listdir(APOD_DIRECTORY) if isfile(join(APOD_DIRECTORY, f))]
    for f in files:
        if f.startswith(f_start):
            return join(APOD_DIRECTORY, f)
    return None


def download_apod(date: datetime) -> tuple[str, bool] | tuple[None, bool]:
    # do we already have date's APOD?
    file = find_saved_image(date)
    if file:
        return file, True

    img_url = None
    date_str = date.strftime("%Y-%m-%d")

    try:  # get the image through the API
        url = f'https://api.nasa.gov/planetary/apod?api_key={APOD_API_KEY}&date={date_str}'
        print(f'Checking the API: {url}')
        response = requests.get(url, timeout=5).json()
        print(f'Response: {response}')
        if 'media_type' in response and response['media_type'] == 'image':
            if 'hdurl' in response and response['hdurl'].lower().endswith(IMAGE_EXTENSIONS):
                img_url = response['hdurl']
            elif 'url' in response and response['url'].lower().endswith(IMAGE_EXTENSIONS):
                img_url = response['url']
    except requests.exceptions.ReadTimeout:  # sometimes the API is down, but the site is up
        url = f'https://apod.nasa.gov/apod/ap{date.strftime("%y%m%d")}.html'
        print(f'Checking the site: {url}')
        response = requests.get(url).content.decode()
        print(f'Response: {response}')
        if '<IMG SRC=' in response:
            hdurl, url = response.split('<IMG SRC=')[:2]
            hdurl, url = hdurl.split('"')[-2], url.split('"')[1]
            if hdurl.lower().endswith(IMAGE_EXTENSIONS):
                img_url = 'https://apod.nasa.gov/apod/' + hdurl
            elif url.lower().endswith(IMAGE_EXTENSIONS):
                img_url = 'https://apod.nasa.gov/apod/' + url

    # download the image and return the filepath
    if img_url is not None:
        try:
            print(f'Downloading the image from this URL: {img_url}.')
            image = requests.get(img_url)
            extension = img_url.split(".")[-1]
            image_path = join(APOD_DIRECTORY, date_str)
            image_path = f'{image_path}.{extension}'
            open(image_path, 'wb').write(image.content)
            return image_path, True
        except:
            print('Download failed.')
            return None, False

    print(f"{date_str}'s A\"P\"OD isn't an image.")
    return None, True


def set_wallpaper(file: str):
    print(f'Changing the wallpaper to {file}')
    # put the widest dimension along the horizontal
    im = Image.open(file)
    width, height = im.size
    if height > width:
        rotated = im.transpose(Image.ROTATE_270)
        ext = file.split(".")[-1]
        image_path = join(APOD_DIRECTORY, 'rotated')
        image_path = f'{image_path}.{ext}'
        rotated.save(image_path)
    else:
        image_path = file
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)


def main():
    # use the COM wallpaper manager
    desk_wall = IDesktopWallpaper.coCreateInstance()
    monitor_id_dict = desk_wall.findAllowedIDs()

    main_monitor_id = None
    for monitor_id in monitor_id_dict:
        display_rect = monitor_id_dict[monitor_id]
        if all((MAIN_MONITOR_TOP_LEFT['left'] == display_rect.left,
            MAIN_MONITOR_TOP_LEFT['top'] == display_rect.top)):
            main_monitor_id = monitor_id
    if main_monitor_id is None:
        raise Exception(f"Unable to find the main monitor. Is MAIN_MONITOR_TOP_LEFT={MAIN_MONITOR_TOP_LEFT} correct?")

    # move the main monitor to the 0th position
    monitor_id_list = list(monitor_id_dict.keys())
    print(monitor_id_list)
    monitor_id_list.remove(main_monitor_id)
    monitor_id_list.insert(0, main_monitor_id)
    print(monitor_id_list)

    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    wallpaper_list = []

    # try "tomorrow's" APOD in case it's already up due to timezone differences
    image_tomorrow, is_success = download_apod(tomorrow)
    if image_tomorrow is not None:
        wallpaper_list.append(image_tomorrow)
    elif is_success:
        # tomorrow's APOD isn't an image --- get a random APOD
        pass
    else:
        # otherwise, try today's APOD
        image_today, is_success = download_apod(today)
        if image_today is not None:
            wallpaper_list.append(image_today)

    # if tomorrow or today didn't work, get a random APOD
    if len(wallpaper_list) == 0:
        image_random = random_retry(today)
        if image_random is not None:
            wallpaper_list.append(image_random)

    # check if we have an image for our main monitor
    if len(wallpaper_list) == 0:
        raise Exception(f"Unable to find an APOD for the main monitor after {MAX_ATTEMPTS} attempts.")

    # random APODs for other monitors
    for i_monitor in range(len(monitor_id_list)-1):
        image_random = random_retry(today)
        if image_random is not None:
            wallpaper_list.append(image_random)
        else:
            break

    # check if we have an image for all other monitors
    if len(wallpaper_list) != len(monitor_id_list):
        raise Exception(f"Unable to find an APOD for the other monitors after {MAX_ATTEMPTS} attempts.")

    # assign wallpapers to each monitor
    for monitor_id, wallpaper in zip(monitor_id_list, wallpaper_list):
        desk_wall.setWallpaper(monitor_id, wallpaper)


if __name__ == '__main__':
    main()

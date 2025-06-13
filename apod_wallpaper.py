from os import listdir
from os.path import isfile, join
import pathlib
import json
import requests
from datetime import datetime, timedelta
import random
from typing import Optional
from os_platform import APOD_DIRECTORY, wallManager

MAX_ATTEMPTS = 10
DIRECTORY = pathlib.Path(__file__).parent.resolve()
with open(join(DIRECTORY, 'apod_api_key.json'), 'r') as api_key_file:
    APOD_API_KEY = json.load(api_key_file)['APOD_API_KEY']
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp')
START_DATE = datetime(1995, 6, 16)  # first day of APOD


def pick_random_date(today: datetime) -> datetime:
    delta = today - START_DATE
    days = random.randint(0, delta.days)
    date = START_DATE + timedelta(days=days)
    return date


def random_retry(date: datetime) -> str | None:
    for i in range(MAX_ATTEMPTS):
        image_random = download_apod(pick_random_date(date))[0]
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

    is_api_error = False
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
        elif 'code' in response and response['code'] >= 400:
            is_api_error = True
    except requests.exceptions.ReadTimeout:
        is_api_error = True

    if is_api_error: # sometimes the API is down, but the site is up
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

    if img_url is None:
        print(f"{date_str}'s A\"P\"OD isn't an image.")
        return None, True

    # download the image and return the filepath
    try:
        print(f'Downloading the image from this URL: {img_url}.')
        image = requests.get(img_url)
        extension = img_url.split(".")[-1]
        image_path = join(APOD_DIRECTORY, date_str)
        image_path = f'{image_path}.{extension}'
        open(image_path, 'wb').write(image.content)
        return image_path, True
    except Exception as e:
        print(f'Download failed with Exception {e}.')
        return None, False


def main():
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    wallpaper_list = []

    # try "tomorrow's" APOD in case it's already up due to timezone differences
    image_tomorrow, is_tomorrow_success = download_apod(tomorrow)
    if image_tomorrow is not None:
        wallpaper_list.append(image_tomorrow)
    elif is_tomorrow_success:
        pass # tomorrow's APOD isn't an image --- get a random APOD
    else:
        # otherwise, try today's APOD
        image_today = download_apod(today)[0]
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

    # get the number of monitors to see how many other wallpapers we need
    num_monitors = wallManager.get_number_of_monitors()

    # random APODs for other monitors
    for i_monitor in range(num_monitors-1):
        image_random = random_retry(today)
        if image_random is not None:
            wallpaper_list.append(image_random)
        else:
            break

    # check if we have an image for all other monitors
    if len(wallpaper_list) != num_monitors:
        raise Exception(f"Unable to find an APOD for the other monitors after {MAX_ATTEMPTS} attempts.")

    # assign the wallpapers to each monitor
    for i, wallpaper in enumerate(wallpaper_list):
        wallManager.change_wallpaper(i, wallpaper)


if __name__ == '__main__':
    main()

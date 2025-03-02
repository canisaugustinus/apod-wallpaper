Replace your wallpaper with NASA's [Astronomy Picture of the Day (APOD)](https://apod.nasa.gov/apod/astropix.html).

To run:
1. Clone this repository.
2. Install Python and use pip to get the packages referenced in this repository's *.py files.
3. Get a NASA API key from [https://api.nasa.gov/#signUp](https://api.nasa.gov/#signUp).
4. Following the example in `apod_api_key_example.json`, create a new file `apod_api_key.json` containing your API key.
5. In `apod_wallpaper.py`, edit the variable `MAIN_MONITOR_TOP_LEFT` with the `top` and `left` values of your main monitor. These are often both `0`, but you might require different values for a multi-monitor setup. `MAIN_MONITOR_TOP_LEFT` will be compared with [IDesktopWallpaper::GetMonitorRECT()](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-idesktopwallpaper-getmonitorrect).
6. Run `python apod_wallpaper.py` to change your main monitor's wallpaper to today's APOD. Any other monitors will be set to random APODs.
7. Run `python apod_wallpaper_random.py` to change all of your monitor's wallpapers to random APODs.

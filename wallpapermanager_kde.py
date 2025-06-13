import subprocess
import os

# https://powersnail.com/2023/set-plasma-wallpaper/

class WallpaperManagerKde:
    def __init__(self):
        pass

    @classmethod
    def get_number_of_monitors(cls):
        result = subprocess.run('/usr/bin/xrandr --listactivemonitors', check=True, shell=True, capture_output=True, text=True).stdout
        result = [x.strip() for x in result.split('\n')]
        return int(result[0].split(':')[1])

    @classmethod
    def change_wallpaper(
            cls,
            i: int,
            image_path: str):
        """
        Change the KDE Plasma wallpaper using qdbus.
        The monitor (0-indexed by from left to right) is assigned the wallpaper image_path.
        """
        script = f"""
            var desktopsList = desktops().filter(d => d.screen != -1);
            desktopsList = desktopsList.sort((a, b) => screenGeometry(a.screen).left - screenGeometry(b.screen).left);
            d = desktopsList[{i}];
            d.wallpaperPlugin = "org.kde.image";
            d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
            d.writeConfig("Image", "{image_path}");
        """
        command = [
            "qdbus",
            "org.kde.plasmashell",
            "/PlasmaShell",
            "org.kde.PlasmaShell.evaluateScript",
            script
        ]
        subprocess.run(command, check=True)

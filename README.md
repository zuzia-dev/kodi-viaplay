# Viaplay unofficial add-on for Kodi 18
This is a Kodi add-on that allows you to stream content from Viaplay in Kodi. This is a Kodi add-on that allows you to stream content from Viaplay in Kodi. Requires subscription. Add-on designed for versions: Polish, Swedish, Norwegian, Danish, Finnish, Dutch, Lithuanian, Estonian, English.

## Disclaimer ##
This add-on is unoffical and is not endorsed or supported by Viaplay in any way. Any trademarks used belong to their owning companies and organisations. Use at Your Own Risk.

## Prerequisites & Dependencies ##
 * A devices compatible with Kodi
 * System with Python 2.7 or later
 * InputStream Adaptive add-on
 * InputStream Helper add-on
 * Widevine CDM library
 * IPTV Manager for TV channels support (optional)

```diff
-> NOTICE: This plugin is compatible with Kodi 18 (Leia). 
-> But we highly recommend upgrading to Kodi 19 (Matrix). 
```

If you're installing straight from git, please make sure you've got the following modules installed:
 * script.module.requests - http://mirrors.kodi.tv/addons/leia/script.module.requests/
 * script.module.iso8601  - http://mirrors.kodi.tv/addons/leia/script.module.iso8601/
 * script.module.inputstreamhelper - http://mirrors.kodi.tv/addons/leia/script.module.inputstreamhelper/
 * script.module.routing  - http://mirrors.kodi.tv/addons/leia/script.module.routing/
 
## Installation & Updates ##
Install add-on manually - updates should always be installed manually:
### ->   - [plugin kodi-viaplay (only Kodi 18)](https://github.com/zuzia-dev/kodi-viaplay/archive/refs/heads/K18.zip).

## DRM protected streams ##
Viaplay's content is DRM protected and requires the proprietary decryption module Widevine CDM for playback. You will be prompted to install this if you're attempting to play a stream without the binary installed.
 
Most Android devices have built-in support for Widevine DRM and doesn't require any additional binaries. You can see if your Android device supports Widevine DRM by using the [DRM Info](https://play.google.com/store/apps/details?id=com.androidfung.drminfo) app available in Play Store.

## Support ##
Please report any issues or bug reports on the [zuzia-dev GitHub Issues](https://github.com/zuzia-dev/kodi-viaplay/issues) or
[emilsvennesson GitHub Issues](https://github.com/emilsvennesson/kodi-viaplay/issues) pages. Remember to include a full, non-cut off Kodi debug log. See the [Kodi wiki page](http://kodi.wiki/view/Log_file/Advanced) for more detailed instructions on how to obtain the log file.

Additional support/discussion about the add-on can be found in the [Viaplay add-on thread](https://forum.kodi.tv/showthread.php?tid=286387).

If you are a person skilled in Python development, you can join as a developer and provide help to fix errors and make new features.

## License ##
This add-on is licensed under the **GNU GENERAL PUBLIC LICENSE Version 3**. Please see the [LICENSE.txt](LICENSE.txt) file for details.

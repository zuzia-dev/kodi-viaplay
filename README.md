# Viaplay unofficial add-on for Kodi
This is a Kodi add-on that allows you to stream content from Viaplay in Kodi.

## Disclaimer ##
This add-on is unoffical and is not endorsed or supported by Viaplay in any way. Any trademarks used belong to their owning companies and organisations.

## Prerequisites & Dependencies ##
 * A devices compatible with Kodi
 * Suggested Kodi 18 or above
 * InputStream Adaptive add-on
 * InputStream Helper add-on
 * Widevine CDM library

If you're installing straight from git, please make sure you've got the following modules installed:
 * script.module.inputstreamhelper
 * script.module.requests
 * script.module.iso8601
 * script.module.routing
 
## Installation & Updates ##
Install add-on via repository - provide automatic installation of updates:
Download repository: [repository.heppen](https://github.com/heppen-dev/repository.heppen/raw/main/repository.heppen.zip)

Or install it via Kodi file-manager:
 - add source: https://heppen-dev.github.io/ or https://zips.ovh/heppen

Install add-on manually - updates should always be installed manually:
- [plugin kodi-viaplay](https://github.com/zuzia-dev/kodi-viaplay/archive/refs/heads/master.zip)

## DRM protected streams ##
Viaplay's content is DRM protected and requires the proprietary decryption module Widevine CDM for playback. You will be prompted to install this if you're attempting to play a stream without the binary installed.
 
Most Android devices have built-in support for Widevine DRM and doesn't require any additional binaries. You can see if your Android device supports Widevine DRM by using the [DRM Info](https://play.google.com/store/apps/details?id=com.androidfung.drminfo) app available in Play Store.

## Support ##
Please report any issues or bug reports on the [zuzia-dev GitHub Issues](https://github.com/zuzia-dev/kodi-viaplay/issues) or
[emilsvennesso GitHub Issues](https://github.com/emilsvennesson/kodi-viaplay/issues) pages. Remember to include a full, non-cut off Kodi debug log. See the [Kodi wiki page](http://kodi.wiki/view/Log_file/Advanced) for more detailed instructions on how to obtain the log file.

Additional support/discussion about the add-on can be found in the [Viaplay add-on thread](https://forum.kodi.tv/showthread.php?tid=286387).
And online forum in polish [forum.kodiwpigulce.pl](https://forum.kodiwpigulce.pl/showthread.php?tid=3804).

If you are a person skilled in Python development, you can join as a developer and provide help to fix errors and make new features.

## License ##
This add-on is licensed under the **GNU GENERAL PUBLIC LICENSE Version 3**. Please see the [LICENSE.txt](LICENSE.txt) file for details.

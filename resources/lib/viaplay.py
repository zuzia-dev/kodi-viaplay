﻿# -*- coding: utf-8 -*-
"""
A Kodi-agnostic library for Viaplay
"""
import sys
import os

if sys.version_info[0] > 2:
    import http.cookiejar as cookielib
    import html
else:
    import cookielib
    import HTMLParser

import calendar
import re
import json
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta

import iso8601
import requests
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon

class Viaplay(object):

    class ViaplayError(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __init__(self, settings_folder, country, debug=False):
        addon = self.get_addon()
        self.debug = debug
        self.country = country
        self.tld = self.get_tld_for(country)
        self.settings_folder = settings_folder
        if sys.version_info[0] > 2:
            self.addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
            self.addon_profile = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
        else:
            self.addon_path = xbmc.translatePath(addon.getAddonInfo('path'))
            self.addon_profile = xbmc.translatePath(addon.getAddonInfo('profile'))
        self.cookie_jar = cookielib.LWPCookieJar(os.path.join(self.settings_folder, 'cookie_file'))
        #self.replace_cookies = self.replace_cookies() ### workaround to switch country sites
        self.tempdir = os.path.join(settings_folder, 'tmp')
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)
        self.deviceid_file = os.path.join(settings_folder, 'deviceId')
        self.http_session = requests.Session()
        self.device_key = 'xdk-%s' % self.country
        self.base_url = 'https://content.viaplay.{0}/{1}'.format(self.tld, self.device_key)
        self.login_api = 'https://login.viaplay.%s/api' % self.tld
        self.profile_url = 'https://viaplay.mtg-api.com'
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except IOError:
            pass
        self.http_session.cookies = self.cookie_jar

    def get_addon(self):
        """Returns a fresh addon instance."""
        return Addon()

    def get_setting(self, setting_id):
        addon = self.get_addon()
        setting = addon.getSetting(setting_id)
        if setting == 'true':
            return True
        elif setting == 'false':
            return False
        else:
            return setting

    def get_country_code(self):
        country_id = self.get_setting('site')
        if country_id == '0':
            country_code = 'se'
        elif country_id == '1':
            country_code = 'dk'
        elif country_id == '2':
            country_code = 'no'
        elif country_id == '3':
            country_code = 'fi'
        elif country_id == '4':
            country_code = 'pl'
        elif country_id == '5':
            country_code = 'lt'
        elif country_id == '6':
            country_code = 'nl'
        elif country_id == '7':
            country_code = 'ee'
        elif country_id == '8':
            country_code = 'gb'

        return country_code
    
    def get_tld(self):
        return self.get_tld_for(self.get_country_code())
    
    def get_tld_for(self, country_code):
        if country_code == "nl" or country_code == "gb":
            return "com"
        return country_code

    def replace_cookies(self):
        cookie_file = os.path.join(self.addon_profile, 'cookie_file')
        f = open(cookie_file, 'r')
        cookies = f.read()

        tld = self.get_tld()

        pattern = re.compile('viaplay.(\w{2})', re.IGNORECASE)
        n_tld = pattern.search(cookies).group(1)

        if n_tld != tld:
            cookies = re.sub('viaplay.{cc}'.format(cc=n_tld), 'viaplay.{cc}'.format(cc=tld), cookies)
            w = open(cookie_file, 'w')
            w.write(cookies)
            w.close()

    def log(self, string):
        if self.debug:
            try:
                print('[Viaplay]: %s' % string)
            except UnicodeEncodeError:
                # we can't anticipate everything in unicode they might throw at
                # us, but we can handle a simple BOM
                bom = unicode(codecs.BOM_UTF8, 'utf8')
                print('[Viaplay]: %s' % string.replace(bom, ''))
            except:
                pass

    def parse_url(self, url):
        """Sometimes, Viaplay adds some weird templated stuff to the URL
        we need to get rid of. Example: https://content.viaplay.se/androiddash-se/serier{?dtg}"""
        template = r'\{.+?\}'
        result = re.search(template, str(url))
        if result:
            self.log('Unparsed URL: {0}'.format(url))
            url = re.sub(template, '', url)

        return url

    def make_request(self, url, method, params=None, payload=None, headers=None):
        """Make an HTTP request. Return the response."""
        if params == None:
            params = {}

        pid = self.get_setting('profile_id')
        if pid:
            params['profileId'] = pid

        try:
            return self._make_request(url, method, params=params, payload=payload, headers=headers)
        except self.ViaplayError:
            self.validate_session()
            return self._make_request(url, method, params=params, payload=payload, headers=headers)

    def _make_request(self, url, method, params=None, payload=None, headers=None):
        """Helper. Make an HTTP request. Return the response."""
        url = self.parse_url(url)
        self.log('Request URL: %s' % url)
        self.log('Method: %s' % method)
        if params:
            self.log('Params: %s' % params)
        if payload:
            self.log('Payload: %s' % payload)
        if headers:
            self.log('Headers: %s' % headers)

        if method == 'get':
            req = self.http_session.get(url, params=params, headers=headers)
        elif method == 'put':
            req = self.http_session.put(url, params=params, data=payload, headers=headers)
        else:  # post
            req = self.http_session.post(url, params=params, data=payload, headers=headers)
        self.log('Response code: %s' % req.status_code)
        self.log('Response: %s' % req.content)
        self.cookie_jar.save(ignore_discard=True, ignore_expires=False)

        return self.parse_response(req.content)

    def parse_response(self, response):
        """Try to load JSON data into dict and raise potential errors."""
        try:
            response = json.loads(response, object_pairs_hook=OrderedDict)  # keep the key order
            if 'success' in response and not response['success']:  # raise ViaplayError when 'success' is False
                raise self.ViaplayError(response['name'])

        except ValueError:  # if response is not json
            pass

        return response

    def get_activation_data(self):
        """Get activation data (reg code etc) needed to authorize the device."""
        url = self.login_api + '/device/code'
        params = {
            'deviceKey': self.device_key,
            'deviceId': self.get_deviceid()
        }

        return self.make_request(url=url, method='get', params=params)

    def authorize_device(self, activation_data):
        """Try to register the device. This will set the session cookies."""
        url = self.login_api + '/device/authorized'
        params = {
            'deviceId': self.get_deviceid(),
            'deviceToken': activation_data['deviceToken'],
            'userCode': activation_data['userCode']
        }

        self._make_request(url=url, method='get', params=params)
        self.validate_session()  # we need this to validate the new cookies
        return True

    def validate_session(self):
        """Check if the session is valid."""
        url = self.login_api + '/persistentLogin/v1'
        params = {
            'deviceKey': self.device_key
        }
        self._make_request(url=url, method='get', params=params)
        return True

    def log_out(self):
        """Log out from Viaplay."""
        url = self.login_api + '/logout/v1'
        params = {
            'deviceKey': self.device_key
        }

        res = self.make_request(url=url, method='get', params=params)
        if res:
            cookie_file = os.path.join(self.settings_folder, 'cookie_file')
            if os.path.exists(cookie_file):
                os.remove(cookie_file)

            xbmc.executebuiltin('Container.Update')

            xbmc.executebuiltin("Dialog.Close(all, true)")
            xbmc.executebuiltin("ActivateWindow(Home)")


    def get_stream(self, guid, pincode=None, tve='false'):
        """Return a dict with the stream URL:s and available subtitle URL:s."""
        stream = {}

        if 'ch-' in guid:
            country_code = self.get_country_code()
            tld = self.get_tld()
            url = 'https://epg.viaplay.{c1}/xdk-{c2}/channel/{guid}/'.format(c1=tld, c2=country_code,guid=guid)
            response = self.make_request(url=url, method='get')['_embedded']['viaplay:products']

            for i in response:
                start_time_obj = self.parse_datetime(i['epg']['startTime'], localize=True)
                end_time_obj = self.parse_datetime(i['epg']['endTime'], localize=True)

                now = datetime.now()
                date_today = now.date()

                if start_time_obj <= now <= end_time_obj:
                    guid = i['system']['guid'] + '-' + country_code.upper()

        #url = 'https://play.viaplay.%s/api/stream/byguid' % self.tld
        url = 'https://play.viaplay.%s/api/stream/bymediaguid' % self.tld

        params = {
            'deviceId': self.get_deviceid(),
            'deviceName': 'web',
            'deviceType': 'pc',
            'userAgent': 'Kodi',
            'deviceKey': 'chromecast-%s' % self.country,
            #'guid': guid
            'mediaGuid': guid
        }
        if pincode:
            params['pgPin'] = pincode
        if tve == 'true':
            params['isTve'] = tve

        data = self.make_request(url=url, method='get', params=params)
        
        if 'viaplay:media' in data['_links']:
            mpd_url = data['_links']['viaplay:media']['href']
        elif 'viaplay:fallbackMedia' in data['_links']:
            mpd_url = data['_links']['viaplay:fallbackMedia'][0]['href']
        elif 'viaplay:playlist' in data['_links']:
            mpd_url = data['_links']['viaplay:playlist']['href']
        elif 'viaplay:encryptedPlaylist' in data['_links']:
            mpd_url = data['_links']['viaplay:encryptedPlaylist']['href']
        else:
            self.log('Failed to retrieve stream URL.')
            return False

        subs_list = []

        stream['mpd_url'] = mpd_url
        stream['license_url'] = data['_links']['viaplay:license']['href']
        stream['release_pid'] = data['_links']['viaplay:license']['releasePid']
        if 'viaplay:sami' in data['_links']:
            #stream['subtitles'] = [x['href'] for x in data['_links']['viaplay:sami']]
            for subs in data['_links']['viaplay:sami']:
                subs_list.append(subs['href'])
                stream['subtitles'] = subs_list

        return stream

    def get_user_id(self):
        url = self.login_api + '/persistentLogin/v1'
        params = {
            'deviceKey': self.device_key
        }
        data = self.make_request(url=url, method='get', params=params)
        return {'id': data['userData']['userId'], 'token': data['userData']['accessToken']}

    def get_profiles(self):
        url = self.profile_url + '/user-profiles/users/{0}/profiles/'.format(self.get_user_id()["id"])
        params = {
            'language': 'en'
        }
        headers = {
            'authorization': 'MTG-AT %s' % self.get_user_id()["token"]
        }
        data = self.make_request(url=url, method='get', params=params, headers=headers)

        profiles = []

        for profile in data['embedded']['profiles']:
            profiles.append({
                'name': profile['data']['name'],
                'id': profile['data']['id'],
                'avatar': profile['embedded']['avatar']['data']['url'],
                'type': profile['data']['type'],
                'owner': 'Owner' if profile['data']['isOwner'] else '',
                'lang': profile['data']['language'].upper() if profile.get('data', {}).get('language') else ''
            })

        return profiles

    def get_root_page(self):
        """Dynamically builds the root page from the returned _links.
        Uses the named dict as 'name' when no 'name' exists in the dict."""
        pages = []
        blacklist = ['byGuid']
        data = self.make_request(url=self.base_url, method='get')

        if 'user' not in data:
            raise self.ViaplayError('MissingSessionCookieError')  # raise error if user is not logged in

        for link in data['_links']:
            if isinstance(data['_links'][link], dict):
                # sort out _links that doesn't contain a title
                if 'title' in data['_links'][link]:
                    title = data['_links'][link]['title']

                    data['_links'][link]['name'] = link  # add name key to dict
                    if title not in blacklist:
                        pages.append(data['_links'][link])
            else:  # list (viaplay:sections for example)
                for i in data['_links'][link]:
                    if 'title' in i:
                        pages.append(i)

        return pages

    def get_collections(self, url):
        """Return all available collections."""
        data = self.make_request(url=url, method='get')
        # return all blocks (collections) with 'list' in type

        return [x for x in data['_embedded']['viaplay:blocks'] if 'list' in x['type'].lower()]

    def get_products(self, url, filter_event=False, search_query=None):
        """Return a dict containing the products and next page if available."""
        if search_query:
            params = {'query': search_query}
        else:
            params = None
        data = self.make_request(url, method='get', params=params)

        if 'list' in data['type'].lower():
            products = data['_embedded']['viaplay:products']
        elif data['type'] == 'tvChannel':
            # sort out 'nobroadcast' items
            products = [x for x in data['_embedded']['viaplay:products'] if 'nobroadcast' not in x['system']['flags']]
        elif data['type'] == 'product':
            # explicity put into list when only one product is returned
            products = [data['_embedded']['viaplay:product']]
        else:
            # try to collect all products found in viaplay:blocks
            products = [p for x in data['_embedded']['viaplay:blocks'] if 'viaplay:products' in x['_embedded'] for p in x['_embedded']['viaplay:products']]


        if filter_event:
            # filter out and only return products with event_status in filter_event
            products = [x for x in products if x['event_status'] in filter_event]

        products_dict = {
            'products': products,
            'next_page': self.get_next_page(data)
        }

        return products_dict

    def get_channels(self, url):
        data = self.make_request(url, method='get')
        channels_block = data['_embedded']['viaplay:blocks'][0]['_embedded']['viaplay:blocks']
        channels = [x['viaplay:channel'] for x in channels_block]
        channels_dict = {
            'channels': channels,
            'next_page': self.get_next_page(data)
        }

        return channels_dict

    def get_seasons(self, url):
        """Return all available series seasons."""
        data = self.make_request(url=url, method='get')
        return [x for x in data['_embedded']['viaplay:blocks'] if x['type'] == 'season-list']

    def get_sport_series(self, url):
        """Return all available sport series."""
        data = self.make_request(url=url, method='get')
        return [p for x in data['_embedded']['viaplay:blocks'] if 'viaplay:products' in x['_embedded'] for p in x['_embedded']['viaplay:products']]

    def download_subtitles(self, suburls):
        """Download the SAMI subtitles, decode the HTML entities and save to temp directory.
        Return a list of the path to the downloaded subtitles."""
        paths = []
        lookup_table_replace = {}

        for url in suburls:
            lang_pattern = re.search(r'[_]([a-z]+)', str(url))
            if lang_pattern:
                sub_lang = lang_pattern.group(1)
            else:
                sub_lang = 'unknown'
                self.log('Failed to identify subtitle language.')

            sami = self.make_request(url=url, method='get').decode('utf-8', 'ignore').strip()

            try:
                if sys.version_info[0] < 3:
                    if sub_lang == 'pl':
                        lookup_table_replace = {
                            '&aogon;': 'ą', '&Aogon;': 'Ą',
                            '&cacute;': 'ć', '&Cacute;': 'Ć',
                            '&eogon;': 'ę', '&Eogon;': 'Ę',
                            '&lstrok;': 'ł', '&Lstrok;': 'Ł',
                            '&nacute;': 'ń', '&Nacute;': 'Ń',
                            '&sacute;': 'ś', '&Sacute;': 'Ś',
                            '&zacute;': 'ź', '&Zacute;': 'Ź',
                            '&zdot;': 'ż', '&Zdot;': 'Ż'
                        }

                for k, v in lookup_table_replace.items():
                    sami = sami.replace(k, v.decode('utf-8'))
            except:
                pass

            if sys.version_info[0] < 3:
                html = HTMLParser.HTMLParser()
            else:
                import html

            subtitle = html.unescape(sami).encode('utf-8')
            path = os.path.join(self.tempdir, '{0}.sami'.format(sub_lang))
            with open(path, 'wb') as subfile:
                subfile.write(subtitle)
            paths.append(path)

        return paths

    def get_deviceid(self):
        """"Read/write deviceId (generated UUID4) from/to file and return it."""
        try:
            with open(self.deviceid_file, 'r') as deviceid:
                return deviceid.read()
        except IOError:
            deviceid = str(uuid.uuid4())
            with open(self.deviceid_file, 'w') as idfile:
                idfile.write(deviceid)
            return deviceid

    def get_event_status(self, data):
        """Return whether the event/program is live/upcoming/archive."""
        now = datetime.utcnow()
        try:
            if data.get('epg'):
                if data['epg'].get('startTime'):
                    start_time = data['epg']['startTime']
                    end_time = data['epg']['endTime']
                else:
                    start_time = data['epg']['start']
                    end_time = data['epg']['end']
            else:
                start_time = data['system']['availability']['start']
                end_time = data['system']['availability']['end']
        except:
            start_time = str(datetime.now())
            end_time = str(datetime.now())

        start_time_obj = self.parse_datetime(start_time).replace(tzinfo=None)
        end_time_obj = self.parse_datetime(end_time).replace(tzinfo=None)

        if 'isLive' in data['system']['flags']:
            status = 'live'
        elif now >= start_time_obj and now < end_time_obj:
            status = 'live'
        elif start_time_obj >= now:
            status = 'upcoming'
        else:
            status = 'archive'

        return status

    def get_next_page(self, data):
        """Return the URL to the next page. Returns False when there is no next page."""
        if data['type'] == 'page':  # multiple blocks in _embedded, find the right one
            for block in data['_embedded']['viaplay:blocks']:
                if 'list' in block['type'].lower() or 'grid' in block['type'].lower():
                    data = block
                    break
        elif data['type'] == 'product':
            data = data['_embedded']['viaplay:product']

        if 'next' in data['_links']:
            next_page_url = data['_links']['next']['href']
            return next_page_url

        return False

    def parse_datetime(self, iso8601_string, localize=False):
        """Parse ISO8601 string to datetime object."""
        datetime_obj = iso8601.parse_date(iso8601_string)
        if localize:
            return self.utc_to_local(datetime_obj)
        else:
            return datetime_obj

    @staticmethod
    def utc_to_local(utc_dt):
        # get integer timestamp to avoid precision lost
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)

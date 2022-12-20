# -*- coding: utf-8 -*-
"""IPTV Manager Integration module"""

import json
import socket
import sys

from resources.lib.kodihelper import KodiHelper


class IPTVManager:
    """Interface to IPTV Manager"""

    def __init__(self, port):
        """Initialize IPTV Manager object"""
        self.port = port
        self.helper = KodiHelper()

    def authorize(self):
        sessionid = self.helper.authorize()
        if not sessionid:
            sessionid = self.helper.authorize()

    def via_socket(func):
        """Send the output of the wrapped function to socket"""

        def send(self):
            """Decorator to send over a socket"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode())
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        channels = list()

        self.authorize()
        url = self.helper.generate_channel_url()
        response = self.helper.vp.make_request(url=url, method='get')
        channellist = [entry['viaplay:channel'] for entry in response['_embedded']
                       ['viaplay:blocks'][0]['_embedded']['viaplay:blocks']]

        for channel in channellist:
            channels.append(dict(
                id=channel.get('system', {}).get('channelGuid'),
                name=channel.get('content', {}).get('title'),
                preset=channel.get('content', {}).get('channelNumber'),
                logo=channel.get('content', {}).get('images', {}).get(
                    'fallback', {}).get('template', '').split('{')[0],
                stream=f"plugin://plugin.video.viaplay/play?guid={channel.get('system', {}).get('channelGuid')}&url=None&tve=true",
            ))

        return dict(version=1, streams=channels)

    @via_socket
    def send_epg(self):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        from collections import defaultdict
        epgs = defaultdict(list)

        self.authorize()
        url = self.helper.generate_channel_url()
        response = self.helper.vp.make_request(url=url, method='get')
        channels = [entry['viaplay:channel'] for entry in response['_embedded']
                    ['viaplay:blocks'][0]['_embedded']['viaplay:blocks']]

        for channel in channels:
            guid = channel.get('system', {}).get('channelGuid')
            tv_events = channel.get('_embedded', {}).get('viaplay:products')

            for event in tv_events:
                epgs[guid].append(dict(
                    start=event.get('epg', {}).get('startTime'),
                    stop=event.get('epg', {}).get('endTime'),
                    title=event.get('content', {}).get('title'),
                    description=event.get('content', {}).get('synopsis'),
                    image=event.get('content', {}).get('images', {}).get(
                        'landscape', {}).get('template', '').split('{')[0],
                    # stream=f"plugin://plugin.video.viaplay/play?guid={event.get('system', {}).get('guid')}-{self.helper.get_country_code().upper()}&url=None&tve=true",
                    # subtitle=?,
                    # genre=?,
                ))

        return dict(version=1, epg=epgs)

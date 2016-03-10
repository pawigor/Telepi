from rtorrent import RTorrent

__author__ = 'z'

rt = RTorrent(url="http://192.168.0.55", _verbose=False)

# torrent T
rt.update()
for torrent in rt.torrents:
    print(torrent.get_name())

    # Torrent

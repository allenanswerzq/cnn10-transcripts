import os
import re
import time
from youtube_dl import *
from youtube_upload import main as ytb_upl
from pathlib import Path
from multiprocessing import process

# TODO(landcold7): written in a object oriented stytle
# add multiprocess support for fast uploading

PLAYLIST_BASE = "https://www.youtube.com/playlist?list="
VIDEO_BASE = "https://www.youtube.com/watch?v="
CNN_PREFIX = "CNN10-"
BLOOMBERG_PREFIX = "Bloomberg-"

CNN_PLAYLIST_NAME = "cnn10"
BLOOMBERG_PLAYLIST_NAME = "Bloomberg Technology"

UPLOAD_DATE = re.compile("([0-9]{4})([0-9]{2})([0-9]{2})")
TITLE_DATE = re.compile('[0-9]+/[0-9]+/[0-9]+$')

# Extract info of a video or the latest video of a playlist
def get_info(video_url, opts=None, download=False, playlist=False):
    ydl_opts = {
        # "proxy" : "socksw5://127.0.0.1:1080/",
        "playlistend": 1
    }
    if opts: ydl_opts.update(opts)
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=download)
        if playlist:
            info = info["entries"][0] if len(info["entries"]) >= 1 else None
    return info

def check_upload_date(video_url, play_url, video_or_play=False, cnn_or_bloomberg=False):
    print("[INFO] Checking video upload availability...")

    video_info = get_info(video_url, playlist=video_or_play)
    if not video_info:
        raise ValueError("Expected video info shold be exist.")
    video_upload_date = video_info["upload_date"]
    video_ext = video_info["ext"]
    video_id = video_info["id"]

    video_match = UPLOAD_DATE.match(video_upload_date)
    if video_match and len(video_match.groups()) == 3:
        g = video_match.groups()
        if not cnn_or_bloomberg:
            mid = (g[1] + "-" + str(int(g[2]) + 1) + "-" + g[0])
            video_name = (CNN_PREFIX + mid + "." + video_ext)
        else:
            mid = (g[1] + "-" + g[2] + "-" + g[0])
            video_name = (BLOOMBERG_PREFIX + mid + "." + video_ext)
    else:
        raise ValueError("Expected video upload date should be match")

    play_info = get_info(play_url, playlist=True)
    # If this playlist if not exist, we can directly upload it.
    if not play_info: return (video_name, video_id)
    play_upload_date = play_info["upload_date"]
    play_title = play_info["title"]

    def shift(seq, n): return seq[n:] + seq[:n]
    play_match = shift(play_title.split('-')[1:], 2)
    if not cnn_or_bloomberg:
        play_match[2] = str(int(play_match[2]) - 1)

    print("[INFO] Upload_dates: {0} /// {1}".format(video_upload_date, play_upload_date))
    tmp = list(zip(video_match.groups(), play_match))
    ret = [1 if int(a) == int(b) else 0 for a, b in tmp]
    return (None, None) if all(ret) else (video_name, video_id)


def check_title_date(video_url, play_url, video_or_play=False, cnn_or_bloomberg=False):
    print("[INFO-TITLE-DATE] Checking video upload availability...")
    ydl_opts = {
        # "proxy" : "socks5://127.0.0.1:2088/",
    }
    video_info = get_info(video_url, ydl_opts, playlist=video_or_play)
    if not video_info:
        raise ValueError("Expected video info shold be exist.")
    video_ext = video_info["ext"]
    video_id = video_info["id"]
    video_title_date = video_info['title']

    video_match = TITLE_DATE.search(video_title_date).group().split('/')

    if video_match and len(video_match) == 3:
        if len(video_match[0]) == 1: video_match[0] = '0' + video_match[0]
        video_match[2] = '20' + video_match[2]
        mid = video_match[0] + '-' + video_match[1] + '-' + video_match[2]
        video_name = (CNN_PREFIX + mid + "." + video_ext)
    else:
        raise ValueError("Expected video title date should be match")

    play_info = get_info(play_url, ydl_opts, playlist=True)
    # If this playlist if not exist, we can directly upload it.
    if not play_info: return (video_name, video_id)
    play_title = play_info["title"]
    play_match = re.search('[0-9]+-[0-9]+-[0-9]+$', play_title).group().split('-')

    print("[INFO-TITLE-DATE] Title_date: {0} /// {1}".format(video_match, play_match))
    tmp = list(zip(video_match, play_match))
    ret = [1 if int(a) == int(b) else 0 for a, b in tmp]
    return (None, None) if all(ret) else (video_name, video_id)

def upload(video_name, playlist):
    title = video_name.split(".")[0]
    desc = ('\
        Hi!, This video is made by other organizations, I uploaded here just for personal '
    'learning purpose, If you have any copyright issues, Please concate me, I will immediately '
    'delete it.')

    args = [
        "--title=" + title,
        "--description=" + desc,
        "--default-language=" + "en",
        "--playlist=" + playlist,
        video_name
    ]
    print("[INFO] Args:", args)
    ytb_upl.main(args)

    # After upload, remove this file.
    Path(video_name).unlink()

def download(video_url, video_name, prefix):
    print("[INFO] Downloading... {0}".format(video_url))
    opts = {
        "outtmpl": prefix + "%(upload_date)s.%(ext)s",
    }
    info = get_info(video_url, opts=opts, download=True)

    file = list(Path('.').glob(prefix + "*"))
    if len(file) == 1:
        src, dst = file[0], Path(video_name)
        print("[INFO] Renaming {0} to {1}".format(str(src), str(dst)))
        Path.rename(src, dst)
    else:
        raise ValueError("""Expected video should be downloaded and there must
            be only one video been leaf""")
    return info

def prog_cnn10():
    video_url = "https://www.cnn.com/cnn10"
    play_url = PLAYLIST_BASE + "PL48o2pI56zBjm_0lZZL_dU2XzENo60rws"
    video_name, _ = check_title_date(video_url, play_url)
    if video_name:
        download(video_url, video_name, CNN_PREFIX)
        upload(video_name, CNN_PLAYLIST_NAME)

def prog_bloomberg():
    offical_url = PLAYLIST_BASE + "PLfAX25ZLrPGRzfILkSd-YiWfsoloCETAe"
    play_url = PLAYLIST_BASE + "PL48o2pI56zBjWzTzCt_iux53p1IKyOVhE"
    video_name, video_id = check_upload_date(offical_url,
                       play_url,
                       video_or_play=True,
                       cnn_or_bloomberg=True)
    if video_name:
        video_url = VIDEO_BASE + video_id
        download(video_url, video_name, BLOOMBERG_PREFIX)
        upload(video_name, BLOOMBERG_PLAYLIST_NAME)

def test_cnn_info():
    video_url = "https://www.cnn.com/cnn10"
    play_url = PLAYLIST_BASE + "PL48o2pI56zBjm_0lZZL_dU2XzENo60rws"
    ydl_opts = {
        "proxy" : "socks5://127.0.0.1:2088/",
        "playlistend": 2
    }
    video_info = get_info(video_url, ydl_opts)
    print("Upload_date:", video_info['upload_date'])
    print("Ext:", video_info['ext'])
    print("Title:", video_info['title'])
    print("Id:", video_info['id'])

    video_url = "https://www.cnn.com/2019/01/16/cnn10/ten-content-thurs/index.html"
    video_info = get_info(video_url, ydl_opts)
    print("Upload_date:", video_info['upload_date'])
    print("Ext:", video_info['ext'])
    print("Title:", video_info['title'])

    info = get_info(play_url, opts=ydl_opts)
    upload_date = info["entries"][0]["upload_date"]
    title = info["entries"][0]["title"]
    ext = info["entries"][0]["ext"]
    print("Play_title:", title)
    print("Play_upload_date:", upload_date)
    print("Play_ext:", ext)

    upload_date = info["entries"][1]["upload_date"]
    title = info["entries"][1]["title"]
    ext = info["entries"][1]["ext"]
    print("Play_title:", title)
    print("Play_upload_date:", upload_date)
    print("Play_ext:", ext)

def test_bloomberg_info():
    offical_url = PLAYLIST_BASE + "PLfAX25ZLrPGRzfILkSd-YiWfsoloCETAe"
    play_url = PLAYLIST_BASE + "PL48o2pI56zBjWzTzCt_iux53p1IKyOVhE"
    ydl_opts = {
        "proxy" : "socks5://127.0.0.1:1080/",
        "playlistend": 2
    }
    info = get_info(offical_url, ydl_opts)
    update_date = info["entries"][0]["upload_date"]
    title = info["entries"][0]["title"]
    ext = info["entries"][0]["ext"]
    print("Title:", title)
    print("Upload_date:", update_date)
    print("Ext:", ext)

def test_all():
    test_cnn_info()
    test_bloomberg_info()

def go():
    prog_cnn10()
    prog_bloomberg()

if __name__ == "__main__":
    go()

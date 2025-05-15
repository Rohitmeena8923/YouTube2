from pytube import YouTube, Search

def search_youtube(query):
    s = Search(query)
    return [{'title': v.title, 'url': v.watch_url} for v in s.results[:20]]

def get_streams(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    return [{'itag': s.itag, 'res': s.resolution} for s in streams if s.resolution in ['144p', '360p', '720p', '1080p']]

def download_stream(url, itag):
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    return stream.download(filename="video.mp4") if stream else None

def download_audio(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    return audio_stream.download(filename="audio.mp3") if audio_stream else None
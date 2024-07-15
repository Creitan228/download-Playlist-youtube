import os
import concurrent.futures
import yt_dlp

def sanitize_filename(name):
    return name.replace('#', '|')

def download_video(video_info, index, resolution="480p", output_template='%(title)s.%(ext)s'):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    title = f"{index:04d}_{sanitize_filename(video_info['title'])}"
    output_path = os.path.join(current_directory, output_template).replace('%(title)s', title)
    
    if os.path.exists(output_path.replace('.%(ext)s', '.mp4')):
        print(f"Видео {title} уже скачано. Пропуск.")
        return
    
    ydl_opts = {
        'format': f'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'ffmpeg_location': r'ваш путь\util\ffmpeg.exe',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'ignoreerrors': True,
        'quiet': True,
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-b:a', '192k'],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info['webpage_url']])
    except yt_dlp.utils.DownloadError as e:
        print(f"Ошибка при скачивании видео {video_info['webpage_url']}: {e}")
    except yt_dlp.utils.ExtractorError as e:
        print(f"Ошибка при извлечении информации о видео {video_info['webpage_url']}: {e}")

def fetch_video_info(ydl, video_url, index):
    try:
        video_info = ydl.extract_info(video_url, download=False)
        return (index, video_info)
    except yt_dlp.utils.DownloadError as e:
        print(f"Ошибка при скачивании видео {video_url}: {e}")
    except yt_dlp.utils.ExtractorError as e:
        print(f"Ошибка при извлечении информации о видео {video_url}: {e}")
    return None

def download_playlist(url, resolution="480p"):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ydl_opts = {
        'format': f'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'merge_output_format': 'mp4',
        'ffmpeg_location': r'C:\Users\DESCTOP228\Documents\project\python\yotube download\util\ffmpeg.exe',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'ignoreerrors': True,
        'quiet': True
    }

    video_list = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_dict = ydl.extract_info(url, download=False)
            playlist_title = sanitize_filename(playlist_dict['title'])
            os.makedirs(os.path.join(current_directory, playlist_title), exist_ok=True)

            video_urls = [(f"https://www.youtube.com/watch?v={entry['id']}", index) 
                          for index, entry in enumerate(playlist_dict['entries'], start=1) if entry is not None]

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(fetch_video_info, ydl, url, index) for url, index in video_urls]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        video_list.append(result)
                    else:
                        print(f"Видео под номером {index} удалено или недоступно.")

    except yt_dlp.utils.ExtractorError as e:
        print(f"Ошибка при извлечении информации о плейлисте: {e}")
    except yt_dlp.utils.DownloadError as e:
        print(f"Ошибка при скачивании плейлиста: {e}")

    # Сортируем видео по индексу
    video_list.sort(key=lambda x: x[0])

    # Скачивание всех видео из списка
    for index, video_info in video_list:
        download_video(video_info, index, resolution, os.path.join(playlist_title, '%(title)s.%(ext)s'))

# Пример использования
if __name__ == "__main__":
    playlist_url = 'ссылка на плейлист'  # замените на URL вашего плейлиста
    download_playlist(playlist_url)

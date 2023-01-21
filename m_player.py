import discord
import discord.utils
import yt_dlp
import data

a = data.datos()


class player:
#--------------YOUTUBE PLAYER---------------#
    async def youtube_player(self, index, vc, j):
        ydl_opts = {
            'quiet': False,
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
            'format': "bestaudio"
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        r = ydl.extract_info(
            j["playlist"]["songs"][index]["link"], download=False)
        
        a.write_json(r, "video")

        vc.play(discord.FFmpegPCMAudio(
        r["url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options= '-vn'))  # reproduciendo

        return r.get('thumbnail', None), r.get('webpage_url')

#--------------FILE PLAYER---------------#
    async def file_player(self, index, vc, j):

        vc.play(discord.FFmpegPCMAudio(j["playlist"]["songs"][index]["link"],
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduciendo

        return 0

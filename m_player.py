import discord
import youtube_dl
import discord.utils


class player:
#--------------YOUTUBE PLAYER---------------#
    async def youtube_player(self, index, vc, j):
        ydl_opts = {
            'quiet': True,
            'youtube_include_dash_manifest': False,
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        r = ydl.extract_info(
            j["playlist"]["songs"][index]["link"], download=False)

        # check if last message was a "Now Playing" from carpbot and if it wasn't delete

        vc.play(discord.FFmpegPCMAudio(r["formats"][0]["url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduciendo

        return r.get('thumbnail', None)

#--------------FILE PLAYER---------------#
    async def file_player(self, index, vc, j):

        vc.play(discord.FFmpegPCMAudio(j["playlist"]["songs"][index]["link"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduciendo

        return 0

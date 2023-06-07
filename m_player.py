import discord
import discord.utils
import yt_dlp
import data
import servermanager as s

a = data.datos()
sm = s.serverManager()

class player:
#--------------YOUTUBE PLAYER---------------#
    async def youtube_player(self, vc, id):
        server = s.servers[sm.get_index(id)]
        ydl_opts = {
            'quiet': False,
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
            'format': "bestaudio"
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        try:
            r = ydl.extract_info(
            s.servers[s.servers_id.index(int(id))]["songs"][server["cplaying"]]["link"], download=False)
        except:
            return 0, 0
        
        sm.apply()

        vc.play(discord.FFmpegPCMAudio(
        r["url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options= '-vn'))  # reproduciendo

        return r.get('thumbnail', None), r.get('webpage_url')

#--------------FILE PLAYER---------------#
    async def file_player(self, vc, id):
        server = s.servers[sm.get_index(id)]
        vc.play(discord.FFmpegPCMAudio(server["songs"][server["cplaying"]]["link"],
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduciendo

        return 0

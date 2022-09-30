import discord
from discord import app_commands
from discord.ext import commands
import wavelink
import random
import json

class wavelinkmusic(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    self.server = {}
    self.is_cycle = False
    self.is_shuffle = False
    self.info_msg = None
    bot.loop.create_task(self.node_connect())

  async def node_connect(self):
    await self.bot.wait_until_ready()
    with open("./json/settings.json","r",encoding = "utf-8") as r:
      settings = json.load(r)
      host = settings["lavalink"]["host"]
      port:int = settings["lavalink"]["port"]
      password = settings["lavalink"]["password"]
    await wavelink.NodePool.create_node(bot = self.bot,
                                        host = host,
                                        port = port, 
                                        password = password)

  @commands.Cog.listener()
  async def on_wavelink_node_ready(self, node: wavelink.Node):
    print(f"Node <{node.identifier}> is ready !")

  @commands.Cog.listener()
  async def on_wavelink_track_end(self, player:wavelink.Player, track: wavelink.Track, reason):
    ctx = player.ctx
    vc: player = ctx.voice_client

    if vc.loop:
      return await vc.play(track)
    elif self.is_cycle:
      vc.queue.extend([track])
    if vc.queue.is_empty:
      return print("[wavelink music] vcqueue is empty")

    next_track = vc.queue.get()
    await vc.play(next_track)
    info = self.songinfo(ctx,next_track,"play")
    await ctx.send(embed = info)
    
  @commands.hybrid_command(name = "join",with_app_command=True)
  async def join(self,ctx):
    """加入你所在的語音頻道"""
    if not ctx.author.voice:
      return await ctx.send("You are not in a voice channel.")

    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
      await voice_channel.connect()
      await ctx.send(f"Joined {voice_channel}")
    else:
      await ctx.voice_channel.move_to(voice_channel)

  @commands.hybrid_command(name = "leave", with_app_command=True)
  async def leave(self,ctx):
    """離開現在所在的語音頻道"""
    if not ctx.author.voice.channel:
      return await ctx.send("You are not in a voice channel.")

    if ctx.voice_client and ctx.author.voice.channel:
      await ctx.voice_client.disconnect()
      await ctx.send(f"Left")
    else:
      await ctx.send("[Error] I am not in a voice channel.",hidden = True)

  @commands.hybrid_command(name = "pau", with_app_command=True)
  async def pau(self,ctx):
    """暫停/繼續播放"""
    if await self.check_voice_client(ctx):return

    if ctx.voice_client.is_paused():
      await ctx.send("[Resumed]")
      await ctx.voice_client.resume()
    else:
      await ctx.send("[Paused]")
      await ctx.voice_client.pause()
      
  @commands.hybrid_command(name = "skip",with_app_command=True)
  async def skip(self,ctx):
    """跳過現在播放的歌"""
    if await self.check_voice_client(ctx):return

    vc: wavelink.Player = ctx.voice_client
    await ctx.send(f"Skipped **{vc.track.title}**")
    return await vc.stop()
  
  @commands.hybrid_command(name = "jump",with_app_command=True)
  async def jump(self,ctx,index:int):
    """播放指定的索引的歌"""
    if await self.check_voice_client(ctx):return

    vc: wavelink.Player = ctx.voice_client
    queue = list(vc.queue.copy())
    size = len(queue)
    if not (0<= index and index <= size):
      return await ctx.send("Index out of range.")

    target = queue[index - 1]
    del queue[index - 1]
    vc.queue.clear()
    vc.queue.extend(queue)
    vc.queue.put_at_front(target)
    await vc.stop()

    await ctx.send(f"Jump to No.{index} Song")   
  
  @commands.hybrid_command(name = "remove", with_app_command=True)
  async def remove(self,ctx,index:int):
    """移除指定索引的歌曲"""
    if await self.check_voice_client(ctx):return

    vc: wavelink.Player = ctx.voice_client
    queue = vc.queue
    size = len(queue)
    if not (1<= index and index <= size):
      return await ctx.send("Index out of range.")
    if index == 1:
      return await ctx.send("You can't remove the song which is been playing.")
    
    target = queue[index - 1]
    del queue[index-1]
    info = self.removeinfo(ctx,target)
    await ctx.send(embed = info)


  @commands.hybrid_command(name = "clear",with_app_command=True)
  async def clear(self,ctx):
    """清空歌單"""
    if await self.check_voice_client(ctx):return
    
    vc:wavelink.Player = ctx.voice_client
    vc.stop()
    vc.queue.clear()
    await ctx.send("已清空歌單")
    
  
  @commands.hybrid_command(name = "play",with_app_command=True)
  async def play(self,ctx,*,song):
    """播放歌曲"""
    if not ctx.voice_client:
      vc: wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player)
    else:    
      vc: wavelink.Player = ctx.voice_client
      vc.queue = wavelink.queue.WaitQueue()
      vc.node = wavelink.Node()
    vc.ctx = ctx
    vc.loop = False

    alreadyplaying = ctx.voice_client.is_playing() or ctx.voice_client.is_paused()
    track = None
    playlist_firstplay = False

    if "https://" in song:
      if "list=" in song:#load in playlist
        playlist = await vc.node.get_playlist(identifier = song, cls = wavelink.YouTubePlaylist)
        vc.queue.extend(playlist.tracks)
        if vc.queue.is_empty and not alreadyplaying:
          playlist_firstplay = True
        else:
          info = discord.Embed(title = f"Added {playlist.name}",description = f"{len(playlist.tracks)} songs",color = 0x0062ff)
          info.set_footer(text = ctx.author,icon_url=str(ctx.author.avatar_url))
          return await ctx.send(embed = info)
        track = vc.queue.get()
      else:#load in a song
        _track = await vc.node.get_tracks(query = song, cls = wavelink.YouTubeTrack)
        track = _track[0]
    else:#keyword search
      track = await wavelink.YouTubeTrack.search(query = song, return_first = True)
      await ctx.send(f"**Searching** `{song}`")

    if (vc.queue.is_empty or playlist_firstplay) and not alreadyplaying:
      await vc.play(track)
      await vc.set_volume(25)
      info = self.songinfo(ctx, track, "play")
      await ctx.send(embed = info)
    else:
      await vc.queue.put_wait(track)
      info = self.songinfo(ctx, track, "add")
      await ctx.send(embed = info)

  @commands.hybrid_command(name = "loop",with_app_command=True)
  async def loop(self,ctx):
    """切換單曲循環模式"""
    if await self.check_voice_client(ctx):return
    
    vc: wavelink.Player = ctx.voice_client

    try:
      vc.loop ^= True
    except Exception:
      vc.loop = False

    return await ctx.send("[Loop] Enabled") if vc.loop else await ctx.send("[Loop] Disabled")

  @commands.hybrid_command(name = "cycle",with_app_command=True)
  async def cycle(self,ctx):
    """切換歌單循環模式"""
    if await self.check_voice_client(ctx):return

    self.is_cycle ^= True 
    return await ctx.send("[Cycle] Enabled") if self.is_cycle else await ctx.send("[Cycle] Disabled")

  @commands.hybrid_command(name = "shuffle",with_app_command=True)
  async def shuffle(self,ctx):
    """隨機歌單順序"""
    if await self.check_voice_client(ctx):return
    
    vc: wavelink.Player = ctx.voice_client
    self.is_shuffle = True
    playlist = list(vc.queue.copy())
    random.shuffle(playlist)
    vc.queue.clear()
    vc.queue.extend(playlist)
    return await ctx.send("[Shuffle]")

  @commands.hybrid_command(name = "playlist",with_app_command=True)
  async def playlist(self,ctx):
    """顯示歌單"""
    if await self.check_voice_client(ctx):return

    vc: wavelink.Player = ctx.voice_client
    if vc.queue.is_empty and not vc.track:
      return await ctx.send("[Error] Song Queue is Empty.")

    queue = vc.queue.copy()
    sq = discord.Embed(title = "Playlist", color = 0x0062ff)
    sq.add_field(name = "NowPlaying ",value = str(vc.track),inline = False)
    songs = ""
    mode = ""

    if queue.is_empty:
      songs = "empty"
    else:
      i = 1
      for song in queue:
        if i <= 10:
          songs += f"{i} {song}\n"
        else:
          songs+=f"*there are **{len(queue) - i + 1}** more songs...  *"
          break
        i += 1
        
    sq.add_field(name = f"{len(queue)} songs", value = songs,inline = False)
    
    if vc.loop: mode += "**Loop** "      
    if self.is_cycle: mode += "**Cycle** "     
    if self.is_shuffle: mode += "**Shuffle**"      
    if not mode: mode = "**Default**" 
      
    sq.add_field(name = "Mode",value = mode,inline = False)    
    await ctx.send(embed = sq)

  @commands.hybrid_command(name = "playnow",with_app_command=True)
  async def playrightnow(self,ctx,song:str):
    """強制播放歌曲"""
    if await self.check_voice_client(ctx):return
      
    vc: wavelink.Player = ctx.voice_client

    track = None
    if "https://" in song:
      _track = await vc.node.get_tracks(query = song, cls = wavelink.YouTubeTrack)
      track = _track[0]
    else:
      track = await wavelink.YouTubeTrack.search(query = song, return_first = True)
      await ctx.send(f"**Searching** `{song}`")

    vc.queue.put_at_front(track)
    await vc.stop()
    return await ctx.send(f"強制插播 **{track.title}**")

  async def check_voice_client(self,ctx):
    if not ctx.voice_client:
      await ctx.send("[Error] I am not in a voice channel.")
      return False

  def get_duration(self,duration):
    hr = int(duration / 3600)
    duration -= hr * 3600
    min = int(duration / 60)
    duration -= min * 60
    sec = int(duration)
    if 0 < hr and hr < 10:
      hr = f"0{str(hr)}"
    if 0 <= min and min < 10:
      min = f"0{str(min)}"
    if 0 <= sec and sec < 10:
      sec = f"0{str(sec)}"
    return f"{hr}:{min}:{sec}" if hr else f"{min}:{sec}"

  def songinfo(self, ctx, track, mode:str):
    selector = {"play":"Now Playing","add":"Added"}
    songinfo = discord.Embed(title = f"{selector[mode]}  {track.title}",description = f"Link: [YoutubeURL]({str(track.uri)})",color = 0x0062ff)
    songinfo.set_author(name = f"Artist: {track.author}")
    try:
      songinfo.set_thumbnail(url = track.thumbnail)
    except:
      print("[wavelink music] Can't load in thumbnail.")
    song_length = self.get_duration(track.length)
    songinfo.add_field(name = "Length", value = song_length,inline = False)
    return songinfo
  
  def removeinfo(self, ctx, track):
    info = discord.Embed(title = "Removed from playlist",color = discord.Color.red())
    song_length = self.get_duration(track.length)
    info.add_field(name = track.title, value = song_length, inline = False)
    return info

async def setup(bot):
  await bot.add_cog(wavelinkmusic(bot))
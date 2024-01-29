import discord
import random
from datetime import datetime
import libs.settings as settings

poll_activity = {}

class PollActivity():
    def __init__(self,title:str,author:discord.Member, options:list, users:dict):
        self.title = title
        self.author = author
        self.options = options
        self.users = users
        #options: [{name:"",votes:0}]
        #users: {"user_id":index}
    
    def get_options(self):return [opt["name"] for opt in self.options]

    def poll_embed(self):
        pollEmbed = discord.Embed(title = f"投票: {self.title}", color = discord.Color.light_gray())        
        i = 1
        for option in self.options:
            votes = option["votes"]
            pollEmbed.add_field(name = f"選項{i} : {votes}票", value = option["name"], inline = False)
            i+= 1
        if self.author: pollEmbed.set_footer(text = f"由 {self.author} 創建",icon_url=self.author.avatar.url)
        return pollEmbed
    
    def info_embed(self) -> discord.Embed:
        users_n = len(self.users.keys())
        opts_n = len(self.get_options())

        infoEmbed = discord.Embed(title = f"投票詳細資訊", description=f"此投票活動有`{opts_n}`個選項  `{users_n}`位用戶投票", color= discord.Color.light_gray(), timestamp=datetime.utcnow())
        
        copy = [{"name":opt["name"],"votes":opt["votes"], "users":""} for opt in self.options]

        for id in self.users.keys(): copy[self.users[id]]["users"] += f"<@{id}>"
        copy.sort(key = lambda t:t["votes"],reverse=True)

        for opt in copy:
            name = opt["name"]
            votes = opt["votes"]
            users = opt["users"]
            if users == "": users = "Nobody"
            persent = round(votes / users_n * 100, 2)
            infoEmbed.add_field(name = f"選項: {name}  ({votes}人/{persent}%)",value=users, inline = False)
        infoEmbed.set_footer(text = f"各選項已依據票數排序", icon_url=settings.avatar)

        return infoEmbed

class select_view(discord.ui.View):
    def __init__(self):super().__init__(timeout=None)

class info_button(discord.ui.Button):
    def __init__(self,poll_id):
        super().__init__(label="查看投票詳細",custom_id="infobutton",emoji="📃")
        self.poll_id = poll_id
    
    async def callback(self, interaction: discord.Interaction):
        global poll_activity
        infoEmbed = poll_activity[self.poll_id].info_embed()
        await interaction.response.send_message(embed = infoEmbed,ephemeral=True)

class vote_select(discord.ui.Select):
    def __init__(self,poll_id,message):
        global poll_activity
        self.poll_id = poll_id
        i = 0
        opts_list = []
        for option in poll_activity[poll_id].get_options():
            opts_list.append(discord.SelectOption(label = option, value = str(i)))
            i+=1
        super().__init__(custom_id="vote",placeholder="選擇一個選項",options=opts_list)
        self.message = message
    
    async def callback(self, interaction: discord.Interaction):
        global poll_activity
        pollact = poll_activity[self.poll_id]
        user_id = interaction.user.id
        choice = int(self.values[0])

        if user_id in pollact.users.keys():
            history = pollact.users[user_id]
            pollact.options[history]["votes"] -= 1
        pollact.users[user_id] = choice
        pollact.options[choice]["votes"] += 1

        pollEmbed = pollact.poll_embed()
        await self.message.edit(embed = pollEmbed)

        option_name = pollact.get_options()[choice]
        await interaction.response.send_message(f"你投給了選項*{choice + 1} : {option_name}*",ephemeral=True)

class PollCreateModal(discord.ui.Modal):
    def __init__(self, guild, channel, author):
        super().__init__(title = "建立一場投票活動", timeout = None)
        self.guild = guild
        self.channel = channel
        self.author = author   

    SubjectContext = discord.ui.TextInput(label = "投票主題",
                                            required = True,
                                            style = discord.TextStyle.short,
                                            max_length = 50)
    OptionsContext = discord.ui.TextInput(label = "投票選項",
                                            placeholder="每行輸入一個選項",
                                            required = True,
                                            style = discord.TextStyle.paragraph,
                                            max_length = 4000)

    async def create_poll(self, title:str, opts:list, author:discord.Member):
        global poll_activity
        while (True):
            id = ""
            for i in range(3):
                id += str(random.randint(0,9))
            if (id not in poll_activity.keys()):break
        poll_activity[id] = PollActivity(title,author,[{"name":option, "votes":0} for option in opts],{})
        return id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True)
        global poll_activity

        options = [] 
        for i in str(self.OptionsContext).split('\n'):
            if i != "":options.append(i)

        if (len(options) <= 1):return await  interaction.followup.send("[Error]必須輸入至少兩個選項",ephemeral=True)
        
        id = await self.create_poll(self.SubjectContext, options, self.author)
        pollEmbed = poll_activity[id].poll_embed()

        msg = await self.channel.send(embed = pollEmbed)
        select = vote_select(id, msg)
        infobutton = info_button(id)
        view = select_view().add_item(select).add_item(infobutton)
        await msg.edit(view = view)
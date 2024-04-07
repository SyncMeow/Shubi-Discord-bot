import discord
from discord import Interaction
from discord import TextStyle
from discord.ext import commands
from datetime import datetime
import json

class QuestionsSetModal(discord.ui.Modal):
    def __init__(self, guild_id:str):
        super().__init__(title = "設定新的題目, 將會覆寫原本的題目", timeout=False)
        self.guild_id = guild_id

    ContextQ = discord.ui.TextInput(label="剛加入伺服器的成員必須回答的問題",
                                    style=TextStyle.paragraph,
                                    placeholder="每行輸入一個題目",
                                    required=True)

    ContextA = discord.ui.TextInput(label="剛加入伺服器的成員必須回答的問題解答",
                                    style=TextStyle.paragraph,
                                    placeholder="每行輸入一個解答",
                                    required=True)
    
    ContextN = discord.ui.TextInput(label="允許錯題數",
                                    style=TextStyle.short,
                                    placeholder="請輸入整數",
                                    required=True)
    
    async def on_submit(self, interaction: Interaction):
        questions = []
        for _ in str(self.ContextQ).split('\n'):
            if _: 
                if len(_) > 44: return await interaction.response.send_message("題目敘述過長, 超過限制了(44)!", ephemeral=True)
                questions.append(_)
        answers = []
        for _ in str(self.ContextA).split('\n'):
            if _ : answers.append(_)
        fault = int(str(self.ContextN))
        if len(questions) != len(answers): return await interaction.response.send_message("輸入的題目與答案數量不一致!", ephemeral=True)
        if len(questions) > 20: return await interaction.response.send_message("輸入的題目太多!", ephemeral=True)
        if fault < 0 or fault > len(questions): return await interaction.response.send_message("允許錯題數有誤!", ephemeral=True)
        data = json.load(open("./json/access.json","r",encoding="utf-8"))
        data[str(self.guild_id)]["questions"] = {}
        for i in range(len(questions)): data[str(self.guild_id)]["questions"][questions[i]] = answers[i]
        data[str(self.guild_id)]["fault"] = fault

        with open("./json/access.json","w",encoding="utf-8") as w:
            json.dump(data,w)
        
        await interaction.response.send_message(f"已設定{len(questions)}個題目, 允許錯{fault}題")  

class VerifyModal(discord.ui.Modal):
    def __init__(self, ctx:commands.Context):
        super().__init__(title = "驗證流程開始, 請回答以下所有問題以通過驗證", timeout=False)
        self.ctx = ctx
    
    async def on_submit(self, interaction: Interaction):
        data = json.load(open("./json/access.json","r",encoding="utf-8"))
        n = 0
        for catch in self.children:
            if not isinstance(catch, discord.ui.TextInput): continue
            if str(catch) != catch.answer: n+=1
            if n > data[str(self.ctx.guild.id)]["fault"]:
                return await interaction.response.send_message(f"很抱歉, 你的錯題數已經超過了允許的範圍(錯{n}題)")
        
        role = self.ctx.guild.get_role(data[str(self.ctx.guild.id)]["role"])
        await self.ctx.author.add_roles(role)
        Embed = self.AccessPassEmbed(self.ctx.author, role)
        await interaction.response.send_message(embed = Embed)
        
    def AccessPassEmbed(self, user:discord.User, role:discord.Role):
        Embed = discord.Embed(color = discord.Color.green(), timestamp=datetime.utcnow())
        Embed.add_field(name = f"{user} 已通過驗證", value = f"給予身分組{role.mention}")
        return Embed

class QuestionContext(discord.ui.TextInput):
    def __init__(self,question,answer):
        super().__init__(label = question, style = TextStyle.short, placeholder="請在這裡輸入你的答案", required=True)
        self.answer = answer

    
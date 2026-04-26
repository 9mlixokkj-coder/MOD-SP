import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
import os
import re

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automod_file = "automod_config.json"
        self.load_config()
    
    def load_config(self):
        """Carrega configurações de automoderação"""
        if os.path.exists(self.automod_file):
            with open(self.automod_file, 'r', encoding='utf-8') as f:
                self.automod_config = json.load(f)
        else:
            self.automod_config = {}
            self.save_config()
    
    def save_config(self):
        """Salva configurações de automoderação"""
        with open(self.automod_file, 'w', encoding='utf-8') as f:
            json.dump(self.automod_config, f, indent=4, ensure_ascii=False)
    
    def get_guild_config(self, guild_id: int):
        """Obtém configuração de automod de um servidor"""
        guild_id = str(guild_id)
        if guild_id not in self.automod_config:
            self.automod_config[guild_id] = {
                "blocked_words": [],
                "blocked_links_channels": []
            }
            self.save_config()
        return self.automod_config[guild_id]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitora mensagens para automod"""
        # Ignora bots e DMs
        if message.author.bot or not message.guild:
            return
        
        # Ignora administradores
        if message.author.guild_permissions.administrator:
            return
        
        config = self.get_guild_config(message.guild.id)
        
        # Verifica palavras bloqueadas
        message_lower = message.content.lower()
        for word in config["blocked_words"]:
            if word.lower() in message_lower:
                try:
                    await message.delete()
                    
                    embed = discord.Embed(
                        title="⚠️ Palavra Bloqueada",
                        description=f"{message.author.mention}, você usou uma palavra que não é permitida neste servidor!",
                        color=discord.Color.red()
                    )
                    
                    msg = await message.channel.send(embed=embed)
                    await msg.delete(delay=5)
                    
                    # Log se configurado
                    server_config = self.bot.get_server_config(message.guild.id)
                    if server_config.get("canal_logs"):
                        canal_logs = message.guild.get_channel(server_config["canal_logs"])
                        if canal_logs:
                            log_embed = discord.Embed(
                                title="🚫 Palavra Bloqueada Detectada",
                                color=discord.Color.red(),
                                timestamp=datetime.now()
                            )
                            log_embed.add_field(name="Usuário", value=message.author.mention, inline=True)
                            log_embed.add_field(name="Canal", value=message.channel.mention, inline=True)
                            log_embed.add_field(name="Palavra Detectada", value=f"||{word}||", inline=True)
                            log_embed.add_field(name="Mensagem Original", value=f"||{message.content[:100]}||", inline=False)
                            await canal_logs.send(embed=log_embed)
                    
                    return
                except:
                    pass
        
        # Verifica links bloqueados em canais específicos
        if str(message.channel.id) in config["blocked_links_channels"]:
            # Regex para detectar URLs
            url_pattern = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )
            
            if url_pattern.search(message.content):
                try:
                    await message.delete()
                    
                    embed = discord.Embed(
                        title="🔗 Links Bloqueados",
                        description=f"{message.author.mention}, links não são permitidos neste canal!",
                        color=discord.Color.red()
                    )
                    
                    msg = await message.channel.send(embed=embed)
                    await msg.delete(delay=5)
                    
                    # Log se configurado
                    server_config = self.bot.get_server_config(message.guild.id)
                    if server_config.get("canal_logs"):
                        canal_logs = message.guild.get_channel(server_config["canal_logs"])
                        if canal_logs:
                            log_embed = discord.Embed(
                                title="🔗 Link Bloqueado Detectado",
                                color=discord.Color.red(),
                                timestamp=datetime.now()
                            )
                            log_embed.add_field(name="Usuário", value=message.author.mention, inline=True)
                            log_embed.add_field(name="Canal", value=message.channel.mention, inline=True)
                            log_embed.add_field(name="Mensagem", value=f"||{message.content[:100]}||", inline=False)
                            await canal_logs.send(embed=log_embed)
                    
                    return
                except:
                    pass
    
    @app_commands.command(name="automod_add", description="Adiciona uma palavra à lista de bloqueio")
    @app_commands.describe(palavra="Palavra a ser bloqueada")
    async def automod_add(self, interaction: discord.Interaction, palavra: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        palavra_lower = palavra.lower()
        
        if palavra_lower in [w.lower() for w in config["blocked_words"]]:
            await interaction.response.send_message(f"❌ A palavra `{palavra}` já está bloqueada!", ephemeral=True)
            return
        
        config["blocked_words"].append(palavra)
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Palavra Bloqueada",
            description=f"A palavra `{palavra}` foi adicionada à lista de bloqueio.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Adicionada por {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="automod_remove", description="Remove uma palavra da lista de bloqueio")
    @app_commands.describe(palavra="Palavra a ser desbloqueada")
    async def automod_remove(self, interaction: discord.Interaction, palavra: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        # Busca palavra case-insensitive
        palavra_encontrada = None
        for w in config["blocked_words"]:
            if w.lower() == palavra.lower():
                palavra_encontrada = w
                break
        
        if not palavra_encontrada:
            await interaction.response.send_message(f"❌ A palavra `{palavra}` não está na lista de bloqueio!", ephemeral=True)
            return
        
        config["blocked_words"].remove(palavra_encontrada)
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Palavra Desbloqueada",
            description=f"A palavra `{palavra_encontrada}` foi removida da lista de bloqueio.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Removida por {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="automod_painel", description="Mostra todas as palavras bloqueadas")
    async def automod_painel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="🚫 Painel de Automoderação",
            description="Lista de palavras bloqueadas neste servidor",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        if config["blocked_words"]:
            # Divide em chunks de 20 palavras
            palavras_formatadas = []
            for i, palavra in enumerate(config["blocked_words"], 1):
                palavras_formatadas.append(f"`{i}.` ||{palavra}||")
            
            # Agrupa em blocos
            chunks = [palavras_formatadas[i:i+20] for i in range(0, len(palavras_formatadas), 20)]
            
            for i, chunk in enumerate(chunks):
                field_name = "Palavras Bloqueadas" if i == 0 else f"Palavras Bloqueadas (cont. {i+1})"
                embed.add_field(
                    name=field_name,
                    value="\n".join(chunk),
                    inline=False
                )
            
            embed.set_footer(text=f"Total: {len(config['blocked_words'])} palavras bloqueadas")
        else:
            embed.description = "Nenhuma palavra está bloqueada no momento."
            embed.color = discord.Color.green()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="automod_link", description="Bloqueia links em um canal específico")
    @app_commands.describe(canal="Canal onde links serão bloqueados")
    async def automod_link(self, interaction: discord.Interaction, canal: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        canal_id = str(canal.id)
        
        if canal_id in config["blocked_links_channels"]:
            await interaction.response.send_message(f"❌ Links já estão bloqueados em {canal.mention}!", ephemeral=True)
            return
        
        config["blocked_links_channels"].append(canal_id)
        self.save_config()
        
        embed = discord.Embed(
            title="🔗 Links Bloqueados",
            description=f"Links agora estão bloqueados no canal {canal.mention}.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Configurado por {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="automod_link_remove", description="Permite links em um canal que estava bloqueado")
    @app_commands.describe(canal="Canal onde links serão permitidos")
    async def automod_link_remove(self, interaction: discord.Interaction, canal: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        canal_id = str(canal.id)
        
        if canal_id not in config["blocked_links_channels"]:
            await interaction.response.send_message(f"❌ Links não estão bloqueados em {canal.mention}!", ephemeral=True)
            return
        
        config["blocked_links_channels"].remove(canal_id)
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Links Permitidos",
            description=f"Links agora estão permitidos no canal {canal.mention}.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Configurado por {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))

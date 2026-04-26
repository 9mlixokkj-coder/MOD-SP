import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
import os

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_file = "user_stats.json"
        self.load_stats()
    
    def load_stats(self):
        """Carrega estatísticas dos usuários"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.user_stats = json.load(f)
        else:
            self.user_stats = {}
            self.save_stats()
    
    def save_stats(self):
        """Salva estatísticas dos usuários"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_stats, f, indent=4, ensure_ascii=False)
    
    def get_user_stats(self, guild_id: int, user_id: int):
        """Obtém estatísticas de um usuário"""
        guild_id = str(guild_id)
        user_id = str(user_id)
        
        if guild_id not in self.user_stats:
            self.user_stats[guild_id] = {}
        
        if user_id not in self.user_stats[guild_id]:
            self.user_stats[guild_id][user_id] = {
                "message_count": 0,
                "mute_count": 0
            }
        
        return self.user_stats[guild_id][user_id]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Conta mensagens dos usuários"""
        if message.author.bot:
            return
        
        if message.guild:
            stats = self.get_user_stats(message.guild.id, message.author.id)
            stats["message_count"] += 1
            self.save_stats()
    
    @app_commands.command(name="lock", description="Tranca um canal impedindo que membros enviem mensagens")
    @app_commands.describe(canal="Canal a ser trancado (opcional, padrão: canal atual)")
    async def lock(self, interaction: discord.Interaction, canal: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Você não tem permissão para trancar canais!", ephemeral=True)
            return
        
        canal = canal or interaction.channel
        
        # Atualiza permissões para @everyone não poder enviar mensagens
        overwrites = canal.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = False
        await canal.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        
        embed = discord.Embed(
            title="🔒 Canal Trancado",
            description=f"O canal {canal.mention} foi trancado.\nApenas moderadores podem enviar mensagens.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Trancado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unlock", description="Destranca um canal permitindo que membros enviem mensagens")
    @app_commands.describe(canal="Canal a ser destrancado (opcional, padrão: canal atual)")
    async def unlock(self, interaction: discord.Interaction, canal: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Você não tem permissão para destrancar canais!", ephemeral=True)
            return
        
        canal = canal or interaction.channel
        
        # Atualiza permissões para @everyone poder enviar mensagens
        overwrites = canal.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = True
        await canal.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        
        embed = discord.Embed(
            title="🔓 Canal Destrancado",
            description=f"O canal {canal.mention} foi destrancado.\nTodos podem enviar mensagens novamente.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Destrancado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clear", description="Limpa mensagens de um canal")
    @app_commands.describe(quantidade="Quantidade de mensagens a limpar (1-1000)")
    async def clear(self, interaction: discord.Interaction, quantidade: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Você não tem permissão para limpar mensagens!", ephemeral=True)
            return
        
        if quantidade < 1 or quantidade > 1000:
            await interaction.response.send_message("❌ A quantidade deve estar entre 1 e 1000!", ephemeral=True)
            return
        
        await interaction.response.send_message(f"🧹 Limpando {quantidade} mensagens...", ephemeral=True)
        
        try:
            deleted = await interaction.channel.purge(limit=quantidade)
            
            embed = discord.Embed(
                title="🧹 Mensagens Limpas",
                description=f"**{len(deleted)}** mensagens foram deletadas.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Limpeza feita por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            
            # Envia mensagem temporária
            msg = await interaction.channel.send(embed=embed)
            await msg.delete(delay=5)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Não tenho permissão para deletar mensagens!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao limpar mensagens: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="userinfo", description="Mostra informações sobre um usuário")
    @app_commands.describe(membro="Membro para ver informações (opcional)")
    async def userinfo(self, interaction: discord.Interaction, membro: discord.Member = None):
        membro = membro or interaction.user
        
        # Obtém estatísticas
        stats = self.get_user_stats(interaction.guild.id, membro.id)
        
        # Cria embed
        embed = discord.Embed(
            title=f"📋 Informações de {membro.name}",
            color=membro.color if membro.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        
        # Informações básicas
        embed.add_field(
            name="👤 Usuário",
            value=f"{membro.mention}\n`{membro.name}`\nID: `{membro.id}`",
            inline=True
        )
        
        # Status
        status_emoji = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Ausente",
            discord.Status.dnd: "🔴 Não Perturbe",
            discord.Status.offline: "⚫ Offline"
        }
        embed.add_field(
            name="📊 Status",
            value=status_emoji.get(membro.status, "❓ Desconhecido"),
            inline=True
        )
        
        # Conta criada
        criacao = membro.created_at.strftime("%d/%m/%Y às %H:%M:%S")
        tempo_criacao = (datetime.now(membro.created_at.tzinfo) - membro.created_at).days
        embed.add_field(
            name="📅 Conta Criada",
            value=f"{criacao}\n({tempo_criacao} dias atrás)",
            inline=False
        )
        
        # Entrou no servidor
        if membro.joined_at:
            entrada = membro.joined_at.strftime("%d/%m/%Y às %H:%M:%S")
            tempo_entrada = (datetime.now(membro.joined_at.tzinfo) - membro.joined_at).days
            embed.add_field(
                name="📥 Entrou no Servidor",
                value=f"{entrada}\n({tempo_entrada} dias atrás)",
                inline=False
            )
        
        # Estatísticas
        embed.add_field(
            name="📨 Mensagens Enviadas",
            value=f"`{stats['message_count']:,}` mensagens",
            inline=True
        )
        
        embed.add_field(
            name="🔇 Punições (Mutes)",
            value=f"`{stats['mute_count']}` mutes",
            inline=True
        )
        
        # Cargos
        if len(membro.roles) > 1:  # Ignora @everyone
            roles = [role.mention for role in reversed(membro.roles) if role != interaction.guild.default_role]
            roles_text = ", ".join(roles[:20])  # Limita a 20 cargos
            if len(membro.roles) > 21:
                roles_text += f"\n*+{len(membro.roles) - 21} cargos...*"
            embed.add_field(
                name=f"🎭 Cargos ({len(membro.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Mostra informações sobre o servidor")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"📊 Informações do Servidor",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informações básicas
        embed.add_field(
            name="🏷️ Nome",
            value=guild.name,
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        embed.add_field(
            name="👑 Dono",
            value=guild.owner.mention if guild.owner else "Desconhecido",
            inline=True
        )
        
        # Data de criação
        criacao = guild.created_at.strftime("%d/%m/%Y às %H:%M:%S")
        tempo_criacao = (datetime.now(guild.created_at.tzinfo) - guild.created_at).days
        embed.add_field(
            name="📅 Criado em",
            value=f"{criacao}\n({tempo_criacao} dias atrás)",
            inline=False
        )
        
        # Membros
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        
        embed.add_field(
            name="👥 Membros",
            value=f"**Total:** {total_members:,}\n**Online:** {online_members:,}",
            inline=True
        )
        
        # Canais
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📁 Canais",
            value=f"**Texto:** {text_channels}\n**Voz:** {voice_channels}\n**Categorias:** {categories}",
            inline=True
        )
        
        # Impulsos
        boost_count = guild.premium_subscription_count or 0
        boost_level = guild.premium_tier
        
        embed.add_field(
            name="🚀 Impulsos",
            value=f"**Nível:** {boost_level}\n**Impulsos:** {boost_count}",
            inline=True
        )
        
        # Cargos
        embed.add_field(
            name="🎭 Cargos",
            value=f"{len(guild.roles)} cargos",
            inline=True
        )
        
        # Emojis
        embed.add_field(
            name="😀 Emojis",
            value=f"{len(guild.emojis)} emojis",
            inline=True
        )
        
        # Nível de verificação
        verification_levels = {
            discord.VerificationLevel.none: "Nenhum",
            discord.VerificationLevel.low: "Baixo",
            discord.VerificationLevel.medium: "Médio",
            discord.VerificationLevel.high: "Alto",
            discord.VerificationLevel.highest: "Máximo"
        }
        
        embed.add_field(
            name="🔐 Verificação",
            value=verification_levels.get(guild.verification_level, "Desconhecido"),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="punições", description="Mostra quantos mutes um membro recebeu")
    @app_commands.describe(membro="Membro para ver punições")
    async def punicoes(self, interaction: discord.Interaction, membro: discord.Member):
        stats = self.get_user_stats(interaction.guild.id, membro.id)
        
        embed = discord.Embed(
            title=f"🔇 Punições de {membro.name}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        
        embed.add_field(
            name="Silenciamentos (Mutes)",
            value=f"**{stats['mute_count']}** mutes recebidos",
            inline=False
        )
        
        embed.set_footer(text=f"Consultado por {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilitarios(bot))

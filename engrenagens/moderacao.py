import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ban", description="Bane um membro do servidor")
    @app_commands.describe(
        membro="O membro a ser banido",
        motivo="Motivo do banimento"
    )
    async def ban(self, interaction: discord.Interaction, membro: discord.Member, motivo: str):
        # Verifica permissões
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ Você não tem permissão para banir membros!", ephemeral=True)
            return
        
        # Verifica se está tentando banir a si mesmo
        if membro.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode banir a si mesmo!", ephemeral=True)
            return
        
        # Verifica se está tentando banir um admin
        if membro.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você não pode banir um administrador!", ephemeral=True)
            return
        
        # Verifica hierarquia de cargos
        if membro.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Você não pode banir alguém com cargo igual ou superior ao seu!", ephemeral=True)
            return
        
        # Tenta enviar DM para o membro antes de banir
        try:
            dm_embed = discord.Embed(
                title="🔨 Você foi banido",
                description=f"Você foi banido do servidor **{interaction.guild.name}**",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            dm_embed.add_field(name="Motivo", value=motivo, inline=False)
            dm_embed.add_field(name="Banido por", value=interaction.user.mention, inline=True)
            await membro.send(embed=dm_embed)
        except:
            pass  # Caso o membro tenha DMs desativadas
        
        # Executa o banimento
        try:
            await membro.ban(reason=f"Banido por {interaction.user} - {motivo}")
            
            # Embed de confirmação
            embed = discord.Embed(
                title="🔨 Membro Banido",
                description=f"{membro.mention} foi banido do servidor",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Usuário", value=f"{membro} (ID: {membro.id})", inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.set_thumbnail(url=membro.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
            # Envia para logs se configurado
            config = self.bot.get_server_config(interaction.guild.id)
            if config.get("canal_logs"):
                canal_logs = interaction.guild.get_channel(config["canal_logs"])
                if canal_logs:
                    await canal_logs.send(embed=embed)
        
        except discord.Forbidden:
            await interaction.response.send_message("❌ Não tenho permissão para banir este membro!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao banir: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="mute", description="Silencia um membro do servidor")
    @app_commands.describe(
        membro="O membro a ser silenciado",
        motivo="Motivo do silenciamento",
        duracao="Duração em minutos (padrão: 60)"
    )
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, motivo: str, duracao: int = 60):
        # Verifica permissões
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Você não tem permissão para silenciar membros!", ephemeral=True)
            return
        
        # Verifica se está tentando mutar a si mesmo
        if membro.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode silenciar a si mesmo!", ephemeral=True)
            return
        
        # Verifica se está tentando mutar um admin
        if membro.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você não pode silenciar um administrador!", ephemeral=True)
            return
        
        # Verifica hierarquia de cargos
        if membro.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Você não pode silenciar alguém com cargo igual ou superior ao seu!", ephemeral=True)
            return
        
        # Calcula duração
        tempo_mute = timedelta(minutes=duracao)
        
        # Tenta enviar DM para o membro antes de mutar
        try:
            dm_embed = discord.Embed(
                title="🔇 Você foi silenciado",
                description=f"Você foi silenciado no servidor **{interaction.guild.name}**",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            dm_embed.add_field(name="Motivo", value=motivo, inline=False)
            dm_embed.add_field(name="Duração", value=f"{duracao} minutos", inline=True)
            dm_embed.add_field(name="Silenciado por", value=interaction.user.mention, inline=True)
            await membro.send(embed=dm_embed)
        except:
            pass
        
        # Executa o mute
        try:
            await membro.timeout(tempo_mute, reason=f"Mutado por {interaction.user} - {motivo}")
            
            # Registra a punição nas estatísticas
            try:
                utilitarios_cog = self.bot.get_cog('Utilitarios')
                if utilitarios_cog:
                    stats = utilitarios_cog.get_user_stats(interaction.guild.id, membro.id)
                    stats["mute_count"] += 1
                    utilitarios_cog.save_stats()
            except:
                pass
            
            # Embed de confirmação
            embed = discord.Embed(
                title="🔇 Membro Silenciado",
                description=f"{membro.mention} foi silenciado",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Usuário", value=f"{membro} (ID: {membro.id})", inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Duração", value=f"{duracao} minutos", inline=True)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.set_thumbnail(url=membro.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
            # Envia para logs se configurado
            config = self.bot.get_server_config(interaction.guild.id)
            if config.get("canal_logs"):
                canal_logs = interaction.guild.get_channel(config["canal_logs"])
                if canal_logs:
                    await canal_logs.send(embed=embed)
        
        except discord.Forbidden:
            await interaction.response.send_message("❌ Não tenho permissão para silenciar este membro!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao silenciar: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unmute", description="Remove o silenciamento de um membro")
    @app_commands.describe(membro="O membro a ter o silenciamento removido")
    async def unmute(self, interaction: discord.Interaction, membro: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Você não tem permissão para remover silenciamentos!", ephemeral=True)
            return
        
        try:
            await membro.timeout(None, reason=f"Desmutado por {interaction.user}")
            
            embed = discord.Embed(
                title="🔊 Silenciamento Removido",
                description=f"{membro.mention} pode falar novamente",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unban", description="Remove o banimento de um usuário")
    @app_commands.describe(
        user_id="ID do usuário a ser desbanido",
        motivo="Motivo do desbanimento"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, motivo: str = "Sem motivo especificado"):
        # Verifica permissões
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ Você não tem permissão para desbanir membros!", ephemeral=True)
            return
        
        # Converte user_id para int
        try:
            user_id_int = int(user_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de usuário inválido! Use apenas números.", ephemeral=True)
            return
        
        # Tenta desbanir o usuário
        try:
            # Busca o usuário banido
            user = await self.bot.fetch_user(user_id_int)
            
            # Remove o banimento
            await interaction.guild.unban(user, reason=f"Desbanido por {interaction.user} - {motivo}")
            
            # Tenta enviar DM para o usuário
            try:
                dm_embed = discord.Embed(
                    title="✅ Você foi desbanido",
                    description=f"Você foi desbanido do servidor **{interaction.guild.name}**",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                dm_embed.add_field(name="Motivo", value=motivo, inline=False)
                dm_embed.add_field(name="Desbanido por", value=interaction.user.mention, inline=True)
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Embed de confirmação
            embed = discord.Embed(
                title="✅ Usuário Desbanido",
                description=f"{user.mention} foi desbanido do servidor",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Usuário", value=f"{user} (ID: {user.id})", inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
            # Envia para logs se configurado
            config = self.bot.get_server_config(interaction.guild.id)
            if config.get("canal_logs"):
                canal_logs = interaction.guild.get_channel(config["canal_logs"])
                if canal_logs:
                    await canal_logs.send(embed=embed)
        
        except discord.NotFound:
            await interaction.response.send_message("❌ Usuário não encontrado ou não está banido!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Não tenho permissão para desbanir este usuário!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao desbanir: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacao(bot))

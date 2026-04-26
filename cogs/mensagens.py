import discord
from discord.ext import commands
from discord import app_commands

class Mensagens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mensagem", description="Envia uma mensagem no canal atual")
    @app_commands.describe(descricao="Conteúdo da mensagem a ser enviada")
    async def mensagem(self, interaction: discord.Interaction, descricao: str):
        # Verifica permissões
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        # Envia a mensagem
        await interaction.channel.send(descricao)
        await interaction.response.send_message("✅ Mensagem enviada com sucesso!", ephemeral=True)
    
    @app_commands.command(name="embed", description="Envia uma embed personalizada")
    @app_commands.describe(
        titulo="Título da embed",
        descricao="Descrição da embed",
        cor="Cor em hexadecimal (ex: #FF0000)",
        url_foto="URL da imagem (opcional)"
    )
    async def embed(self, interaction: discord.Interaction, titulo: str, descricao: str, cor: str, url_foto: str = None):
        # Verifica permissões
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
            return
        
        # Processa a cor
        try:
            # Remove # se presente e converte para int
            cor_limpa = cor.replace("#", "")
            cor_int = int(cor_limpa, 16)
        except ValueError:
            await interaction.response.send_message("❌ Cor inválida! Use formato hexadecimal (ex: #FF0000 ou FF0000)", ephemeral=True)
            return
        
        # Cria a embed
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor_int
        )
        
        # Adiciona imagem se fornecida
        if url_foto:
            # Verifica se é uma URL válida
            if url_foto.startswith("http://") or url_foto.startswith("https://"):
                embed.set_image(url=url_foto)
            else:
                await interaction.response.send_message("❌ URL da foto inválida! Deve começar com http:// ou https://", ephemeral=True)
                return
        
        # Define footer com autor
        embed.set_footer(text=f"Enviado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        # Envia a embed
        try:
            await interaction.channel.send(embed=embed)
            await interaction.response.send_message("✅ Embed enviada com sucesso!", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Erro ao enviar embed: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Mensagens(bot))

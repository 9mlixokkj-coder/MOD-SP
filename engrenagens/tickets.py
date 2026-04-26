import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio
import json
import os

# Modal para motivo de fechamento
class FecharTicketModal(discord.ui.Modal, title="Fechar Ticket"):
    motivo = discord.ui.TextInput(
        label="Motivo do fechamento",
        style=discord.TextStyle.paragraph,
        placeholder="Descreva o motivo do fechamento...",
        required=True,
        max_length=1000
    )
    
    def __init__(self, bot, channel, interaction_user):
        super().__init__()
        self.bot = bot
        self.channel = channel
        self.interaction_user = interaction_user
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔒 Fechando ticket e gerando transcript...", ephemeral=True)
        
        config = self.bot.get_server_config(interaction.guild.id)
        
        # Carrega informações do ticket
        ticket_data_file = f"ticket_data_{self.channel.id}.json"
        ticket_info = {
            "nome_canal": self.channel.name,
            "fechado_por": self.interaction_user.id,
            "aberto_por": None,
            "tipo": "suporte",
            "horario_abertura": None,
            "motivo_fechamento": self.motivo.value
        }
        
        # Tenta carregar dados salvos do ticket
        if os.path.exists(ticket_data_file):
            with open(ticket_data_file, 'r', encoding='utf-8') as f:
                ticket_info.update(json.load(f))
        
        # Cria transcript completo do ticket
        messages = []
        async for message in self.channel.history(limit=500, oldest_first=True):
            timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
            content = message.content if message.content else "[Sem conteúdo de texto]"
            
            # Adiciona informações de anexos
            if message.attachments:
                attachments = ", ".join([f"{att.filename} ({att.url})" for att in message.attachments])
                content += f"\n[Anexos: {attachments}]"
            
            # Adiciona informações de embeds
            if message.embeds:
                content += f"\n[{len(message.embeds)} embed(s)]"
            
            messages.append(f"[{timestamp}] {message.author.name}: {content}")
        
        transcript = "\n".join(messages)
        
        # Calcula tempo de duração do ticket
        horario_fechamento = datetime.now()
        if ticket_info["horario_abertura"]:
            horario_abertura = datetime.fromisoformat(ticket_info["horario_abertura"])
            duracao = horario_fechamento - horario_abertura
            
            # Formata duração
            dias = duracao.days
            horas, resto = divmod(duracao.seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            
            if dias > 0:
                duracao_str = f"{dias}d {horas}h {minutos}m"
            elif horas > 0:
                duracao_str = f"{horas}h {minutos}m"
            else:
                duracao_str = f"{minutos}m {segundos}s"
        else:
            duracao_str = "Desconhecido"
            horario_abertura = datetime.now()
        
        # Envia DM para avaliação
        if ticket_info["aberto_por"]:
            try:
                user = await self.bot.fetch_user(ticket_info["aberto_por"])
                view = AvaliacaoView(self.bot, interaction.guild.id, ticket_info)
                embed = discord.Embed(
                    title="📊 Avalie o Atendimento",
                    description="Seu ticket foi fechado! Por favor, avalie o atendimento:",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Motivo do Fechamento", value=self.motivo.value, inline=False)
                await user.send(embed=embed, view=view)
            except:
                pass
        
        # Envia logs detalhadas
        if config["canal_logs"]:
            canal_logs = interaction.guild.get_channel(config["canal_logs"])
            if canal_logs:
                # Embed principal com informações do ticket
                log_embed = discord.Embed(
                    title="🔒 Ticket Fechado",
                    color=discord.Color.red(),
                    timestamp=horario_fechamento
                )
                log_embed.add_field(name="📋 Canal", value=self.channel.name, inline=True)
                log_embed.add_field(name="🎫 Tipo", value=ticket_info["tipo"], inline=True)
                log_embed.add_field(name="⏱️ Duração", value=duracao_str, inline=True)
                
                log_embed.add_field(
                    name="👤 Aberto por",
                    value=f"<@{ticket_info['aberto_por']}>" if ticket_info['aberto_por'] else "Desconhecido",
                    inline=True
                )
                log_embed.add_field(
                    name="🔒 Fechado por",
                    value=f"<@{ticket_info['fechado_por']}>",
                    inline=True
                )
                log_embed.add_field(
                    name="📅 Fechado em",
                    value=horario_fechamento.strftime("%d/%m/%Y às %H:%M:%S"),
                    inline=True
                )
                
                log_embed.add_field(
                    name="📝 Motivo do Fechamento",
                    value=self.motivo.value,
                    inline=False
                )
                
                await canal_logs.send(embed=log_embed)
                
                # Envia transcript em arquivo de texto
                if len(transcript) > 0:
                    # Salva transcript em arquivo com nome fixo
                    transcript_filename = "transcript.txt"
                    with open(transcript_filename, 'w', encoding='utf-8') as f:
                        f.write(f"TRANSCRIPT DO TICKET: {self.channel.name}\n")
                        f.write(f"Tipo: {ticket_info['tipo']}\n")
                        f.write(f"Aberto por: {ticket_info['aberto_por']}\n")
                        f.write(f"Fechado por: {ticket_info['fechado_por']}\n")
                        f.write(f"Aberto em: {ticket_info.get('horario_abertura', 'Desconhecido')}\n")
                        f.write(f"Fechado em: {horario_fechamento.isoformat()}\n")
                        f.write(f"Duração: {duracao_str}\n")
                        f.write(f"Motivo: {self.motivo.value}\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(transcript)
                    
                    # Envia arquivo
                    await canal_logs.send(
                        "📄 **Transcript Completo:**",
                        file=discord.File(transcript_filename)
                    )
                    
                    # Remove arquivo temporário
                    os.remove(transcript_filename)
        
        # Remove arquivo de dados do ticket
        if os.path.exists(ticket_data_file):
            os.remove(ticket_data_file)
        
        # Deleta o canal após 5 segundos
        await asyncio.sleep(5)
        await self.channel.delete()

# View para botões do ticket
class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.danger, custom_id="fechar_ticket", emoji="🔒")
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verifica se é admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem fechar tickets!", ephemeral=True)
            return
        
        # Abre modal para motivo de fechamento
        modal = FecharTicketModal(self.bot, interaction.channel, interaction.user)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Assumir", style=discord.ButtonStyle.primary, custom_id="assumir_ticket", emoji="✋")
    async def assumir_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem assumir tickets!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✋ Ticket Assumido",
            description=f"{interaction.user.mention} assumiu este ticket!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="Renomear", style=discord.ButtonStyle.secondary, custom_id="renomear_ticket", emoji="✏️")
    async def renomear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas administradores podem renomear tickets!", ephemeral=True)
            return
        
        modal = RenomearModal()
        await interaction.response.send_modal(modal)

# Modal para renomear ticket
class RenomearModal(discord.ui.Modal, title="Renomear Ticket"):
    novo_nome = discord.ui.TextInput(
        label="Novo nome do canal",
        placeholder="Digite o novo nome...",
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=self.novo_nome.value)
        await interaction.response.send_message(f"✏️ Canal renomeado para: `{self.novo_nome.value}`", ephemeral=True)

# View para avaliação do ticket
class AvaliacaoView(discord.ui.View):
    def __init__(self, bot, guild_id, ticket_info):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.ticket_info = ticket_info
        
        # Adiciona botões de 1 a 5 estrelas
        for i in range(1, 6):
            button = discord.ui.Button(
                label=f"{'⭐' * i}",
                style=discord.ButtonStyle.primary,
                custom_id=f"avaliar_{i}"
            )
            button.callback = self.criar_callback(i)
            self.add_item(button)
    
    def criar_callback(self, estrelas):
        async def callback(interaction: discord.Interaction):
            modal = AvaliacaoModal(self.bot, self.guild_id, self.ticket_info, estrelas)
            await interaction.response.send_modal(modal)
        return callback

# Modal para motivo da avaliação
class AvaliacaoModal(discord.ui.Modal, title="Motivo da Avaliação"):
    motivo = discord.ui.TextInput(
        label="Qual foi o motivo da sua avaliação?",
        style=discord.TextStyle.paragraph,
        placeholder="Descreva sua experiência...",
        max_length=1000
    )
    
    def __init__(self, bot, guild_id, ticket_info, estrelas):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        self.ticket_info = ticket_info
        self.estrelas = estrelas
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Obrigado pela avaliação!", ephemeral=True)
        
        # Envia avaliação para o canal de logs
        config = self.bot.get_server_config(self.guild_id)
        if config["canal_logs"]:
            guild = self.bot.get_guild(self.guild_id)
            canal_logs = guild.get_channel(config["canal_logs"])
            
            if canal_logs:
                embed = discord.Embed(
                    title="📊 Avaliação de Ticket",
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Canal", value=self.ticket_info["nome_canal"], inline=False)
                embed.add_field(name="Tipo", value=self.ticket_info["tipo"], inline=True)
                embed.add_field(name="Avaliação", value="⭐" * self.estrelas, inline=True)
                embed.add_field(name="Aberto por", value=f"<@{self.ticket_info['aberto_por']}>", inline=True)
                embed.add_field(name="Fechado por", value=f"<@{self.ticket_info['fechado_por']}>", inline=True)
                embed.add_field(name="Motivo", value=self.motivo.value, inline=False)
                
                await canal_logs.send(embed=embed)

# Select Menu para escolher tipo de ticket
class TipoTicketSelect(discord.ui.Select):
    def __init__(self, bot, tipos):
        self.bot = bot
        options = []
        for tipo in tipos:
            emoji_map = {
                "suporte": "🎫",
                "comprar": "💰",
                "vender": "🏪",
                "dúvida": "❓",
                "report": "⚠️"
            }
            options.append(
                discord.SelectOption(
                    label=tipo.capitalize(),
                    value=tipo,
                    emoji=emoji_map.get(tipo.lower(), "📋")
                )
            )
        
        super().__init__(
            placeholder="Selecione o tipo de ticket...",
            options=options,
            custom_id="tipo_ticket_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        config = self.bot.get_server_config(interaction.guild.id)
        
        if not config["categoria_ticket"]:
            await interaction.response.send_message("❌ Categoria de tickets não configurada!", ephemeral=True)
            return
        
        categoria = interaction.guild.get_channel(config["categoria_ticket"])
        if not categoria:
            await interaction.response.send_message("❌ Categoria não encontrada!", ephemeral=True)
            return
        
        # Verifica se usuário já tem ticket aberto
        for channel in categoria.channels:
            if f"ticket-{interaction.user.id}" in channel.name:
                await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
                return
        
        # Cria o canal do ticket
        config["ticket_counter"] += 1
        self.bot.save_config()
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        tipo_selecionado = self.values[0]
        nome_canal = f"ticket-{interaction.user.id}-{tipo_selecionado}"
        
        canal_ticket = await categoria.create_text_channel(
            name=nome_canal,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user.name} | Tipo: {tipo_selecionado}"
        )
        
        # Salva informações do ticket para usar ao fechar
        ticket_data = {
            "aberto_por": interaction.user.id,
            "tipo": tipo_selecionado,
            "horario_abertura": datetime.now().isoformat(),
            "nome_canal": nome_canal
        }
        
        ticket_data_file = f"ticket_data_{canal_ticket.id}.json"
        with open(ticket_data_file, 'w', encoding='utf-8') as f:
            json.dump(ticket_data, f, indent=4, ensure_ascii=False)
        
        # Envia mensagem inicial no ticket
        embed = discord.Embed(
            title=f"🎫 Ticket - {tipo_selecionado.capitalize()}",
            description=f"Olá {interaction.user.mention}!\n\nSeu ticket foi criado com sucesso. Um membro da equipe irá atendê-lo em breve.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Ticket #{config['ticket_counter']}")
        
        view = TicketView(self.bot)
        await canal_ticket.send(f"{interaction.user.mention}", embed=embed, view=view)
        
        await interaction.response.send_message(f"✅ Ticket criado: {canal_ticket.mention}", ephemeral=True)
        
        # Log de abertura
        if config["canal_logs"]:
            canal_logs = interaction.guild.get_channel(config["canal_logs"])
            if canal_logs:
                log_embed = discord.Embed(
                    title="📝 Ticket Aberto",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="Usuário", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Canal", value=canal_ticket.mention, inline=True)
                log_embed.add_field(name="Tipo", value=tipo_selecionado, inline=True)
                await canal_logs.send(embed=log_embed)

class PainelTicketView(discord.ui.View):
    def __init__(self, bot, tipos):
        super().__init__(timeout=None)
        self.add_item(TipoTicketSelect(bot, tipos))

# Cog de Tickets
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setcategoria", description="Define a categoria onde os tickets serão criados")
    @app_commands.describe(categoria="A categoria para os tickets")
    async def setcategoria(self, interaction: discord.Interaction, categoria: discord.CategoryChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.bot.get_server_config(interaction.guild.id)
        config["categoria_ticket"] = categoria.id
        self.bot.save_config()
        
        await interaction.response.send_message(f"✅ Categoria de tickets definida: {categoria.mention}", ephemeral=True)
    
    @app_commands.command(name="setcanal", description="Define o canal do painel de tickets")
    @app_commands.describe(canal="O canal para o painel")
    async def setcanal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.bot.get_server_config(interaction.guild.id)
        config["canal_painel"] = canal.id
        self.bot.save_config()
        
        await interaction.response.send_message(f"✅ Canal do painel definido: {canal.mention}", ephemeral=True)
    
    @app_commands.command(name="setlogs", description="Define o canal de logs dos tickets")
    @app_commands.describe(canal="O canal para logs")
    async def setlogs(self, interaction: discord.Interaction, canal: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.bot.get_server_config(interaction.guild.id)
        config["canal_logs"] = canal.id
        self.bot.save_config()
        
        await interaction.response.send_message(f"✅ Canal de logs definido: {canal.mention}", ephemeral=True)
    
    @app_commands.command(name="painel", description="Cria o painel de tickets")
    @app_commands.describe(
        titulo="Título do painel",
        descricao="Descrição do painel",
        cor="Cor em hexadecimal (ex: #FF0000)",
        tipos="Tipos de ticket separados por vírgula (ex: suporte,comprar,vender)"
    )
    async def painel(self, interaction: discord.Interaction, titulo: str, descricao: str, cor: str, tipos: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Você precisa ser administrador!", ephemeral=True)
            return
        
        config = self.bot.get_server_config(interaction.guild.id)
        
        if not config["canal_painel"]:
            await interaction.response.send_message("❌ Configure o canal do painel primeiro com /setcanal", ephemeral=True)
            return
        
        canal = interaction.guild.get_channel(config["canal_painel"])
        if not canal:
            await interaction.response.send_message("❌ Canal do painel não encontrado!", ephemeral=True)
            return
        
        # Processa cor
        try:
            cor_int = int(cor.replace("#", ""), 16)
        except:
            cor_int = 0x5865F2
        
        # Processa tipos
        lista_tipos = [t.strip() for t in tipos.split(",")]
        
        # Cria embed do painel
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor_int
        )
        embed.set_footer(text="Selecione uma opção abaixo para abrir um ticket")
        
        view = PainelTicketView(self.bot, lista_tipos)
        
        await canal.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Painel criado com sucesso!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))

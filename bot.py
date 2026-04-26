import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class TicketBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.config_file = "config.json"
        self.load_config()
        
    def load_config(self):
        """Carrega configurações do servidor"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}
            self.save_config()
    
    def save_config(self):
        """Salva configurações do servidor"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get_server_config(self, guild_id: int):
        """Obtém configuração de um servidor específico"""
        guild_id = str(guild_id)
        if guild_id not in self.config:
            self.config[guild_id] = {
                "categoria_ticket": None,
                "canal_painel": None,
                "canal_logs": None,
                "ticket_counter": 0
            }
            self.save_config()
        return self.config[guild_id]
    
    async def setup_hook(self):
        """Carrega extensões (cogs)"""
        try:
            await self.load_extension("engrenagens.tickets")
            print("✅ Módulo de tickets carregado")
            await self.load_extension("engrenagens.moderacao")
            print("✅ Módulo de moderação carregado")
            await self.load_extension("engrenagens.mensagens")
            print("✅ Módulo de mensagens carregado")
            await self.load_extension("engrenagens.utilitarios")
            print("✅ Módulo de utilitários carregado")
            await self.load_extension("engrenagens.automod")
            print("✅ Módulo de automoderação carregado")
            await self.tree.sync()
            print("✅ Comandos sincronizados!")
        except Exception as e:
            print(f"❌ Erro ao carregar módulos: {e}")

bot = TicketBot()

@bot.event
async def on_ready():
    print('=' * 50)
    print(f'🤖 Bot conectado como {bot.user}')
    print(f'🆔 ID: {bot.user.id}')
    print(f'🌐 Servidores: {len(bot.guilds)}')
    print('=' * 50)

    # COLOCA ISSO AQUI
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

    # status do bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="by dn"
        )
    )
    
    # Define status do bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="tickets e moderação"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Tratamento global de erros"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Parâmetro faltando! Verifique o uso correto do comando.")
    else:
        print(f"Erro: {error}")

# Obtém o token do .env ou usa o valor padrão
TOKEN = os.getenv("DISCORD_TOKEN", "SEU_TOKEN_AQUI")

if __name__ == "__main__":
    if TOKEN == "SEU_TOKEN_AQUI":
        print("❌ ERRO: Configure o token do bot!")
        print("📝 Crie um arquivo .env com: DISCORD_TOKEN=seu_token")
        print("📝 Ou edite bot.py e substitua SEU_TOKEN_AQUI")
    else:
        print("🚀 Iniciando bot...")
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ Token inválido! Verifique suas credenciais.")
        except Exception as e:
            print(f"❌ Erro ao iniciar: {e}")

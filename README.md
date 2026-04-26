# 🤖 Bot de Tickets e Moderação Discord

Bot completo de Discord em Python com sistema de tickets avançado e comandos de moderação.

## 📋 Funcionalidades

### Sistema de Tickets
- ✅ Criação de tickets via menu dropdown personalizado
- ✅ Categorias e tipos de tickets configuráveis (suporte, comprar, vender, etc.)
- ✅ Botões interativos no ticket (Fechar, Assumir, Renomear)
- ✅ **Motivo obrigatório** ao fechar ticket (via modal)
- ✅ Sistema de avaliação por DM após fechamento (1-5 estrelas + motivo)
- ✅ **Logs completas e detalhadas:**
  - 👤 Usuário que abriu e fechou
  - ⏱️ Tempo de duração do ticket
  - 📅 Data e horário de fechamento
  - 📝 Motivo do fechamento
  - 📄 **Transcript completo** em arquivo .txt (nome fixo: transcript.txt)
  - ⭐ Avaliação do usuário
- ✅ Permissões controladas (apenas admins podem gerenciar tickets)

### Sistema de Moderação
- 🔨 **Ban**: Banir membros com motivo
- ✅ **Unban**: Desbanir membros (requer ID do usuário)
- 🔇 **Mute**: Silenciar membros temporariamente
- 🔊 **Unmute**: Remover silenciamento
- 📊 **Punições**: Ver histórico de mutes de um membro
- 📊 Logs automáticos de ações de moderação

### Sistema de Utilitários
- 🔒 **Lock**: Trancar canais (bloquear envio de mensagens)
- 🔓 **Unlock**: Destrancar canais
- 🧹 **Clear**: Limpar mensagens (1-1000)
- 👤 **UserInfo**: Informações detalhadas sobre usuários
  - Data de criação da conta
  - Data de entrada no servidor
  - Número de mensagens enviadas
  - Cargos do membro
  - Histórico de punições
- 📊 **ServerInfo**: Informações completas do servidor
  - Data de criação
  - Membros totais e online
  - Impulsos (boosts)
  - Estatísticas de canais

### Sistema de Automoderação
- 🚫 **AutoMod Add**: Bloquear palavras específicas
- ✅ **AutoMod Remove**: Remover palavras da lista de bloqueio
- 📋 **AutoMod Painel**: Ver todas palavras bloqueadas
- 🔗 **AutoMod Link**: Bloquear links em canais específicos
- ✅ **AutoMod Link Remove**: Permitir links em canais
- 🤖 Detecção automática e remoção de mensagens proibidas
- 📊 Logs de violações de automoderação

### Comandos de Mensagens
- 💬 **Mensagem**: Enviar mensagens simples
- 📝 **Embed**: Criar embeds personalizadas com título, descrição, cor e imagem

## 🚀 Instalação

### 1. Pré-requisitos
- Python 3.8 ou superior
- Uma conta Discord
- Um servidor Discord onde você seja administrador

### 2. Criar o Bot no Discord

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome ao seu bot e clique em "Create"
4. Vá na aba "Bot" no menu lateral
5. Clique em "Add Bot" e confirme
6. **Ative as seguintes Privileged Gateway Intents:**
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
7. Copie o Token do bot (clique em "Reset Token" se necessário)

### 3. Convidar o Bot para seu Servidor

1. No Developer Portal, vá em "OAuth2" > "URL Generator"
2. Selecione os seguintes scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Selecione as seguintes permissões:
   - ✅ Administrator (ou configure manualmente as permissões necessárias)
4. Copie a URL gerada e abra no navegador
5. Selecione seu servidor e autorize

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar o Token

Abra o arquivo `bot.py` e substitua `"SEU_TOKEN_AQUI"` pelo token do seu bot:

```python
TOKEN = "seu_token_aqui"
```

**IMPORTANTE**: Nunca compartilhe seu token! Mantenha-o em segredo.

### 6. Executar o Bot

```bash
python bot.py
```

Se tudo estiver correto, você verá:
```
Bot conectado como NomeDoBot#1234
ID: 123456789
------
Comandos sincronizados!
```

## 📖 Como Usar

### Configuração Inicial

1. **Configurar Categoria de Tickets**
   ```
   /setcategoria categoria: [selecione a categoria]
   ```
   Define onde os canais de ticket serão criados.

2. **Configurar Canal de Logs**
   ```
   /setlogs canal: [selecione o canal]
   ```
   Define onde as logs serão enviadas.

3. **Configurar Canal do Painel**
   ```
   /setcanal canal: [selecione o canal]
   ```
   Define onde o painel de tickets será exibido.

4. **Criar Painel de Tickets**
   ```
   /painel 
     titulo: Sistema de Tickets
     descricao: Selecione uma opção para abrir um ticket
     cor: #5865F2
     tipos: suporte,comprar,vender
   ```

### Comandos de Tickets

| Comando | Descrição | Parâmetros |
|---------|-----------|------------|
| `/setcategoria` | Define categoria dos tickets | categoria |
| `/setcanal` | Define canal do painel | canal |
| `/setlogs` | Define canal de logs | canal |
| `/painel` | Cria painel de tickets | titulo, descricao, cor, tipos |

**Exemplo de uso do /painel:**
```
/painel 
  titulo: 🎫 Central de Atendimento
  descricao: Bem-vindo! Selecione o tipo de atendimento que você precisa:
  cor: #00FF00
  tipos: suporte,dúvida,comprar,vender,report
```

### Botões do Ticket

Dentro de cada ticket, há 3 botões disponíveis (apenas para administradores):

- 🔒 **Fechar**: Abre modal para motivo, fecha o ticket, gera transcript e envia avaliação
- ✋ **Assumir**: Marca que um admin assumiu o atendimento
- ✏️ **Renomear**: Permite renomear o canal do ticket

### Comandos de Moderação

| Comando | Descrição | Parâmetros | Permissão Necessária |
|---------|-----------|------------|---------------------|
| `/ban` | Bane um membro | membro, motivo | Ban Members |
| `/unban` | Desbane um usuário | user_id, motivo | Ban Members |
| `/mute` | Silencia um membro | membro, motivo, duracao | Moderate Members |
| `/unmute` | Remove silenciamento | membro | Moderate Members |
| `/punições` | Ver histórico de mutes | membro | Nenhuma |

### Comandos de Utilitários

| Comando | Descrição | Parâmetros | Permissão Necessária |
|---------|-----------|------------|---------------------|
| `/lock` | Tranca um canal | canal (opcional) | Manage Channels |
| `/unlock` | Destranca um canal | canal (opcional) | Manage Channels |
| `/clear` | Limpa mensagens (1-1000) | quantidade | Manage Messages |
| `/userinfo` | Informações de usuário | membro (opcional) | Nenhuma |
| `/serverinfo` | Informações do servidor | - | Nenhuma |

### Comandos de Automoderação

| Comando | Descrição | Parâmetros | Permissão Necessária |
|---------|-----------|------------|---------------------|
| `/automod_add` | Bloqueia uma palavra | palavra | Administrator |
| `/automod_remove` | Desbloqueia uma palavra | palavra | Administrator |
| `/automod_painel` | Lista palavras bloqueadas | - | Administrator |
| `/automod_link` | Bloqueia links em canal | canal | Administrator |
| `/automod_link_remove` | Permite links em canal | canal | Administrator |

**Exemplos:**
```
/ban membro: @Usuario motivo: Spam
/unban user_id: 123456789 motivo: Apelação aceita
/mute membro: @Usuario motivo: Flood duracao: 30
/unmute membro: @Usuario
```

**Nota**: Para usar `/unban`, você precisa do ID do usuário banido. Para obter o ID:
1. Vá em Configurações do Servidor > Banimentos
2. Clique com botão direito no usuário
3. Copie o ID

### Comandos de Mensagens

| Comando | Descrição | Parâmetros | Permissão Necessária |
|---------|-----------|------------|---------------------|
| `/mensagem` | Envia mensagem simples | descricao | Manage Messages |
| `/embed` | Envia embed personalizada | titulo, descricao, cor, url_foto | Manage Messages |

**Exemplos:**
```
/mensagem descricao: Bem-vindos ao servidor!

/embed 
  titulo: Regras do Servidor
  descricao: 1. Seja respeitoso\n2. Sem spam\n3. Divirta-se!
  cor: #FF0000
  url_foto: https://exemplo.com/imagem.png
```

## 🎨 Cores Hexadecimais

Algumas cores populares para usar:

- 🔴 Vermelho: `#FF0000`
- 🟢 Verde: `#00FF00`
- 🔵 Azul: `#0000FF`
- 🟣 Roxo: `#9B59B6`
- 🟡 Amarelo: `#FFFF00`
- 🟠 Laranja: `#FFA500`
- ⚫ Discord Blurple: `#5865F2`

## 📊 Sistema de Avaliação e Logs Completas

### Fechamento de Ticket

Quando um administrador fecha um ticket:

1. **Modal de Fechamento**: Aparece solicitando o motivo do fechamento
2. **Geração de Transcript**: Todo histórico do ticket é salvo automaticamente
3. **Notificação ao Usuário**: DM enviada com botões de avaliação (1-5 estrelas)
4. **Logs Detalhadas**: Enviadas ao canal de logs configurado

### Logs de Fechamento

As logs incluem todas estas informações:

**Embed Principal:**
- 📋 Nome do canal do ticket
- 🎫 Tipo do ticket (suporte, comprar, vender, etc.)
- ⏱️ **Duração total** (calculado automaticamente - ex: "2h 15m", "1d 3h 45m")
- 👤 Usuário que abriu o ticket
- 🔒 Administrador que fechou o ticket
- 📅 **Data e horário exato** do fechamento
- 📝 **Motivo do fechamento** (fornecido pelo admin)

**Arquivo de Transcript:**
- 📄 Arquivo .txt anexado automaticamente
- Contém todo o histórico de mensagens com timestamps
- Inclui informações de anexos e embeds
- Formato legível e organizado
- Nome do arquivo: `transcript_ticket-nome_AAAAMMDD_HHMMSS.txt`

### Avaliação do Usuário

Após o ticket ser fechado, o usuário recebe:

1. DM com botões de 1 a 5 estrelas (⭐)
2. Ao clicar, abre formulário para motivo da avaliação
3. Avaliação é registrada no canal de logs:
   - ⭐ Número de estrelas
   - 📝 Motivo detalhado fornecido
   - 👤 Usuário que avaliou
   - 🔒 Moderador avaliado
   - 🎫 Tipo do ticket

## 🔧 Estrutura de Arquivos

```
bot/
├── bot.py              # Arquivo principal
├── config.json         # Configurações (gerado automaticamente)
├── requirements.txt    # Dependências
├── README.md          # Este arquivo
└── cogs/              # Módulos do bot
    ├── tickets.py     # Sistema de tickets
    ├── moderacao.py   # Comandos de moderação
    └── mensagens.py   # Comandos de mensagens
```

## ⚙️ Configuração Avançada

### Usando .env para Token (Recomendado)

1. Crie um arquivo `.env` na raiz do projeto:
```env
DISCORD_TOKEN=seu_token_aqui
```

2. Modifique `bot.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
```

### Personalização

Você pode personalizar:
- Emojis dos botões em `cogs/tickets.py`
- Cores padrão das embeds
- Mensagens do sistema
- Tipos de tickets padrão

## 🛠️ Troubleshooting

### Bot não conecta
- Verifique se o token está correto
- Confirme que as intents estão ativadas no Developer Portal

### Comandos não aparecem
- Aguarde alguns minutos para sincronização
- Verifique se o bot tem permissão de "Use Application Commands"

### Botões não funcionam
- Confirme que o bot tem permissões de "Send Messages" e "Embed Links"
- Verifique se as views estão sendo carregadas corretamente

### Erros de permissão
- O bot precisa de permissões administrativas ou configure manualmente:
  - Manage Channels (criar/deletar canais de ticket)
  - Manage Messages
  - Ban Members
  - Moderate Members
  - Send Messages
  - Embed Links

## 📝 Logs

Todas as ações importantes são registradas no canal de logs configurado com informações detalhadas:

**Tickets:**
- 📝 Abertura de tickets (usuário, tipo, canal)
- 🔒 Fechamento de tickets (completo com duração, motivo, transcript)
- ⭐ Avaliações de atendimento (estrelas e feedback)

**Moderação:**
- 🔨 Banimentos (usuário, motivo, moderador)
- ✅ Desbanimentos (usuário, motivo, moderador)
- 🔇 Silenciamentos (usuário, duração, motivo)

Cada log inclui:
- 📅 Timestamp com data e hora
- 👤 Usuários envolvidos
- 📋 Detalhes da ação
- 🎨 Embeds coloridas para fácil visualização

## 🔐 Segurança

- Nunca compartilhe o token do bot
- Use `.env` para armazenar informações sensíveis
- Não adicione `config.json` ou `.env` ao controle de versão
- Revise permissões antes de usar em produção

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para modificar e usar como desejar.

## 💡 Suporte

Se encontrar problemas ou tiver sugestões, sinta-se à vontade para criar uma issue ou contribuir com o projeto!

## 🎯 Próximas Funcionalidades

- [ ] Sistema de warnings
- [ ] Comandos de diversão
- [ ] Sistema de níveis/XP
- [ ] Backup automático de configurações
- [ ] Dashboard web

# 📋 Lista Completa de Comandos

## 🎫 TICKETS (4 comandos)

```
/setcategoria  - Define categoria dos tickets
/setcanal      - Define canal do painel  
/setlogs       - Define canal de logs
/painel        - Cria painel de tickets personalizado
```

## 🔨 MODERAÇÃO (5 comandos)

```
/ban       - Bane membro (requer motivo)
/unban     - Desbane usando ID do usuário
/mute      - Silencia temporariamente (em minutos)
/unmute    - Remove silenciamento
/punições  - Ver histórico de mutes do membro
```

## 🔧 UTILITÁRIOS (5 comandos)

```
/lock        - Tranca canal (bloqueia mensagens)
/unlock      - Destranca canal
/clear       - Limpa mensagens (1-1000)
/userinfo    - Info completa do usuário
/serverinfo  - Info completa do servidor
```

## 🚫 AUTOMODERAÇÃO (5 comandos)

```
/automod_add           - Bloqueia palavra
/automod_remove        - Desbloqueia palavra
/automod_painel        - Lista palavras bloqueadas
/automod_link          - Bloqueia links em canal
/automod_link_remove   - Permite links em canal
```

## 💬 MENSAGENS (2 comandos)

```
/mensagem  - Envia mensagem simples
/embed     - Cria embed personalizada (título, descrição, cor, foto)
```

---

# 🎯 TOTAL: 21 COMANDOS SLASH

---

## ⚡ Comandos Mais Usados

### Configuração Inicial:
```
/setcategoria categoria: Tickets
/setlogs canal: #logs
/setcanal canal: #abrir-ticket
/painel titulo: Suporte descricao: Abra um ticket cor: #5865F2 tipos: suporte,dúvida
```

### Moderação Rápida:
```
/mute membro: @Usuario motivo: Spam duracao: 30
/clear quantidade: 50
/lock
```

### Automoderação Básica:
```
/automod_add palavra: spam
/automod_link canal: #chat
/automod_painel
```

### Informações:
```
/userinfo membro: @Usuario
/serverinfo
/punições membro: @Usuario
```

---

## 📊 Por Categoria

| Categoria | Comandos | Permissões |
|-----------|----------|------------|
| 🎫 Tickets | 4 | Admin |
| 🔨 Moderação | 5 | Moderador+ |
| 🔧 Utilitários | 5 | Variadas |
| 🚫 AutoMod | 5 | Admin |
| 💬 Mensagens | 2 | Manage Messages |

**Total: 21 comandos**

---

## 🎨 Atalhos Úteis

### Limpar e Trancar:
```
/clear quantidade: 100
/lock
```

### Verificar e Punir:
```
/userinfo membro: @Suspeito
/punições membro: @Suspeito
/mute membro: @Suspeito motivo: Comportamento suspeito duracao: 60
```

### Configurar AutoMod Completo:
```
/automod_add palavra: spam
/automod_add palavra: scam
/automod_add palavra: hack
/automod_link canal: #geral
/automod_link canal: #apresentações
```

---

## 🔍 Busca Rápida

**Quero trancar um canal:** `/lock`  
**Quero limpar spam:** `/clear`  
**Quero ver info de alguém:** `/userinfo`  
**Quero bloquear palavra:** `/automod_add`  
**Quero bloquear links:** `/automod_link`  
**Quero silenciar alguém:** `/mute`  
**Quero banir alguém:** `/ban`  
**Quero ver punições:** `/punições`  
**Quero criar ticket:** Configure com `/painel`  
**Quero enviar embed:** `/embed`

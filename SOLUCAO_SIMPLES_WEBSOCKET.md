# 🎯 SOLUÇÃO SIMPLES - AUTO-STOP INTELIGENTE

## ✅ **LÓGICA (Aprovada pelo usuário):**

```
Internet OK → Bot pesca normalmente ✅
Internet cai < 10s → Tenta reconectar (3x com 2s entre cada) ✅
Internet cai > 10s → PARA BOT + Avisa usuário ⚠️
```

---

## 🔧 **IMPLEMENTAÇÃO:**

### **1. Adicionar no ws_client.py:**

```python
class WebSocketClient:
    def __init__(self, ...):
        # ... código existente ...

        # ✅ NOVO: Configuração de auto-stop
        self.auto_stop_enabled = True
        self.max_reconnect_time = 10  # segundos
        self.on_connection_lost_callback = None

    def register_connection_lost_callback(self, callback):
        """
        Callback chamado quando conexão é perdida por muito tempo

        Args:
            callback: função que para o bot
        """
        self.on_connection_lost_callback = callback

    async def _connect_and_listen(self):
        """Conectar ao servidor e escutar mensagens"""

        while self.running:
            try:
                # ... código existente de conexão ...

            except Exception as e:
                self.connected = False
                logger.error(f"❌ Erro na conexão: {e}")

                if self.running:
                    self.reconnect_attempts += 1

                    # ✅ NOVO: Auto-stop se não reconectar rápido
                    if self.reconnect_attempts == 1:
                        # Primeira tentativa → Tentar reconectar rápido
                        self.reconnect_start_time = time.time()

                    elapsed_time = time.time() - self.reconnect_start_time

                    if elapsed_time > self.max_reconnect_time:
                        # ❌ Passou de 10s tentando → PARAR BOT
                        _safe_print("=" * 70)
                        _safe_print("❌ CONEXÃO PERDIDA POR MUITO TEMPO")
                        _safe_print("=" * 70)
                        _safe_print(f"   Tempo tentando reconectar: {elapsed_time:.0f}s")
                        _safe_print(f"   Limite: {self.max_reconnect_time}s")
                        _safe_print("   🛑 Bot será pausado automaticamente")
                        _safe_print("=" * 70)

                        # Chamar callback para parar bot
                        if self.on_connection_lost_callback:
                            self.on_connection_lost_callback()

                        self.running = False
                        break

                    # Ainda dentro do limite → Continuar tentando
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        wait_time = 2  # 2s entre tentativas (fixo)
                        _safe_print(f"🔄 Reconectando em {wait_time}s... (tentativa {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                        await asyncio.sleep(wait_time)
                    else:
                        _safe_print(f"❌ Máximo de tentativas atingido")
                        self.running = False
                        break
```

---

### **2. Adicionar no fishing_engine.py:**

```python
class FishingEngine:
    def __init__(self, ...):
        # ... código existente ...

    def on_server_connection_lost(self):
        """
        Callback chamado quando servidor perde conexão por muito tempo

        AÇÕES:
        1. Pausa o bot automaticamente
        2. Mostra popup de aviso
        3. Aguarda usuário reconectar e apertar F9
        """
        _safe_print("\n" + "=" * 70)
        _safe_print("🛑 SERVIDOR DESCONECTADO - BOT PAUSADO")
        _safe_print("=" * 70)

        # Pausar bot
        self.pause()

        # Mostrar popup (se UI disponível)
        if hasattr(self, 'root'):
            try:
                from tkinter import messagebox
                self.root.after(0, lambda: messagebox.showwarning(
                    "Servidor Desconectado",
                    "Conexão com servidor foi perdida!\n\n"
                    "O bot foi pausado automaticamente.\n\n"
                    "Passos:\n"
                    "1. Verifique sua conexão de internet\n"
                    "2. Aguarde alguns segundos\n"
                    "3. Pressione F9 para retomar\n\n"
                    "Nota: O servidor tentará reconectar automaticamente."
                ))
            except:
                pass

        _safe_print("💡 Para retomar:")
        _safe_print("   1. Verifique internet")
        _safe_print("   2. Pressione F9")
        _safe_print("=" * 70)
```

---

### **3. Conectar tudo no main.py:**

```python
# No main.py, após conectar WebSocket:

if ws_client and ws_client.is_connected():
    # ... código existente ...

    # ✅ NOVO: Registrar callback de auto-stop
    ws_client.register_connection_lost_callback(
        fishing_engine.on_server_connection_lost
    )

    _safe_print("   🛡️ Auto-stop ativado (timeout: 10s)")
```

---

## 📊 **CENÁRIOS DE TESTE:**

### **Cenário 1: Lag Rápido (2s)**
```
1. Internet oscila (2s offline)
2. WebSocket detecta desconexão
3. Tenta reconectar (tentativa 1)
4. Sucesso! ✅
5. Bot continua pescando normalmente
6. Usuário nem percebe
```

### **Cenário 2: Queda Média (8s)**
```
1. Internet cai (8s offline)
2. WebSocket detecta desconexão
3. Tenta reconectar:
   - Tentativa 1: Falha (2s)
   - Tentativa 2: Falha (4s)
   - Tentativa 3: Falha (6s)
   - Tentativa 4: Sucesso! ✅ (8s)
4. Reconectado dentro de 10s
5. Bot continua pescando
```

### **Cenário 3: Queda Longa (> 10s)**
```
1. Internet cai completamente
2. WebSocket detecta desconexão
3. Tenta reconectar por 10s:
   - Tentativa 1-5: Todas falham
4. Passou de 10s → PARA BOT ⚠️
5. Popup aparece:
   "Servidor desconectado. Bot pausado."
6. Usuário vê o aviso
7. Corrige internet
8. Pressiona F9 para retomar
```

---

## ⚙️ **CONFIGURAÇÕES POSSÍVEIS:**

```python
# No config.json (futuro):
"websocket": {
    "auto_stop_enabled": true,        # Habilitar auto-stop
    "max_reconnect_time": 10,         # Tempo máximo (segundos)
    "max_reconnect_attempts": 5,      # Tentativas máximas
    "retry_interval": 2               # Segundos entre tentativas
}
```

---

## ✅ **BENEFÍCIOS:**

1. ✅ **Simples** - Lógica clara e direta
2. ✅ **Robusto** - Não perde tempo pescando offline
3. ✅ **UX Melhor** - Usuário sabe o que aconteceu
4. ✅ **Sem Complexidade** - Sem queue, sem cache, sem overkill
5. ✅ **Testável** - Fácil de testar (desligar WiFi)

---

## 🎯 **CONCLUSÃO:**

**Implementar APENAS:**
- ✅ Retry rápido (10s máximo)
- ✅ Auto-stop se não reconectar
- ✅ Popup de aviso

**Esquecer:**
- ❌ Queue offline (complexo)
- ❌ Cache de token (marginal)
- ❌ Outras otimizações (overkill)

**Resultado:**
- 🎯 Solução simples e eficaz
- 🎯 Fácil de entender
- 🎯 Fácil de manter

---

## 💭 **FILOSOFIA:**

> "Melhor parar e avisar do que continuar errado"
>
> "Keep it simple, stupid (KISS)"

---

## ❓ **QUER QUE EU IMPLEMENTE ISSO?**

Implementação estimada:
- ⏱️ 30-45 minutos
- 📝 3 arquivos modificados
- ✅ Simples e direto

**Implementar agora?**

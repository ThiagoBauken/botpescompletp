"""
PATCH: Logs Ultra-Detalhados para Debug do Mouse
=================================================

Este arquivo contém os trechos que devem ser SUBSTITUÍDOS nos arquivos:
- core/arduino_input_manager.py
- core/chest_manager.py
- core/feeding_system.py

Para diferenciar:
🎮 [ARDUINO] = Movimento via Arduino HID
🖱️ [PYAUTOGUI] = Movimento via PyAutoGUI (fallback)
📍 = Posição atual
🎯 = Posição destino
➡️ = Delta/movimento
🔧 = Correção de erro
"""

# ==============================================================================
# ARQUIVO: core/arduino_input_manager.py
# ==============================================================================

# ------------------------------------------------------------------------------
# FUNÇÃO: move_to() - Linha ~582
# SUBSTITUIR O TRECHO COMPLETO desde "# Obter posição atual REAL" até "if abs(error_x) > 15"
# ------------------------------------------------------------------------------

MOVE_TO_LOGS = '''
            # Obter posição atual REAL
            current_x, current_y = self._get_current_mouse_position()

            # 📍 LOG DETALHADO: Posição antes do movimento
            _safe_print(f"🎮 [ARDUINO] MOVIMENTO REQUISITADO:")
            _safe_print(f"   📍 Atual: ({current_x}, {current_y})")
            _safe_print(f"   🎯 Destino: ({x}, {y})")

            # Calcular delta (movimento relativo)
            delta_x = x - current_x
            delta_y = y - current_y
            _safe_print(f"   ➡️  Delta: ({delta_x:+d}, {delta_y:+d})")

            # Se já está na posição, não fazer nada
            if abs(delta_x) < 5 and abs(delta_y) < 5:
                _safe_print(f"   ✅ Já na posição (delta < 5px)")
                self.mouse_state['last_position'] = (x, y)
                return True

            # Movimento em um único comando se possível
            distance = max(abs(delta_x), abs(delta_y))
            _safe_print(f"   📏 Distância: {distance}px")

            if distance < 127:  # Arduino suporta até ±127 por comando
                # Movimento direto
                _safe_print(f"   🚀 MOUSEMOVE:{delta_x}:{delta_y}")
                self._send_command_fast(f"MOUSEMOVE:{delta_x}:{delta_y}")
                time.sleep(0.05)
            else:
                # Movimento em 3 passos rápidos
                steps = 3
                step_x = delta_x // steps
                step_y = delta_y // steps
                _safe_print(f"   🚀 {steps} PASSOS: ({step_x}, {step_y}) cada")

                for i in range(steps):
                    _safe_print(f"      Passo {i+1}: MOUSEMOVE:{step_x}:{step_y}")
                    self._send_command_fast(f"MOUSEMOVE:{step_x}:{step_y}")
                time.sleep(0.05)

                # Ajuste fino
                remainder_x = delta_x - (step_x * steps)
                remainder_y = delta_y - (step_y * steps)
                if remainder_x != 0 or remainder_y != 0:
                    _safe_print(f"      Ajuste: MOUSEMOVE:{remainder_x}:{remainder_y}")
                    self._send_command_fast(f"MOUSEMOVE:{remainder_x}:{remainder_y}")
                    time.sleep(0.05)

            # ✅ CORREÇÃO: Verificar se chegou no lugar certo
            if PYAUTOGUI_AVAILABLE:
                time.sleep(0.1)
                actual_x, actual_y = self._get_current_mouse_position()
                _safe_print(f"   🔍 Verificação:")
                _safe_print(f"      Esperado: ({x}, {y})")
                _safe_print(f"      Real: ({actual_x}, {actual_y})")

                error_x = x - actual_x
                error_y = y - actual_y
                _safe_print(f"      Erro: ({error_x:+d}, {error_y:+d})")

                # Se erro > 15 pixels, corrigir
                if abs(error_x) > 15 or abs(error_y) > 15:
                    _safe_print(f"   🔧 CORREÇÃO (erro > 15px)")
'''

# ------------------------------------------------------------------------------
# FUNÇÃO: calibrate_mouseto() - Linha ~545
# SUBSTITUIR print simples por logs detalhados
# ------------------------------------------------------------------------------

CALIBRATE_MOUSETO_LOGS = '''
        try:
            # LOG DETALHADO: Antes de calibrar
            current_x, current_y = self._get_current_mouse_position()
            _safe_print(f"")
            _safe_print(f"🎯 [ARDUINO] CALIBRANDO MOUSETO:")
            _safe_print(f"   📍 Posição atual do cursor: ({current_x}, {current_y})")
            _safe_print(f"   🔄 Sincronizando MouseTo para: ({x}, {y})")

            command = f"RESET_POS:{x}:{y}"
            _safe_print(f"   📤 Enviando: {command}")

            response = self._send_command(command, timeout=5.0)
            _safe_print(f"   📥 Resposta: {response}")

            if response and "OK:RESET_POS" in response:
                self.mouse_state['last_position'] = (x, y)
                _safe_print(f"   ✅ MouseTo calibrado!")
                _safe_print(f"   ℹ️  Próximos movimentos serão calculados a partir de ({x}, {y})")
                _safe_print(f"")
                return True
            else:
'''

# ------------------------------------------------------------------------------
# FUNÇÃO: click() - Linha ~452
# ADICIONAR log de click com posição
# ------------------------------------------------------------------------------

CLICK_LOGS_BEFORE = '''
    def click(self, x: Optional[int] = None, y: Optional[int] = None,
              button: str = 'left') -> bool:
        """Click do mouse (com movimento opcional)"""
        _safe_print(f"🖱️  [ARDUINO] CLICK requisitado:")
        _safe_print(f"   Posição: ({x}, {y})" if x and y else "   Posição: ATUAL")
        _safe_print(f"   Botão: {button}")

        # Se coordenadas fornecidas, mover mouse primeiro
        if x is not None and y is not None:
            if not self.move_to(x, y):
                _safe_print(f"⚠️ Falha ao mover mouse para ({x}, {y})")
                return False
            time.sleep(0.05)
'''

# ==============================================================================
# ARQUIVO: core/chest_manager.py
# ==============================================================================

# ------------------------------------------------------------------------------
# FUNÇÃO: execute_standard_macro() - Adicionar logs no movimento da câmera
# Procurar por "# Executar movimento do mouse via API Windows"
# ------------------------------------------------------------------------------

CHEST_CAMERA_LOGS = '''
            # ========================================
            # MOVIMENTO DA CÂMERA (ALT + Mouse)
            # ========================================
            _safe_print(f"")
            _safe_print(f"📹 [CHEST] MOVIMENTO DA CÂMERA:")
            _safe_print(f"   🎮 Modo: API Windows (freelook ALT)")
            _safe_print(f"   ➡️  Deslocamento: DX={dx}, DY={dy}")
            _safe_print(f"")

            # Executar movimento do mouse via API Windows
            if self.input_manager and hasattr(self.input_manager, 'camera_turn_in_game'):
                _safe_print(f"   🚀 Executando camera_turn_in_game(dx={dx}, dy={dy})...")
                success = self.input_manager.camera_turn_in_game(dx, dy)
                if success:
                    _safe_print(f"   ✅ Câmera movida com sucesso!")
                else:
                    _safe_print(f"   ❌ Falha ao mover câmera")
'''

# ==============================================================================
# ARQUIVO: core/feeding_system.py
# ==============================================================================

# ------------------------------------------------------------------------------
# FUNÇÃO: feed_using_detection() - Adicionar logs antes de cada movimento
# Procurar por "self.input_manager.move_to"
# ------------------------------------------------------------------------------

FEEDING_LOGS = '''
            # LOG: Movimento para comida
            _safe_print(f"")
            _safe_print(f"🍖 [FEEDING] MOVENDO PARA COMIDA:")
            _safe_print(f"   🎯 Template detectado: {food_template}")
            _safe_print(f"   📍 Posição: ({food_x}, {food_y})")
            _safe_print(f"   🔍 Confiança: {food_confidence:.3f}")

            if not self.input_manager.move_to(food_x, food_y):
'''

# ==============================================================================
# INSTRUÇÕES DE APLICAÇÃO
# ==============================================================================

INSTRUCOES = """
COMO APLICAR ESTE PATCH:
========================

1. ARDUINO INPUT MANAGER (core/arduino_input_manager.py)

   a) Função move_to() - Linha ~624-669
      - Procurar: "# Obter posição atual REAL"
      - Substituir TODO o trecho até "if abs(error_x) > 15 or abs(error_y) > 15:"
      - Colar: MOVE_TO_LOGS

   b) Função calibrate_mouseto() - Linha ~564-574
      - Procurar: "try:" dentro de calibrate_mouseto
      - Substituir até "if response and..."
      - Colar: CALIBRATE_MOUSETO_LOGS

   c) Função click() - Linha ~452
      - Procurar: "def click(self, x: Optional[int]"
      - Adicionar logs no início
      - Usar: CLICK_LOGS_BEFORE

2. CHEST MANAGER (core/chest_manager.py)

   - Procurar: "# Executar movimento do mouse via API Windows"
   - Adicionar ANTES dessa linha: CHEST_CAMERA_LOGS

3. FEEDING SYSTEM (core/feeding_system.py)

   - Procurar: "if not self.input_manager.move_to(food_x, food_y):"
   - Adicionar ANTES: FEEDING_LOGS

RESULTADO ESPERADO NOS LOGS:
=============================

Ao apertar F6, você verá:

📹 [CHEST] MOVIMENTO DA CÂMERA:
   🎮 Modo: API Windows (freelook ALT)
   ➡️  Deslocamento: DX=1200, DY=200

🎯 [ARDUINO] CALIBRANDO MOUSETO:
   📍 Posição atual do cursor: (959, 539)
   🔄 Sincronizando MouseTo para: (959, 539)
   📤 Enviando: RESET_POS:959:539
   📥 Resposta: OK:RESET_POS:(959,539)
   ✅ MouseTo calibrado!

🎮 [ARDUINO] MOVIMENTO REQUISITADO:
   📍 Atual: (959, 539)
   🎯 Destino: (1562, 756)
   ➡️  Delta: (+603, +217)
   📏 Distância: 603px
   🚀 3 PASSOS: (201, 72) cada
      Passo 1: MOUSEMOVE:201:72
      Passo 2: MOUSEMOVE:201:72
      Passo 3: MOUSEMOVE:201:72
   🔍 Verificação:
      Esperado: (1562, 756)
      Real: (1562, 756)
      Erro: (+0, +0)
   ✅ Movimento OK!

Isso vai revelar EXATAMENTE onde está o problema!
"""

print(__doc__)
print(INSTRUCOES)

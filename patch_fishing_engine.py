#!/usr/bin/env python3
"""
Script para aplicar correções no fishing_engine.py
"""

import os
import re

def apply_patches():
    file_path = r'c:\Users\Thiago\Desktop\v5\core\fishing_engine.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Aplicando patches...")

    # PATCH 1: Adicionar fila de comandos no __init__
    patch1_search = """        # ✅ NOVO: Flag de controle pelo servidor
        # Quando True, desativa prioridades locais (feeding, cleaning, maintenance)
        # O servidor passa a controlar TUDO via WebSocket
        self.server_controlled = False

        # Contadores de timeout para triggers automáticos
        self.timeout_count = 0"""

    patch1_replace = """        # ✅ NOVO: Flag de controle pelo servidor
        # Quando True, desativa prioridades locais (feeding, cleaning, maintenance)
        # O servidor passa a controlar TUDO via WebSocket
        self.server_controlled = False

        # ✅ NOVO: Fila de comandos do servidor
        # Comandos recebidos via WebSocket são enfileirados e executados entre ciclos
        self.pending_server_commands = []
        self.command_lock = threading.Lock()
        _safe_print("📋 Fila de comandos do servidor inicializada")

        # Contadores de timeout para triggers automáticos
        self.timeout_count = 0"""

    if patch1_search in content:
        content = content.replace(patch1_search, patch1_replace)
        print("✅ PATCH 1: Fila de comandos adicionada")
    else:
        print("⚠️ PATCH 1: Pattern não encontrado (pode já estar aplicado)")

    # PATCH 2: Corrigir ordem de rod_uses
    patch2_search = """                        # Incrementar pausas naturais
                        self.natural_breaks['catches_since_break'] += 1

                        # Notificar sistemas (feeding, cleaning)
                        _safe_print("📢 Notificando sistemas (feeding/cleaning)...")
                        self.increment_fish_count()
                        self._force_stats_update()"""

    patch2_replace = """                        # Incrementar pausas naturais
                        self.natural_breaks['catches_since_break'] += 1

                        # ✅ CRÍTICO: PRIMEIRO registrar uso da vara (incrementa rod_uses)
                        # DEPOIS enviar fish_caught (com rod_uses correto)
                        _safe_print("📝 [REGISTRO PRÉ] Registrando uso da vara ANTES de notificar servidor...")
                        if self.rod_manager:
                            current_rod = self.rod_manager.get_current_rod()
                            self.rod_manager.rod_uses[current_rod] += 1
                            _safe_print(f"   ✅ Vara {current_rod}: {self.rod_manager.rod_uses[current_rod]} usos")

                        # AGORA sim notificar sistemas (com rod_uses correto!)
                        _safe_print("📢 Notificando sistemas e servidor...")
                        self.increment_fish_count()
                        self._force_stats_update()"""

    if patch2_search in content:
        content = content.replace(patch2_search, patch2_replace)
        print("✅ PATCH 2: Ordem de rod_uses corrigida")
    else:
        print("⚠️ PATCH 2: Pattern não encontrado (pode já estar aplicado)")

    # PATCH 3: Modificar _will_open_chest_next_cycle
    patch3_search = """    def _will_open_chest_next_cycle(self) -> bool:
        \"\"\"
        🔍 Verificar se o próximo ciclo vai abrir o baú

        Checa TODAS as condições que podem abrir baú:
        1. Feeding (tempo ou pescas)
        2. Cleaning (inventário cheio)
        3. Manutenção (timeout de vara detectado)

        Se qualquer um for TRUE, não devemos trocar vara agora - o coordinator fará isso

        Returns:
            bool: True se vai abrir baú no próximo ciclo
        \"\"\"
        try:
            # 1. Verificar FEEDING
            if self.feeding_system and self.feeding_system.should_trigger_feeding():
                _safe_print("🍖 [CHECK] Feeding pendente - baú será aberto")
                return True

            # 2. Verificar CLEANING
            if self.inventory_manager and self.inventory_manager.should_trigger_cleaning():
                _safe_print("🧹 [CHECK] Cleaning pendente - baú será aberto")
                return True"""

    patch3_replace = """    def _will_open_chest_next_cycle(self) -> bool:
        \"\"\"
        🔍 Verificar se o próximo ciclo vai abrir o baú

        ✅ ARQUITETURA SERVIDOR:
        - Se conectado: aguarda comandos do servidor (2s)
        - Se offline: retorna False (sem lógica local)

        Servidor decide TUDO via comandos enfileirados:
        - feed → callback abre baú
        - clean → callback abre baú
        - switch_rod_pair → callback abre baú

        Returns:
            bool: True se servidor enviou comandos
        \"\"\"
        try:
            # Se conectado ao servidor, aguardar comandos
            if self.ws_client and self.ws_client.is_connected():
                _safe_print("🌐 [SERVER] Aguardando comandos do servidor (2s)...")
                time.sleep(2.0)

                # Verificar se tem comandos na fila
                with self.command_lock:
                    has_commands = len(self.pending_server_commands) > 0
                    if has_commands:
                        _safe_print(f"📋 [SERVER] {len(self.pending_server_commands)} comando(s) recebido(s)")
                    return has_commands

            # Se offline, não abre baú (sem lógica local)
            _safe_print("💻 [LOCAL] Modo offline - sem operações de baú")
            return False

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar operações pendentes: {e}")
            import traceback
            traceback.print_exc()
            return False"""

    if patch3_search in content:
        content = content.replace(patch3_search, patch3_replace)
        print("✅ PATCH 3: _will_open_chest_next_cycle modificado")
    else:
        print("⚠️ PATCH 3: Pattern não encontrado (pode já estar aplicado)")

    # Salvar arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ Todos os patches aplicados com sucesso!")
    print("📄 Arquivo salvo: core/fishing_engine.py")

if __name__ == "__main__":
    apply_patches()

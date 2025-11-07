#!/usr/bin/env python3
"""
⌨️ HotkeyManager - Sistema Global de Hotkeys
Ultimate Fishing Bot v4.0

Gerencia todas as hotkeys globais do sistema baseado no botpesca.py v3
"""

import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    _safe_print("⚠️ keyboard library não disponível - hotkeys desabilitados")


class HotkeyAction(Enum):
    """Ações disponíveis para hotkeys"""
    START_BOT = "start_bot"              # F9
    PAUSE_BOT = "pause_bot"              # F10
    STOP_BOT = "stop_bot"                # F2
    EMERGENCY_STOP = "emergency_stop"    # ESC
    TOGGLE_UI = "toggle_ui"              # F4
    MANUAL_FEEDING = "manual_feeding"    # F6
    EXECUTE_MACRO = "execute_macro"      # F8
    TEST_MACRO = "test_macro"            # F11
    ROD_MAINTENANCE = "rod_maintenance"  # Page Down
    MANUAL_ROD_SWITCH = "manual_rod_switch"  # TAB
    MANUAL_CLEANING = "manual_cleaning"  # F5


class HotkeyManager:
    """
    ⌨️ Gerenciador Global de Hotkeys

    Controla todas as hotkeys do sistema e conecta aos componentes apropriados
    """

    def __init__(self, fishing_engine=None, config_manager=None):
        """
        Inicializar gerenciador de hotkeys

        Args:
            fishing_engine: FishingEngine para controlar bot
            config_manager: ConfigManager para carregar configurações
        """
        if not KEYBOARD_AVAILABLE:
            _safe_print("❌ Biblioteca 'keyboard' não disponível. Hotkeys desabilitados.")
            self.enabled = False
            return

        self.fishing_engine = fishing_engine
        self.config_manager = config_manager

        # Estado do sistema
        self.enabled = False
        self.registered_hotkeys = {}

        # Lock para thread safety
        self.hotkey_lock = threading.RLock()

        # Callbacks customizados para ações
        self.action_callbacks: Dict[HotkeyAction, Callable] = {}

        # Mapeamento padrão de hotkeys (baseado no v3)
        self.default_hotkey_map = {
            'f9': HotkeyAction.START_BOT,
            'f10': HotkeyAction.PAUSE_BOT,
            'f2': HotkeyAction.STOP_BOT,
            'esc': HotkeyAction.EMERGENCY_STOP,
            'f4': HotkeyAction.TOGGLE_UI,
            'f6': HotkeyAction.MANUAL_FEEDING,
            'f5': HotkeyAction.MANUAL_CLEANING,
            'f8': HotkeyAction.EXECUTE_MACRO,
            'f11': HotkeyAction.TEST_MACRO,
            'page down': HotkeyAction.ROD_MAINTENANCE,
            'tab': HotkeyAction.MANUAL_ROD_SWITCH
        }

        # Carregar mapeamento customizado se disponível
        self.hotkey_map = self._load_hotkey_config()

        # Estatísticas
        self.stats = {
            'total_triggers': 0,
            'triggers_by_action': {}
        }

        _safe_print("⌨️ HotkeyManager inicializado")

    def _load_hotkey_config(self) -> Dict[str, HotkeyAction]:
        """Carregar configuração de hotkeys do config"""
        try:
            if self.config_manager:
                custom_hotkeys = self.config_manager.get('hotkeys', {})

                if custom_hotkeys:
                    _safe_print("⚙️ Carregando hotkeys customizadas do config")
                    # Converter strings para enums
                    loaded_map = {}
                    for key, action_str in custom_hotkeys.items():
                        try:
                            action = HotkeyAction(action_str)
                            loaded_map[key.lower()] = action
                        except ValueError:
                            _safe_print(f"⚠️ Ação inválida para hotkey '{key}': {action_str}")

                    return loaded_map

            # Usar padrão se não houver customização
            _safe_print("⚙️ Usando mapeamento padrão de hotkeys")
            return self.default_hotkey_map.copy()

        except Exception as e:
            _safe_print(f"❌ Erro ao carregar config de hotkeys: {e}")
            return self.default_hotkey_map.copy()

    def register_action_callback(self, action: HotkeyAction, callback: Callable):
        """
        Registrar callback customizado para ação

        Args:
            action: Ação do hotkey
            callback: Função a ser chamada quando hotkey ativada
        """
        self.action_callbacks[action] = callback
        _safe_print(f"✅ Callback registrado para {action.value}")

    def enable(self) -> bool:
        """Habilitar sistema de hotkeys"""
        try:
            if not KEYBOARD_AVAILABLE:
                _safe_print("❌ keyboard library não disponível")
                return False

            if self.enabled:
                _safe_print("⚠️ Hotkeys já estão habilitados")
                return True

            _safe_print("🔧 Habilitando sistema de hotkeys...")

            # Registrar todos os hotkeys
            for key, action in self.hotkey_map.items():
                try:
                    # Registrar hotkey com keyboard library
                    keyboard.add_hotkey(
                        key,
                        lambda a=action: self._handle_hotkey(a),
                        suppress=False  # Não suprimir tecla (deixar passar para o jogo)
                    )

                    self.registered_hotkeys[key] = action
                    _safe_print(f"  ✅ Hotkey registrada: {key.upper()} -> {action.value}")

                except Exception as e:
                    _safe_print(f"  ❌ Erro ao registrar {key}: {e}")

            self.enabled = True
            _safe_print(f"✅ Sistema de hotkeys habilitado com {len(self.registered_hotkeys)} hotkeys")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao habilitar hotkeys: {e}")
            return False

    def disable(self) -> bool:
        """Desabilitar sistema de hotkeys"""
        try:
            if not self.enabled:
                _safe_print("⚠️ Hotkeys já estão desabilitados")
                return True

            _safe_print("🔧 Desabilitando sistema de hotkeys...")

            # Remover todos os hotkeys registrados
            if KEYBOARD_AVAILABLE:
                for key in self.registered_hotkeys.keys():
                    try:
                        keyboard.remove_hotkey(key)
                        _safe_print(f"  ✅ Hotkey removida: {key.upper()}")
                    except Exception as e:
                        _safe_print(f"  ⚠️ Erro ao remover {key}: {e}")

            self.registered_hotkeys.clear()
            self.enabled = False

            _safe_print("✅ Sistema de hotkeys desabilitado")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao desabilitar hotkeys: {e}")
            return False

    def _handle_hotkey(self, action: HotkeyAction):
        """
        Handler interno para hotkeys

        Args:
            action: Ação a ser executada
        """
        try:
            with self.hotkey_lock:
                # Atualizar estatísticas
                self.stats['total_triggers'] += 1
                if action.value not in self.stats['triggers_by_action']:
                    self.stats['triggers_by_action'][action.value] = 0
                self.stats['triggers_by_action'][action.value] += 1

                _safe_print(f"\n⌨️ Hotkey ativada: {action.value}")

                # Verificar se há callback customizado
                if action in self.action_callbacks:
                    _safe_print(f"🔧 Executando callback customizado para {action.value}")
                    try:
                        self.action_callbacks[action]()
                        return
                    except Exception as e:
                        _safe_print(f"❌ Erro no callback customizado: {e}")
                        # Continuar para ação padrão

                # Executar ação padrão
                self._execute_default_action(action)

        except Exception as e:
            _safe_print(f"❌ Erro ao processar hotkey {action.value}: {e}")

    def _execute_default_action(self, action: HotkeyAction):
        """Executar ação padrão do hotkey"""
        try:
            if action == HotkeyAction.START_BOT:
                self._handle_start_bot()

            elif action == HotkeyAction.PAUSE_BOT:
                self._handle_pause_bot()

            elif action == HotkeyAction.STOP_BOT:
                self._handle_stop_bot()

            elif action == HotkeyAction.EMERGENCY_STOP:
                self._handle_emergency_stop()

            elif action == HotkeyAction.TOGGLE_UI:
                self._handle_toggle_ui()

            elif action == HotkeyAction.MANUAL_FEEDING:
                self._handle_manual_feeding()

            elif action == HotkeyAction.MANUAL_CLEANING:
                self._handle_manual_cleaning()

            elif action == HotkeyAction.EXECUTE_MACRO:
                self._handle_execute_macro()

            elif action == HotkeyAction.TEST_MACRO:
                self._handle_test_macro()

            elif action == HotkeyAction.ROD_MAINTENANCE:
                self._handle_rod_maintenance()

            elif action == HotkeyAction.MANUAL_ROD_SWITCH:
                self._handle_manual_rod_switch()

            else:
                _safe_print(f"⚠️ Ação não implementada: {action.value}")

        except Exception as e:
            _safe_print(f"❌ Erro ao executar ação {action.value}: {e}")

    # ===== HANDLERS DE AÇÕES =====

    def _handle_start_bot(self):
        """F9 - Iniciar bot"""
        _safe_print("🚀 [F9] Iniciando bot...")
        if self.fishing_engine:
            if self.fishing_engine.start():
                _safe_print("✅ [F9] Bot iniciado com sucesso")
            else:
                _safe_print("❌ [F9] Falha ao iniciar bot")
        else:
            _safe_print("⚠️ [F9] FishingEngine não disponível")

    def _handle_pause_bot(self):
        """F10 - Pausar/Despausar bot"""
        _safe_print("⏸️ [F10] Alternando pausa...")
        if self.fishing_engine:
            if self.fishing_engine.pause():
                if self.fishing_engine.is_paused:
                    _safe_print("⏸️ [F10] Bot pausado")
                else:
                    _safe_print("▶️ [F10] Bot despausado")
            else:
                _safe_print("❌ [F10] Falha ao pausar bot")
        else:
            _safe_print("⚠️ [F10] FishingEngine não disponível")

    def _handle_stop_bot(self):
        """F2 - Parar bot"""
        _safe_print("🛑 [F2] Parando bot...")
        if self.fishing_engine:
            if self.fishing_engine.stop():
                _safe_print("✅ [F2] Bot parado com sucesso")
            else:
                _safe_print("❌ [F2] Falha ao parar bot")
        else:
            _safe_print("⚠️ [F2] FishingEngine não disponível")

    def _handle_emergency_stop(self):
        """ESC - Parada de emergência"""
        _safe_print("🚨 [ESC] PARADA DE EMERGÊNCIA!")
        if self.fishing_engine:
            self.fishing_engine.stop()

            # Liberar todos os inputs
            if hasattr(self.fishing_engine, 'input_manager') and self.fishing_engine.input_manager:
                self.fishing_engine.input_manager.emergency_stop()

            _safe_print("✅ [ESC] Parada de emergência executada")
        else:
            _safe_print("⚠️ [ESC] FishingEngine não disponível")

    def _handle_toggle_ui(self):
        """F4 - Alternar visibilidade da UI"""
        _safe_print("🎨 [F4] Alternando UI...")
        # Será implementado pela UI principal
        _safe_print("⚠️ [F4] Funcionalidade delegada para UI")

    def _handle_manual_feeding(self):
        """F6 - Alimentação manual"""
        _safe_print("🍖 [F6] Executando alimentação manual...")
        if self.fishing_engine:
            if self.fishing_engine.trigger_feeding():
                _safe_print("✅ [F6] Alimentação executada com sucesso")
            else:
                _safe_print("❌ [F6] Falha na alimentação")
        else:
            _safe_print("⚠️ [F6] FishingEngine não disponível")

    def _handle_manual_cleaning(self):
        """F5 - Limpeza manual do inventário"""
        _safe_print("🧹 [F5] Executando limpeza manual...")
        if self.fishing_engine:
            if self.fishing_engine.trigger_cleaning():
                _safe_print("✅ [F5] Limpeza executada com sucesso")
            else:
                _safe_print("❌ [F5] Falha na limpeza")
        else:
            _safe_print("⚠️ [F5] FishingEngine não disponível")

    def _handle_execute_macro(self):
        """F8 - Executar macro"""
        _safe_print("🎯 [F8] Executando macro...")
        # Será implementado pelo sistema de macros
        _safe_print("⚠️ [F8] Sistema de macros não implementado")

    def _handle_test_macro(self):
        """F11 - Testar macro de baú"""
        _safe_print("🧪 [F11] Testando macro de baú...")
        # Será implementado pelo sistema de macros
        _safe_print("⚠️ [F11] Sistema de macros não implementado")

    def _handle_rod_maintenance(self):
        """Page Down - Manutenção de varas"""
        _safe_print("🔧 [Page Down] Executando manutenção de varas...")
        if self.fishing_engine:
            if self.fishing_engine.trigger_rod_maintenance():
                _safe_print("✅ [Page Down] Manutenção executada com sucesso")
            else:
                _safe_print("❌ [Page Down] Falha na manutenção")
        else:
            _safe_print("⚠️ [Page Down] FishingEngine não disponível")

    def _handle_manual_rod_switch(self):
        """TAB - Troca manual de vara"""
        _safe_print("🔄 [TAB] Executando troca manual de vara...")
        if self.fishing_engine:
            if self.fishing_engine.trigger_rod_switch():
                _safe_print("✅ [TAB] Troca de vara executada com sucesso")
            else:
                _safe_print("❌ [TAB] Falha na troca de vara")
        else:
            _safe_print("⚠️ [TAB] FishingEngine não disponível")

    # ===== MÉTODOS PÚBLICOS =====

    def set_fishing_engine(self, fishing_engine):
        """Definir FishingEngine para controlar bot"""
        self.fishing_engine = fishing_engine
        _safe_print("✅ FishingEngine conectado ao HotkeyManager")

    def is_enabled(self) -> bool:
        """Verificar se hotkeys estão habilitados"""
        return self.enabled

    def get_registered_hotkeys(self) -> Dict[str, str]:
        """Obter lista de hotkeys registrados"""
        return {
            key: action.value
            for key, action in self.registered_hotkeys.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de uso"""
        return self.stats.copy()

    def reload_hotkeys(self) -> bool:
        """Recarregar hotkeys (útil após mudanças no config)"""
        try:
            _safe_print("🔄 Recarregando hotkeys...")

            # Desabilitar primeiro
            if self.enabled:
                self.disable()

            # Recarregar config
            self.hotkey_map = self._load_hotkey_config()

            # Habilitar novamente
            return self.enable()

        except Exception as e:
            _safe_print(f"❌ Erro ao recarregar hotkeys: {e}")
            return False

    def print_hotkey_help(self):
        """Imprimir ajuda de hotkeys"""
        _safe_print("\n" + "="*60)
        _safe_print("⌨️ HOTKEYS DISPONÍVEIS")
        _safe_print("="*60)

        for key, action in self.hotkey_map.items():
            description = self._get_action_description(action)
            _safe_print(f"  {key.upper():15} - {description}")

        _safe_print("="*60)

    def _get_action_description(self, action: HotkeyAction) -> str:
        """Obter descrição da ação"""
        descriptions = {
            HotkeyAction.START_BOT: "Iniciar bot",
            HotkeyAction.PAUSE_BOT: "Pausar/Despausar bot",
            HotkeyAction.STOP_BOT: "Parar bot",
            HotkeyAction.EMERGENCY_STOP: "Parada de emergência",
            HotkeyAction.TOGGLE_UI: "Alternar visibilidade da UI",
            HotkeyAction.MANUAL_FEEDING: "Alimentação manual",
            HotkeyAction.MANUAL_CLEANING: "Limpeza manual do inventário",
            HotkeyAction.EXECUTE_MACRO: "Executar macro",
            HotkeyAction.TEST_MACRO: "Testar macro de baú",
            HotkeyAction.ROD_MAINTENANCE: "Manutenção de varas",
            HotkeyAction.MANUAL_ROD_SWITCH: "Troca manual de vara"
        }
        return descriptions.get(action, "Ação desconhecida")

    def __del__(self):
        """Cleanup ao destruir objeto"""
        try:
            if self.enabled:
                self.disable()
        except:
            pass
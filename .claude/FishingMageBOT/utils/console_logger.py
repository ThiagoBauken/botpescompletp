#!/usr/bin/env python3
"""
🎨 Console Logger - Sistema de Logs Limpos
Controla verbosidade dos logs no console
"""

import re
from enum import Enum

class LogLevel(Enum):
    """Níveis de verbosidade"""
    QUIET = 0      # Apenas essencial (peixes, comandos servidor, erros)
    NORMAL = 1     # Normal (+ inicialização, estatísticas)
    VERBOSE = 2    # Tudo (debug completo)

class ConsoleLogger:
    """
    Gerenciador de logs no console com níveis de verbosidade

    Uso:
        from utils.console_logger import console_logger, LogLevel

        console_logger.set_level(LogLevel.QUIET)  # Modo silencioso
        console_logger.info("Mensagem normal")    # Não aparece em QUIET
        console_logger.important("Peixe capturado!")  # Sempre aparece
    """

    def __init__(self):
        self.level = LogLevel.NORMAL
        self.enabled = True

    def set_level(self, level: LogLevel):
        """Definir nível de verbosidade"""
        self.level = level

    def disable(self):
        """Desabilitar completamente os logs"""
        self.enabled = False

    def enable(self):
        """Reabilitar logs"""
        self.enabled = True

    def _safe_print(self, text):
        """Print com fallback para Unicode"""
        if not self.enabled:
            return
        try:
            print(text)
        except (UnicodeEncodeError, UnicodeDecodeError):
            clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
            print(clean)

    # ═══════════════════════════════════════════════════════
    # NÍVEIS DE LOG
    # ═══════════════════════════════════════════════════════

    def critical(self, text):
        """SEMPRE aparece (erros críticos)"""
        if self.enabled:
            self._safe_print(f"❌ {text}")

    def important(self, text):
        """Aparece em QUIET, NORMAL e VERBOSE (eventos importantes)"""
        if self.enabled:
            self._safe_print(text)

    def info(self, text):
        """Aparece em NORMAL e VERBOSE (informações gerais)"""
        if self.enabled and self.level.value >= LogLevel.NORMAL.value:
            self._safe_print(text)

    def debug(self, text):
        """Apenas em VERBOSE (debug detalhado)"""
        if self.enabled and self.level.value >= LogLevel.VERBOSE.value:
            self._safe_print(text)

    # ═══════════════════════════════════════════════════════
    # ATALHOS SEMÂNTICOS
    # ═══════════════════════════════════════════════════════

    def fish_caught(self, fish_number):
        """Peixe capturado (SEMPRE visível)"""
        self.important(f"🐟 Peixe #{fish_number} capturado!")

    def server_command(self, command, params=None):
        """Comando do servidor (SEMPRE visível)"""
        if params:
            self.important(f"📥 [SERVIDOR] {command.upper()} - {params}")
        else:
            self.important(f"📥 [SERVIDOR] {command.upper()}")

    def server_send(self, event, data=None):
        """Envio para servidor (SEMPRE visível)"""
        if data:
            self.important(f"📤 [→SERVER] {event} - {data}")
        else:
            self.important(f"📤 [→SERVER] {event}")

    def action_start(self, action):
        """Início de ação (NORMAL+)"""
        self.info(f"⚡ {action}")

    def action_complete(self, action):
        """Conclusão de ação (NORMAL+)"""
        self.info(f"✅ {action}")

    def system_init(self, component):
        """Inicialização de componente (NORMAL+)"""
        self.info(f"🔧 {component}")

    def mouse_position(self, x, y, context=""):
        """Posição do mouse (VERBOSE apenas)"""
        if context:
            self.debug(f"🖱️ Mouse: ({x}, {y}) - {context}")
        else:
            self.debug(f"🖱️ Mouse: ({x}, {y})")

    def separator(self, char="=", length=60):
        """Separador visual (VERBOSE apenas)"""
        self.debug(char * length)

# ═══════════════════════════════════════════════════════
# INSTÂNCIA GLOBAL
# ═══════════════════════════════════════════════════════

console_logger = ConsoleLogger()

# ═══════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🎨 Demonstração do Console Logger\n")

    # Teste em diferentes níveis
    for level in [LogLevel.QUIET, LogLevel.NORMAL, LogLevel.VERBOSE]:
        print(f"\n{'='*60}")
        print(f"Nível: {level.name}")
        print('='*60)

        console_logger.set_level(level)

        console_logger.critical("Erro crítico")
        console_logger.important("Evento importante")
        console_logger.info("Informação geral")
        console_logger.debug("Debug detalhado")
        console_logger.fish_caught(1)
        console_logger.server_command("feed", {"clicks": 5})
        console_logger.mouse_position(100, 200, "antes do clique")

    print("\n" + "="*60)
    print("✅ Demonstração completa!")
    print("="*60)

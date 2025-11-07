#!/usr/bin/env python3
"""
🎨 Log Helper - Wrapper para console_logger
Usado pelos componentes core para logs filtrados
"""

import re

# Importar console_logger se disponível
try:
    from utils.console_logger import console_logger, LogLevel
    CONSOLE_LOGGER_AVAILABLE = True
except ImportError:
    CONSOLE_LOGGER_AVAILABLE = False
    console_logger = None

def _safe_print_base(text):
    """Print básico com fallback Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def log_important(text):
    """Log importante (sempre aparece)"""
    if CONSOLE_LOGGER_AVAILABLE and console_logger:
        console_logger.important(text)
    else:
        _safe_print_base(text)

def log_info(text):
    """Log info (NORMAL e VERBOSE)"""
    if CONSOLE_LOGGER_AVAILABLE and console_logger:
        console_logger.info(text)
    else:
        _safe_print_base(text)

def log_debug(text):
    """Log debug (apenas VERBOSE)"""
    if CONSOLE_LOGGER_AVAILABLE and console_logger:
        console_logger.debug(text)
    else:
        # Em fallback, não mostrar debug
        pass

def is_debug_enabled():
    """Verificar se debug está ativo"""
    if CONSOLE_LOGGER_AVAILABLE and console_logger:
        return console_logger.level.value >= LogLevel.VERBOSE.value
    return False

# Atalhos semânticos
def log_fish_caught(fish_number):
    """Peixe capturado"""
    log_important(f"🐟 Peixe #{fish_number} capturado!")

def log_cycle_start():
    """Início de ciclo de pesca"""
    log_debug("\n🎣 Iniciando ciclo de pesca...")

def log_mouse_position(x, y, context=""):
    """Posição do mouse (apenas debug)"""
    if context:
        log_debug(f"🖱️ Mouse: ({x}, {y}) - {context}")
    else:
        log_debug(f"🖱️ Mouse: ({x}, {y})")

def log_separator(char="=", length=60):
    """Separador (apenas debug)"""
    log_debug(char * length)

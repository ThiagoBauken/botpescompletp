#!/usr/bin/env python3
"""
📝 Sistema de Logging Simplificado - VERSÃO OTIMIZADA
Reduz drasticamente o número de arquivos de log gerados
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# ⚙️ CONFIGURAÇÃO GLOBAL DE LOGS
LOG_ENABLED = True  # Mude para False para desabilitar completamente os logs
LOG_LEVEL = "WARNING"  # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
MAX_LOG_SIZE_MB = 10  # Tamanho máximo por arquivo (MB)
MAX_LOG_FILES = 3  # Número máximo de arquivos de backup

def setup_logging(log_level=None, log_dir="data/logs"):
    """
    Configurar sistema de logging SIMPLIFICADO

    MUDANÇAS:
    - Apenas 1 arquivo de log: fishing_bot.log
    - Rotação automática quando atingir MAX_LOG_SIZE_MB
    - Mantém apenas MAX_LOG_FILES backups
    - Sem logs por data (evita 100+ arquivos)
    """

    # Verificar se logging está habilitado
    if not LOG_ENABLED:
        # Desabilitar completamente os logs
        logging.disable(logging.CRITICAL)
        return None

    # Criar diretório de logs
    os.makedirs(log_dir, exist_ok=True)

    # Usar configuração global ou parâmetro
    level_str = log_level if log_level else LOG_LEVEL
    level = getattr(logging, level_str.upper(), logging.WARNING)

    # Formato das mensagens (simplificado)
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configurar logger raiz com APENAS 1 arquivo
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler (apenas erros)
            logging.StreamHandler(sys.stdout),

            # ÚNICO arquivo de log com rotação
            RotatingFileHandler(
                os.path.join(log_dir, "fishing_bot.log"),
                maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024,
                backupCount=MAX_LOG_FILES,
                encoding='utf-8'
            )
        ],
        force=True  # Forçar reconfiguração
    )

    # Retornar logger principal
    return logging.getLogger()


def get_logger(name=None):
    """
    Obter logger para um componente específico
    Todos usam o mesmo arquivo fishing_bot.log
    """
    if not LOG_ENABLED:
        # Retornar logger desabilitado
        logger = logging.getLogger(name or __name__)
        logger.disabled = True
        return logger

    return logging.getLogger(name or __name__)


# Funções de conveniência
def log_debug(message, *args, **kwargs):
    """Log DEBUG"""
    if LOG_ENABLED:
        logging.debug(message, *args, **kwargs)


def log_info(message, *args, **kwargs):
    """Log INFO"""
    if LOG_ENABLED:
        logging.info(message, *args, **kwargs)


def log_warning(message, *args, **kwargs):
    """Log WARNING"""
    if LOG_ENABLED:
        logging.warning(message, *args, **kwargs)


def log_error(message, *args, **kwargs):
    """Log ERROR"""
    if LOG_ENABLED:
        logging.error(message, *args, **kwargs)


def log_critical(message, *args, **kwargs):
    """Log CRITICAL"""
    if LOG_ENABLED:
        logging.critical(message, *args, **kwargs)


# ============================================================================
# CONFIGURAÇÃO ANTIGA (OBSOLETA - mantida para compatibilidade)
# ============================================================================

def setup_component_logger(component_name, log_dir, level):
    """
    OBSOLETO: Não cria mais logs separados por componente
    Retorna o logger principal
    """
    return get_logger(component_name)

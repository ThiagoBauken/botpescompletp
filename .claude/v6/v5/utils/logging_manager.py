#!/usr/bin/env python3
"""
📝 Sistema de Logging Unificado
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging(log_level="INFO", log_dir="data/logs"):
    """Configurar sistema de logging"""
    
    # Criar diretório de logs
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar nível de log
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Formato das mensagens
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar logger raiz
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            
            # Arquivo principal
            RotatingFileHandler(
                os.path.join(log_dir, f"fishing_bot_{datetime.now().strftime('%Y-%m-%d')}.log"),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # Logger específico para diferentes componentes
    loggers = {
        'fishing': setup_component_logger('fishing', log_dir, level),
        'template': setup_component_logger('template_matching', log_dir, level),
        'ui': setup_component_logger('ui', log_dir, level),
        'performance': setup_component_logger('performance', log_dir, level)
    }
    
    return loggers

def setup_component_logger(component_name, log_dir, level):
    """Configurar logger para componente específico"""
    logger = logging.getLogger(component_name)
    logger.setLevel(level)
    
    # Handler para arquivo específico
    handler = RotatingFileHandler(
        os.path.join(log_dir, f"{component_name}_{datetime.now().strftime('%Y-%m-%d')}.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
"""
Sistema de logging simples e funcional
"""

import logging
import os
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Setup básico de logging"""
    
    # Criar diretório de logs
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nome do arquivo com data
    log_file = os.path.join(log_dir, f"fishing_bot_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Configurar logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Logger principal
    logger = logging.getLogger('FishingBot')
    logger.info("🎣 Fishing Bot Logger inicializado")
    
    return logger
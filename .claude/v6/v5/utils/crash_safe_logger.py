#!/usr/bin/env python3
"""
🛡️ CRASH-SAFE LOGGER - Sistema de logging ultra-detalhado
Salva TUDO em arquivo, com flush imediato, sobrevive a crashes e desligamentos forçados
"""

import os
import sys
import traceback
import threading
from datetime import datetime
from pathlib import Path

class CrashSafeLogger:
    """Logger que garante que TUDO é salvo em arquivo, mesmo em crashes"""

    def __init__(self, log_dir="data/logs", prefix="DEBUG"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.log_dir / f"{prefix}_{timestamp}.log"

        # Abrir arquivo em modo append com flush automático
        self.file_handle = open(self.log_file, 'a', encoding='utf-8', buffering=1)

        # Lock para thread-safety
        self.lock = threading.RLock()

        # Contador de linhas
        self.line_count = 0

        # Escrever header
        self._write_header()

    def _write_header(self):
        """Escrever cabeçalho do log"""
        header = f"""
{'='*100}
🛡️ CRASH-SAFE DEBUG LOG
{'='*100}
Arquivo: {self.log_file}
Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
PID: {os.getpid()}
Python: {sys.version}
Platform: {sys.platform}
{'='*100}

"""
        self.file_handle.write(header)
        self.file_handle.flush()
        os.fsync(self.file_handle.fileno())  # Força escrita no disco

    def log(self, level, module, message, **kwargs):
        """
        Escrever log com timestamp preciso e flush imediato

        Args:
            level: DEBUG, INFO, WARNING, ERROR, CRITICAL
            module: Nome do módulo/componente
            message: Mensagem
            **kwargs: Dados extras (serão formatados)
        """
        with self.lock:
            try:
                self.line_count += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                thread_id = threading.current_thread().name

                # Montar linha de log
                log_line = f"[{timestamp}] [{level:8s}] [{module:20s}] [Thread:{thread_id:15s}] {message}"

                # Adicionar kwargs se houver
                if kwargs:
                    extras = " | ".join(f"{k}={v}" for k, v in kwargs.items())
                    log_line += f" | {extras}"

                log_line += "\n"

                # Escrever e forçar flush IMEDIATO
                self.file_handle.write(log_line)
                self.file_handle.flush()
                os.fsync(self.file_handle.fileno())  # CRUCIAL: força escrita física no disco

            except Exception as e:
                # Se falhar ao escrever, tentar salvar o erro
                try:
                    error_msg = f"[{datetime.now()}] [ERROR] [CrashSafeLogger] Falha ao escrever log: {e}\n"
                    self.file_handle.write(error_msg)
                    self.file_handle.flush()
                except:
                    pass  # Se até isso falhar, não há nada que possamos fazer

    def debug(self, module, message, **kwargs):
        """Log DEBUG"""
        self.log("DEBUG", module, message, **kwargs)

    def info(self, module, message, **kwargs):
        """Log INFO"""
        self.log("INFO", module, message, **kwargs)

    def warning(self, module, message, **kwargs):
        """Log WARNING"""
        self.log("WARNING", module, message, **kwargs)

    def error(self, module, message, **kwargs):
        """Log ERROR"""
        self.log("ERROR", module, message, **kwargs)

    def critical(self, module, message, **kwargs):
        """Log CRITICAL"""
        self.log("CRITICAL", module, message, **kwargs)

    def exception(self, module, message):
        """Log exception com traceback completo"""
        with self.lock:
            self.error(module, message)
            tb = traceback.format_exc()
            self.file_handle.write(f"{'─'*100}\n")
            self.file_handle.write(f"TRACEBACK:\n{tb}\n")
            self.file_handle.write(f"{'─'*100}\n")
            self.file_handle.flush()
            os.fsync(self.file_handle.fileno())

    def section(self, title):
        """Escrever seção separadora"""
        with self.lock:
            separator = f"\n{'='*100}\n{title.center(100)}\n{'='*100}\n"
            self.file_handle.write(separator)
            self.file_handle.flush()
            os.fsync(self.file_handle.fileno())

    def state_snapshot(self, module, state_dict):
        """Registrar snapshot completo de estado"""
        with self.lock:
            self.file_handle.write(f"\n{'─'*100}\n")
            self.file_handle.write(f"STATE SNAPSHOT - {module} - {datetime.now().strftime('%H:%M:%S.%f')[:-3]}\n")
            self.file_handle.write(f"{'─'*100}\n")
            for key, value in state_dict.items():
                self.file_handle.write(f"  {key:30s} = {value}\n")
            self.file_handle.write(f"{'─'*100}\n")
            self.file_handle.flush()
            os.fsync(self.file_handle.fileno())

    def close(self):
        """Fechar arquivo de log"""
        with self.lock:
            try:
                footer = f"""
{'='*100}
Fim do log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
Total de linhas: {self.line_count}
{'='*100}
"""
                self.file_handle.write(footer)
                self.file_handle.flush()
                os.fsync(self.file_handle.fileno())
                self.file_handle.close()
            except:
                pass

    def __del__(self):
        """Garantir que arquivo é fechado mesmo em crash"""
        try:
            self.close()
        except:
            pass


# Instância global (singleton)
_global_logger = None
_logger_lock = threading.Lock()

def get_crash_safe_logger(log_dir="data/logs", prefix="DEBUG"):
    """Obter instância singleton do logger"""
    global _global_logger
    with _logger_lock:
        if _global_logger is None:
            _global_logger = CrashSafeLogger(log_dir=log_dir, prefix=prefix)
        return _global_logger


# Funções de conveniência para uso rápido
def log_debug(module, message, **kwargs):
    """Log DEBUG via logger global"""
    get_crash_safe_logger().debug(module, message, **kwargs)

def log_info(module, message, **kwargs):
    """Log INFO via logger global"""
    get_crash_safe_logger().info(module, message, **kwargs)

def log_warning(module, message, **kwargs):
    """Log WARNING via logger global"""
    get_crash_safe_logger().warning(module, message, **kwargs)

def log_error(module, message, **kwargs):
    """Log ERROR via logger global"""
    get_crash_safe_logger().error(module, message, **kwargs)

def log_critical(module, message, **kwargs):
    """Log CRITICAL via logger global"""
    get_crash_safe_logger().critical(module, message, **kwargs)

def log_exception(module, message):
    """Log exception via logger global"""
    get_crash_safe_logger().exception(module, message)

def log_section(title):
    """Separador de seção via logger global"""
    get_crash_safe_logger().section(title)

def log_state(module, state_dict):
    """State snapshot via logger global"""
    get_crash_safe_logger().state_snapshot(module, state_dict)

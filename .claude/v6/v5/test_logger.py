#!/usr/bin/env python3
"""
🧪 Teste Rápido do Sistema de Logging
Verifica se o crash-safe logger está funcionando corretamente
"""

import sys
import os
import time

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "="*60)
    print("🧪 TESTE DO CRASH-SAFE LOGGER")
    print("="*60)

    # Importar logger
    try:
        from utils.crash_safe_logger import (
            get_crash_safe_logger,
            log_debug, log_info, log_warning, log_error, log_critical,
            log_section, log_state
        )
        print("✅ Módulo crash_safe_logger importado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao importar logger: {e}")
        return 1

    # Criar instância do logger
    try:
        logger = get_crash_safe_logger(log_dir="data/logs", prefix="TEST")
        print(f"✅ Logger criado: {logger.log_file}")
        print(f"   Arquivo: {logger.log_file.absolute()}")
    except Exception as e:
        print(f"❌ Erro ao criar logger: {e}")
        return 1

    # Testar todas as funções
    print("\n📝 Testando funções de logging...")

    try:
        log_section("TESTE INICIADO")
        log_debug("TEST", "Esta é uma mensagem DEBUG", valor=123)
        log_info("TEST", "Esta é uma mensagem INFO", status="ok")
        log_warning("TEST", "Esta é uma mensagem WARNING", alerta="teste")
        log_error("TEST", "Esta é uma mensagem ERROR (simulado)", erro="fake")
        log_critical("TEST", "Esta é uma mensagem CRITICAL (simulado)", nivel="maximo")

        # Testar state snapshot
        state_test = {
            "tecla_pressionada": "alt",
            "mouse_x": 1920,
            "mouse_y": 1080,
            "timestamp": time.time()
        }
        log_state("TEST", state_test)

        print("✅ Todas as funções de logging executadas!")
    except Exception as e:
        print(f"❌ Erro ao executar logging: {e}")
        return 1

    # Verificar se o arquivo existe e tem conteúdo
    try:
        if logger.log_file.exists():
            file_size = logger.log_file.stat().st_size
            print(f"\n📊 Arquivo de log criado com sucesso!")
            print(f"   Tamanho: {file_size} bytes")
            print(f"   Linhas escritas: {logger.line_count}")

            # Mostrar últimas 10 linhas do log
            print("\n📄 Últimas 10 linhas do log:")
            print("-" * 60)
            with open(logger.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(line.rstrip())
            print("-" * 60)
        else:
            print(f"❌ Arquivo de log não foi criado!")
            return 1
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
        return 1

    # Fechar logger
    try:
        logger.close()
        print("\n✅ Logger fechado corretamente!")
    except Exception as e:
        print(f"⚠️ Erro ao fechar logger: {e}")

    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print(f"\n📂 Arquivo de log salvo em:")
    print(f"   {logger.log_file.absolute()}")
    print("\n💡 O sistema de logging está funcionando corretamente!")
    print("   Agora você pode rodar o bot e capturar o bug!\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())

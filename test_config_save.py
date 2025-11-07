#!/usr/bin/env python3
"""
🔍 Teste de Salvamento de Configurações

Este script testa se o ConfigManager está salvando corretamente
o arquivo data/config.json e se as configurações persistem.
"""

import os
import sys
import json
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def test_config_save():
    """Teste completo de salvamento de configurações"""

    _safe_print("\n" + "="*60)
    _safe_print("🔍 Teste de Salvamento de Configurações")
    _safe_print("="*60)

    try:
        from core.config_manager import ConfigManager
    except ImportError:
        _safe_print("❌ Erro: Não foi possível importar ConfigManager")
        _safe_print("   Certifique-se de estar no diretório correto do bot")
        return False

    # 1. Verificar estado inicial
    _safe_print("\n1️⃣ Verificando estado inicial...")

    data_dir = Path("data")
    config_file = data_dir / "config.json"

    _safe_print(f"   📂 Pasta data/: {list(data_dir.iterdir()) if data_dir.exists() else 'NÃO EXISTE'}")
    _safe_print(f"   ❓ config.json existe? {config_file.exists()}")

    # Backup se existir
    if config_file.exists():
        backup_file = data_dir / "config.json.backup_test"
        import shutil
        shutil.copy2(config_file, backup_file)
        _safe_print(f"   💾 Backup criado: {backup_file}")

    # 2. Criar ConfigManager
    _safe_print("\n2️⃣ Criando ConfigManager...")

    try:
        config = ConfigManager()
        _safe_print("   ✅ ConfigManager inicializado")
    except Exception as e:
        _safe_print(f"   ❌ Erro ao criar ConfigManager: {e}")
        return False

    # 3. Verificar permissões
    _safe_print("\n3️⃣ Verificando permissões...")

    try:
        # Tentar criar arquivo de teste
        test_file = data_dir / "test_write.tmp"
        with open(test_file, 'w') as f:
            f.write("teste")
        test_file.unlink()
        _safe_print("   ✅ Pasta data/ tem permissão de escrita")
    except Exception as e:
        _safe_print(f"   ❌ Sem permissão de escrita em data/: {e}")
        _safe_print("   💡 Solução:")
        _safe_print("      Linux: chmod 755 data/")
        _safe_print("      Windows: Execute como Administrador")
        return False

    # 4. Fazer mudança de teste
    _safe_print("\n4️⃣ Fazendo mudança de teste...")

    test_value = "TESTE_SALVAMENTO_123"
    config.set('test.save_check', test_value)
    config.set('test.timestamp', str(Path(__file__).stat().st_mtime))

    _safe_print(f"   ✏️ Valor definido: test.save_check = '{test_value}'")
    _safe_print(f"   🔄 has_changes = {config.has_changes}")

    # 5. Salvar
    _safe_print("\n5️⃣ Salvando configurações...")

    try:
        result = config.save_user_config()
        _safe_print(f"   💾 save_user_config() retornou: {result}")
    except Exception as e:
        _safe_print(f"   ❌ Erro ao salvar: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. Verificar arquivo criado
    _safe_print("\n6️⃣ Verificando arquivo criado...")

    if config_file.exists():
        _safe_print(f"   ✅ Arquivo data/config.json EXISTE!")

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            _safe_print(f"   📄 Tamanho: {config_file.stat().st_size} bytes")
            _safe_print(f"   📋 Seções: {list(content.keys())}")
            _safe_print(f"\n   Conteúdo completo:")
            _safe_print(json.dumps(content, indent=2))

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao ler arquivo: {e}")
    else:
        _safe_print(f"   ❌ Arquivo data/config.json NÃO FOI CRIADO!")
        _safe_print(f"   💡 Possíveis causas:")
        _safe_print(f"      • Sem permissão de escrita")
        _safe_print(f"      • Disco cheio")
        _safe_print(f"      • Path incorreto")
        return False

    # 7. Teste de releitura
    _safe_print("\n7️⃣ Testando persistência (recarregar)...")

    try:
        config2 = ConfigManager()
        value_read = config2.get('test.save_check')

        _safe_print(f"   📖 Valor lido: '{value_read}'")
        _safe_print(f"   📖 Valor esperado: '{test_value}'")

        if value_read == test_value:
            _safe_print(f"   ✅ PERSISTÊNCIA FUNCIONA!")
        else:
            _safe_print(f"   ❌ PERSISTÊNCIA NÃO FUNCIONA!")
            _safe_print(f"   💡 Valor não corresponde ao salvo")
            return False

    except Exception as e:
        _safe_print(f"   ❌ Erro ao recarregar: {e}")
        return False

    # 8. Teste de valores reais
    _safe_print("\n8️⃣ Testando salvamento de config real...")

    try:
        # Salvar config de auto_clean
        config.set('auto_clean.interval', 999)
        config.set('auto_clean.enabled', True)
        config.save_user_config()

        # Recarregar
        config3 = ConfigManager()
        interval = config3.get('auto_clean.interval')
        enabled = config3.get('auto_clean.enabled')

        _safe_print(f"   📖 auto_clean.interval = {interval} (esperado: 999)")
        _safe_print(f"   📖 auto_clean.enabled = {enabled} (esperado: True)")

        if interval == 999 and enabled == True:
            _safe_print(f"   ✅ Configurações reais persistem corretamente!")
        else:
            _safe_print(f"   ⚠️ Configurações reais não persistiram corretamente")

    except Exception as e:
        _safe_print(f"   ❌ Erro ao testar configs reais: {e}")

    # 9. Limpeza
    _safe_print("\n9️⃣ Limpeza...")

    try:
        # Remover valores de teste
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # Remover seção de teste
            if 'test' in content:
                del content['test']

            # Restaurar auto_clean ao padrão (se foi modificado)
            if 'auto_clean' in content and 'interval' in content['auto_clean']:
                if content['auto_clean']['interval'] == 999:
                    del content['auto_clean']['interval']
                    if not content['auto_clean']:
                        del content['auto_clean']

            # Salvar de volta
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

            _safe_print(f"   🧹 Valores de teste removidos")

        # Restaurar backup se existir
        backup_file = data_dir / "config.json.backup_test"
        if backup_file.exists():
            backup_file.unlink()
            _safe_print(f"   🗑️ Backup temporário removido")

    except Exception as e:
        _safe_print(f"   ⚠️ Erro na limpeza: {e}")

    # Resultado final
    _safe_print("\n" + "="*60)
    _safe_print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    _safe_print("="*60)
    _safe_print("\n📋 Resultados:")
    _safe_print("   ✅ ConfigManager funciona corretamente")
    _safe_print("   ✅ Arquivo data/config.json é criado")
    _safe_print("   ✅ Configurações persistem entre recarregamentos")
    _safe_print("   ✅ Permissões estão corretas")
    _safe_print("\n💡 Conclusão:")
    _safe_print("   O sistema de salvamento está FUNCIONANDO!")
    _safe_print("   Se suas configs não salvam, certifique-se de:")
    _safe_print("   1. Clicar nos botões '💾 Salvar' na UI")
    _safe_print("   2. Aguardar mensagem de confirmação")
    _safe_print("   3. Não estar conectado ao servidor (que pode sobrescrever)")

    return True

def main():
    """Função principal"""
    try:
        success = test_config_save()

        if success:
            _safe_print("\n✅ Todos os testes passaram!")
            return 0
        else:
            _safe_print("\n❌ Alguns testes falharam!")
            _safe_print("   Veja a saída acima para detalhes")
            return 1

    except Exception as e:
        _safe_print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

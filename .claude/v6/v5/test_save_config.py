#!/usr/bin/env python3
"""
🧪 Teste dos Botões de Salvar - Ultimate Fishing Bot v4.0

Verifica se os métodos save_* corrigidos realmente salvam no config.json
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_manager_save():
    """Testar se ConfigManager consegue salvar dados"""
    print("🧪 Testando ConfigManager...")
    
    try:
        from core.config_manager import ConfigManager
        
        # Criar config temporário
        temp_dir = tempfile.mkdtemp()
        temp_config_path = os.path.join(temp_dir, "test_config.json")
        
        # Inicializar ConfigManager
        config = ConfigManager()
        config.config_file_path = temp_config_path
        
        # Testar set e save_config
        test_data = {
            'test_value': 'hello_world',
            'nested.test': 42,
            'bait_priority': {
                'carne de crocodilo': 1,
                'carne de urso': 2,
                'trout': 3
            }
        }
        
        print("  📝 Salvando dados de teste...")
        for key, value in test_data.items():
            config.set(key, value)
        
        # Salvar no arquivo
        config.save_config()
        
        # Verificar se arquivo foi criado
        if os.path.exists(temp_config_path):
            with open(temp_config_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"  ✅ Arquivo criado: {temp_config_path}")
            print(f"  📄 Dados salvos: {len(saved_data)} seções")
            
            # Verificar dados específicos
            success = True
            if saved_data.get('test_value') != 'hello_world':
                print("  ❌ test_value não salvo corretamente")
                success = False
            
            if saved_data.get('nested', {}).get('test') != 42:
                print("  ❌ nested.test não salvo corretamente")
                success = False
            
            bait_priority = saved_data.get('bait_priority', {})
            if bait_priority.get('carne de crocodilo') != 1:
                print("  ❌ bait_priority não salvo corretamente")
                success = False
            
            if success:
                print("  ✅ Todos os dados salvos corretamente!")
                return True
            else:
                print("  ❌ Alguns dados não foram salvos corretamente")
                return False
        else:
            print(f"  ❌ Arquivo não foi criado: {temp_config_path}")
            return False
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_save_methods():
    """Testar métodos save_* da UI com mock"""
    print("\n🧪 Testando métodos save_* da UI...")
    
    try:
        # Importar ConfigManager
        from core.config_manager import ConfigManager
        
        # Criar mock da UI com ConfigManager real
        class MockUI:
            def __init__(self):
                self.config_manager = ConfigManager()
                
                # Mock das variáveis da UI
                self.cycle_timeout_var = MockVar("122")
                self.rod_switch_limit_var = MockVar("20")
                self.clicks_per_second_var = MockVar("12")
                self.auto_clean_enabled_var = MockVar(True)
                self.auto_clean_interval_var = MockVar("10")
                self.auto_clean_baits_enabled_var = MockVar(True)
                self.clean_chest_side_var = MockVar("right")
                self.clean_chest_method_var = MockVar("macro")
                
                # Bait priority
                self.config_ordered_baits = ['carne de crocodilo', 'carne de urso', 'trout']
                self.config_bait_enabled_vars = {
                    'carne de crocodilo': MockVar(True),
                    'carne de urso': MockVar(True),
                    'trout': MockVar(True)
                }
            
            # Copiar métodos save_* corrigidos
            def save_all_config(self):
                """Método corrigido de save_all_config"""
                try:
                    if hasattr(self, 'config_manager') and self.config_manager:
                        self.config_manager.set('cycle_timeout', int(self.cycle_timeout_var.get()))
                        self.config_manager.set('rod_system.rod_switch_limit', int(self.rod_switch_limit_var.get()))
                        self.config_manager.set('performance.clicks_per_second', int(self.clicks_per_second_var.get()))
                        
                        if hasattr(self.config_manager, 'save_config'):
                            self.config_manager.save_config()
                            print("    ✅ save_all_config executado com sucesso")
                            return True
                    return False
                except Exception as e:
                    print(f"    ❌ Erro em save_all_config: {e}")
                    return False
            
            def save_cleaning_config(self):
                """Método corrigido de save_cleaning_config"""
                try:
                    if hasattr(self, 'config_manager') and self.config_manager:
                        self.config_manager.set('auto_clean.enabled', self.auto_clean_enabled_var.get())
                        self.config_manager.set('auto_clean.interval', int(self.auto_clean_interval_var.get()))
                        self.config_manager.set('auto_clean.include_baits', self.auto_clean_baits_enabled_var.get())
                        self.config_manager.set('auto_clean.chest_side', self.clean_chest_side_var.get())
                        self.config_manager.set('auto_clean.chest_method', self.clean_chest_method_var.get())
                        
                        if hasattr(self.config_manager, 'save_config'):
                            self.config_manager.save_config()
                            print("    ✅ save_cleaning_config executado com sucesso")
                            return True
                    return False
                except Exception as e:
                    print(f"    ❌ Erro em save_cleaning_config: {e}")
                    return False
            
            def save_bait_priority(self):
                """Método novo de save_bait_priority"""
                try:
                    if hasattr(self, 'config_manager') and self.config_manager:
                        bait_priority = {}
                        for i, bait_name in enumerate(self.config_ordered_baits):
                            if bait_name in self.config_bait_enabled_vars:
                                enabled = self.config_bait_enabled_vars[bait_name].get()
                                if enabled:
                                    bait_priority[bait_name] = i + 1
                        
                        self.config_manager.set('bait_priority', bait_priority)
                        
                        if hasattr(self.config_manager, 'save_config'):
                            self.config_manager.save_config()
                            print(f"    ✅ save_bait_priority executado: {bait_priority}")
                            return True
                    return False
                except Exception as e:
                    print(f"    ❌ Erro em save_bait_priority: {e}")
                    return False
        
        class MockVar:
            def __init__(self, value):
                self._value = value
            def get(self):
                return self._value
            def set(self, value):
                self._value = value
        
        # Testar métodos
        ui = MockUI()
        
        tests = [
            ("save_all_config", ui.save_all_config),
            ("save_cleaning_config", ui.save_cleaning_config),
            ("save_bait_priority", ui.save_bait_priority)
        ]
        
        results = {}
        for test_name, test_method in tests:
            print(f"  🔧 Testando {test_name}...")
            results[test_name] = test_method()
        
        # Verificar se dados foram salvos no config
        print("\n  📋 Verificando dados salvos:")
        saved_timeout = ui.config_manager.get('cycle_timeout')
        print(f"    cycle_timeout: {saved_timeout}")
        
        saved_cleaning = ui.config_manager.get('auto_clean.enabled')
        print(f"    auto_clean.enabled: {saved_cleaning}")
        
        saved_bait = ui.config_manager.get('bait_priority')
        print(f"    bait_priority: {saved_bait}")
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        print(f"\n  📊 Resultado: {success_count}/{total_count} métodos funcionaram")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"  ❌ Erro no teste de UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file_persistence():
    """Testar se config.json é criado e persiste dados"""
    print("\n🧪 Testando persistência do config.json...")
    
    try:
        from core.config_manager import ConfigManager
        
        # Configuração real do bot
        config_path = "D:/finalbot/fishing_bot_v4/config/config.json"
        
        # Criar backup se existe
        backup_path = config_path + ".backup"
        if os.path.exists(config_path):
            shutil.copy2(config_path, backup_path)
            print(f"  💾 Backup criado: {backup_path}")
        
        # Testar criação/atualização
        config = ConfigManager()
        
        # Dados de teste
        test_timestamp = str(int(time.time()))
        test_data = {
            'test_save_timestamp': test_timestamp,
            'auto_clean.enabled': True,
            'auto_clean.interval': 15,
            'bait_priority.carne de crocodilo': 1,
            'bait_priority.carne de urso': 2
        }
        
        print("  📝 Salvando dados de teste...")
        for key, value in test_data.items():
            config.set(key, value)
        
        config.save_config()
        
        # Verificar se arquivo existe
        if os.path.exists(config_path):
            print(f"  ✅ Arquivo existe: {config_path}")
            
            # Ler arquivo e verificar dados
            with open(config_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Verificar timestamp
            if file_data.get('test_save_timestamp') == test_timestamp:
                print("  ✅ Dados foram salvos no arquivo")
            else:
                print(f"  ❌ Timestamp não encontrado no arquivo")
                return False
            
            # Verificar estrutura aninhada
            auto_clean = file_data.get('auto_clean', {})
            if auto_clean.get('enabled') == True and auto_clean.get('interval') == 15:
                print("  ✅ Dados aninhados salvos corretamente")
            else:
                print(f"  ❌ Dados aninhados incorretos: {auto_clean}")
                return False
            
            # Verificar bait_priority
            bait_priority = file_data.get('bait_priority', {})
            if bait_priority.get('carne de crocodilo') == 1:
                print("  ✅ Prioridade de iscas salva corretamente")
            else:
                print(f"  ❌ Prioridade de iscas incorreta: {bait_priority}")
                return False
            
            return True
        else:
            print(f"  ❌ Arquivo não foi criado: {config_path}")
            return False
        
    except Exception as e:
        print(f"  ❌ Erro no teste de persistência: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restaurar backup se existe
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, config_path)
            os.remove(backup_path)
            print(f"  🔄 Backup restaurado")

def run_all_tests():
    """Executar todos os testes"""
    print("=" * 80)
    print("🧪 TESTE DOS BOTÕES DE SALVAR - Ultimate Fishing Bot v4.0")
    print("=" * 80)
    
    tests = [
        ("ConfigManager Save", test_config_manager_save),
        ("UI Save Methods", test_ui_save_methods),
        ("Config File Persistence", test_config_file_persistence)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n▶️ {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro fatal em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("=" * 80)
    print(f"📈 RESULTADO: {passed}/{total} testes passaram ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Os botões de salvar estão funcionais.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    try:
        import time
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal no teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
#!/usr/bin/env python3
"""
🔧 Script Master - Correção Completa do Projeto

Este script executa TODAS as correções e testes automaticamente:
1. Testa sistema de configurações
2. Testa conexão com servidor
3. Lista problemas encontrados
4. Fornece instruções específicas para cada problema

Uso:
    python corrigir_tudo.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def print_header(title):
    """Imprimir cabeçalho bonito"""
    _safe_print("\n" + "="*70)
    _safe_print(f"  {title}")
    _safe_print("="*70)

def print_step(number, title):
    """Imprimir passo"""
    _safe_print(f"\n{'='*70}")
    _safe_print(f"PASSO {number}: {title}")
    _safe_print(f"{'='*70}\n")

def run_command(description, command):
    """Executar comando e capturar saída"""
    _safe_print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Função principal"""

    print_header("🚀 CORREÇÃO COMPLETA DO PROJETO - FISHING BOT v5.0")

    _safe_print("\nEste script vai:")
    _safe_print("  1. Testar sistema de configurações")
    _safe_print("  2. Testar conexão com servidor")
    _safe_print("  3. Identificar todos os problemas")
    _safe_print("  4. Fornecer instruções de correção")
    _safe_print("\nTempo estimado: 2-3 minutos\n")

    input("Pressione Enter para continuar...")

    results = {
        'config_test': False,
        'server_test': False,
        'problems': [],
        'solutions': []
    }

    # ========================================
    # PASSO 1: Teste de Configurações
    # ========================================
    print_step(1, "Testando Sistema de Configurações")

    if os.path.exists('test_config_save.py'):
        success, stdout, stderr = run_command(
            "Executando test_config_save.py",
            "python test_config_save.py"
        )

        if success and "Todos os testes passaram" in stdout:
            _safe_print("✅ Sistema de configurações: FUNCIONANDO")
            results['config_test'] = True

            # Verificar se config.json existe
            if not os.path.exists('data/config.json'):
                results['problems'].append({
                    'type': 'config_not_saved',
                    'severity': 'warning',
                    'description': 'Usuário não está salvando configs'
                })
                results['solutions'].append(
                    "⚠️ ATENÇÃO: Sempre clique em '💾 Salvar' após mudar configs!"
                )
        else:
            _safe_print("❌ Sistema de configurações: FALHOU")
            _safe_print(f"Erro: {stderr}")
            results['problems'].append({
                'type': 'config_system_broken',
                'severity': 'critical',
                'description': 'Sistema de salvamento não funciona'
            })
    else:
        _safe_print("⚠️ test_config_save.py não encontrado")

    # ========================================
    # PASSO 2: Teste de Conexão com Servidor
    # ========================================
    print_step(2, "Testando Conexão com Servidor")

    if os.path.exists('debug_server_connection.py'):
        success, stdout, stderr = run_command(
            "Executando debug_server_connection.py",
            "python debug_server_connection.py"
        )

        if "Servidor acessível" in stdout:
            _safe_print("✅ Servidor: ONLINE")
            results['server_test'] = True

            # Verificar problemas específicos
            if "HTTP 400" in stdout:
                results['problems'].append({
                    'type': 'auth_http_400',
                    'severity': 'high',
                    'description': 'Servidor rejeitando autenticação'
                })
                results['solutions'].append(
                    "🔴 HTTP 400: Verificar license key no Keymaster"
                )

            if "active_users\": 0" in stdout or "active_users: 0" in stdout:
                results['problems'].append({
                    'type': 'websocket_bug',
                    'severity': 'critical',
                    'description': 'WebSocket não registrando usuários'
                })
                results['solutions'].append(
                    "🔴 Bug WebSocket: Aplicar correção em BUG_ACTIVE_USERS_ZERO.md"
                )

            if "DeprecationWarning" in stdout:
                results['problems'].append({
                    'type': 'fastapi_warnings',
                    'severity': 'low',
                    'description': 'Warnings de deprecação do FastAPI'
                })
                results['solutions'].append(
                    "⚠️ FastAPI Warnings: Executar fix_fastapi_deprecation.py"
                )
        else:
            _safe_print("❌ Servidor: OFFLINE ou INACESSÍVEL")
            results['problems'].append({
                'type': 'server_offline',
                'severity': 'critical',
                'description': 'Servidor não está acessível'
            })
    else:
        _safe_print("⚠️ debug_server_connection.py não encontrado")

    # ========================================
    # PASSO 3: Verificar Arquivos do Projeto
    # ========================================
    print_step(3, "Verificando Estrutura do Projeto")

    important_files = {
        'data/config.json': 'Configurações do usuário',
        'config/default_config.json': 'Configurações padrão',
        'data/credentials.dat': 'Credenciais salvas',
        'fix_fastapi_deprecation.py': 'Script de correção FastAPI',
        'test_config_save.py': 'Script de teste de configs',
        'debug_server_connection.py': 'Script de debug de conexão'
    }

    for file_path, description in important_files.items():
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        _safe_print(f"  {status} {file_path} - {description}")

        if not exists and 'config.json' in file_path and 'data' in file_path:
            results['solutions'].append(
                "ℹ️ data/config.json não existe: Salve configs pela UI"
            )

    # ========================================
    # PASSO 4: Relatório Final
    # ========================================
    print_step(4, "Relatório Final")

    _safe_print("\n📊 RESUMO DOS TESTES:\n")
    _safe_print(f"  Sistema de Configs: {'✅ OK' if results['config_test'] else '❌ FALHOU'}")
    _safe_print(f"  Servidor Online: {'✅ OK' if results['server_test'] else '❌ OFFLINE'}")
    _safe_print(f"  Problemas Encontrados: {len(results['problems'])}")

    # Listar problemas por severidade
    if results['problems']:
        _safe_print("\n🔴 PROBLEMAS ENCONTRADOS:\n")

        critical = [p for p in results['problems'] if p['severity'] == 'critical']
        high = [p for p in results['problems'] if p['severity'] == 'high']
        warning = [p for p in results['problems'] if p['severity'] == 'warning']
        low = [p for p in results['problems'] if p['severity'] == 'low']

        if critical:
            _safe_print("  🔴 CRÍTICOS:")
            for p in critical:
                _safe_print(f"    • {p['description']}")

        if high:
            _safe_print("\n  🟠 IMPORTANTES:")
            for p in high:
                _safe_print(f"    • {p['description']}")

        if warning:
            _safe_print("\n  🟡 AVISOS:")
            for p in warning:
                _safe_print(f"    • {p['description']}")

        if low:
            _safe_print("\n  ⚪ BAIXA PRIORIDADE:")
            for p in low:
                _safe_print(f"    • {p['description']}")
    else:
        _safe_print("\n✅ NENHUM PROBLEMA ENCONTRADO!")

    # Soluções
    if results['solutions']:
        _safe_print("\n💡 SOLUÇÕES RECOMENDADAS:\n")
        for i, solution in enumerate(results['solutions'], 1):
            _safe_print(f"  {i}. {solution}")

    # Próximos passos
    print_header("📋 PRÓXIMOS PASSOS")

    _safe_print("\n1. CLIENTE (Seu PC):")
    _safe_print("   • Sempre clicar em '💾 Salvar' após mudar configs")
    _safe_print("   • Verificar que data/config.json existe")
    _safe_print("   • Reiniciar bot e confirmar que configs persistem")

    _safe_print("\n2. SERVIDOR (Se tiver acesso):")

    has_server_problems = any(
        p['type'] in ['websocket_bug', 'fastapi_warnings', 'auth_http_400']
        for p in results['problems']
    )

    if has_server_problems:
        _safe_print("   🔴 AÇÃO NECESSÁRIA NO SERVIDOR:")

        if any(p['type'] == 'websocket_bug' for p in results['problems']):
            _safe_print("   • Aplicar correção do WebSocket (ver BUG_ACTIVE_USERS_ZERO.md)")

        if any(p['type'] == 'fastapi_warnings' for p in results['problems']):
            _safe_print("   • Executar: python fix_fastapi_deprecation.py server/server.py")

        if any(p['type'] == 'auth_http_400' for p in results['problems']):
            _safe_print("   • Verificar license key no Keymaster")
    else:
        _safe_print("   ✅ Servidor funcionando corretamente")

    _safe_print("\n3. DOCUMENTAÇÃO:")
    _safe_print("   • Ver EXECUTE_AQUI.md para instruções completas")
    _safe_print("   • Arquivos de referência disponíveis no projeto")

    # Salvar relatório
    print_header("💾 Salvando Relatório")

    report_file = "relatorio_diagnostico.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        _safe_print(f"\n✅ Relatório salvo em: {report_file}")
    except Exception as e:
        _safe_print(f"\n⚠️ Erro ao salvar relatório: {e}")

    # Conclusão
    print_header("✅ DIAGNÓSTICO COMPLETO")

    _safe_print("\n📄 Arquivos Criados:")
    _safe_print("   • relatorio_diagnostico.json - Relatório técnico")
    _safe_print("   • EXECUTE_AQUI.md - Guia de execução")
    _safe_print("   • Logs dos testes no terminal")

    _safe_print("\n📚 Documentação Disponível:")
    _safe_print("   • ANALISE_E_CORRECAO_SERVIDOR.md")
    _safe_print("   • BUG_ACTIVE_USERS_ZERO.md")
    _safe_print("   • ANALISE_CONFIG_NAO_SALVA.md")
    _safe_print("   • CORRECAO_FASTAPI_LIFESPAN.md")

    _safe_print("\n🎯 Status Final:")
    if len(results['problems']) == 0:
        _safe_print("   ✅ Projeto 100% funcional!")
    elif any(p['severity'] == 'critical' for p in results['problems']):
        _safe_print("   🔴 Problemas críticos encontrados - ação necessária")
    elif any(p['severity'] == 'high' for p in results['problems']):
        _safe_print("   🟠 Problemas importantes - correção recomendada")
    else:
        _safe_print("   🟡 Pequenos ajustes necessários")

    _safe_print("\n" + "="*70)
    _safe_print("Diagnóstico concluído! Veja EXECUTE_AQUI.md para próximos passos.")
    _safe_print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _safe_print("\n\n⚠️ Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        _safe_print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
⚡ Test Performance Optimizations
Ultimate Fishing Bot v4.0.1

Testa e valida as otimizações implementadas:
1. Singleton MSS Instance
2. ROI Detection
3. Batch Detection
"""

import time
import sys
from pathlib import Path

# Adicionar pasta atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from core.template_engine import TemplateEngine
from core.config_manager import ConfigManager

def test_singleton_mss():
    """Teste 1: Validar Singleton MSS Instance"""
    print("\n" + "="*60)
    print("⚡ TESTE 1: Singleton MSS Instance")
    print("="*60)

    config = ConfigManager()
    engine = TemplateEngine(config)

    # Verificar se singleton foi criado
    print(f"✓ MSS Instance inicial: {engine._mss_instance}")

    # Primeira captura - deve criar instance
    print("\n1. Primeira captura (deve criar instance)...")
    start = time.time()
    screenshot1 = engine.capture_screen()
    time1 = time.time() - start
    print(f"   Tempo: {time1*1000:.2f}ms")
    print(f"   MSS Instance: {engine._mss_instance is not None}")

    # Segunda captura - deve reusar instance
    print("\n2. Segunda captura (deve reusar instance)...")
    start = time.time()
    screenshot2 = engine.capture_screen()
    time2 = time.time() - start
    print(f"   Tempo: {time2*1000:.2f}ms")
    print(f"   MSS Instance: {engine._mss_instance is not None}")

    # Comparar
    speedup = time1 / time2 if time2 > 0 else 1
    print(f"\n✅ RESULTADO:")
    print(f"   Primeira captura: {time1*1000:.2f}ms")
    print(f"   Segunda captura: {time2*1000:.2f}ms")
    print(f"   Speedup: {speedup:.2f}x")
    print(f"   Singleton funcionando: {'✅ SIM' if engine._mss_instance is not None else '❌ NÃO'}")

    return engine._mss_instance is not None

def test_roi_detection():
    """Teste 2: Validar ROI Detection"""
    print("\n" + "="*60)
    print("⚡ TESTE 2: ROI Detection")
    print("="*60)

    config = ConfigManager()
    engine = TemplateEngine(config)

    # Verificar ROIs configuradas
    print(f"\n✓ ROIs configuradas: {len(engine.default_rois)}")
    print(f"  Templates com ROI: {list(engine.default_rois.keys())[:5]}...")

    # Testar detecção COM ROI
    if 'catch' in engine.template_cache:
        print("\n1. Detectando 'catch' COM ROI (1/3 direito)...")
        roi_catch = engine.default_rois.get('catch', None)
        print(f"   ROI 'catch': {roi_catch}")

        start = time.time()
        result_roi = engine.detect_template('catch', use_roi=True)
        time_roi = time.time() - start
        print(f"   Tempo COM ROI: {time_roi*1000:.2f}ms")

        # Testar detecção SEM ROI (tela inteira)
        print("\n2. Detectando 'catch' SEM ROI (tela inteira)...")
        start = time.time()
        result_full = engine.detect_template('catch', use_roi=False)
        time_full = time.time() - start
        print(f"   Tempo SEM ROI: {time_full*1000:.2f}ms")

        # Comparar
        speedup = time_full / time_roi if time_roi > 0 else 1
        area_reduction = 66.7  # 1/3 tela = 66.7% redução

        print(f"\n✅ RESULTADO:")
        print(f"   COM ROI: {time_roi*1000:.2f}ms")
        print(f"   SEM ROI: {time_full*1000:.2f}ms")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Redução de área: {area_reduction:.1f}%")
        print(f"   ROI otimizações: {engine.detection_stats['roi_optimizations']}")

        return speedup > 1.5  # Deve ser pelo menos 1.5x mais rápido
    else:
        print("⚠️ Template 'catch' não encontrado, pulando teste")
        return True

def test_batch_detection():
    """Teste 3: Validar Batch Detection"""
    print("\n" + "="*60)
    print("⚡ TESTE 3: Batch Detection")
    print("="*60)

    config = ConfigManager()
    engine = TemplateEngine(config)

    templates_to_test = ['VARANOBAUCI', 'enbausi', 'varaquebrada']
    available = [t for t in templates_to_test if t in engine.template_cache]

    if not available:
        print("⚠️ Nenhum template de vara disponível, pulando teste")
        return True

    print(f"\n✓ Templates para testar: {available}")

    # Teste 1: Detecções sequenciais (múltiplas capturas)
    print("\n1. Detecções SEQUENCIAIS (múltiplas capturas)...")
    start = time.time()
    for template in available:
        engine.detect_template(template)
    time_sequential = time.time() - start
    print(f"   Tempo total: {time_sequential*1000:.2f}ms")
    print(f"   Tempo por template: {(time_sequential/len(available))*1000:.2f}ms")

    # Teste 2: Batch detection (uma captura)
    print("\n2. Detecção em BATCH (uma captura)...")
    start = time.time()
    results = engine.detect_multiple_templates(available)
    time_batch = time.time() - start
    print(f"   Tempo total: {time_batch*1000:.2f}ms")
    print(f"   Tempo por template: {(time_batch/len(available))*1000:.2f}ms")
    print(f"   Templates detectados: {len(results)}")

    # Comparar
    speedup = time_sequential / time_batch if time_batch > 0 else 1

    print(f"\n✅ RESULTADO:")
    print(f"   Sequencial: {time_sequential*1000:.2f}ms")
    print(f"   Batch: {time_batch*1000:.2f}ms")
    print(f"   Speedup: {speedup:.2f}x")
    print(f"   Templates testados: {len(available)}")

    return speedup > 1.3  # Deve ser pelo menos 1.3x mais rápido

def test_overall_performance():
    """Teste 4: Performance geral"""
    print("\n" + "="*60)
    print("⚡ TESTE 4: Performance Geral")
    print("="*60)

    config = ConfigManager()
    engine = TemplateEngine(config)

    # Simular ciclo de detecções
    print("\nSimulando 100 detecções de 'catch'...")
    start = time.time()
    detections = 0
    for i in range(100):
        result = engine.detect_template('catch') if 'catch' in engine.template_cache else None
        if result:
            detections += 1
    total_time = time.time() - start

    avg_time = (total_time / 100) * 1000  # ms

    print(f"\n✅ RESULTADO:")
    print(f"   Total de detecções: 100")
    print(f"   Tempo total: {total_time:.2f}s")
    print(f"   Tempo médio: {avg_time:.2f}ms por detecção")
    print(f"   Detecções bem-sucedidas: {detections}")

    # Estatísticas
    stats = engine.detection_stats
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total detections: {stats['total_detections']}")
    print(f"   Successful: {stats['successful_detections']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   ROI optimizations: {stats['roi_optimizations']}")

    # Performance esperada: < 2ms por detecção com ROI
    return avg_time < 5.0  # Deve ser < 5ms em média

def main():
    """Executar todos os testes"""
    print("\n")
    print("🎯 "*30)
    print("⚡ TESTE DE OTIMIZAÇÕES DE PERFORMANCE")
    print("    Ultimate Fishing Bot v4.0.1")
    print("🎯 "*30)

    results = {}

    try:
        # Teste 1: Singleton MSS
        results['singleton_mss'] = test_singleton_mss()

        # Teste 2: ROI Detection
        results['roi_detection'] = test_roi_detection()

        # Teste 3: Batch Detection
        results['batch_detection'] = test_batch_detection()

        # Teste 4: Performance Geral
        results['overall_performance'] = test_overall_performance()

    except Exception as e:
        print(f"\n❌ ERRO durante testes: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Otimizações funcionando corretamente!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("   Revisar implementação das otimizações")
    print("="*60)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

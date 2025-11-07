#!/usr/bin/env python3
"""
📦 InventoryManager - Sistema de Gerenciamento de Inventário v4.0

Baseado na lógica FUNCIONAL do auto_clean_inventario_no_chest() 
do botpesca.py que JÁ FUNCIONA no v3.

Funcionalidades:
- Detecção automática de peixes no inventário
- Transferência inteligente para baú
- Limpeza coordenada via ChestManager
- Template matching para identificação de itens
- Configuração de intervalos automáticos
"""

import time
import threading
from typing import Optional, Dict, List, Tuple, Set
from enum import Enum
from .chest_manager import ChestOperation
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class ItemType(Enum):
    """Tipos de itens detectáveis"""
    FISH = "fish"
    BAIT = "bait"
    TOOL = "tool"
    MISC = "misc"
    UNKNOWN = "unknown"

class CleaningMode(Enum):
    """Modos de limpeza"""
    AUTO_INTERVAL = "auto_interval"  # A cada X pescas
    MANUAL_TRIGGER = "manual"        # Trigger manual (F8)
    INVENTORY_FULL = "full"          # Quando inventário cheio

class InventoryManager:
    """
    📦 Gerenciador de Inventário Inteligente
    
    Baseado na lógica comprovada do v3 que FUNCIONA
    """
    
    def __init__(self, template_engine, chest_manager, input_manager, config_manager=None):
        """Inicializar gerenciador de inventário"""
        self.template_engine = template_engine
        self.chest_manager = chest_manager
        self.input_manager = input_manager
        self.config_manager = config_manager
        
        # Lock para thread safety
        self.cleaning_lock = threading.RLock()
        
        # Estado do sistema
        self.last_cleaning_time = 0
        self.fish_count_since_cleaning = 0
        self.cleaning_in_progress = False
        self.last_cleaning_attempt = 0  # ✅ NOVO: Evita múltiplas chamadas em sequência
        
        # ===== CONFIGURAÇÃO BASEADA NO V3 =====
        
        # Coordenadas baseadas no v3 (EXATAS que funcionam)
        self.inventory_config = {
            # Área do inventário (lado esquerdo)
            'inventory_area': {
                'left': 633,
                'top': 541, 
                'width': 600,  # 1233 - 633
                'height': 412  # 953 - 541
            },
            
            # Área do baú (lado direito) 
            'chest_area': {
                'left': 1214,
                'top': 117,
                'width': 620,  # 1834 - 1214
                'height': 811  # 928 - 117
            },
            
            # Divisor entre inventário e baú
            'divider_x': 1242,
            
            # Grid do inventário (calculado)
            'slots_per_row': 6,
            'slot_width': 94,
            'slot_height': 94,
            'grid_start_x': 649,
            'grid_start_y': 560
        }
        
        # Templates de peixes para transferência
        self.fish_templates = {
            # Peixes que serão transferidos
            'SALMONN': 'SALMONN.png',           # Salmão
            'TROUTT': 'TROUTT.png',             # Truta
            'sardine': 'sardine.png',           # Sardinha
            'anchovy': 'anchovy.png',           # Anchova
            'yellowperch': 'yellowperch.png',   # Perca amarela
            'herring': 'herring.png',           # Arenque
            'peixecru': 'peixecru.png',         # Peixe cru
            'shark': 'shark.png',               # Tubarão
            'catfish': 'catfish.png',           # Bagre
            'roughy': 'roughy.png'              # Roughy
        }

        # Templates de iscas (TAMBÉM SERÃO TRANSFERIDAS para o baú)
        self.bait_templates = {
            'crocodilo': 'crocodilo.png',       # Carne de crocodilo
            'carneurso': 'carneurso.png',       # Carne de urso
            'carnedelobo': 'carnedelobo.png',   # Carne de lobo
            'grub': 'grub.png',                 # Larva
            'minhoca': 'minhoca.png'            # Minhoca
        }
        
        # Estatísticas
        self.stats = {
            'total_cleanings': 0,
            'successful_cleanings': 0,
            'failed_cleanings': 0,
            'items_transferred': 0,
            'fish_detected': 0
        }
        
        # Configurações padrão
        self.default_config = {
            'cleaning_mode': CleaningMode.AUTO_INTERVAL.value,
            'auto_clean_interval': 40,  # ✅ CORRIGIDO: A cada 40 peixes (não 1!)
            'transfer_fish_only': True,  # Transferir apenas peixes
            'keep_bait_in_inventory': True,  # Manter iscas no inventário
            'max_transfer_attempts': 3,  # Máx tentativas por item
            'transfer_delay': 0.15  # Delay entre transferências (0.1-0.2s)
        }
        
        _safe_print("📦 InventoryManager inicializado com lógica do v3")
    
    def get_cleaning_config(self) -> Dict:
        """Obter configurações de limpeza"""
        if not self.config_manager:
            return self.default_config.copy()

        # ✅ CORRIGIDO: Mapear keys corretamente entre código e config file
        # Código usa 'auto_clean_interval' mas config file usa 'interval'
        config = {
            'cleaning_mode': self.config_manager.get('auto_clean.mode', self.default_config['cleaning_mode']),
            'auto_clean_interval': self.config_manager.get('auto_clean.interval', self.default_config['auto_clean_interval']),
            'transfer_fish_only': self.config_manager.get('auto_clean.transfer_fish_only', self.default_config['transfer_fish_only']),
            'keep_bait_in_inventory': self.config_manager.get('auto_clean.keep_bait_in_inventory', self.default_config['keep_bait_in_inventory']),
            'max_transfer_attempts': self.default_config['max_transfer_attempts'],  # Sem config externo
            'transfer_delay': self.default_config['transfer_delay']  # Sem config externo
        }
        return config
    
    # ✅ MÉTODOS REMOVIDOS: should_trigger_cleaning() e increment_fish_count()
    # Lógica de decisão agora está no SERVIDOR (server.py)
    # Cliente apenas executa limpeza quando servidor comandar

    def execute_auto_clean(self, chest_managed_externally: bool = False) -> bool:
        """
        🧹 Executar limpeza automática completa
        
        Baseado em auto_clean_inventario_no_chest() do v3 linha ~22000
        Lógica EXATA que FUNCIONA no v3
        """
        try:
            with self.cleaning_lock:
                if self.cleaning_in_progress:
                    _safe_print("⚠️ Limpeza já em progresso")
                    return False

                # ✅ PROTEÇÃO EXTRA: Registrar tentativa
                self.last_cleaning_attempt = time.time()

                self.cleaning_in_progress = True
                
                _safe_print("\n" + "="*50)
                _safe_print("🧹 EXECUTANDO LIMPEZA AUTOMÁTICA DO INVENTÁRIO")
                _safe_print("="*50)
                
                self.stats['total_cleanings'] += 1
                
                # PASSO 1: Verificar se baú é gerenciado externamente (coordenador)
                if chest_managed_externally:
                    _safe_print("📦 PASSO 1: Baú gerenciado pelo coordenador (já aberto)")
                else:
                    _safe_print("📦 PASSO 1: Abrindo baú para limpeza...")
                    if not self._open_chest_for_cleaning():
                        _safe_print("❌ Falha ao abrir baú")
                        return False

                # PASSO 2: Aguardar baú estabilizar e itens carregarem
                if chest_managed_externally:
                    _safe_print("⏳ PASSO 2: Aguardando estabilizar e itens carregarem...")
                    time.sleep(2.0)  # Mais tempo para itens carregarem
                else:
                    _safe_print("⏳ PASSO 2: Aguardando baú abrir e itens carregarem...")
                    time.sleep(2.5)  # Mais tempo para abertura + carregamento
                
                # PASSO 3: Detectar e transferir itens
                _safe_print("🔍 PASSO 3: Detectando e transferindo peixes...")
                transfer_success = self._execute_fish_transfer()
                
                # PASSO 4: Fechar baú (apenas se abrimos nós mesmos)
                if chest_managed_externally:
                    _safe_print("📦 PASSO 4: Baú será fechado pelo coordenador")
                else:
                    _safe_print("📦 PASSO 4: Fechando baú...")
                    self._close_chest_after_cleaning()
                
                if transfer_success:
                    # Resetar contadores
                    self.last_cleaning_time = time.time()
                    self.fish_count_since_cleaning = 0
                    self.stats['successful_cleanings'] += 1
                    _safe_print("✅ Limpeza executada com sucesso!")
                    _safe_print("="*50)
                    return True
                else:
                    # ✅ Incrementar contador de falhas
                    self.stats['failed_cleanings'] += 1

                    # ✅ CRÍTICO: Resetar contadores para evitar loop infinito
                    _safe_print("⚠️ Falha na limpeza - resetando contadores...")
                    self.last_cleaning_time = time.time()
                    self.fish_count_since_cleaning = 0

                    _safe_print("❌ Falha na transferência de itens")
                    _safe_print("="*50)
                    return False

        except Exception as e:
            # ✅ Incrementar contador de falhas
            self.stats['failed_cleanings'] += 1

            # ✅ CRÍTICO: Resetar contadores para evitar loop infinito após erro
            _safe_print("⚠️ Erro na limpeza - resetando contadores...")
            self.last_cleaning_time = time.time()
            self.fish_count_since_cleaning = 0

            _safe_print(f"❌ Erro na limpeza: {e}")
            return False
        
        finally:
            self.cleaning_in_progress = False
            # Tentar fechar baú em caso de erro
            try:
                self._close_chest_after_cleaning()
            except:
                pass
    
    def _open_chest_for_cleaning(self) -> bool:
        """Abrir baú usando ChestManager"""
        try:
            if self.chest_manager:
                return self.chest_manager.open_chest(
                    operation=ChestOperation.CLEANING,
                    context="Limpeza automática do inventário"
                )
            
            _safe_print("⚠️ ChestManager não disponível")
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao abrir baú para limpeza: {e}")
            return False
    
    def _close_chest_after_cleaning(self) -> bool:
        """Fechar baú após limpeza"""
        try:
            if self.chest_manager:
                return self.chest_manager.close_chest(
                    context="Fim da limpeza"
                )
            
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao fechar baú: {e}")
            return False
    
    def _execute_fish_transfer(self) -> bool:
        """
        Executar transferência de peixes

        Baseado na lógica EXATA do v3:
        - Detectar peixes no inventário
        - Arrastar do inventário para baú
        - Evitar transferir iscas
        """
        try:
            config = self.get_cleaning_config()
            max_attempts = config['max_transfer_attempts']
            transfer_delay = config['transfer_delay']

            transferred_count = 0
            max_scan_attempts = 1  # ✅ APENAS 1 ESCANEAMENTO! Clicar 1x e voltar a pescar
            scan_attempt = 0

            _safe_print("🔍 Iniciando limpeza (1 escaneamento apenas)...")

            while scan_attempt < max_scan_attempts:
                scan_attempt += 1
                _safe_print(f"📍 Escaneamento {scan_attempt}/{max_scan_attempts}...")

                # Detectar peixes no inventário
                fish_positions = self._detect_fish_in_inventory()

                if not fish_positions:
                    _safe_print("✅ Nenhum peixe detectado - limpeza concluída!")
                    break

                # Limitar a 30 peixes máximo conforme solicitado
                fish_to_transfer = fish_positions[:30]
                if len(fish_positions) > 30:
                    _safe_print(f"⚠️ Detectados {len(fish_positions)} peixes, limitando a 30 conforme solicitado")

                _safe_print(f"🎯 Transferindo {len(fish_to_transfer)} peixes...")

                # ✅ CRÍTICO: Soltar ALT ANTES de CADA lote de cliques!
                _safe_print("🔓 Soltando ALT antes dos cliques direitos...")
                try:
                    if self.input_manager and hasattr(self.input_manager, 'key_up'):
                        self.input_manager.key_up('ALT')
                        _safe_print("   ✅ ALT solto via InputManager")
                    else:
                        import pyautogui
                        pyautogui.keyUp('alt')
                        _safe_print("   ✅ ALT solto via PyAutoGUI")
                    time.sleep(0.3)  # Delay para garantir que ALT foi solto
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro ao soltar ALT: {e}")

                # Transferir TODOS os peixes detectados (máximo 30)
                # ✅ CRÍTICO: max_attempts=1 - Clicar APENAS 1x por item (evitar loop)
                transferred_in_batch = 0

                for i, (fish_name, position) in enumerate(fish_to_transfer):
                    _safe_print(f"  🐟 {i+1}/{len(fish_to_transfer)}: {fish_name} em {position}...")

                    # ✅ CRÍTICO: max_attempts=1 - Apenas 1 clique por item!
                    if self._transfer_item_to_chest(position, max_attempts=1):
                        transferred_count += 1
                        transferred_in_batch += 1
                        _safe_print(f"    ✅ Transferido!")
                    else:
                        _safe_print(f"    ❌ Falha!")

                    # Delay mínimo entre cliques
                    if i < len(fish_to_transfer) - 1:  # Não esperar no último
                        time.sleep(0.1)  # Delay mínimo

                _safe_print(f"📦 Lote transferido: {transferred_in_batch}/{len(fish_to_transfer)}")

                # ✅ CRÍTICO: Sempre sair após 1 escaneamento (não re-escanear!)
                _safe_print("✅ Limpeza concluída (1 escaneamento executado)")
                _safe_print("🎣 Retornando à pesca (mesmo que itens permaneçam no inventário)")
                break

            _safe_print(f"📊 Total transferido: {transferred_count} itens em {scan_attempt} escaneamentos")

            if scan_attempt >= max_scan_attempts:
                _safe_print("⚠️ Atingido limite máximo de escaneamentos")

            return transferred_count > 0
            
        except Exception as e:
            _safe_print(f"❌ Erro na transferência de peixes: {e}")
            return False
    
    def _detect_fish_in_inventory(self) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Detectar peixes E ISCAS no inventário com NMS por grupos e global

        Returns:
            Lista de (nome_item, (x, y)) para cada item encontrado (peixes + iscas)
        """
        try:
            if not self.template_engine:
                _safe_print("❌ Template engine não disponível")
                return []

            # Capturar tela uma vez para eficiência
            screenshot = self.template_engine.capture_screen()
            if screenshot is None:
                _safe_print("❌ Falha ao capturar tela")
                return []

            # ✅ COPIAR LÓGICA DO CATCH VIEWER - TODOS OS PEIXES NO MESMO GRUPO
            template_groups = {
                'fish_general': list(self.fish_templates.keys()),  # ✅ TODOS os peixes juntos (igual Catch Viewer)
                'bait_general': list(self.bait_templates.keys())   # Iscas separadas
            }

            # Mapear template para grupo
            template_to_group = {}
            for group_name, templates in template_groups.items():
                for template in templates:
                    template_to_group[template.lower()] = group_name

            _safe_print(f"🔄 Detectando peixes E ISCAS com NMS avançado...")

            # Coletar todas as detecções de todos os templates (PEIXES + ISCAS)
            all_detections = []

            # ✅ Detectar PEIXES
            for fish_name in self.fish_templates.keys():
                if not self.template_engine.has_template(fish_name):
                    continue

                # Buscar múltiplas ocorrências deste template
                multiple_results = self._detect_multiple_occurrences_raw(fish_name, screenshot)

                # ✅ FILTRAR APENAS INVENTÁRIO (não baú)
                in_inventory = 0
                for x, y, conf, w, h in multiple_results:
                    if self._is_position_in_inventory(x, y):
                        in_inventory += 1
                        all_detections.append({
                            'template': fish_name,
                            'x': x, 'y': y,
                            'confidence': conf,
                            'w': w, 'h': h,
                            'group': template_to_group.get(fish_name.lower(), 'fish_general')
                        })


            # ✅ Detectar ISCAS
            for bait_name in self.bait_templates.keys():
                if not self.template_engine.has_template(bait_name):
                    continue

                # Buscar múltiplas ocorrências deste template de isca
                multiple_results = self._detect_multiple_occurrences_raw(bait_name, screenshot)

                for x, y, conf, w, h in multiple_results:
                    if self._is_position_in_inventory(x, y):
                        all_detections.append({
                            'template': bait_name,
                            'x': x, 'y': y,
                            'confidence': conf,
                            'w': w, 'h': h,
                            'group': 'bait_general'
                        })

            if not all_detections:
                _safe_print("ℹ️ Nenhum peixe ou isca detectado")
                return []

            # ✅ NMS POR GRUPOS (Task 1)
            group_filtered = []
            for group_name, templates in template_groups.items():
                group_detections = [d for d in all_detections if d['group'] == group_name]

                if not group_detections:
                    continue

                # Ordenar por qualidade
                def calc_quality(det):
                    distance = ((det['x'] - screenshot.shape[1]//2)**2 + (det['y'] - screenshot.shape[0]//2)**2)**0.5
                    return det['confidence'] * (1 - min(distance/10, 100)/100)

                group_detections.sort(key=calc_quality, reverse=True)

                # NMS dentro do grupo (80px)
                filtered = []
                for det in group_detections:
                    is_duplicate = False
                    for existing in filtered:
                        distance = ((det['x'] - existing['x'])**2 + (det['y'] - existing['y'])**2)**0.5
                        if distance < 80:
                            is_duplicate = True
                            _safe_print(f"   ❌ {det['template']} suprimido por {existing['template']} (dist: {distance:.1f})")
                            break

                    if not is_duplicate:
                        filtered.append(det)
                        quality = calc_quality(det)
                        _safe_print(f"   ✅ {det['template']} aceito (conf: {det['confidence']:.3f}, qual: {quality:.3f})")

                group_filtered.extend(filtered)

            # ✅ NMS GLOBAL CROSS-TEMPLATE (Task 2)
            _safe_print(f"🔄 Aplicando NMS GLOBAL em {len(group_filtered)} detecções...")

            # Ordenar todas por qualidade
            def calc_quality_final(det):
                distance = ((det['x'] - screenshot.shape[1]//2)**2 + (det['y'] - screenshot.shape[0]//2)**2)**0.5
                return det['confidence'] * (1 - min(distance/10, 100)/100)

            for det in group_filtered:
                det['quality'] = calc_quality_final(det)

            group_filtered.sort(key=lambda x: x['quality'], reverse=True)

            # NMS global entre grupos
            final_detections = []
            for det in group_filtered:
                is_overlapping = False

                for approved in final_detections:
                    distance = ((det['x'] - approved['x'])**2 + (det['y'] - approved['y'])**2)**0.5

                    # Mesmo grupo ou peixes similares
                    same_group = det['group'] == approved['group']
                    fish_groups = {'salmonn', 'troutt', 'fish_general'}
                    both_fish = det['group'] in fish_groups and approved['group'] in fish_groups

                    # ✅ LÓGICA CORRIGIDA: Manter apenas a detecção com MAIOR CONFIDENCE
                    # Se duas detecções estão próximas (< 50px), só uma é real
                    # Manter a de MAIOR confidence, independente do template

                    if distance < 50:
                        # Detecções próximas: comparar CONFIDENCE
                        if approved['confidence'] > det['confidence']:
                            # Approved tem maior confidence → descartar current
                            is_overlapping = True
                            _safe_print(f"   ❌ {det['template']} (conf:{det['confidence']:.3f}) suprimido por {approved['template']} (conf:{approved['confidence']:.3f}) - dist:{distance:.1f}px")
                            break
                        elif det['confidence'] > approved['confidence']:
                            # Current tem maior confidence → SUBSTITUIR approved
                            _safe_print(f"   🔄 {approved['template']} (conf:{approved['confidence']:.3f}) SUBSTITUÍDO por {det['template']} (conf:{det['confidence']:.3f}) - dist:{distance:.1f}px")
                            final_detections.remove(approved)
                            # Não marcar como overlapping - vai ser adicionado depois
                            break

                if not is_overlapping:
                    final_detections.append(det)
                    _safe_print(f"   ✅ {det['template']} FINAL aceito (qual: {det['quality']:.3f})")

            _safe_print(f"✅ NMS GLOBAL concluído: {len(final_detections)} detecções finais")

            # Converter para formato de retorno
            items_positions = []
            for det in final_detections:
                items_positions.append((det['template'], (det['x'], det['y'])))
                self.stats['fish_detected'] += 1

                # Identificar se é peixe ou isca
                item_type = "🎣 ISCA" if det['group'] == 'bait_general' else "🐟 PEIXE"
                _safe_print(f"    🎯 {item_type} {det['template']} detectado em ({det['x']}, {det['y']})")

            return items_positions

        except Exception as e:
            _safe_print(f"❌ Erro na detecção de peixes: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _detect_multiple_occurrences_raw(self, template_name: str, screenshot) -> List[Tuple[int, int, float, int, int]]:
        """
        Detectar múltiplas ocorrências RAW (sem NMS) para processamento em grupo

        Returns:
            Lista de (x, y, confidence, width, height)
        """
        try:
            import cv2
            import numpy as np

            # Verificar se template existe no cache
            if not self.template_engine.has_template(template_name):
                return []

            # Obter template do cache
            template = self.template_engine.template_cache[template_name]

            # Obter confidence do config
            confidence_threshold = self.template_engine.get_template_confidence(template_name)

            # ✅ COPIAR LÓGICA DO CATCH VIEWER - Threshold 0.85 para SALMONN/TROUTT
            template_clean = template_name.replace('.png', '').lower()
            if template_clean in ['salmonn', 'troutt']:
                confidence_threshold = 0.85  # ✅ EXATAMENTE como Catch Viewer (linha 3407-3410)

            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Encontrar múltiplas ocorrências acima do threshold
            locations = np.where(result >= confidence_threshold)

            # Obter dimensões do template
            h, w = template.shape[:2]

            # Converter para lista de coordenadas RAW (sem NMS)
            detections = []
            for y, x in zip(locations[0], locations[1]):
                center_x = x + w // 2
                center_y = y + h // 2
                confidence = result[y, x]

                detections.append((center_x, center_y, confidence, w, h))

            return detections

        except Exception as e:
            _safe_print(f"❌ Erro na detecção múltipla RAW de {template_name}: {e}")
            return []

    def _detect_multiple_occurrences(self, template_name: str, screenshot) -> List[Tuple[int, int]]:
        """Detectar múltiplas ocorrências com NMS avançado (viewer logic) - DEPRECATED"""
        try:
            import cv2
            import numpy as np

            # Verificar se template existe no cache
            if not self.template_engine.has_template(template_name):
                return []

            # Obter template do cache
            template = self.template_engine.template_cache[template_name]

            # Obter confidence do config
            confidence_threshold = self.template_engine.get_template_confidence(template_name)

            # ✅ THRESHOLD ESPECIAL para SALMONN/TROUTT (Task 3)
            template_clean = template_name.replace('.png', '').lower()
            if template_clean in ['salmonn', 'troutt']:
                confidence_threshold = max(confidence_threshold, 0.85)
                _safe_print(f"🎯 {template_name}: usando threshold 0.85 para maior precisão")

            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Encontrar múltiplas ocorrências acima do threshold
            locations = np.where(result >= confidence_threshold)

            # Obter dimensões do template
            h, w = template.shape[:2]

            # Converter para lista de coordenadas com confidence
            detections = []
            for y, x in zip(locations[0], locations[1]):
                center_x = x + w // 2
                center_y = y + h // 2
                confidence = result[y, x]

                detections.append((center_x, center_y, confidence, w, h))

            if not detections:
                return []

            # ✅ SISTEMA DE QUALIDADE (Task 5)
            def calculate_quality(det):
                """Calcular qualidade = confidence × (1 - distance_from_center/100)"""
                x, y, conf, w, h = det
                # Distância do centro da tela (normalizada)
                screen_center_x = screenshot.shape[1] // 2
                screen_center_y = screenshot.shape[0] // 2
                distance = ((x - screen_center_x)**2 + (y - screen_center_y)**2)**0.5
                distance_normalized = min(distance / 10, 100)  # Normalizar para 0-100
                quality = conf * (1 - distance_normalized / 100)
                return quality

            # Ordenar por qualidade (maior primeiro)
            detections.sort(key=calculate_quality, reverse=True)

            # ✅ NMS COM DISTÂNCIA AUMENTADA (Task 4)
            filtered_detections = []
            min_distance = 80  # ✅ Aumentado de 25→80px

            for x, y, conf, w, h in detections:
                # Verificar se está muito próximo de detecções já aceitas
                too_close = False
                for fx, fy in filtered_detections:
                    distance = ((x - fx)**2 + (y - fy)**2)**0.5
                    if distance < min_distance:
                        too_close = True
                        break

                if not too_close:
                    filtered_detections.append((x, y))
                    quality = calculate_quality((x, y, conf, w, h))
                    _safe_print(f"   ✅ {template_name} aceito em ({x},{y}) - conf: {conf:.3f}, qual: {quality:.3f}")

            return filtered_detections

        except Exception as e:
            _safe_print(f"❌ Erro na detecção múltipla de {template_name}: {e}")
            return []
    
    def _is_position_in_inventory(self, x: int, y: int) -> bool:
        """Verificar se posição está na área do inventário"""
        inv_area = self.inventory_config['inventory_area']
        
        return (inv_area['left'] <= x <= inv_area['left'] + inv_area['width'] and
                inv_area['top'] <= y <= inv_area['top'] + inv_area['height'])
    
    def _transfer_item_to_chest(self, from_position: Tuple[int, int], max_attempts: int = 3) -> bool:
        """
        Transferir item específico do inventário para o baú

        NOVA LÓGICA: Clique direito no centro da detecção do peixe
        """
        try:
            from_x, from_y = from_position

            for attempt in range(max_attempts):
                try:
                    _safe_print(f"    🖱️ Tentativa {attempt + 1}: Clique direito em ({from_x}, {from_y})")

                    if self.input_manager:
                        # NOVA LÓGICA: Clique direito no centro da detecção
                        success = self._perform_right_click_transfer(from_x, from_y)

                        if success:
                            return True
                        else:
                            _safe_print(f"    ⚠️ Tentativa {attempt + 1} falhou")

                except Exception as e:
                    _safe_print(f"    ❌ Erro na tentativa {attempt + 1}: {e}")
                
                # Aguardar antes da próxima tentativa
                time.sleep(0.5)
            
            _safe_print(f"    ❌ Todas as {max_attempts} tentativas falharam")
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro na transferência: {e}")
            return False
    
    def _perform_right_click_transfer(self, center_x: int, center_y: int) -> bool:
        """
        Executar transferência via clique direito no centro da detecção

        GARANTIA: Mouse sempre no centro exato da detecção
        """
        try:
            # 1. Mover mouse para o centro EXATO da detecção
            try:
                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'move_to'):
                    self.input_manager.move_to(center_x, center_y)
                else:
                    import pyautogui
                    pyautogui.moveTo(center_x, center_y, duration=0.05)  # Movimento rápido e preciso
            except:
                return False

            # 2. Verificar se mouse está na posição correta
            time.sleep(0.05)  # Delay mínimo para estabilizar

            # 3. Clique direito EXATO no centro para transferir
            if not self.input_manager.click_right(center_x, center_y):
                _safe_print(f"    ❌ Falha no clique direito em ({center_x}, {center_y})")
                return False

            # 4. Delay otimizado para transferência processar (0.1-0.2s)
            time.sleep(0.15)

            _safe_print(f"    ✅ Clique direito executado em ({center_x}, {center_y})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique direito: {e}")
            return False
    
    def execute_cleaning(self) -> bool:
        """Método para o coordenador chamar - baú já está aberto"""
        return self.execute_auto_clean(chest_managed_externally=True)

    def manual_trigger(self) -> bool:
        """Trigger manual de limpeza (F5)"""
        _safe_print("🔧 [CLEANING] Trigger manual ativado (F5)")
        return self.execute_auto_clean()
    
    def reset_cleaning_counters(self):
        """Resetar contadores de limpeza"""
        with self.cleaning_lock:
            self.last_cleaning_time = time.time()
            self.fish_count_since_cleaning = 0
            _safe_print("🔄 Contadores de limpeza resetados")
    
    def get_cleaning_stats(self) -> Dict:
        """Obter estatísticas de limpeza"""
        return {
            'last_cleaning_time': self.last_cleaning_time,
            'fish_count_since_cleaning': self.fish_count_since_cleaning,
            'cleaning_in_progress': self.cleaning_in_progress,
            'stats': self.stats.copy(),
            'config': self.get_cleaning_config()
        }
    
    def get_inventory_info(self) -> Dict:
        """Obter informações do inventário"""
        try:
            if not self.template_engine:
                return {'error': 'Template engine não disponível'}
            
            # Detectar peixes atualmente no inventário
            fish_positions = self._detect_fish_in_inventory()
            
            return {
                'fish_count': len(fish_positions),
                'fish_detected': [name for name, pos in fish_positions],
                'inventory_area': self.inventory_config['inventory_area'],
                'chest_area': self.inventory_config['chest_area']
            }
            
        except Exception as e:
            return {'error': f'Erro ao obter info do inventário: {e}'}
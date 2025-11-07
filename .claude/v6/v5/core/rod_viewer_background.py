"""
🎣 Sistema de Análise Universal em Background - v4.0

Baseado na lógica EXATA do viewer da UI que funciona perfeitamente.
Usado para: MANUTENÇÃO, LIMPEZA, ALIMENTAÇÃO e qualquer sistema que precise detectar status de varas.
Executa análise sem abrir janela visual.
"""

import time
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)



@dataclass
class RodDetectionResult:
    """Resultado de detecção de vara"""
    slot: int
    status: str  # 'with_bait', 'without_bait', 'broken', 'empty'
    template: str
    confidence: float
    x: int
    y: int


class RodViewerBackground:
    """
    🎣 Sistema de Análise de Varas em Background

    Usa a mesma lógica do viewer da UI mas roda silenciosamente.
    Perfeito para manutenção de varas e sistemas automatizados.
    """

    def __init__(self, template_engine, config_manager):
        self.template_engine = template_engine
        self.config_manager = config_manager

        # Sistema de rastreamento (igual UI)
        self.rod_status_tracking = {
            'available_with_bait': [],
            'available_without_bait': [],
            'broken_rods': [],
            'empty_slots': [],
            'last_inventory_check': 0,
            'slots': {}  # Mapeamento detalhado por slot
        }

        # Coordenadas dos slots (EXATAS do v4 UI)
        self.SLOT_POSITIONS = {
            1: (709, 1005),   # Slot 1
            2: (805, 1005),   # Slot 2
            3: (899, 1005),   # Slot 3
            4: (992, 1005),   # Slot 4
            5: (1092, 1005),  # Slot 5
            6: (1188, 1005)   # Slot 6
        }

        # Templates de varas (IGUAL UI - baseados em arquivos EXISTENTES)
        self.rod_templates = {
            # VARAS COM ISCA (grupo rod_with_bait) - templates existentes
            'varanobauci': 'with_bait',        # varanobauci.png existe
            'VARANOBAUCI': 'with_bait',        # VARANOBAUCI.png existe (maiúsculo)
            'varacomisca': 'with_bait',        # varacomisca.png existe
            'comiscavara': 'with_bait',        # comiscavara.png existe
            'namaocomisca': 'with_bait',       # namaocomisca.png existe (restaurado)
            'comiscanamao': 'with_bait',       # comiscanamao.png existe (restaurado)

            # VARAS SEM ISCA (grupo rod_without_bait) - templates existentes
            'enbausi': 'without_bait',         # enbausi.png existe
            'varasemisca': 'without_bait',     # varasemisca.png existe
            'semiscavara': 'without_bait',     # semiscavara.png existe
            'namaosemisca': 'without_bait',    # namaosemisca.png existe (restaurado)
            'semiscanam': 'without_bait',      # semiscanam.png existe (restaurado)
            'semiscavaraescura': 'without_bait', # semiscavaraescura.png existe

            # VARAS QUEBRADAS (grupo rod_broken) - templates existentes
            'varaquebrada': 'broken',          # varaquebrada.png existe
            'nobauquebrada': 'broken'          # nobauquebrada.png existe
        }

        # Sistema de prioridades (EXATO do v4 UI)
        self.rod_priority = {
            'broken': 3,        # Maior prioridade
            'with_bait': 2,     # Prioridade média
            'without_bait': 1,  # Menor prioridade
            'empty': 0          # Sem prioridade
        }

        _safe_print("🎣 RodViewerBackground inicializado com lógica da UI v4")

    def analyze_rods_background(self, force_analysis: bool = False) -> Dict[int, str]:
        """
        🎯 Análise completa das varas em background

        Usa a MESMA lógica do viewer da UI, mas sem interface visual.

        Returns:
            Dict[int, str]: Mapeamento slot -> status
        """
        try:
            _safe_print("🎣 [BACKGROUND] Iniciando análise de varas...")

            # Verificar se inventário está aberto (obrigatório para análise precisa)
            inventory_open = self._check_inventory_open()
            if not inventory_open and not force_analysis:
                _safe_print("⚠️ [BACKGROUND] Inventário não está aberto - análise pode ser imprecisa")
                _safe_print("   💡 Dica: Abra o inventário para análise mais precisa")

            # Limpar listas atuais (igual UI)
            self.rod_status_tracking['available_with_bait'].clear()
            self.rod_status_tracking['available_without_bait'].clear()
            self.rod_status_tracking['broken_rods'].clear()
            self.rod_status_tracking['empty_slots'].clear()

            # Detectar todos os templates de vara (igual UI)
            current_frame_detections = self._detect_all_rod_templates()

            # Sistema de mapeamento de slots (IGUAL UI)
            slot_status = {1: 'empty', 2: 'empty', 3: 'empty', 4: 'empty', 5: 'empty', 6: 'empty'}
            slot_best_detection = {}

            # Analisar cada detecção e mapear para slots (IGUAL UI)
            detections_found = list(current_frame_detections.keys())

            for template_name in detections_found:
                template_clean = template_name.replace('.png', '')
                if template_clean in self.rod_templates:
                    rod_type = self.rod_templates[template_clean]

                    # Processar todas as detecções deste template
                    for det_x, det_y, confidence in current_frame_detections[template_name]:
                        # Encontrar slot mais próximo (IGUAL UI)
                        closest_slot = None
                        min_distance = float('inf')

                        for slot_num, (slot_x, slot_y) in self.SLOT_POSITIONS.items():
                            distance = ((det_x - slot_x)**2 + (det_y - slot_y)**2)**0.5
                            if distance < min_distance and distance < 100:  # Threshold igual UI
                                min_distance = distance
                                closest_slot = slot_num

                        # APLICAR SISTEMA DE PRIORIDADES (100% IGUAL UI - sem filtros extras)
                        if closest_slot:
                            current_priority = self.rod_priority.get(rod_type, 0)

                            # ✅ LÓGICA EXATA DO VIEWER DA UI QUE FUNCIONA:
                            # Se slot ainda não tem detecção OU nova detecção tem MAIOR PRIORIDADE
                            if (closest_slot not in slot_best_detection or
                                current_priority > slot_best_detection[closest_slot]['priority']):

                                slot_best_detection[closest_slot] = {
                                    'type': rod_type,
                                    'priority': current_priority,
                                    'template': template_name,
                                    'confidence': confidence,
                                    'distance': min_distance
                                }

            # Atualizar slot_status com as melhores detecções (IGUAL UI)
            for slot_num, detection_info in slot_best_detection.items():
                slot_status[slot_num] = detection_info['type']

            # Log do sistema de prioridades (IGUAL UI)
            if slot_best_detection:
                priority_log = []
                for slot_num, info in slot_best_detection.items():
                    priority_names = {3: 'QUEBRADA', 2: 'COM_ISCA', 1: 'SEM_ISCA'}
                    priority_log.append(f"Slot{slot_num}:{priority_names.get(info['priority'], 'UNKNOWN')}")
                _safe_print(f"🎯 [BACKGROUND] Prioridades aplicadas: {', '.join(priority_log)}")

            # Atualizar tracking baseado nos slots (IGUAL UI)
            for slot_num, status in slot_status.items():
                if status == 'with_bait':
                    self.rod_status_tracking['available_with_bait'].append(slot_num)
                elif status == 'without_bait':
                    self.rod_status_tracking['available_without_bait'].append(slot_num)
                elif status == 'broken':
                    self.rod_status_tracking['broken_rods'].append(slot_num)
                elif status == 'empty':
                    self.rod_status_tracking['empty_slots'].append(slot_num)

            # Salvar detalhes no mapeamento de slots
            self.rod_status_tracking['slots'] = slot_best_detection

            # Atualizar timestamp
            if inventory_open:
                self.rod_status_tracking['last_inventory_check'] = time.time()

            # Log resumo (igual UI mas mais conciso)
            with_bait_count = len(self.rod_status_tracking['available_with_bait'])
            without_bait_count = len(self.rod_status_tracking['available_without_bait'])
            broken_count = len(self.rod_status_tracking['broken_rods'])
            empty_count = len(self.rod_status_tracking['empty_slots'])

            _safe_print(f"📊 [BACKGROUND] Resultado da análise:")
            _safe_print(f"   ✅ COM isca: {with_bait_count} varas {self.rod_status_tracking['available_with_bait']}")
            _safe_print(f"   ⚠️ SEM isca: {without_bait_count} varas {self.rod_status_tracking['available_without_bait']}")
            _safe_print(f"   💥 QUEBRADAS: {broken_count} varas {self.rod_status_tracking['broken_rods']}")
            _safe_print(f"   ⚪ VAZIOS: {empty_count} slots {self.rod_status_tracking['empty_slots']}")

            return slot_status

        except Exception as e:
            _safe_print(f"❌ [BACKGROUND] Erro na análise: {e}")
            import traceback
            traceback.print_exc()
            return {1: 'unknown', 2: 'unknown', 3: 'unknown', 4: 'unknown', 5: 'unknown', 6: 'unknown'}

    def check_if_maintenance_needed(self) -> Dict[str, any]:
        """
        🔍 Verificar se manutenção é necessária (IDEAL para fluxos de comida/limpeza)

        Usado para decidir se vale a pena fazer manutenção já que o inventário está aberto.

        Returns:
            Dict com informações de necessidade de manutenção
        """
        try:
            # Análise rápida enquanto inventário está aberto
            slot_status = self.analyze_rods_background(force_analysis=True)

            broken_slots = [slot for slot, status in slot_status.items() if status == 'broken']
            empty_slots = [slot for slot, status in slot_status.items() if status == 'empty']
            no_bait_slots = [slot for slot, status in slot_status.items() if status == 'without_bait']

            # Calcular prioridade de manutenção
            needs_rods = len(broken_slots) + len(empty_slots)
            needs_bait = len(no_bait_slots)
            total_issues = needs_rods + needs_bait

            # Determinar se vale a pena fazer manutenção agora
            maintenance_recommended = total_issues >= 2  # Se 2+ problemas, vale a pena

            return {
                'maintenance_needed': total_issues > 0,
                'maintenance_recommended': maintenance_recommended,
                'priority_score': total_issues,
                'broken_slots': broken_slots,
                'empty_slots': empty_slots,
                'no_bait_slots': no_bait_slots,
                'needs_rods': needs_rods,
                'needs_bait': needs_bait,
                'summary': f"{needs_rods} varas, {needs_bait} iscas"
            }
        except Exception as e:
            _safe_print(f"❌ Verificação de manutenção falhou: {e}")
            return {
                'maintenance_needed': False,
                'maintenance_recommended': False,
                'priority_score': 0,
                'broken_slots': [], 'empty_slots': [], 'no_bait_slots': [],
                'needs_rods': 0, 'needs_bait': 0,
                'summary': "Erro na verificação"
            }

    def quick_rod_check(self) -> Dict[str, List[int]]:
        """
        🚀 Verificação rápida para sistemas automatizados

        Ideal para alimentação, limpeza e outros sistemas que precisam
        saber rapidamente o status sem logs detalhados.

        Returns:
            Dict contendo listas de slots por categoria
        """
        try:
            # Análise silenciosa (sem logs detalhados)
            slot_status = self.analyze_rods_background(force_analysis=True)

            # Retornar resumo organizado
            return {
                'with_bait': [slot for slot, status in slot_status.items() if status == 'with_bait'],
                'without_bait': [slot for slot, status in slot_status.items() if status == 'without_bait'],
                'broken': [slot for slot, status in slot_status.items() if status == 'broken'],
                'empty': [slot for slot, status in slot_status.items() if status == 'empty'],
                'total_rods': len([s for s in slot_status.values() if s != 'empty']),
                'needs_attention': len([s for s in slot_status.values() if s in ['broken', 'without_bait']])
            }
        except Exception as e:
            _safe_print(f"❌ Quick check falhou: {e}")
            return {
                'with_bait': [], 'without_bait': [], 'broken': [], 'empty': [1,2,3,4,5,6],
                'total_rods': 0, 'needs_attention': 0
            }

    def _detect_all_rod_templates(self) -> Dict[str, List[Tuple[int, int, float]]]:
        """Detectar TODAS as ocorrências de templates de vara com NMS GLOBAL"""
        detections = {}

        _safe_print(f"🔍 [BACKGROUND] Detectando TODAS as ocorrências de {len(self.rod_templates)} templates...")

        # Capturar screenshot uma vez só para todas as detecções
        screenshot = self._capture_screenshot()
        if screenshot is None:
            _safe_print("❌ [BACKGROUND] Falha ao capturar screenshot")
            return detections

        # ✅ FASE 1: Detectar cada template individualmente
        raw_detections = {}
        for template_name in self.rod_templates.keys():
            try:
                # DETECTAR MÚLTIPLAS OCORRÊNCIAS usando OpenCV diretamente
                multiple_detections = self._detect_multiple_occurrences(template_name, screenshot)

                if multiple_detections:
                    raw_detections[template_name] = multiple_detections
                    _safe_print(f"   ✅ {template_name}: {len(multiple_detections)} detecções brutas")

            except Exception as e:
                _safe_print(f"⚠️ [BACKGROUND] Erro ao detectar {template_name}: {e}")
                continue

        total_raw = sum(len(det_list) for det_list in raw_detections.values())
        _safe_print(f"📊 [BACKGROUND] Total bruto: {total_raw} detecções")

        # ✅ FASE 2: Aplicar NMS GLOBAL CROSS-TEMPLATE (igual viewer UI)
        _safe_print(f"🔄 [BACKGROUND] Aplicando NMS global cross-template...")
        filtered_detections = self._apply_global_cross_template_nms(raw_detections)

        # Converter para formato de saída com .png
        for template_name, det_list in filtered_detections.items():
            detections[f"{template_name}.png"] = det_list
            if det_list:
                _safe_print(f"   ✅ {template_name}: {len(det_list)} detecções finais")
                for i, (x, y, conf) in enumerate(det_list, 1):
                    _safe_print(f"      {i}. centro=({x},{y}) conf={conf:.3f}")

        total_final = sum(len(det_list) for det_list in detections.values())
        _safe_print(f"✅ [BACKGROUND] Total final: {total_final} detecções após NMS global")

        return detections

    def _apply_global_cross_template_nms(self, raw_detections: Dict[str, List[Tuple[int, int, float]]]) -> Dict[str, List[Tuple[int, int, float]]]:
        """Aplicar NMS global entre diferentes templates (igual viewer UI)"""

        # ✅ IGUAL VISUALIZADOR: Todos os templates de vara no MESMO GRUPO
        template_groups = {
            'rod_all': ['varanobauci', 'VARANOBAUCI', 'varacomisca', 'comiscavara', 'namaocomisca', 'comiscanamao',
                       'enbausi', 'varasemisca', 'semiscavara', 'namaosemisca', 'semiscanam', 'semiscavaraescura',
                       'varaquebrada', 'nobauquebrada']
        }

        # Mapear template para grupo (CASE-INSENSITIVE como visualizador!)
        template_to_group = {}
        for group_name, templates in template_groups.items():
            for template in templates:
                # Adicionar em TODOS os casos para garantir match
                template_to_group[template] = group_name
                template_to_group[template.lower()] = group_name
                template_to_group[template.upper()] = group_name

        # Coletar todas as detecções com metadata
        all_detections = []
        for template_name, det_list in raw_detections.items():
            group = template_to_group.get(template_name, 'unknown')
            for x, y, conf in det_list:
                all_detections.append({
                    'template': template_name,
                    'x': x, 'y': y,
                    'confidence': conf,
                    'group': group,
                    'priority': self.rod_priority.get(self.rod_templates.get(template_name, 'empty'), 0)
                })

        if not all_detections:
            return {}

        _safe_print(f"   📊 Processando {len(all_detections)} detecções brutas...")

        # ✅ NMS POR GRUPOS (primeira passagem)
        group_filtered = []
        for group_name in template_groups.keys():
            group_dets = [d for d in all_detections if d['group'] == group_name]
            if not group_dets:
                continue

            _safe_print(f"   🔄 Grupo '{group_name}': {len(group_dets)} detecções - aplicando NMS...")

            # Ordenar por confiança + prioridade
            group_dets.sort(key=lambda d: (d['priority'], d['confidence']), reverse=True)

            # NMS dentro do grupo (80px)
            filtered = []
            for det in group_dets:
                is_duplicate = False
                for existing in filtered:
                    distance = ((det['x'] - existing['x'])**2 + (det['y'] - existing['y'])**2)**0.5
                    if distance < 80:
                        is_duplicate = True
                        _safe_print(f"      ❌ {det['template']} suprimido por {existing['template']} (dist: {distance:.1f})")
                        break

                if not is_duplicate:
                    filtered.append(det)
                    _safe_print(f"      ✅ {det['template']} aceito (conf: {det['confidence']:.3f})")

            group_filtered.extend(filtered)

        # ✅ NMS GLOBAL entre grupos (segunda passagem) - LÓGICA EXATA DA UI
        _safe_print(f"   🔄 Aplicando NMS global em {len(group_filtered)} detecções...")

        # Calcular qualidade para cada detecção (IGUAL UI)
        for det in group_filtered:
            det['quality'] = det['confidence']

        # Ordenar por qualidade (melhor primeiro) - IGUAL UI
        group_filtered.sort(key=lambda d: d['quality'], reverse=True)

        # ✅ THRESHOLDS DIFERENCIADOS (IGUAL UI)
        overlap_threshold_same_template = 15   # Mesmo template (IGUAL UI linha 3572)
        overlap_threshold_different = 80       # Templates diferentes (IGUAL UI linha 3573)

        final_filtered = []
        for det in group_filtered:
            is_overlapping = False

            for approved in final_filtered:
                distance = ((det['x'] - approved['x'])**2 + (det['y'] - approved['y'])**2)**0.5

                # Verificar tipo de conflito
                same_template = det['template'] == approved['template']
                same_group = det['group'] == approved['group']

                # ✅ LÓGICA DIFERENCIADA (IGUAL UI linhas 3597-3633)
                if same_template:
                    # MESMO template: threshold 15px (IGUAL UI)
                    if distance < overlap_threshold_same_template:
                        is_overlapping = True
                        _safe_print(f"      ❌ {det['template']} duplicata suprimida (dist: {distance:.1f})")
                        break

                elif same_group:
                    # MESMO GRUPO: threshold 80px, pode substituir (IGUAL UI)
                    if distance < overlap_threshold_different:
                        if approved['quality'] > det['quality']:
                            is_overlapping = True
                            _safe_print(f"      ❌ {det['template']} suprimido por {approved['template']} (mesmo grupo, qual: {approved['quality']:.3f} > {det['quality']:.3f})")
                            break
                        else:
                            # Novo é melhor, remover o aprovado (IGUAL UI linha 3613)
                            final_filtered.remove(approved)
                            _safe_print(f"      🔄 {approved['template']} removido, {det['template']} é melhor (qual: {det['quality']:.3f} > {approved['quality']:.3f})")

                else:
                    # GRUPOS DIFERENTES: threshold 80px com margem de qualidade (IGUAL UI linha 3627)
                    if distance < overlap_threshold_different:
                        quality_diff = approved['quality'] - det['quality']
                        if quality_diff > 0.15:  # Diferença significativa (IGUAL UI linha 3630)
                            is_overlapping = True
                            _safe_print(f"      ❌ {det['template']} suprimido por {approved['template']} (qual: {quality_diff:.3f})")
                            break

            if not is_overlapping:
                final_filtered.append(det)
                _safe_print(f"      ✅ {det['template']} FINAL aceito (qual: {det['quality']:.3f})")

        # Reagrupar por template
        result = {}
        for det in final_filtered:
            template_name = det['template']
            if template_name not in result:
                result[template_name] = []
            result[template_name].append((det['x'], det['y'], det['confidence']))

        return result

    def _capture_screenshot(self):
        """
        Capturar screenshot usando TemplateEngine (thread-safe!)

        Reutiliza o sistema de captura já otimizado e thread-safe do TemplateEngine
        ao invés de criar nova instância MSS.
        """
        try:
            # ✅ USAR TEMPLATE ENGINE (thread-safe com MSS thread-local)
            screenshot = self.template_engine.capture_screen()

            if screenshot is not None:
                _safe_print(f"✅ [BACKGROUND] Screenshot capturado: {screenshot.shape[1]}x{screenshot.shape[0]}")
                return screenshot
            else:
                _safe_print("❌ [BACKGROUND] Falha na captura via TemplateEngine")
                return None

        except Exception as e:
            _safe_print(f"❌ [BACKGROUND] Erro ao capturar screenshot: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _detect_multiple_occurrences(self, template_name: str, screenshot) -> List[Tuple[int, int, float]]:
        """Detectar múltiplas ocorrências de um template com NMS avançado"""
        detections = []

        try:
            # Obter template do cache
            if template_name not in self.template_engine.template_cache:
                # 🔍 DEBUG: Verificar se template existe em lowercase ou outras variações
                _safe_print(f"⚠️ [DEBUG] Template '{template_name}' não encontrado no cache!")
                _safe_print(f"   Cache disponível ({len(self.template_engine.template_cache)} templates): {list(self.template_engine.template_cache.keys())[:15]}...")

                # Tentar lowercase
                template_name_lower = template_name.lower()
                if template_name_lower in self.template_engine.template_cache:
                    _safe_print(f"   ✅ Encontrado em lowercase: {template_name_lower}")
                    template_name = template_name_lower
                else:
                    return detections

            template = self.template_engine.template_cache[template_name]
            if template is None:
                return detections

            # Configuração de confiança (IGUAL UI - sem override especial)
            confidence_threshold = self.template_engine.confidence_config.get(template_name, 0.7)

            # Executar template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Encontrar todas as localizações acima do threshold
            locations = np.where(result >= confidence_threshold)

            # Obter tamanho do template
            template_height, template_width = template.shape[:2]

            # Processar cada detecção
            for y, x in zip(locations[0], locations[1]):
                confidence = result[y, x]

                # Calcular centro (não canto superior esquerdo)
                center_x = x + template_width // 2
                center_y = y + template_height // 2

                detections.append((center_x, center_y, float(confidence), template_width, template_height))

            # ✅ NMS COM SISTEMA DE QUALIDADE (igual viewer)
            detections = self._apply_advanced_nms(detections, screenshot)

            # Converter de volta para formato (x, y, conf) sem dimensions
            detections = [(x, y, conf) for x, y, conf, w, h in detections]

            return detections

        except Exception as e:
            _safe_print(f"❌ Erro na detecção múltipla de {template_name}: {e}")
            return detections

    def _apply_advanced_nms(self, detections: List[Tuple[int, int, float, int, int]], screenshot) -> List[Tuple[int, int, float, int, int]]:
        """Aplicar NMS avançado com sistema de qualidade (igual viewer UI)"""
        if not detections:
            return detections

        # ✅ SISTEMA DE QUALIDADE (igual viewer)
        def calculate_quality(det):
            x, y, conf, w, h = det
            # Distância do centro da tela (normalizada)
            screen_center_x = screenshot.shape[1] // 2
            screen_center_y = screenshot.shape[0] // 2
            distance = ((x - screen_center_x)**2 + (y - screen_center_y)**2)**0.5
            distance_normalized = min(distance / 10, 100)
            quality = conf * (1 - distance_normalized / 100)
            return quality

        # Ordenar por qualidade (maior primeiro)
        detections_with_quality = [(det, calculate_quality(det)) for det in detections]
        detections_with_quality.sort(key=lambda x: x[1], reverse=True)

        # NMS com distância de 80px
        filtered = []
        min_distance = 80

        for det, quality in detections_with_quality:
            x, y, conf, w, h = det
            is_duplicate = False

            # Verificar se está muito próximo de detecções já aceitas
            for existing, _ in filtered:
                ex_x, ex_y, ex_conf, ex_w, ex_h = existing
                distance = ((x - ex_x)**2 + (y - ex_y)**2)**0.5

                if distance < min_distance:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append((det, quality))

        # Retornar apenas as detecções (sem qualidade)
        return [det for det, quality in filtered]

    def _remove_close_detections(self, detections: List[Tuple[int, int, float]], min_distance: int = 30) -> List[Tuple[int, int, float]]:
        """Remover detecções muito próximas (duplicatas)"""
        if len(detections) <= 1:
            return detections

        filtered = []

        for det in detections:
            x, y, conf = det
            is_duplicate = False

            # Verificar se já existe uma detecção próxima
            for existing in filtered:
                ex_x, ex_y, ex_conf = existing
                distance = ((x - ex_x)**2 + (y - ex_y)**2)**0.5

                if distance < min_distance:
                    # É duplicata - manter a com maior confiança
                    if conf > ex_conf:
                        filtered.remove(existing)
                        filtered.append(det)
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(det)

        return filtered

    def _check_inventory_open(self) -> bool:
        """Verificar se inventário está aberto (usando template inventory)"""
        try:
            result = self.template_engine.detect_template('inventory')
            return result and result.found
        except:
            return False

    def get_rod_status_dict(self) -> Dict[int, str]:
        """
        Obter status das varas em formato dict

        Returns:
            Dict[int, str]: {slot: status} para slots 1-6
        """
        slot_status = {}

        for slot in range(1, 7):
            if slot in self.rod_status_tracking['available_with_bait']:
                slot_status[slot] = 'with_bait'
            elif slot in self.rod_status_tracking['available_without_bait']:
                slot_status[slot] = 'without_bait'
            elif slot in self.rod_status_tracking['broken_rods']:
                slot_status[slot] = 'broken'
            else:
                slot_status[slot] = 'empty'

        return slot_status

    def get_summary(self) -> Dict[str, any]:
        """Obter resumo completo do status das varas"""
        return {
            'with_bait': self.rod_status_tracking['available_with_bait'].copy(),
            'without_bait': self.rod_status_tracking['available_without_bait'].copy(),
            'broken': self.rod_status_tracking['broken_rods'].copy(),
            'empty': self.rod_status_tracking['empty_slots'].copy(),
            'last_check': self.rod_status_tracking['last_inventory_check'],
            'total_detected': len(self.rod_status_tracking['available_with_bait']) +
                            len(self.rod_status_tracking['available_without_bait']) +
                            len(self.rod_status_tracking['broken_rods'])
        }
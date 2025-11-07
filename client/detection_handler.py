"""
Detection Handler - Sistema de Detecção e Report para Servidor

Este módulo é responsável por:
1. Detectar templates localmente (comida, botão eat, peixes, varas, iscas)
2. Aplicar NMS (Non-Maximum Suppression) para evitar duplicatas
3. Reportar resultados ao servidor via WebSocket

ARQUITETURA:
- Cliente FAZ detecções localmente (rápido, sem latência)
- Cliente ENVIA coordenadas ao servidor
- Servidor DECIDE o que fazer com as coordenadas
- Servidor CONSTRÓI sequência de ações
- Cliente EXECUTA sequência
"""

import re
import time
from typing import List, Dict, Optional, Tuple

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class DetectionHandler:
    """
    Handler para detecções de templates e report ao servidor

    Este handler é "burro" - apenas detecta e reporta.
    NÃO decide o que fazer com as detecções.
    """

    def __init__(self, template_engine, config_manager=None, chest_manager=None):
        """
        Inicializar handler

        Args:
            template_engine: TemplateEngine para detecções
            config_manager: ConfigManager para áreas de scan (opcional)
            chest_manager: ChestManager para abrir/fechar baú (opcional)
        """
        self.template_engine = template_engine
        self.config_manager = config_manager
        self.chest_manager = chest_manager

        _safe_print("🔍 DetectionHandler inicializado")

    # ========== MÉTODOS PÚBLICOS ==========

    def detect_food_and_eat(self) -> Optional[Dict]:
        """
        Detectar comida e botão "eat" no baú

        ✅ NOVA ARQUITETURA: Baú JÁ ESTÁ ABERTO (BatchCoordinator abriu!)
        DetectionHandler apenas DETECTA e RETORNA coordenadas.

        Returns:
            {"food_location": {"x": 1306, "y": 858}, "eat_location": {"x": 1083, "y": 373}}
            ou None se não detectado
        """
        _safe_print("🔍 Detectando comida e botão eat...")

        # ✅ BAÚ JÁ ESTÁ ABERTO - NÃO PRECISA ABRIR!
        # (BatchCoordinator já abriu antes de chamar este método)

        # Detectar comida (filefrito)
        food_result = self.template_engine.detect_template("filefrito", confidence_threshold=0.70)

        if not food_result or not food_result.found:
            _safe_print("   ❌ Comida não detectada")
            return None

        food_x, food_y = food_result.location
        _safe_print(f"   ✅ Comida detectada em ({food_x}, {food_y})")

        # Detectar botão eat
        eat_result = self.template_engine.detect_template("eat", confidence_threshold=0.70)

        if not eat_result or not eat_result.found:
            _safe_print("   ❌ Botão eat não detectado")
            return None

        eat_x, eat_y = eat_result.location
        _safe_print(f"   ✅ Botão eat detectado em ({eat_x}, {eat_y})")

        # ✅ NÃO FECHAR BAÚ - BatchCoordinator fecha após executar TODAS as operações

        return {
            "food_location": {"x": food_x, "y": food_y},
            "eat_location": {"x": eat_x, "y": eat_y}
        }

    def scan_inventory(self) -> Optional[Dict]:
        """
        Escanear inventário e detectar todos os peixes

        ✅ NOVA ARQUITETURA: Baú JÁ ESTÁ ABERTO (BatchCoordinator abriu!)
        DetectionHandler apenas DETECTA e RETORNA coordenadas.

        Aplica NMS (Non-Maximum Suppression) para evitar duplicatas

        Returns:
            {"fish_locations": [{"x": 709, "y": 700}, ...]}
            ou None se nenhum peixe detectado
        """
        _safe_print("🔍 Escaneando inventário...")

        # ✅ BAÚ JÁ ESTÁ ABERTO - NÃO PRECISA ABRIR!
        # (BatchCoordinator já abriu antes de chamar este método)

        # Lista de templates de peixes
        fish_templates = [
            "SALMONN", "TROUTT", "shark", "sardine", "anchovy",
            "yellowperch", "herring", "rawfish", "peixecru",
            "salmon", "smalltrout", "catfish", "roughy"
        ]

        all_detections = []

        # Capturar screenshot uma vez
        screenshot = self.template_engine.capture_screen()
        if screenshot is None:
            _safe_print("   ❌ Falha ao capturar tela")
            return None

        # Importar OpenCV para detecção múltipla
        import cv2
        import numpy as np

        # Detectar múltiplas instâncias de cada tipo de peixe
        for template_name in fish_templates:
            # Carregar template do cache
            if template_name.lower() not in self.template_engine.template_cache:
                continue

            template = self.template_engine.template_cache[template_name.lower()]

            # Match template
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Threshold de confiança
            threshold = 0.7
            locations = np.where(result >= threshold)

            # Para cada match encontrado
            for pt in zip(*locations[::-1]):
                x = pt[0] + template.shape[1] // 2
                y = pt[1] + template.shape[0] // 2
                all_detections.append((x, y))

        _safe_print(f"   📊 Total de detecções antes de NMS: {len(all_detections)}")

        if not all_detections:
            _safe_print("   ℹ️  Nenhum peixe detectado (inventário limpo)")
            return {"fish_locations": []}  # Retornar lista vazia ao invés de None

        _safe_print(f"   📊 {len(all_detections)} detecções brutas")

        # Aplicar NMS para remover duplicatas
        unique_detections = self._apply_nms(all_detections, threshold=50)

        _safe_print(f"   ✅ {len(unique_detections)} peixes únicos após NMS")

        # Converter para formato esperado pelo servidor
        fish_locations = [
            {"x": int(x), "y": int(y)}
            for x, y in unique_detections
        ]

        # ✅ NÃO FECHAR BAÚ - BatchCoordinator fecha após executar TODAS as operações

        return {"fish_locations": fish_locations}

    def analyze_rod_slots(self) -> Optional[Dict]:
        """
        Analisar status de todos os slots de varas (1-6)

        Para cada slot:
        - Detectar status (COM_ISCA, SEM_ISCA, QUEBRADA, VAZIO)
        - Buscar varas disponíveis no baú
        - Buscar iscas disponíveis no baú (com prioridade)

        Returns:
            {
                "rod_status": {1: "COM_ISCA", 2: "SEM_ISCA", 3: "QUEBRADA", ...},
                "available_items": {
                    "rods": [{"x": 1300, "y": 200}, ...],
                    "baits": [{"x": 1400, "y": 300, "type": "carneurso"}, ...]
                }
            }
        """
        _safe_print("🔍 Analisando slots de varas...")

        rod_status = {}

        # Templates de status de vara
        status_templates = {
            "COM_ISCA": ["VARANOBAUCI", "varacomisca", "comiscavara"],
            "SEM_ISCA": ["enbausi", "varasemisca", "semiscavara"],
            "QUEBRADA": ["varaquebrada", "nobauquebrada"]
        }

        # Obter coordenadas dos slots
        slot_positions = self._get_slot_positions()

        # Para cada slot (1-6)
        for slot_num in range(1, 7):
            if slot_num not in slot_positions:
                continue

            slot_x, slot_y = slot_positions[slot_num]

            # Definir ROI ao redor do slot (±50 pixels)
            roi = [slot_x - 50, slot_y - 50, slot_x + 50, slot_y + 50]

            # Detectar status
            detected_status = "VAZIO"  # Default

            for status_name, templates in status_templates.items():
                for template in templates:
                    result = self.template_engine.detect_template(
                        template,
                        confidence_threshold=0.75,
                        region=roi
                    )

                    if result and result.found:
                        detected_status = status_name
                        break

                if detected_status != "VAZIO":
                    break

            rod_status[slot_num] = detected_status
            _safe_print(f"   Slot {slot_num}: {detected_status}")

        # ✅ ABRIR BAÚ ANTES DE BUSCAR VARAS/ISCAS DISPONÍVEIS
        _safe_print("   🚪 Abrindo baú para buscar items...")
        if not self._open_chest():
            _safe_print("   ❌ Falha ao abrir baú - retornando apenas status dos slots")
            return {
                "rod_status": rod_status,
                "available_items": {
                    "rods": [],
                    "baits": []
                }
            }

        _safe_print("   ⏳ Aguardando baú abrir...")
        import time
        time.sleep(1.5)

        # Buscar varas disponíveis no baú
        available_rods = self._find_available_rods()
        _safe_print(f"   📦 {len(available_rods)} varas disponíveis no baú")

        # Buscar iscas disponíveis no baú
        available_baits = self._find_available_baits()
        _safe_print(f"   🪱 {len(available_baits)} iscas disponíveis no baú")

        # ✅ FECHAR BAÚ APÓS BUSCAR
        _safe_print("   🚪 Fechando baú após análise...")
        self._close_chest()

        return {
            "rod_status": rod_status,
            "available_items": {
                "rods": available_rods,
                "baits": available_baits
            }
        }

    # ========== MÉTODOS AUXILIARES PRIVADOS ==========

    def _apply_nms(
        self,
        detections: List[Tuple[int, int]],
        threshold: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Aplicar Non-Maximum Suppression para remover detecções duplicadas

        Args:
            detections: Lista de coordenadas (x, y)
            threshold: Distância mínima entre detecções (pixels)

        Returns:
            Lista de detecções únicas
        """
        if not detections:
            return []

        # Ordenar por x, depois y
        sorted_detections = sorted(detections, key=lambda d: (d[0], d[1]))

        unique = []
        for detection in sorted_detections:
            x, y = detection

            # Verificar se está muito próximo de alguma detecção já aceita
            is_duplicate = False
            for ux, uy in unique:
                distance = ((x - ux) ** 2 + (y - uy) ** 2) ** 0.5
                if distance < threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(detection)

        return unique

    def _get_slot_positions(self) -> Dict[int, Tuple[int, int]]:
        """
        Obter coordenadas dos slots de varas

        Returns:
            {1: (709, 1005), 2: (805, 1005), ...}
        """
        if self.config_manager:
            # Tentar obter do config
            slot_positions = self.config_manager.get('coordinates.slot_positions', {})
            if slot_positions:
                # Converter strings para int se necessário
                return {
                    int(k): tuple(v) if isinstance(v, list) else v
                    for k, v in slot_positions.items()
                }

        # Defaults (do v3)
        return {
            1: (709, 1005),
            2: (805, 1005),
            3: (899, 1005),
            4: (992, 1005),
            5: (1092, 1005),
            6: (1188, 1005)
        }

    def _find_available_rods(self) -> List[Dict]:
        """
        Buscar varas disponíveis no baú

        Returns:
            [{"x": 1300, "y": 200}, ...]
        """
        # Templates de varas no baú
        rod_templates = ["varacomisca", "varasemisca", "VARANOBAUCI"]

        rod_locations = []

        # Área do baú (lado direito)
        chest_area = self._get_chest_area()

        for template in rod_templates:
            results = self.template_engine.detect_multiple_instances(
                template,
                confidence=0.75,
                region=chest_area,
                max_results=10
            )

            if results:
                for x, y in results:
                    rod_locations.append({"x": int(x), "y": int(y)})

        # Aplicar NMS
        unique_rods = self._apply_nms(
            [(loc["x"], loc["y"]) for loc in rod_locations],
            threshold=30
        )

        return [{"x": x, "y": y} for x, y in unique_rods]

    def _find_available_baits(self) -> List[Dict]:
        """
        Buscar iscas disponíveis no baú (com tipo)

        Returns:
            [{"x": 1400, "y": 300, "type": "carneurso"}, ...]
        """
        # Templates de iscas (em ordem de prioridade)
        bait_templates = [
            ("carneurso", "carneurso"),
            ("carnedelobo", "carnedelobo"),
            ("TROUTT", "TROUTT"),
            ("grub", "grub"),
            ("minhoca", "minhoca"),
            ("worm", "minhoca")  # Alias
        ]

        bait_locations = []

        # Área do baú
        chest_area = self._get_chest_area()

        for template_name, bait_type in bait_templates:
            results = self.template_engine.detect_multiple_instances(
                template_name,
                confidence=0.75,
                region=chest_area,
                max_results=20
            )

            if results:
                for x, y in results:
                    bait_locations.append({
                        "x": int(x),
                        "y": int(y),
                        "type": bait_type
                    })

        # Aplicar NMS
        unique_baits_coords = self._apply_nms(
            [(loc["x"], loc["y"]) for loc in bait_locations],
            threshold=30
        )

        # Reconstruir lista com tipos
        unique_baits = []
        for x, y in unique_baits_coords:
            # Encontrar tipo da isca na lista original
            for bait in bait_locations:
                if bait["x"] == x and bait["y"] == y:
                    unique_baits.append(bait)
                    break

        return unique_baits

    def _get_chest_area(self) -> List[int]:
        """
        Obter área do baú para scan

        Returns:
            [x1, y1, x2, y2]
        """
        if self.config_manager:
            chest_area = self.config_manager.get('coordinates.chest_area', None)
            if chest_area:
                return chest_area

        # Default (lado direito da tela)
        return [1214, 117, 1834, 928]

    def _get_inventory_area(self) -> List[int]:
        """
        Obter área do inventário para scan

        Returns:
            [x1, y1, x2, y2]
        """
        if self.config_manager:
            inv_area = self.config_manager.get('coordinates.inventory_area', None)
            if inv_area:
                return inv_area

        # Default (lado esquerdo da tela quando baú aberto)
        return [633, 541, 1233, 953]

    def _open_chest(self) -> bool:
        """
        ✅ Abrir baú para detecção

        Usa ChestManager para abrir o baú da mesma forma que o jogo espera.

        Returns:
            bool: True se abriu com sucesso
        """
        try:
            if not self.chest_manager:
                _safe_print("❌ ChestManager não disponível")
                return False

            # Chamar método de abrir baú do ChestManager
            success = self.chest_manager.open_chest()

            if success:
                _safe_print("   ✅ Baú aberto com sucesso")
            else:
                _safe_print("   ❌ Falha ao abrir baú")

            return success

        except Exception as e:
            _safe_print(f"❌ Erro ao abrir baú: {e}")
            return False

    def _close_chest(self) -> bool:
        """
        ✅ Fechar baú após detecção

        Returns:
            bool: True se fechou com sucesso
        """
        try:
            if not self.chest_manager:
                return False

            # Chamar método de fechar baú do ChestManager
            success = self.chest_manager.close_chest()

            if success:
                _safe_print("   ✅ Baú fechado")

            return success

        except Exception as e:
            _safe_print(f"❌ Erro ao fechar baú: {e}")
            return False

#!/usr/bin/env python3
"""
🎯 TemplateEngine - Sistema Unificado de Template Matching
Ultimate Fishing Bot v4.0

Consolida e otimiza o sistema de detecção de templates do botpesca.py
"""

import cv2
import numpy as np
import mss
import os
from typing import Optional, Dict, List, Tuple, NamedTuple
from pathlib import Path
import time
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class TemplateResult(NamedTuple):
    """Resultado de detecção de template"""
    found: bool
    confidence: float
    location: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]      # (width, height)
    template_name: str

class TemplateEngine:
    """
    🎯 Motor Unificado de Template Matching
    
    Consolidação das funcionalidades do botpesca.py:
    - Template matching otimizado
    - Cache de templates
    - Configuração de confiança por template
    - Captura de tela otimizada
    """
    
    def __init__(self, config_manager=None):
        """Inicializar template engine"""
        self.config_manager = config_manager

        # Caches para performance
        self.template_cache: Dict[str, np.ndarray] = {}
        self.confidence_config: Dict[str, float] = {}

        # ⚡ OTIMIZAÇÃO: Thread-local MSS instances
        import threading
        self._mss_instances = threading.local()

        # Configuração de captura de tela
        self.screen_capture = None
        self.screenshot_region = None

        # ⚡ OTIMIZAÇÃO: Regiões de interesse (ROI) por template (case-insensitive - lowercase keys)
        self.default_rois = {
            # Catch aparece no 1/3 direito da tela (↓66.7% área!)
            'catch': [1280, 0, 1920, 1080],

            # Varas/itens só no inventário
            'varanobauci': [633, 541, 1233, 953],  # Lowercase para case-insensitive
            'enbausi': [633, 541, 1233, 953],
            'varaquebrada': [633, 541, 1233, 953],
            'comiscavara': [633, 541, 1233, 953],
            'semiscavara': [633, 541, 1233, 953],

            # Comida/iscas no baú
            'filefrito': [1214, 117, 1834, 928],
            'carneurso': [1214, 117, 1834, 928],
            'carnedelobo': [1214, 117, 1834, 928],
            'grub': [1214, 117, 1834, 928],
            'minhoca': [1214, 117, 1834, 928],

            # Peixes no inventário
            'salmon': [633, 541, 1233, 953],
            'shark': [633, 541, 1233, 953],
            'herring': [633, 541, 1233, 953],
            'sardine': [633, 541, 1233, 953],
            'anchovy': [633, 541, 1233, 953],
            'yellowperch': [633, 541, 1233, 953],

            # UI pode aparecer em qualquer lugar (tela inteira)
            'inventory': [0, 0, 1920, 1080],
            'loot': [0, 0, 1920, 1080],
            'eat': [0, 0, 1920, 1080],
        }

        # Estatísticas
        self.detection_stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'cache_hits': 0,
            'roi_optimizations': 0,  # ⚡ Nova métrica
        }

        # Inicializar
        self._init_screen_capture()
        self._load_templates()
        self._load_confidence_config()

        _safe_print("🎯 TemplateEngine inicializado com otimizações")

    def __del__(self):
        """⚡ OTIMIZAÇÃO: Cleanup de thread-local MSS instances"""
        try:
            # Thread-local cleanup acontece automaticamente
            # Tentar fechar instância da thread atual se existir
            if hasattr(self._mss_instances, 'instance') and self._mss_instances.instance is not None:
                self._mss_instances.instance.close()
                self._mss_instances.instance = None
        except Exception:
            pass  # Ignorar erros no cleanup

    def _init_screen_capture(self):
        """Inicializar captura de tela otimizada (do botpesca.py)"""
        try:
            # Não inicializar mss aqui, criar nova instância a cada captura
            self.screen_capture = True  # Flag para indicar que está habilitado
            
            # Carregar região de screenshot do config
            if self.config_manager:
                coords = self.config_manager.get('coordinates', {})
                self.screenshot_region = coords.get('screenshot_region', [0, 0, 1920, 1080])
            else:
                self.screenshot_region = [0, 0, 1920, 1080]
            
            _safe_print(f"✅ Captura de tela configurada: {self.screenshot_region}")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao configurar captura: {e}")
            self.screen_capture = None
    
    def _load_templates(self):
        """Carregar todos os templates da pasta templates/"""
        try:
            templates_dir = Path(__file__).parent.parent / "templates"

            if not templates_dir.exists():
                _safe_print(f"⚠️ Pasta templates não encontrada: {templates_dir}")
                return

            template_files = list(templates_dir.glob("*.png"))

            for template_file in template_files:
                template_name = template_file.stem

                try:
                    # Carregar template
                    template_img = cv2.imread(str(template_file), cv2.IMREAD_COLOR)

                    if template_img is not None:
                        # Armazenar com nome original E lowercase para case-insensitive lookup
                        self.template_cache[template_name] = template_img
                        # Adicionar versão lowercase se diferente
                        template_name_lower = template_name.lower()
                        if template_name_lower != template_name:
                            self.template_cache[template_name_lower] = template_img
                        _safe_print(f"  ✅ Template carregado: {template_name}")
                    else:
                        _safe_print(f"  ❌ Erro ao carregar: {template_name}")

                except Exception as e:
                    _safe_print(f"  ❌ Erro em {template_name}: {e}")

            _safe_print(f"📁 {len(self.template_cache)} templates carregados no cache")

            # Debug: verificar se templates críticos estão carregados (case-insensitive)
            critical_templates = ['varanobauci', 'enbausi', 'varaquebrada']
            missing_templates = []
            for template in critical_templates:
                template_lower = template.lower()
                if template_lower not in self.template_cache:
                    missing_templates.append(template)
                else:
                    _safe_print(f"  ✅ Template crítico encontrado: {template}")

            if missing_templates:
                _safe_print(f"  ⚠️ Templates críticos FALTANDO: {missing_templates}")
                _safe_print(f"  📂 Pasta verificada: {templates_dir}")
                _safe_print(f"  📋 Templates carregados: {list(self.template_cache.keys())}")

        except Exception as e:
            _safe_print(f"❌ Erro ao carregar templates: {e}")

    def _load_single_template(self, template_name: str) -> bool:
        """Carregar um template individual quando não encontrado no cache"""
        try:
            # Verificar múltiplos locais de templates
            possible_paths = [
                Path(__file__).parent.parent / "templates" / f"{template_name}.png",
                Path("D:/finalbot/fishing_bot_v4/templates") / f"{template_name}.png",
                Path("D:/finalbot/templates") / f"{template_name}.png"
            ]

            for template_path in possible_paths:
                if template_path.exists():
                    try:
                        # Carregar template
                        template_img = cv2.imread(str(template_path), cv2.IMREAD_COLOR)

                        if template_img is not None:
                            self.template_cache[template_name] = template_img
                            _safe_print(f"  ✅ Template carregado de: {template_path}")
                            return True
                        else:
                            _safe_print(f"  ❌ Erro ao ler imagem: {template_path}")

                    except Exception as e:
                        _safe_print(f"  ❌ Erro ao carregar {template_path}: {e}")

            _safe_print(f"❌ Template '{template_name}' não encontrado em nenhum local")
            _safe_print(f"   Locais verificados: {[str(p) for p in possible_paths]}")
            return False

        except Exception as e:
            _safe_print(f"❌ Erro no carregamento individual de {template_name}: {e}")
            return False

    def _load_confidence_config(self):
        """Carregar configurações de confiança do config.json"""
        try:
            if self.config_manager:
                # Verificar formato unified vs legado
                if self.config_manager.is_unified_format:
                    # Formato unified: template_confidence.values.*
                    self.confidence_config = self.config_manager.get('template_confidence.values', {})
                    _safe_print("📋 Carregando formato UNIFIED de confiança")
                else:
                    # Formato legado: template_confidence.*
                    self.confidence_config = self.config_manager.get('template_confidence', {})
                    _safe_print("📋 Carregando formato LEGADO de confiança")
            else:
                self.confidence_config = {}
            
            # Valores padrão para templates críticos
            defaults = {
                'catch': 0.8,
                'inventory': 0.8,
                'loot': 0.8,
                'comiscavara': 0.8,
                'semiscavara': 0.7,
                'varaquebrada': 0.7,
                'VARANOBAUCI': 0.8,
                'enbausi': 0.7
            }
            
            for template, confidence in defaults.items():
                if template not in self.confidence_config:
                    self.confidence_config[template] = confidence
            
            _safe_print(f"⚙️ Configurações de confiança carregadas: {len(self.confidence_config)} templates")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao carregar config de confiança: {e}")
    
    def capture_screen(self, region: Optional[List[int]] = None) -> Optional[np.ndarray]:
        """
        ⚡ OTIMIZADO: Capturar tela usando thread-local MSS + ROI support

        Args:
            region: [left, top, right, bottom] ou None para usar screenshot_region padrão

        Otimizações:
        - Thread-local MSS instance (thread-safe!)
        - ROI customizável para áreas específicas
        - Conversão BGR otimizada
        """
        try:
            if not self.screen_capture:
                return None

            # ⚡ OTIMIZAÇÃO: Criar thread-local MSS instance sob demanda
            if not hasattr(self._mss_instances, 'instance') or self._mss_instances.instance is None:
                self._mss_instances.instance = mss.mss()

            # Definir região de captura
            if region is None:
                region = self.screenshot_region

            capture_region = {
                'left': region[0],
                'top': region[1],
                'width': region[2] - region[0],
                'height': region[3] - region[1]
            }

            # Capturar usando thread-local instance
            screenshot = self._mss_instances.instance.grab(capture_region)

            # Converter para formato OpenCV
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            return img

        except Exception as e:
            _safe_print(f"❌ Erro na captura de tela: {e}")
            # Em caso de erro, tentar recriar instância thread-local
            try:
                if hasattr(self._mss_instances, 'instance') and self._mss_instances.instance is not None:
                    self._mss_instances.instance.close()
            except:
                pass
            self._mss_instances.instance = None
            return None
    
    def detect_template(self, template_name: str, confidence_threshold: Optional[float] = None,
                       screenshot: Optional[np.ndarray] = None, region: Optional[List[int]] = None,
                       use_roi: bool = True) -> Optional[TemplateResult]:
        """
        ⚡ OTIMIZADO: Detectar template com suporte a ROI automático

        Args:
            template_name: Nome do template (sem .png) - case-insensitive
            confidence_threshold: Threshold específico (usa config se None)
            screenshot: Screenshot específico (captura novo se None)
            region: ROI customizada [left, top, right, bottom]
            use_roi: Se True, usa ROI padrão do template (se disponível)

        Returns:
            TemplateResult se encontrado, None caso contrário
        """
        try:
            self.detection_stats['total_detections'] += 1

            # Normalizar nome do template para lowercase (case-insensitive lookup)
            template_name_normalized = template_name.lower()

            # Verificar se template existe (case-insensitive)
            if template_name_normalized not in self.template_cache:
                _safe_print(f"❌ Template '{template_name}' não encontrado no cache")

                # Tentar carregar template individual
                if self._load_single_template(template_name):
                    _safe_print(f"✅ Template '{template_name}' carregado individualmente")
                else:
                    _safe_print(f"❌ Falha ao carregar template '{template_name}'")
                    return None

            # Obter template do cache (usando nome normalizado)
            template = self.template_cache[template_name_normalized]
            self.detection_stats['cache_hits'] += 1

            # Obter threshold de confiança
            if confidence_threshold is None:
                confidence_threshold = self.confidence_config.get(template_name, 0.7)

            # ⚡ OTIMIZAÇÃO: Determinar ROI a usar (case-insensitive)
            roi_to_use = None
            if screenshot is None:  # Só otimizar se for capturar nova screenshot
                if region is not None:
                    roi_to_use = region
                elif use_roi and template_name_normalized in self.default_rois:
                    roi_to_use = self.default_rois[template_name_normalized]
                    self.detection_stats['roi_optimizations'] += 1

            # Capturar tela se necessário (com ROI se aplicável)
            roi_offset = [0, 0]  # Offset para ajustar coordenadas
            if screenshot is None:
                screenshot = self.capture_screen(region=roi_to_use)
                if screenshot is None:
                    return None
                # Se usou ROI, precisamos ajustar coordenadas do resultado
                if roi_to_use:
                    roi_offset = [roi_to_use[0], roi_to_use[1]]

            # Template matching (algoritmo do botpesca.py)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Verificar confiança
            if max_val >= confidence_threshold:
                # Calcular posição e tamanho
                template_h, template_w = template.shape[:2]

                # Ajustar coordenadas se usou ROI
                adjusted_location = (max_loc[0] + roi_offset[0], max_loc[1] + roi_offset[1])

                result_obj = TemplateResult(
                    found=True,
                    confidence=max_val,
                    location=adjusted_location,
                    size=(template_w, template_h),
                    template_name=template_name
                )

                self.detection_stats['successful_detections'] += 1
                return result_obj

            return None

        except Exception as e:
            _safe_print(f"❌ Erro na detecção de {template_name}: {e}")
            return None
    
    def detect_multiple_templates(self, template_names: List[str], 
                                 screenshot: Optional[np.ndarray] = None) -> List[TemplateResult]:
        """
        Detectar múltiplos templates em uma única captura
        
        Otimização: uma captura para múltiplas detecções
        """
        try:
            results = []
            
            # Capturar tela uma vez
            if screenshot is None:
                screenshot = self.capture_screen()
                if screenshot is None:
                    return results
            
            # Detectar cada template
            for template_name in template_names:
                result = self.detect_template(template_name, screenshot=screenshot)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção múltipla: {e}")
            return []
    
    def has_template(self, template_name: str) -> bool:
        """Verificar se template existe no cache"""
        return template_name in self.template_cache
    
    def get_template_confidence(self, template_name: str) -> float:
        """Obter threshold de confiança para template"""
        # Primeiro tentar do config local
        confidence = self.confidence_config.get(template_name)
        
        if confidence is not None:
            return confidence
        
        # Senão, tentar do ConfigManager
        if self.config_manager:
            # Verificar se o config manager tem o atributo is_unified_format
            if hasattr(self.config_manager, 'is_unified_format') and self.config_manager.is_unified_format:
                confidence = self.config_manager.get(f'template_confidence.values.{template_name}')
            else:
                confidence = self.config_manager.get(f'template_confidence.{template_name}')
            
            if confidence is not None:
                # Cache local para próximas consultas
                self.confidence_config[template_name] = confidence
                return confidence
        
        # Valor padrão se não encontrar
        return 0.7
    
    def set_template_confidence(self, template_name: str, confidence: float):
        """Definir threshold de confiança para template"""
        self.confidence_config[template_name] = confidence
        
        # Persistir no ConfigManager se disponível
        if self.config_manager:
            try:
                # Atualizar no ConfigManager (unified format)
                if hasattr(self.config_manager, 'is_unified_format') and self.config_manager.is_unified_format:
                    self.config_manager.set(f'template_confidence.values.{template_name}', confidence)
                else:
                    # Formato legado
                    self.config_manager.set(f'template_confidence.{template_name}', confidence)
                
                # Salvar no arquivo
                self.config_manager.save_config()
                _safe_print(f"💾 Confiança salva: {template_name} = {confidence}")
            except Exception as e:
                _safe_print(f"⚠️ Erro ao salvar confiança: {e}")
        else:
            _safe_print(f"⚙️ Confiança atualizada: {template_name} = {confidence} (não salvo)")
    
    def reload_templates(self):
        """Recarregar templates da pasta"""
        self.template_cache.clear()
        self._load_templates()
        _safe_print("🔄 Templates recarregados")
    
    def get_stats(self) -> Dict:
        """Obter estatísticas de detecção"""
        stats = self.detection_stats.copy()
        
        if stats['total_detections'] > 0:
            stats['success_rate'] = stats['successful_detections'] / stats['total_detections']
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_detections']
        else:
            stats['success_rate'] = 0.0
            stats['cache_hit_rate'] = 0.0
        
        return stats
    
    def get_available_templates(self) -> List[str]:
        """Obter lista de templates disponíveis"""
        return list(self.template_cache.keys())
    
    def validate_critical_templates(self) -> bool:
        """Validar se templates críticos estão disponíveis"""
        critical_templates = ['catch', 'inventory', 'loot']
        
        for template in critical_templates:
            if template not in self.template_cache:
                _safe_print(f"❌ Template crítico ausente: {template}")
                return False
        
        _safe_print("✅ Todos os templates críticos estão disponíveis")
        return True
    
    # ====== IMPLEMENTAÇÕES BASEADAS NO BOTPESCA.PY V3 ======
    
    def detect_fish_caught(self, threshold: Optional[float] = None) -> Tuple[bool, float]:
        """
        🐟 Detectar peixe capturado - LÓGICA EXATA DO BOTPESCA.PY LINHA 14691
        
        Adaptada do detect_fish_caught_template() que FUNCIONA no v3
        """
        try:
            # Usar threshold configurado ou padrão
            if threshold is None:
                threshold = self.get_template_confidence('catch')
            
            # Detectar usando sistema unificado
            result = self.detect_template('catch', confidence_threshold=threshold)
            
            if result and result.found:
                _safe_print(f"🎣 Peixe detectado! Confiança: {result.confidence:.3f} (threshold: {threshold:.3f})")
                return True, result.confidence
            
            return False, 0.0
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção de peixe: {e}")
            return False, 0.0
    
    def wait_for_fish_caught(self, timeout: int = 120, check_interval: float = 0.1) -> Tuple[bool, float]:
        """
        ⏱️ Aguardar peixe ser capturado com timeout
        
        Args:
            timeout: Timeout em segundos (padrão 120s do v3)
            check_interval: Intervalo entre verificações (0.1s = 100ms)
            
        Returns:
            Tuple[bool, float]: (fish_caught, confidence)
        """
        try:
            _safe_print(f"🎣 Aguardando peixe por {timeout}s...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Verificar se peixe foi capturado
                found, confidence = self.detect_fish_caught()
                
                if found:
                    elapsed = time.time() - start_time
                    _safe_print(f"🐟 Peixe capturado após {elapsed:.1f}s! Confiança: {confidence:.3f}")
                    return True, confidence
                
                # Aguardar próxima verificação
                time.sleep(check_interval)
            
            _safe_print(f"⏰ Timeout de {timeout}s alcançado sem capturar peixe")
            return False, 0.0
            
        except Exception as e:
            _safe_print(f"❌ Erro ao aguardar peixe: {e}")
            return False, 0.0
    
    def detect_rod_status(self, slot: int) -> str:
        """
        🎣 Detectar status da vara no slot específico
        
        Baseado na lógica do v3 para detecção de varas
        
        Args:
            slot: Número do slot (1-6)
            
        Returns:
            str: "com_isca", "sem_isca", "quebrada", "vazio"
        """
        try:
            # Templates de vara em ordem de prioridade
            rod_templates = {
                'VARANOBAUCI': 'com_isca',      # Vara com isca (prioritário)
                'comiscavara': 'com_isca',      # Vara com isca (alternativo)
                'enbausi': 'sem_isca',          # Vara sem isca (prioritário)
                'semiscavara': 'sem_isca',      # Vara sem isca (alternativo)
                'varaquebrada': 'quebrada',     # Vara quebrada
                'nobauquebrada': 'quebrada'     # Vara quebrada (alternativo)
            }
            
            # Capturar tela uma vez para eficiência
            screenshot = self.capture_screen()
            if screenshot is None:
                _safe_print(f"⚠️ Falha na captura de tela para slot {slot}")
                return "vazio"
            
            # Testar cada template
            for template_name, status in rod_templates.items():
                if template_name in self.template_cache:
                    result = self.detect_template(
                        template_name, 
                        screenshot=screenshot
                    )
                    
                    if result and result.found:
                        _safe_print(f"🎯 Vara no slot {slot}: {status} (template: {template_name}, conf: {result.confidence:.3f})")
                        return status
            
            # Nenhum template detectado = slot vazio
            return "vazio"
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar vara no slot {slot}: {e}")
            return "vazio"
    
    def detect_inventory_state(self) -> bool:
        """
        📦 Detectar se inventário está aberto
        
        Returns:
            bool: True se inventário aberto
        """
        try:
            result = self.detect_template('inventory')
            is_open = result and result.found
            
            if is_open:
                _safe_print(f"📦 Inventário detectado como ABERTO (conf: {result.confidence:.3f})")
            
            return is_open
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar inventário: {e}")
            return False
    
    def detect_chest_state(self) -> bool:
        """
        🎁 Detectar se baú está aberto
        
        Returns:
            bool: True se baú aberto
        """
        try:
            result = self.detect_template('loot')
            is_open = result and result.found
            
            if is_open:
                _safe_print(f"🎁 Baú detectado como ABERTO (conf: {result.confidence:.3f})")
            
            return is_open
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar baú: {e}")
            return False
    
    def detect_food_templates(self) -> List[TemplateResult]:
        """
        🍖 Detectar templates de comida disponíveis
        
        Baseado em find_and_click_food_automatically() do v3
        """
        try:
            # Templates de comida do v3
            food_templates = [
                'filefrito',     # Filé frito (prioritário)
                'frito',         # Comida frita
                'eat'            # Botão eat
            ]
            
            # Detectar todos os templates de comida
            available_templates = [t for t in food_templates if t in self.template_cache]
            
            if available_templates:
                results = self.detect_multiple_templates(available_templates)
                _safe_print(f"🍖 Detectados {len(results)} templates de comida")
                return results
            
            return []
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar comida: {e}")
            return []
    
    def detect_bait_templates(self) -> List[TemplateResult]:
        """
        🎣 Detectar templates de isca disponíveis
        
        Usa configuração de prioridade de isca da UI
        """
        try:
            # Obter prioridades da configuração da UI
            if self.config_manager:
                bait_priority = self.config_manager.get('bait_priority', {})
                
                # Ordenar iscas por prioridade (menor número = maior prioridade)
                sorted_baits = sorted(bait_priority.items(), key=lambda x: x[1])
                bait_templates = [bait_name for bait_name, priority in sorted_baits]
                
                _safe_print(f"🎣 Prioridade de iscas da UI: {bait_templates}")
            else:
                # Fallback para prioridades padrão
                bait_templates = [
                    'carne de crocodilo', # Prioridade 1
                    'carne de urso',      # Prioridade 2  
                    'carne de lobo',      # Prioridade 3
                    'trout',              # Prioridade 4
                    'grub',               # Prioridade 5
                    'worm'                # Prioridade 6
                ]
            
            # Detectar apenas templates que existem
            available_templates = [t for t in bait_templates if t in self.template_cache]
            
            if available_templates:
                results = self.detect_multiple_templates(available_templates)
                _safe_print(f"🎣 Detectadas {len(results)} iscas disponíveis")
                return results
            
            return []
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar iscas: {e}")
            return []
    
    def detect_ui_elements(self) -> Dict[str, TemplateResult]:
        """
        🖥️ Detectar elementos de UI em lote
        
        Returns:
            Dict[str, TemplateResult]: Elementos encontrados
        """
        try:
            ui_templates = ['inventory', 'loot', 'options', 'map']
            screenshot = self.capture_screen()
            
            results = {}
            for template_name in ui_templates:
                if template_name in self.template_cache:
                    result = self.detect_template(template_name, screenshot=screenshot)
                    if result and result.found:
                        results[template_name] = result
            
            return results
            
        except Exception as e:
            _safe_print(f"❌ Erro ao detectar UI: {e}")
            return {}
    
    def wait_for_template(self, template_name: str, timeout: int = 10, 
                         check_interval: float = 0.5) -> Optional[TemplateResult]:
        """
        ⏱️ Aguardar template aparecer com timeout
        
        Args:
            template_name: Nome do template
            timeout: Timeout em segundos
            check_interval: Intervalo entre verificações
            
        Returns:
            TemplateResult se encontrado, None se timeout
        """
        try:
            _safe_print(f"⏱️ Aguardando template '{template_name}' por {timeout}s...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                result = self.detect_template(template_name)
                
                if result and result.found:
                    elapsed = time.time() - start_time
                    _safe_print(f"✅ Template '{template_name}' encontrado após {elapsed:.1f}s")
                    return result
                
                time.sleep(check_interval)
            
            _safe_print(f"⏰ Timeout: template '{template_name}' não encontrado em {timeout}s")
            return None
            
        except Exception as e:
            _safe_print(f"❌ Erro ao aguardar template: {e}")
            return None
    
    def wait_for_template_disappear(self, template_name: str, timeout: int = 10,
                                   check_interval: float = 0.5) -> bool:
        """
        ⏱️ Aguardar template desaparecer
        
        Returns:
            bool: True se desapareceu, False se timeout
        """
        try:
            _safe_print(f"⏱️ Aguardando template '{template_name}' desaparecer...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                result = self.detect_template(template_name)
                
                if not result or not result.found:
                    elapsed = time.time() - start_time
                    _safe_print(f"✅ Template '{template_name}' desapareceu após {elapsed:.1f}s")
                    return True
                
                time.sleep(check_interval)
            
            _safe_print(f"⏰ Timeout: template '{template_name}' ainda presente após {timeout}s")
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao aguardar desaparecimento: {e}")
            return False
    
    def batch_detect(self, template_names: List[str]) -> Dict[str, TemplateResult]:
        """
        🎯 Detecção em lote otimizada
        
        Args:
            template_names: Lista de templates para detectar
            
        Returns:
            Dict[str, TemplateResult]: Resultados encontrados
        """
        try:
            results = {}
            
            # Uma captura para todas as detecções
            screenshot = self.capture_screen()
            if screenshot is None:
                return results
            
            # Detectar cada template
            for template_name in template_names:
                if template_name in self.template_cache:
                    result = self.detect_template(template_name, screenshot=screenshot)
                    if result and result.found:
                        results[template_name] = result
            
            return results
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção em lote: {e}")
            return {}
    
    def get_detection_region(self, template_name: str) -> Optional[Tuple[int, int, int, int]]:
        """
        📐 Obter região específica para detecção (otimização)
        
        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) ou None
        """
        try:
            # Regiões específicas baseadas no conhecimento do jogo
            regions = {
                'catch': (400, 300, 1120, 480),      # Região central para captura
                'inventory': (600, 500, 700, 500),   # Região do inventário
                'loot': (1200, 100, 650, 850),      # Região do baú
                'VARANOBAUCI': (650, 950, 600, 100), # Região das varas
                'enbausi': (650, 950, 600, 100),     # Região das varas
                'varaquebrada': (650, 950, 600, 100) # Região das varas
            }
            
            return regions.get(template_name)
            
        except Exception as e:
            _safe_print(f"❌ Erro ao obter região: {e}")
            return None
    
    def detect_in_region(self, template_name: str, region: Tuple[int, int, int, int],
                        confidence_threshold: Optional[float] = None) -> Optional[TemplateResult]:
        """
        🎯 Detectar template em região específica (otimização)
        
        Args:
            template_name: Nome do template
            region: (x, y, width, height)
            confidence_threshold: Threshold de confiança
            
        Returns:
            TemplateResult se encontrado
        """
        try:
            if template_name not in self.template_cache:
                return None
            
            # Capturar apenas a região especificada
            x, y, width, height = region
            region_dict = {
                'left': x,
                'top': y,
                'width': width,
                'height': height
            }
            
            if not self.screen_capture:
                return None
            
            # Capturar região
            screenshot = self.screen_capture.grab(region_dict)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Template matching
            template = self.template_cache[template_name]
            
            # Obter threshold
            if confidence_threshold is None:
                confidence_threshold = self.get_template_confidence(template_name)

            # 🎯 LÓGICA REMOVIDA: ULTRA PRECISION causava confusão visual
            # Agora respeitamos exatamente o threshold configurado

            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence_threshold:
                template_h, template_w = template.shape[:2]
                
                # Ajustar localização para coordenadas absolutas
                absolute_location = (max_loc[0] + x, max_loc[1] + y)
                
                return TemplateResult(
                    found=True,
                    confidence=max_val,
                    location=absolute_location,
                    size=(template_w, template_h),
                    template_name=template_name
                )
            
            return None
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção regional: {e}")
            return None
    
    def optimize_detection(self, template_name: str, 
                          confidence_threshold: Optional[float] = None) -> Optional[TemplateResult]:
        """
        ⚡ Detecção otimizada com região específica se disponível
        
        Args:
            template_name: Nome do template
            confidence_threshold: Threshold de confiança
            
        Returns:
            TemplateResult se encontrado
        """
        try:
            # Tentar detecção regional primeiro (mais rápido)
            region = self.get_detection_region(template_name)
            
            if region:
                result = self.detect_in_region(template_name, region, confidence_threshold)
                if result:
                    return result
            
            # Fallback para detecção completa
            return self.detect_template(template_name, confidence_threshold)
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção otimizada: {e}")
            return None
    
    def clear_cache(self):
        """🗑️ Limpar cache de templates"""
        self.template_cache.clear()
        _safe_print("🗑️ Cache de templates limpo")
    
    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """📋 Obter informações sobre template"""
        try:
            if template_name not in self.template_cache:
                return None
            
            template = self.template_cache[template_name]
            height, width = template.shape[:2]
            confidence = self.get_template_confidence(template_name)
            
            return {
                'name': template_name,
                'size': (width, height),
                'confidence_threshold': confidence,
                'cached': True
            }
            
        except Exception as e:
            _safe_print(f"❌ Erro ao obter info do template: {e}")
            return None
    
    def benchmark_detection(self, template_name: str, iterations: int = 10) -> Dict:
        """🏁 Benchmark de detecção de template"""
        try:
            if template_name not in self.template_cache:
                return {'error': 'Template não encontrado'}
            
            times = []
            successes = 0
            
            for i in range(iterations):
                start_time = time.time()
                result = self.detect_template(template_name)
                end_time = time.time()
                
                times.append(end_time - start_time)
                if result and result.found:
                    successes += 1
            
            avg_time = sum(times) / len(times)
            success_rate = successes / iterations
            
            return {
                'template': template_name,
                'iterations': iterations,
                'avg_time_ms': avg_time * 1000,
                'success_rate': success_rate,
                'successes': successes
            }
            
        except Exception as e:
            _safe_print(f"❌ Erro no benchmark: {e}")
            return {'error': str(e)}
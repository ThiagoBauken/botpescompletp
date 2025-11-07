"""
Sistema único de template matching
Consolida toda a lógica de detecção de templates
"""

import cv2
import numpy as np
import os
import mss
from typing import Tuple, Optional, Dict, Any
import logging
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


logger = logging.getLogger('FishingBot.TemplateMatcher')

class TemplateMatcher:
    """Sistema unificado de template matching"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.templates = {}
        self.sct = mss.mss()
        self.confidence_thresholds = {}
        self.load_templates()
    
    def load_templates(self):
        """Carregar todos os templates disponíveis"""
        if not os.path.exists(self.template_dir):
            logger.warning(f"Diretório de templates não encontrado: {self.template_dir}")
            return
        
        template_files = [f for f in os.listdir(self.template_dir) if f.endswith('.png')]
        
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            template_path = os.path.join(self.template_dir, template_file)
            
            try:
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    self.templates[template_name] = template
                    logger.info(f"Template carregado: {template_name}")
                else:
                    logger.error(f"Erro ao carregar template: {template_file}")
            except Exception as e:
                logger.error(f"Erro ao carregar {template_file}: {e}")
        
        logger.info(f"Total de templates carregados: {len(self.templates)}")
    
    def set_confidence(self, template_name: str, confidence: float):
        """Definir confiança para um template específico"""
        self.confidence_thresholds[template_name] = confidence
    
    def get_confidence(self, template_name: str) -> float:
        """Obter confiança para um template"""
        return self.confidence_thresholds.get(template_name, 0.7)
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capturar tela ou região específica"""
        try:
            if region:
                monitor = {"top": region[1], "left": region[0], 
                          "width": region[2] - region[0], "height": region[3] - region[1]}
            else:
                monitor = self.sct.monitors[1]  # Monitor principal
            
            screenshot = self.sct.grab(monitor)
            img = np.array(screenshot)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
        except Exception as e:
            logger.error(f"Erro ao capturar tela: {e}")
            return np.array([])
    
    def find_template(self, template_name: str, 
                     region: Optional[Tuple[int, int, int, int]] = None,
                     confidence: Optional[float] = None) -> Tuple[bool, float, Optional[Tuple[int, int]]]:
        """
        Encontrar template na tela
        
        Returns:
            (found, confidence, (x, y)) onde x,y é o centro do match
        """
        if template_name not in self.templates:
            logger.warning(f"Template não encontrado: {template_name}")
            return False, 0.0, None
        
        # Capturar tela
        screenshot = self.capture_screen(region)
        if screenshot.size == 0:
            return False, 0.0, None
        
        # Template
        template = self.templates[template_name]
        
        # Confiança
        conf_threshold = confidence or self.get_confidence(template_name)
        
        try:
            # Match template
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= conf_threshold:
                # Calcular centro
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                # Ajustar para coordenadas globais se região foi especificada
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                logger.debug(f"Template {template_name} encontrado com confiança {max_val:.3f} em ({center_x}, {center_y})")
                return True, max_val, (center_x, center_y)
            else:
                logger.debug(f"Template {template_name} não encontrado. Confiança: {max_val:.3f} < {conf_threshold:.3f}")
                return False, max_val, None
                
        except Exception as e:
            logger.error(f"Erro ao procurar template {template_name}: {e}")
            return False, 0.0, None
    
    def wait_for_template(self, template_name: str, timeout: int = 30,
                         region: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, float, Optional[Tuple[int, int]]]:
        """Aguardar por um template aparecer"""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            found, confidence, position = self.find_template(template_name, region)
            if found:
                return True, confidence, position
            
            time.sleep(0.1)  # 100ms entre verificações
        
        logger.warning(f"Timeout aguardando template: {template_name}")
        return False, 0.0, None
    
    def get_available_templates(self) -> list:
        """Listar templates disponíveis"""
        return list(self.templates.keys())
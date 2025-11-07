#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManager - Sistema Unificado de Configuracao
Ultimate Fishing Bot v4.0

Extrai e consolida o sistema de configuracao do botpesca.py
"""

import json
import os
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path
import copy

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

class ConfigManager:
    """
    ⚙️ Gerenciador Unificado de Configuração
    
    Responsabilidades:
    - Carregar/salvar configurações JSON
    - Validar estruturas de configuração
    - Fornecer acesso unificado aos dados
    - Gerenciar configurações padrão e personalizadas
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Inicializar ConfigManager"""
        
        # Paths de configuração
        self.config_dir = Path(__file__).parent.parent / "config"
        self.data_dir = Path(__file__).parent.parent / "data"
        self.default_config_path = self.config_dir / "default_config.json"
        self.user_config_path = self.data_dir / "config.json"
        
        # Se um path específico foi fornecido, usá-lo
        if config_path:
            self.user_config_path = Path(config_path)
        
        # Dados de configuração
        self.default_config: Dict[str, Any] = {}
        self.user_config: Dict[str, Any] = {}
        self.merged_config: Dict[str, Any] = {}
        
        # Estado
        self.is_loaded = False
        self.has_changes = False
        self.is_unified_format = False  # Formato v4 usa template_confidence.* (legado)
        
        # Carregar configurações
        self.load_configs()
        
        _safe_print("⚙️ ConfigManager inicializado")
    
    def load_configs(self) -> bool:
        """Carregar configurações padrão e do usuário"""
        try:
            # 1. Carregar configuração padrão
            if not self._load_default_config():
                _safe_print("❌ Falha ao carregar configuração padrão")
                return False
            
            # 2. Carregar configuração do usuário (se existir)
            self._load_user_config()
            
            # 3. Mesclar configurações
            self._merge_configs()
            
            self.is_loaded = True
            _safe_print("✅ Configurações carregadas com sucesso")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao carregar configurações: {e}")
            return False
    
    def _load_default_config(self) -> bool:
        """Carregar configuração padrão"""
        try:
            if not self.default_config_path.exists():
                _safe_print(f"❌ Configuração padrão não encontrada: {self.default_config_path}")
                return False
            
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                self.default_config = json.load(f)
            
            _safe_print(f"✅ Configuração padrão carregada: {len(self.default_config)} seções")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao carregar config padrão: {e}")
            return False
    
    def _load_user_config(self) -> bool:
        """Carregar configuração do usuário"""
        try:
            if not self.user_config_path.exists():
                _safe_print(f"ℹ️ Configuração do usuário não existe: {self.user_config_path}")
                self.user_config = {}
                return True
            
            with open(self.user_config_path, 'r', encoding='utf-8') as f:
                self.user_config = json.load(f)
            
            _safe_print(f"✅ Configuração do usuário carregada: {len(self.user_config)} seções")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao carregar config do usuário: {e}")
            self.user_config = {}
            return False
    
    def _merge_configs(self):
        """Mesclar configuração padrão com do usuário"""
        try:
            # Começar com configuração padrão
            self.merged_config = copy.deepcopy(self.default_config)
            
            # Sobrescrever com configurações do usuário
            self._deep_merge(self.merged_config, self.user_config)
            
            _safe_print(f"✅ Configurações mescladas: {len(self.merged_config)} seções")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao mesclar configs: {e}")
            self.merged_config = self.default_config.copy()
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Mesclar dicionários recursivamente"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obter valor de configuração usando notação de ponto"""
        try:
            keys = key.split('.')
            current = self.merged_config
            
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            
            return current
            
        except Exception as e:
            _safe_print(f"❌ Erro ao obter config '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Definir valor de configuração usando notação de ponto"""
        try:
            keys = key.split('.')
            current = self.merged_config
            
            # Navegar até o penúltimo nível
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]
            
            # Definir valor final
            current[keys[-1]] = value
            self.has_changes = True
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao definir config '{key}': {e}")
            return False
    
    def save_user_config(self) -> bool:
        """Salvar configurações do usuário"""
        try:
            # Criar diretório se não existir
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Calcular diferenças em relação ao padrão
            user_changes = self._calculate_differences()
            
            # Salvar apenas as diferenças
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(user_changes, f, indent=2, ensure_ascii=False)
            
            self.user_config = user_changes
            self.has_changes = False
            
            _safe_print(f"✅ Configuração salva: {self.user_config_path}")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao salvar config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Alias para save_user_config para compatibilidade"""
        return self.save_user_config()
    
    def _calculate_differences(self) -> Dict:
        """Calcular diferenças entre config atual e padrão"""
        differences = {}
        self._compare_dicts(self.default_config, self.merged_config, differences)
        return differences
    
    def _compare_dicts(self, default: Dict, current: Dict, result: Dict, path: str = ""):
        """Comparar dicionários recursivamente"""
        for key, current_value in current.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in default:
                # Chave nova
                result[key] = current_value
            elif isinstance(current_value, dict) and isinstance(default[key], dict):
                # Recursão para subdicionários
                nested_result = {}
                self._compare_dicts(default[key], current_value, nested_result, current_path)
                if nested_result:
                    result[key] = nested_result
            elif current_value != default[key]:
                # Valor diferente
                result[key] = current_value
    
    def reset_to_defaults(self):
        """Resetar configurações para padrão"""
        self.merged_config = copy.deepcopy(self.default_config)
        self.user_config = {}
        self.has_changes = True
        _safe_print("🔄 Configurações resetadas para padrão")
    
    def validate_config(self) -> bool:
        """Validar estrutura de configuração"""
        try:
            required_sections = [
                'coordinates',
                'template_confidence', 
                'bait_priority',
                'rod_system',
                'feeding',
                'auto_clean',
                'performance',
                'hotkeys'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in self.merged_config:
                    missing_sections.append(section)
            
            if missing_sections:
                _safe_print(f"❌ Seções faltando na configuração: {missing_sections}")
                return False
            
            _safe_print("✅ Configuração validada")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro na validação: {e}")
            return False
    
    # ===== MÉTODOS ESPECÍFICOS (extraídos do botpesca.py) =====
    
    def get_template_confidence(self, template_name: str) -> float:
        """Obter confiança para template específico"""
        return self.get(f'template_confidence.{template_name}', 0.7)
    
    def set_template_confidence(self, template_name: str, confidence: float):
        """Definir confiança para template específico"""
        self.set(f'template_confidence.{template_name}', confidence)
    
    def get_bait_priority(self) -> Dict[str, int]:
        """Obter prioridades de iscas"""
        return self.get('bait_priority', {})
    
    def get_rod_config(self) -> Dict[str, Any]:
        """Obter configuração do sistema de varas"""
        return self.get('rod_system', {})
    
    def get_feeding_config(self) -> Dict[str, Any]:
        """Obter configuração do sistema de alimentação"""
        return self.get('feeding', {})
    
    def get_auto_clean_config(self) -> Dict[str, Any]:
        """Obter configuração de limpeza automática"""
        return self.get('auto_clean', {})
    
    def get_coordinates(self) -> Dict[str, Any]:
        """Obter todas as coordenadas"""
        return self.get('coordinates', {})
    
    def get_hotkeys(self) -> Dict[str, str]:
        """Obter configuração de hotkeys"""
        return self.get('hotkeys', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Obter configurações de performance"""
        return self.get('performance', {})
    
    def get_feeding_position(self, slot: str) -> tuple:
        """Obter posição de alimentação para slot específico"""
        positions = self.get('coordinates.feeding_positions', {})
        pos = positions.get(slot, [1306, 858])
        return tuple(pos) if isinstance(pos, list) else pos
    
    def get_slot_position(self, slot_number: Union[str, int]) -> tuple:
        """Obter posição de slot do inventário"""
        positions = self.get('coordinates.slot_positions', {})
        pos = positions.get(str(slot_number), [700, 1000])
        return tuple(pos) if isinstance(pos, list) else pos
    
    def get_screenshot_region(self) -> list:
        """Obter região de screenshot"""
        return self.get('coordinates.screenshot_region', [0, 0, 1920, 1080])
    
    def is_enabled(self, feature: str) -> bool:
        """Verificar se feature está habilitada"""
        return self.get(f'{feature}.enabled', False)
    
    def get_cycle_timeout(self) -> int:
        """Obter timeout do ciclo de pesca"""
        return self.get('cycle_timeout', 120)
    
    def get_detection_interval(self) -> int:
        """Obter intervalo de detecção em ms"""
        return self.get('performance.detection_interval_ms', 100)
    
    # ===== MÉTODOS DE DEBUG E INFORMAÇÃO =====
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obter resumo da configuração"""
        return {
            'sections': list(self.merged_config.keys()),
            'templates_count': len(self.get('template_confidence', {})),
            'baits_count': len(self.get('bait_priority', {})),
            'hotkeys_count': len(self.get('hotkeys', {})),
            'has_user_changes': bool(self.user_config),
            'config_valid': self.validate_config()
        }
    
    def export_current_config(self, filepath: str) -> bool:
        """Exportar configuração atual para arquivo"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.merged_config, f, indent=2, ensure_ascii=False)
            
            _safe_print(f"✅ Configuração exportada: {filepath}")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao exportar config: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """Obter configuração completa mesclada"""
        return copy.deepcopy(self.merged_config)
    
    def __str__(self) -> str:
        """Representação string do ConfigManager"""
        summary = self.get_config_summary()
        return f"ConfigManager(sections={summary['sections']}, templates={summary['templates_count']}, valid={summary['config_valid']})"
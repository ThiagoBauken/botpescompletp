#!/usr/bin/env python3
"""
⚙️ Gerenciador de Configurações
Reutiliza coordenadas e configurações funcionais do código atual
"""

import json
import os
from typing import Dict, Any, Optional
try:
    from utils.i18n import i18n
except ImportError:
    class MockI18n:
        current_language = "pt"
    i18n = MockI18n()

class ConfigManager:
    """Gerenciador unificado de configurações"""
    
    def __init__(self):
        self.config_file = "config.json"  # Usar o config.json principal
        self.unified_config_file = "config.json"  # Mesmo arquivo para unified
        self.default_config_file = "config/default_config.json"
        self.config = {}
        self.template_categories = {}
        self.is_unified_format = False
        self.load_config()
        
    def get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão com coordenadas funcionais REUTILIZADAS"""
        return {
            "version": "4.0.0",
            "language": i18n.current_language,
            
            # Coordenadas FUNCIONAIS reutilizadas do código atual
            "coordinates": {
                "inventory_area": [633, 541, 1233, 953],
                "chest_area": [1214, 117, 1834, 928], 
                "inventory_chest_divider_x": 1243,
                
                # Posições das 6 varas (TESTADAS e FUNCIONAIS)
                "slot_positions": {
                    "1": [709, 1005], "2": [805, 1005], "3": [899, 1005],
                    "4": [992, 1005], "5": [1092, 1005], "6": [1188, 1005]
                },
                
                # Posições de alimentação (FUNCIONAIS)
                "feeding_positions": {
                    "slot1": [1306, 858],
                    "slot2": [1403, 877], 
                    "eat": [1083, 373]
                },
                
                # Região de captura de tela
                "screenshot_region": [0, 0, 1920, 1080]
            },
            
            # Configurações de confiança dos templates (TESTADAS)
            "template_confidence": {
                "catch": 0.8,               # Template crítico
                "VARANOBAUCI": 0.8,         # Vara com isca
                "enbausi": 0.7,             # Vara sem isca
                "varaquebrada": 0.7,        # Vara quebrada
                "inventory": 0.8,           # Inventário aberto
                "loot": 0.8,                # Baú aberto
                "carneurso": 0.7,           # Carne de urso
                "wolfmeat": 0.7,            # Carne de lobo
                "grub": 0.6,                # Larva
                "worm": 0.6,                # Minhoca
                "salmon": 0.7,              # Salmão
                "smalltrout": 0.7           # Truta pequena
            },
            
            # Prioridade de iscas (FUNCIONAL)
            "bait_priority": {
                "carne de urso": 1,
                "carne de lobo": 2,
                "trout": 3,
                "grub": 4,
                "worm": 5
            },
            
            # Sistema de varas
            "rod_system": {
                "enabled": True,
                "rod_pairs": [[1, 2], [3, 4], [5, 6]],
                "initial_uses": 20,
                "reload_uses": 10,
                "auto_replace_broken": True,
                "broken_rod_action": "save"  # ou "discard"
            },
            
            # Sistema de alimentação
            "feeding": {
                "enabled": True,
                "mode": "detecao_auto",      # auto, manual, disabled
                "trigger_mode": "catches",   # catches ou time
                "trigger_catches": 2,
                "trigger_minutes": 20,
                "max_uses_per_slot": 20,
                "feeds_per_session": 5
            },
            
            # Limpeza automática
            "auto_clean": {
                "enabled": True,
                "interval": 1,               # A cada X peixes
                "chest_side": "right",       # left ou right
                "chest_method": "macro",     # macro ou alt_movement
                "fish_selection": {
                    "salmon": True,
                    "sardine": True,
                    "anchovy": True,
                    "shark": True,
                    "yellowperch": True,
                    "herring": True,
                    "smalltrout": True,
                    "rawfish": True
                }
            },
            
            # Performance
            "performance": {
                "detection_interval_ms": 100,
                "screenshot_optimization": True,
                "template_caching": True
            },
            
            # Anti-detecção
            "anti_detection": {
                "enabled": True,
                "click_variation": False,
                "click_delay_range": [80, 150],
                "movement_variation": True,
                "natural_breaks": True,
                "break_mode": "catches",     # catches ou time
                "break_catches": 50,
                "break_minutes": 45
            },
            
            # Logging
            "logging": {
                "enabled": True,
                "level": "INFO",             # DEBUG, INFO, WARNING, ERROR
                "file_rotation": True,
                "max_log_size_mb": 10
            },
            
            # Hotkeys (FUNCIONAIS)
            "hotkeys": {
                "start_bot": "F9",
                "pause_resume": "F1",
                "stop_bot": "F2",
                "emergency_stop": "ESC",
                "open_interface": "F4",
                "test_macro": "F11",
                "execute_macro": "F8"
            },
            
            # Servidor (para Fase 2)
            "server": {
                "enabled": False,
                "url": "ws://localhost:8765",
                "auto_connect": False,
                "username": "",
                "operating_mode": "local"    # local, hybrid, server
            },
            
            # Arduino (para Fase 2) 
            "arduino": {
                "enabled": False,
                "com_port": "COM3",
                "baud_rate": 9600,
                "timeout": 1,
                "auto_connect": False
            }
        }
    
    def load_config(self):
        """Carregar configuração do arquivo config.json (detecta formato automaticamente)"""
        os.makedirs(os.path.dirname(self.default_config_file), exist_ok=True)
        
        config_loaded = False
        
        # Tentar carregar config.json
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Verificar se é formato unified (tem _categories)
                if 'template_confidence' in config_data and '_categories' in config_data['template_confidence']:
                    self.config = config_data
                    self.template_categories = config_data['template_confidence']['_categories']
                    self.is_unified_format = True
                    print(f"✅ Configuração UNIFIED carregada de: {self.config_file}")
                    print(f"   • {len(self.template_categories)} categorias de templates")
                    config_loaded = True
                else:
                    # Formato legado - merge com configuração padrão
                    default_config = self.get_default_config()
                    self.config = self._merge_configs(default_config, config_data)
                    self.is_unified_format = False
                    print(f"✅ Configuração LEGADO carregada de: {self.config_file}")
                    config_loaded = True
                    
            except Exception as e:
                print(f"❌ Erro ao carregar {self.config_file}: {e}")
        
        # Se não conseguiu carregar, usar configuração padrão
        if not config_loaded:
            self.config = self.get_default_config()
            self.is_unified_format = False
            print("✅ Usando configuração padrão")
            
        # Configurar idioma
        language = self.get('language') or self.get('ui_settings.language', 'pt')
        try:
            i18n.set_language(language)
        except:
            pass
            
        # Salvar configuração padrão
        self.save_default_config()
    
    def _load_unified_config(self):
        """Carregar configuração no formato unified"""
        try:
            with open(self.unified_config_file, 'r', encoding='utf-8') as f:
                unified_config = json.load(f)
            
            # Verificar se é formato unified
            if 'template_confidence' in unified_config and '_categories' in unified_config['template_confidence']:
                self.config = unified_config
                self.template_categories = unified_config['template_confidence']['_categories']
                self.is_unified_format = True
                print(f"✅ Configuração UNIFIED carregada de: {self.unified_config_file}")
                print(f"   • {len(self.template_categories)} categorias de templates")
                return True
            else:
                print(f"⚠️ Arquivo {self.unified_config_file} não é formato unified válido")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar {self.unified_config_file}: {e}")
            return False
    
    def _load_user_config(self):
        """Carregar configuração do usuário (formato antigo)"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Merge com configuração padrão
            default_config = self.get_default_config()
            self.config = self._merge_configs(default_config, user_config)
            self.is_unified_format = False
            print(f"✅ Configuração do usuário carregada de: {self.config_file}")
            return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar {self.config_file}: {e}")
            return False
    
    def save_config(self):
        """Salvar configuração atual no config.json"""
        try:
            # Atualizar idioma atual
            if 'language' in self.config:
                self.config['language'] = i18n.current_language
            elif 'ui_settings' in self.config:
                self.config['ui_settings']['language'] = i18n.current_language
            
            # Salvar no config.json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                print(f"✅ Configuração salva em: {self.config_file}")
                
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def save_default_config(self):
        """Salvar configuração padrão como referência"""
        try:
            os.makedirs(os.path.dirname(self.default_config_file), exist_ok=True)
            
            with open(self.default_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.get_default_config(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar configuração padrão: {e}")
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge configuração do usuário com padrão"""
        result = default.copy()
        
        for key, value in user.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obter valor de configuração usando notação de ponto"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Definir valor de configuração usando notação de ponto"""
        keys = key.split('.')
        config = self.config
        
        # Navegar até o último nível
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Definir valor
        config[keys[-1]] = value
    
    def get_slot_position(self, slot_number: int) -> Optional[tuple]:
        """Obter posição de um slot específico"""
        positions = self.get('coordinates.slot_positions', {})
        pos = positions.get(str(slot_number))
        return tuple(pos) if pos else None
    
    def get_feeding_position(self, position_type: str) -> Optional[tuple]:
        """Obter posição de alimentação (slot1, slot2, eat)"""
        positions = self.get('coordinates.feeding_positions', {})
        pos = positions.get(position_type)
        return tuple(pos) if pos else None
    
    def get_template_confidence(self, template_name: str) -> float:
        """Obter confiança de um template específico (suporta formato unified)"""
        if self.is_unified_format:
            # Formato unified: template_confidence.values.template_name
            return self.get(f'template_confidence.values.{template_name}', 0.7)
        else:
            # Formato antigo: template_confidence.template_name
            return self.get(f'template_confidence.{template_name}', 0.7)
    
    def get_template_categories(self) -> dict:
        """Obter categorias de templates (apenas formato unified)"""
        if self.is_unified_format:
            return self.get('template_confidence._categories', {})
        else:
            return {}
    
    def has_template_categories(self) -> bool:
        """Verificar se tem categorias (formato unified)"""
        return self.is_unified_format and bool(self.template_categories)
    
    def reset_to_default(self):
        """Resetar para configuração padrão"""
        self.config = self.get_default_config()
        self.save_config()
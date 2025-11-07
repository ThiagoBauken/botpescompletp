#!/usr/bin/env python3
"""
🌍 Sistema de Internacionalização - Reutilizado e Expandido
Baseado no i18n.py existente com adição do idioma russo
"""

import json
import locale
import os
from typing import Dict, Optional

class I18NManager:
    """Gerenciador completo de internacionalização PT/EN/RU"""
    
    SUPPORTED_LANGUAGES = {
        'pt_BR': 'Português (Brasil)',
        'en_US': 'English',
        'ru_RU': 'Русский'
    }
    
    def __init__(self):
        self.current_language = self.detect_system_language()
        self.translations: Dict[str, Dict] = {}
        self.load_all_translations()
        
    def detect_system_language(self) -> str:
        """Detectar idioma do sistema automaticamente"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                if system_locale.startswith('pt_BR') or system_locale.startswith('pt'):
                    return 'pt_BR'
                elif system_locale.startswith('en'):
                    return 'en_US'
                elif system_locale.startswith('ru'):
                    return 'ru_RU'
        except:
            pass
        return 'pt_BR'  # Padrão brasileiro
        
    def load_all_translations(self):
        """Carregar todas as traduções dos arquivos JSON"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        locales_dir = os.path.join(base_dir, 'locales')
        
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            self.translations[lang_code] = {}
            lang_dir = os.path.join(locales_dir, lang_code)
            
            # Arquivos de tradução por categoria
            translation_files = [
                'ui.json',          # Interface principal
                'messages.json',    # Mensagens do sistema
                'errors.json',      # Mensagens de erro
                'tooltips.json',    # Tooltips e ajuda
                'status.json'       # Status e logs
            ]
            
            for file_name in translation_files:
                file_path = os.path.join(lang_dir, file_name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            category = file_name.replace('.json', '')
                            self.translations[lang_code][category] = json.load(f)
                    except Exception as e:
                        print(f"Erro ao carregar {file_path}: {e}")
                        
        # Se não conseguiu carregar, usar traduções hardcoded básicas
        if not self.translations:
            self._load_fallback_translations()
                        
    def _load_fallback_translations(self):
        """Carregar traduções básicas como fallback"""
        # Traduções básicas hardcoded para funcionamento mínimo
        basic_translations = {
            'pt_BR': {
                'ui': {
                    'main_window': {'title': 'Ultimate Fishing Bot v4.0'},
                    'tabs': {
                        'control': 'Controle',
                        'config': 'Configuração',
                        'confidence': 'Confiança',
                        'feeding': 'Alimentação',
                        'analytics': 'Análises'
                    },
                    'buttons': {
                        'start': 'Iniciar Bot',
                        'stop': 'Parar Bot',
                        'emergency': 'EMERGÊNCIA'
                    }
                }
            },
            'en_US': {
                'ui': {
                    'main_window': {'title': 'Ultimate Fishing Bot v4.0'},
                    'tabs': {
                        'control': 'Control',
                        'config': 'Configuration', 
                        'confidence': 'Confidence',
                        'feeding': 'Feeding',
                        'analytics': 'Analytics'
                    },
                    'buttons': {
                        'start': 'Start Bot',
                        'stop': 'Stop Bot',
                        'emergency': 'EMERGENCY'
                    }
                }
            },
            'ru_RU': {
                'ui': {
                    'main_window': {'title': 'Ultimate Fishing Bot v4.0'},
                    'tabs': {
                        'control': 'Управление',
                        'config': 'Настройки',
                        'confidence': 'Точность', 
                        'feeding': 'Питание',
                        'analytics': 'Аналитика'
                    },
                    'buttons': {
                        'start': 'Запустить Бота',
                        'stop': 'Остановить Бота',
                        'emergency': 'АВАРИЙНАЯ ОСТАНОВКА'
                    }
                }
            }
        }
        
        self.translations = basic_translations
            
    def set_language(self, language_code: str):
        """Definir idioma atual"""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            
    def translate(self, key: str, category: str = 'ui', **kwargs) -> str:
        """
        Traduzir chave com suporte a parâmetros
        
        Args:
            key: Chave da tradução (ex: 'main_window.title' ou 'buttons.start')
            category: Categoria da tradução ('ui', 'messages', 'errors', etc.)
            **kwargs: Parâmetros para interpolação de strings
            
        Returns:
            Texto traduzido
        """
        try:
            # Navegar pela estrutura aninhada usando pontos
            keys = key.split('.')
            text = self.translations[self.current_language][category]
            
            for k in keys:
                text = text[k]
            
            # Aplicar parâmetros se fornecidos
            if kwargs and isinstance(text, str):
                text = text.format(**kwargs)
                
            return text
            
        except (KeyError, TypeError, IndexError):
            # Fallback 1: Tentar inglês
            try:
                keys = key.split('.')
                text = self.translations['en_US'][category]
                
                for k in keys:
                    text = text[k]
                    
                if kwargs and isinstance(text, str):
                    text = text.format(**kwargs)
                    
                return text
                
            except (KeyError, TypeError, IndexError):
                # Fallback 2: Tentar português
                try:
                    keys = key.split('.')
                    text = self.translations['pt_BR'][category]
                    
                    for k in keys:
                        text = text[k]
                        
                    if kwargs and isinstance(text, str):
                        text = text.format(**kwargs)
                        
                    return text
                    
                except (KeyError, TypeError, IndexError):
                    # Fallback final: retornar a chave
                    return f"[{key}]"
                    
    def get_available_languages(self) -> Dict[str, str]:
        """Obter lista de idiomas disponíveis"""
        return self.SUPPORTED_LANGUAGES.copy()
        
    def get_current_language_name(self) -> str:
        """Obter nome do idioma atual"""
        return self.SUPPORTED_LANGUAGES.get(self.current_language, "Unknown")

# Instância global para compatibilidade com código existente
i18n = I18NManager()

# Função helper para uso rápido (compatibilidade com código existente)
def _(key: str, category: str = 'ui', **kwargs) -> str:
    """
    Função helper para tradução rápida
    
    Exemplos:
        _("main_window.title")
        _("buttons.start") 
        _("status.fish_caught", count=5)
        _("error_occurred", "errors", error="Falha na conexão")
    """
    return i18n.translate(key, category, **kwargs)
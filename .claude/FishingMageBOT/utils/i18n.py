# -*- coding: utf-8 -*-
"""
Sistema de Internacionalização (i18n) para Ultimate Fishing Bot
Suporte multilingual com detecção automática de idioma
"""

import json
import os
import locale
from typing import Dict, Optional

class I18nManager:
    """🌍 Gerenciador de Internacionalização Multilingual"""
    
    def __init__(self):
        self.system_language = self.detect_system_language()
        self.current_language = self.system_language
        self.translations = {}
        self.fallback_language = 'en'
        self.locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        self.load_translations()
    
    def detect_system_language(self) -> str:
        """🔍 Detectar idioma do sistema automaticamente"""
        try:
            # Tentar detectar idioma do sistema
            system_locale = locale.getdefaultlocale()[0]
            
            if system_locale:
                if system_locale.startswith('pt'):
                    return 'pt'
                elif system_locale.startswith('en'):
                    return 'en'
                elif system_locale.startswith('es'):
                    return 'es'
                elif system_locale.startswith('ru'):
                    return 'ru'
            
            # Fallback para inglês se não conseguir detectar
            return 'en'
            
        except Exception as e:
            print(f"⚠️ Erro ao detectar idioma do sistema: {e}")
            return 'en'
    
    def get_available_languages(self) -> Dict[str, str]:
        """📋 Lista de idiomas disponíveis"""
        return {
            'pt': 'Português (Brasil)',
            'en': 'English (US)',
            'es': 'Español',
            'ru': 'Русский'
        }
    
    def load_translations(self):
        """Carregar todas as traduções dos arquivos JSON em locales"""
        try:
            # Mapear códigos de idioma para diretórios
            language_mapping = {
                'pt': 'pt_BR',
                'en': 'en_US',
                'es': 'es_ES',
                'ru': 'ru_RU'
            }

            # Carregar traduções dos arquivos JSON
            for lang_code, locale_dir in language_mapping.items():
                locale_path = os.path.join(self.locales_dir, locale_dir, 'ui.json')

                if os.path.exists(locale_path):
                    try:
                        with open(locale_path, 'r', encoding='utf-8') as f:
                            self.translations[lang_code] = json.load(f)
                        print(f"[OK] Loaded {lang_code} translations from {locale_path}")
                    except Exception as e:
                        print(f"[WARN] Error loading {lang_code} translations: {e}")
                        # Fallback para traduções básicas se arquivo não carregar
                        self.translations[lang_code] = self._get_fallback_translations(lang_code)
                else:
                    print(f"[WARN] Translation file not found: {locale_path}")
                    # Fallback para traduções básicas se arquivo não existir
                    self.translations[lang_code] = self._get_fallback_translations(lang_code)

        except Exception as e:
            print(f"[ERROR] Error loading translations: {e}")
            # Se tudo falhar, carregar traduções básicas hardcoded
            self._load_basic_translations()
    
    def _get_fallback_translations(self, lang_code: str) -> Dict[str, any]:
        """🔄 Obter traduções básicas de fallback"""
        fallback_translations = {
            'pt': {
                "tabs": {"control": "🎮 Controle", "config": "⚙️ Configuração"},
                "buttons": {"start": "🚀 Iniciar", "stop": "🛑 Parar"},
                "status": {"ready": "✅ Pronto", "running": "🟢 Executando"}
            },
            'en': {
                "tabs": {"control": "🎮 Control", "config": "⚙️ Configuration"},  
                "buttons": {"start": "🚀 Start", "stop": "🛑 Stop"},
                "status": {"ready": "✅ Ready", "running": "🟢 Running"}
            },
            'es': {
                "tabs": {"control": "🎮 Control", "config": "⚙️ Configuración"},
                "buttons": {"start": "🚀 Iniciar", "stop": "🛑 Detener"},
                "status": {"ready": "✅ Listo", "running": "🟢 Ejecutando"}
            },
            'ru': {
                "tabs": {"control": "🎮 Управление", "config": "⚙️ Настройки"},
                "buttons": {"start": "🚀 Старт", "stop": "🛑 Стоп"},
                "status": {"ready": "✅ Готов", "running": "🟢 Работает"}
            }
        }
        
        return fallback_translations.get(lang_code, fallback_translations['en'])
    
    def _load_basic_translations(self):
        """📥 Carregar traduções básicas hardcoded como último recurso"""
        # 🇧🇷 PORTUGUÊS (BRASIL) - Traduções básicas
        self.translations['pt'] = {
            'app_title': '🧙‍♂️ ULTIMATE FISHING BOT v4.0',
            'control_tab': '🎮 Controle',
            'config_tab': '⚙️ Configurações',
            'start': '🚀 Iniciar',
            'stop': '🛑 Parar',
            'ready': '✅ Pronto'
        }
        
        # 🇺🇸 ENGLISH (US) - Basic translations
        self.translations['en'] = {
            'app_title': '🧙‍♂️ ULTIMATE FISHING BOT v4.0',
            'control_tab': '🎮 Control',
            'config_tab': '⚙️ Configuration',
            'start': '🚀 Start',
            'stop': '🛑 Stop',
            'ready': '✅ Ready'
        }
    
    def set_language(self, language_code: str):
        """🔄 Trocar idioma manualmente"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def reload_translations(self):
        """Recarregar todas as traduções dos arquivos"""
        print("[INFO] Recarregando traducoes...")
        self.translations.clear()
        self.load_translations()
        print(f"[OK] Traducoes recarregadas. Idioma atual: {self.current_language}")
    
    def get_available_keys(self, category: str = None) -> list:
        """📋 Obter lista de chaves disponíveis (útil para debug)"""
        if self.current_language not in self.translations:
            return []
        
        if category:
            # Retornar chaves de uma categoria específica
            category_data = self.translations[self.current_language].get(category, {})
            if isinstance(category_data, dict):
                return [f"{category}.{key}" for key in category_data.keys()]
            return []
        else:
            # Retornar todas as chaves de nível superior
            return list(self.translations[self.current_language].keys())
    
    def get_text(self, key: str, **kwargs) -> str:
        """📝 Obter texto traduzido com suporte a formatação e chaves aninhadas"""
        try:
            # Tentar obter tradução no idioma atual
            translation = self._get_nested_translation(self.current_language, key)
            if translation:
                return translation.format(**kwargs) if kwargs else translation
            
            # Fallback para idioma padrão
            translation = self._get_nested_translation(self.fallback_language, key)
            if translation:
                return translation.format(**kwargs) if kwargs else translation
            
            # Se não encontrar, retornar a chave
            return key


        except Exception as e:
            print(f"[WARN] Error getting translation for '{key}': {e}")
            return key
    
    def _get_nested_translation(self, language: str, key: str) -> Optional[str]:
        """🔍 Obter tradução de chave aninhada (ex: 'tabs.control')"""
        if language not in self.translations:
            return None
            
        try:
            # Dividir chave por pontos para navegação aninhada
            keys = key.split('.')
            current = self.translations[language]
            
            # Navegar pela estrutura aninhada
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            
            # Retornar apenas se for string
            return current if isinstance(current, str) else None
            
        except Exception:
            return None

# 🌍 Instância global do gerenciador de idiomas
i18n = I18nManager()

# 🔧 Função helper para facilitar o uso
def _(key: str, **kwargs) -> str:
    """🌍 Função helper para obter tradução rapidamente"""
    return i18n.get_text(key, **kwargs)
#!/usr/bin/env python3
"""
🌍 Translation Helper for Ultimate Fishing Bot v4.0
Helper functions to easily use translations in the UI
"""

from utils.i18n import i18n, _

class TranslationHelper:
    """🌍 Helper class for UI translations"""
    
    @staticmethod
    def get_tab_text(tab_name: str) -> str:
        """📋 Get translated tab text"""
        return _(f"tabs.{tab_name}")
    
    @staticmethod
    def get_button_text(button_name: str) -> str:
        """🔘 Get translated button text"""
        return _(f"buttons.{button_name}")
    
    @staticmethod
    def get_status_text(status_name: str) -> str:
        """📊 Get translated status text"""
        return _(f"status.{status_name}")
    
    @staticmethod
    def get_control_text(control_name: str) -> str:
        """🎮 Get translated control text"""
        return _(f"control.{control_name}")
    
    @staticmethod
    def get_manual_text(manual_name: str) -> str:
        """🎮 Get translated manual control text"""
        return _(f"manual.{manual_name}")
    
    @staticmethod
    def get_config_text(config_name: str) -> str:
        """⚙️ Get translated config text"""
        return _(f"config.{config_name}")
    
    @staticmethod
    def get_confidence_text(confidence_name: str) -> str:
        """🎯 Get translated confidence text"""
        return _(f"confidence.{confidence_name}")
    
    @staticmethod
    def get_feeding_text(feeding_name: str) -> str:
        """🍖 Get translated feeding text"""
        return _(f"feeding.{feeding_name}")
    
    @staticmethod
    def get_autoclean_text(autoclean_name: str) -> str:
        """🧹 Get translated autoclean text"""
        return _(f"autoclean.{autoclean_name}")
    
    @staticmethod
    def get_rod_management_text(rod_name: str) -> str:
        """🎣 Get translated rod management text"""
        return _(f"rod_management.{rod_name}")
    
    @staticmethod
    def get_analytics_text(analytics_name: str) -> str:
        """📊 Get translated analytics text"""
        return _(f"analytics.{analytics_name}")
    
    @staticmethod
    def get_advanced_text(advanced_name: str) -> str:
        """⚡ Get translated advanced text"""
        return _(f"advanced.{advanced_name}")
    
    @staticmethod
    def get_server_text(server_name: str) -> str:
        """🌐 Get translated server text"""
        return _(f"server.{server_name}")
    
    @staticmethod
    def get_log_text(log_name: str) -> str:
        """📝 Get translated log text"""
        return _(f"log.{log_name}")
    
    @staticmethod
    def get_rod_text(rod_name: str) -> str:
        """🎣 Get translated rod text"""
        return _(f"rod.{rod_name}")
    
    @staticmethod
    def get_emergency_text(emergency_name: str) -> str:
        """🚨 Get translated emergency text"""
        return _(f"emergency.{emergency_name}")
    
    @staticmethod
    def get_menu_text(menu_name: str) -> str:
        """📁 Get translated menu text"""
        return _(f"menu.{menu_name}")
    
    @staticmethod
    def get_license_text(license_name: str) -> str:
        """🔐 Get translated license text"""
        return _(f"license.{license_name}")
    
    @staticmethod
    def get_app_text(app_name: str) -> str:
        """🔧 Get translated app text"""
        return _(f"app.{app_name}")
    
    @staticmethod
    def get_about_text(about_name: str) -> str:
        """ℹ️ Get translated about text"""
        return _(f"about.{about_name}")
    
    @staticmethod
    def get_tooltip_text(tooltip_name: str) -> str:
        """💬 Get translated tooltip text"""
        return _(f"tooltips.{tooltip_name}")
    
    @staticmethod
    def get_notification_text(notification_name: str, **kwargs) -> str:
        """🔔 Get translated notification text with formatting"""
        return _(f"notifications.{notification_name}", **kwargs)
    
    @staticmethod
    def change_language(language_code: str) -> bool:
        """🌍 Change interface language"""
        success = i18n.set_language(language_code)
        if success:
            print(f"✅ Language changed to: {language_code}")
        else:
            print(f"❌ Failed to change language to: {language_code}")
        return success
    
    @staticmethod
    def get_current_language() -> str:
        """🌍 Get current language code"""
        return i18n.current_language
    
    @staticmethod
    def get_available_languages() -> dict:
        """📋 Get available languages"""
        return i18n.get_available_languages()
    
    @staticmethod
    def reload_translations():
        """🔄 Reload all translations from files"""
        i18n.reload_translations()
    
    @staticmethod
    def debug_translations(category: str = None) -> list:
        """🐛 Debug: get available translation keys"""
        return i18n.get_available_keys(category)

# Create global instance for easy access
t = TranslationHelper()

# Example usage functions for the UI
def get_tab_title(tab_name: str) -> str:
    """Get translated tab title"""
    return t.get_tab_text(tab_name)

def get_button_label(button_name: str) -> str:
    """Get translated button label"""
    return t.get_button_text(button_name)

def get_status_label(status_name: str) -> str:
    """Get translated status label"""
    return t.get_status_text(status_name)
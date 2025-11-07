# -*- coding: utf-8 -*-
"""
MAPEAMENTO COMPLETO - TODAS as strings que precisam ser traduzidas
Organizado por aba e tipo de widget
"""

# ==============================================================================
# ABA 1: CONTROLE
# ==============================================================================
CONTROL_TAB = {
    # LabelFrames
    'status_frame': 'ui.bot_status',
    'stats_frame': 'ui.detailed_statistics',
    'auto_frame': 'ui.auto_clean',
    'manual_frame': 'ui.manual_controls',

    # Labels de estatísticas
    'fish_caught_label': 'ui.fish_caught',
    'session_time_label': 'ui.session_time',
    'fish_per_hour_label': 'ui.fish_per_hour',
    'success_rate_label': 'ui.success_rate',
    'feedings_label': 'ui.feedings',
    'cleanings_label': 'ui.cleanings',
    'broken_rods_label': 'ui.broken_rods',
    'timeouts_label': 'ui.timeouts',
    'last_rod_label': 'ui.last_rod',

    # Limpeza automática
    'clean_every_label': 'ui.clean_every',
    'catches_label': 'ui.catches',
    'enable_clean_check': 'ui.enable_auto_clean',
    'include_baits_check': 'ui.include_baits_clean',
    'next_clean_label': 'ui.next_clean_in',
    'save_clean_btn': 'ui.save_clean_config',

    # Botões de controle
    'start_btn': 'ui.start_bot',
    'stop_btn': 'ui.stop_bot',
    'pause_btn': 'ui.pause_bot',
    'resume_btn': 'ui.resume_bot',
    'emergency_btn': 'ui.emergency_stop',
    'test_feeding_btn': 'ui.test_feeding',
    'test_cleaning_btn': 'ui.test_cleaning',
    'test_maintenance_btn': 'ui.test_maintenance',
}

# ==============================================================================
# ABA 2: CONFIGURAÇÃO
# ==============================================================================
CONFIG_TAB = {
    # Frames principais
    'general_frame': 'ui.general_config',
    'timeout_frame': 'ui.timeouts_cycles',
    'chest_frame': 'ui.chest_config',
    'options_frame': 'ui.additional_options',
    'broken_frame': 'ui.broken_rod_handling',
    'bait_frame': 'ui.bait_priority',

    # Labels de configuração
    'cycle_timeout_label': 'ui.cycle_timeout_seconds',
    'rod_switch_label': 'ui.rod_pair_switch_limit',
    'clicks_per_sec_label': 'ui.clicks_per_second',
    'maintenance_timeout_label': 'ui.maintenance_timeout',
    'chest_side_label': 'ui.chest_side',
    'chest_type_label': 'ui.macro_type',
    'chest_distance_label': 'ui.chest_distance',

    # Opções
    'auto_reload_check': 'ui.auto_reload',
    'auto_focus_check': 'ui.auto_focus',

    # Varas quebradas
    'discard_radio': 'ui.discard_broken',
    'save_radio': 'ui.save_broken',
    'auto_replace_check': 'ui.auto_replace_broken',

    # Botões
    'save_config_btn': 'ui.save_all_config',
    'restore_bait_btn': 'ui.restore_default',
    'save_bait_btn': 'ui.save_priorities',
}

# ==============================================================================
# ABA 3: ALIMENTAÇÃO
# ==============================================================================
FEEDING_TAB = {
    # Frames
    'feeding_frame': 'ui.smart_feeding_system',
    'enable_frame': 'ui.general_control',
    'trigger_frame': 'ui.when_to_feed',
    'consumption_frame': 'ui.feeding_config',
    'tech_frame': 'ui.technical_info',
    'controls_frame': 'ui.controls_tests',

    # Labels e checks
    'enable_feeding_check': 'ui.feeding_system_enabled',
    'mode_label': 'ui.auto_detection_mode',
    'mode_desc_label': 'ui.system_identical_v3',
    'trigger_mode_label': 'ui.trigger_mode',
    'by_catches_radio': 'ui.trigger_by_catches',
    'by_time_radio': 'ui.trigger_by_time',
    'feed_every_label': 'ui.feed_every',
    'catches_unit_label': 'ui.catches_captured',
    'minutes_label': 'ui.minutes',
    'food_quantity_label': 'ui.food_quantity_per_session',
    'fish_unit_label': 'ui.fish_unit',

    # Botões
    'save_feeding_btn': 'ui.save_feeding_config',
    'restore_feeding_btn': 'ui.restore_default',
    'test_feeding_btn': 'ui.test_auto_feeding',
}

# ==============================================================================
# ABA 4: TEMPLATES
# ==============================================================================
TEMPLATES_TAB = {
    # Frame principal
    'confidence_frame': 'ui.templates_confidence',

    # Headers
    'template_header': 'ui.template',
    'value_header': 'ui.value',
    'confidence_header': 'ui.confidence',
    'fine_tune_header': 'ui.fine_tune',

    # Categorias
    'critical_category': 'ui.critical_fish',
    'rods_category': 'ui.rods',
    'baits_category': 'ui.baits',
    'ui_category': 'ui.ui_elements',
    'fish_category': 'ui.fish',

    # Botões
    'reset_btn': 'ui.apply_default',
    'high_precision_btn': 'ui.critical_high_precision',
    'save_all_btn': 'ui.save_all',
    'save_as_default_btn': 'ui.save_as_default',
    'open_folder_btn': 'ui.open_templates_folder',
}

# ==============================================================================
# ABA 5: ANTI-DETECÇÃO
# ==============================================================================
ANTI_DETECTION_TAB = {
    # Frames
    'anti_frame': 'ui.anti_detection_system',
    'main_frame': 'ui.general_activation',
    'click_frame': 'ui.click_variation',
    'movement_frame': 'ui.movement_variation',
    'pause_frame': 'ui.pauses_between_movements',
    'breaks_frame': 'ui.natural_breaks',

    # Checks e labels
    'enable_anti_check': 'ui.enable_anti_detection',
    'enable_click_check': 'ui.enable_click_variation',
    'min_delay_label': 'ui.min_delay_ms',
    'max_delay_label': 'ui.max_delay_ms',
    'enable_movement_check': 'ui.enable_movement_variation',
    'min_a_duration_label': 'ui.min_a_duration',
    'max_a_duration_label': 'ui.max_a_duration',
    'min_d_duration_label': 'ui.min_d_duration',
    'max_d_duration_label': 'ui.max_d_duration',
    'min_pause_label': 'ui.min_pause',
    'max_pause_label': 'ui.max_pause',
    'enable_breaks_check': 'ui.enable_natural_breaks',
    'break_after_label': 'ui.break_after_x_catches',
    'break_duration_label': 'ui.break_duration_minutes',

    # Botões
    'save_anti_btn': 'ui.save_anti_detection',
}

# ==============================================================================
# ABA 6: VISUALIZADOR
# ==============================================================================
VIEWER_TAB = {
    # Frames
    'viewer_frame': 'ui.template_viewer',
    'status_frame': 'ui.viewer_status',
    'stats_frame': 'ui.detection_stats',
    'controls_frame': 'ui.viewer_controls',

    # Labels
    'status_label': 'ui.status_stopped',
    'total_detections_label': 'ui.total_detections',
    'catch_detections_label': 'ui.catch_detections',
    'false_positives_label': 'ui.false_positives',
    'fps_label': 'ui.viewer_fps',
    'confidence_label': 'ui.confidence_threshold',

    # Botões e checks
    'start_viewer_btn': 'ui.start_viewer',
    'stop_viewer_btn': 'ui.stop_viewer',
    'save_image_check': 'ui.save_detection_image',
}

# ==============================================================================
# ABA 7: HOTKEYS
# ==============================================================================
HOTKEYS_TAB = {
    # Frame e headers
    'hotkeys_frame': 'ui.hotkeys_config',
    'hotkey_header': 'ui.hotkey',
    'action_header': 'ui.action',
    'current_key_header': 'ui.current_key',
    'capture_header': 'ui.capture',

    # Actions
    'start_fishing_action': 'ui.start_fishing',
    'pause_resume_action': 'ui.pause_resume',
    'stop_fishing_action': 'ui.stop_fishing',
    'toggle_ui_action': 'ui.toggle_ui',
    'manual_feeding_action': 'ui.manual_feeding',
    'manual_cleaning_action': 'ui.manual_cleaning',
    'rod_maintenance_action': 'ui.rod_maintenance',
    'rod_switch_action': 'ui.rod_switch',
    'execute_macro_action': 'ui.execute_macro',
    'chest_macro_action': 'ui.chest_macro',
    'record_macro_action': 'ui.record_macro',
    'test_mouse_action': 'ui.test_mouse',
    'emergency_action': 'ui.emergency_esc',
}

# ==============================================================================
# ABA 8: ARDUINO
# ==============================================================================
ARDUINO_TAB = {
    # Frames
    'arduino_frame': 'ui.arduino_leonardo',
    'connection_frame': 'ui.connection_status',
    'command_frame': 'ui.send_command',
    'log_frame': 'ui.connection_log',
    'info_frame': 'ui.arduino_info',

    # Labels
    'status_label': 'ui.not_connected',
    'com_port_label': 'ui.com_port',
    'baud_rate_label': 'ui.baud_rate',
    'timeout_label': 'ui.timeout',
    'command_label': 'ui.command',

    # Botões
    'test_btn': 'ui.test_connection',
    'connect_btn': 'ui.connect',
    'disconnect_btn': 'ui.disconnect',
    'send_btn': 'ui.send',
    'clear_log_btn': 'ui.clear_log',
}

# ==============================================================================
# ABA 9: AJUDA
# ==============================================================================
HELP_TAB = {
    # Frames
    'help_frame': 'ui.help_documentation',
    'hotkeys_frame': 'ui.main_hotkeys',
    'config_frame': 'ui.initial_config',
    'troubleshoot_frame': 'ui.troubleshooting',
    'support_frame': 'ui.support',

    # Hotkeys (9 items)
    'hotkey_f9': 'ui.hotkey_f9',
    'hotkey_f1': 'ui.hotkey_f1',
    'hotkey_f2': 'ui.hotkey_f2',
    'hotkey_esc': 'ui.hotkey_esc',
    'hotkey_f4': 'ui.hotkey_f4',
    'hotkey_f6': 'ui.hotkey_f6',
    'hotkey_f5': 'ui.hotkey_f5',
    'hotkey_pgdn': 'ui.hotkey_pgdn',
    'hotkey_tab': 'ui.hotkey_tab',

    # Config steps (5 items)
    'config_step1': 'ui.config_step1',
    'config_step2': 'ui.config_step2',
    'config_step3': 'ui.config_step3',
    'config_step4': 'ui.config_step4',
    'config_step5': 'ui.config_step5',

    # Troubleshooting (5 items)
    'trouble1': 'ui.trouble1',
    'trouble2': 'ui.trouble2',
    'trouble3': 'ui.trouble3',
    'trouble4': 'ui.trouble4',
    'trouble5': 'ui.trouble5',
}

print(f"[INFO] Total de widgets mapeados:")
print(f"  ABA 1 - Controle: {len(CONTROL_TAB)} widgets")
print(f"  ABA 2 - Config: {len(CONFIG_TAB)} widgets")
print(f"  ABA 3 - Alimentacao: {len(FEEDING_TAB)} widgets")
print(f"  ABA 4 - Templates: {len(TEMPLATES_TAB)} widgets")
print(f"  ABA 5 - Anti-Deteccao: {len(ANTI_DETECTION_TAB)} widgets")
print(f"  ABA 6 - Visualizador: {len(VIEWER_TAB)} widgets")
print(f"  ABA 7 - Hotkeys: {len(HOTKEYS_TAB)} widgets")
print(f"  ABA 8 - Arduino: {len(ARDUINO_TAB)} widgets")
print(f"  ABA 9 - Ajuda: {len(HELP_TAB)} widgets")
print(f"  TOTAL: {sum([len(CONTROL_TAB), len(CONFIG_TAB), len(FEEDING_TAB), len(TEMPLATES_TAB), len(ANTI_DETECTION_TAB), len(VIEWER_TAB), len(HOTKEYS_TAB), len(ARDUINO_TAB), len(HELP_TAB)])} widgets")

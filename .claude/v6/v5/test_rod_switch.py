#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do sistema de troca de varas
"""

import sys
import os
import time

# Configurar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config_manager import ConfigManager
from core.template_engine import TemplateEngine
from core.input_manager import InputManager
from core.rod_manager import RodManager
from core.game_state import GameState

def test_rod_switch():
    print("\n" + "="*60)
    print("TESTE DO SISTEMA DE TROCA DE VARAS")
    print("="*60)

    try:
        # Inicializar componentes
        print("\nInicializando componentes...")
        config_manager = ConfigManager()
        template_engine = TemplateEngine(config_manager=config_manager)
        input_manager = InputManager(config_manager=config_manager)
        game_state = GameState(config_manager=config_manager)

        print("Inicializando RodManager...")
        rod_manager = RodManager(
            template_engine=template_engine,
            input_manager=input_manager,
            config_manager=config_manager,
            game_state=game_state
        )

        print("\n" + "="*60)
        print("INFORMACOES DO SISTEMA DE VARAS")
        print("="*60)

        print(f"Vara atual: {rod_manager.get_current_rod()}")
        print(f"Pares de varas: {rod_manager.rod_pairs}")
        print(f"Usos por vara: {rod_manager.rod_uses}")

        print("\n" + "="*60)
        print("Pressione TAB no jogo para testar a troca de vara")
        print("Pressione ESC aqui para sair")
        print("="*60)

        import keyboard

        def test_switch():
            print("\n[TAB] Testando troca de vara...")
            success = rod_manager.manual_rod_switch()
            if success:
                print(f"Nova vara: {rod_manager.get_current_rod()}")
            else:
                print("Falha na troca")

        keyboard.add_hotkey('tab', test_switch)

        print("\nAguardando comandos...")
        while True:
            if keyboard.is_pressed('esc'):
                print("\nSaindo...")
                break
            time.sleep(0.1)

    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rod_switch()
    print("\nTeste finalizado!")
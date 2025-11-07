#!/usr/bin/env python3
"""
⚡ Action Executor - Executor Burro de Sequências
Cliente APENAS executa comandos do servidor cegamente
NÃO SABE coordenadas, sequências ou lógica de negócio
"""

import time
import pyautogui
import keyboard
import re

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

class ActionExecutor:
    """
    Executor genérico de sequências de ações

    NÃO SABE:
    - Onde clicar (coordenadas vêm do servidor)
    - Quando fazer (decisão do servidor)
    - O que está fazendo (apenas executa lista)

    APENAS SABE:
    - Como executar ações atômicas (click, key, wait)
    """

    def __init__(self, input_manager=None, template_engine=None, fishing_engine=None):
        """
        Inicializar executor

        Args:
            input_manager: InputManager (opcional, usa pyautogui se None)
            template_engine: TemplateEngine (para detecções locais)
            fishing_engine: FishingEngine (para parar ações contínuas)
        """
        self.input_manager = input_manager
        self.template_engine = template_engine
        self.fishing_engine = fishing_engine
        self.last_detected = None  # Para armazenar última detecção

        _safe_print("⚡ ActionExecutor inicializado (modo executor burro)")

    def execute_sequence(self, actions: list) -> bool:
        """
        Executar sequência de ações do servidor

        Cliente NÃO sabe o que está fazendo - apenas executa lista cegamente

        Args:
            actions: Lista de ações do servidor
                [
                    {"type": "click", "x": 100, "y": 200},
                    {"type": "wait", "duration": 1.5},
                    {"type": "key", "key": "esc"},
                    ...
                ]

        Returns:
            True se sucesso, False se falhou
        """
        try:
            _safe_print(f"\n⚡ Executando sequência de {len(actions)} ações...")

            for i, action in enumerate(actions, 1):
                action_type = action.get("type")

                if not action_type:
                    _safe_print(f"⚠️ Ação #{i} sem tipo, pulando...")
                    continue

                # Executar ação apropriada
                if action_type == "click":
                    self._execute_click(action, i)

                elif action_type == "click_right":
                    self._execute_click_right(action, i)

                elif action_type == "wait":
                    self._execute_wait(action, i)

                elif action_type == "key":
                    self._execute_key(action, i)

                elif action_type == "key_press":
                    self._execute_key_press(action, i)

                elif action_type == "key_down":
                    self._execute_key_down(action, i)

                elif action_type == "key_up":
                    self._execute_key_up(action, i)

                elif action_type == "move_camera":
                    self._execute_move_camera(action, i)

                elif action_type == "mouse_down_relative":
                    self._execute_mouse_down_relative(action, i)

                elif action_type == "mouse_up":
                    self._execute_mouse_up(action, i)

                elif action_type == "force_release_key":
                    self._execute_force_release_key(action, i)

                elif action_type == "stop_continuous_clicking":
                    self._execute_stop_continuous_clicking(action, i)

                elif action_type == "stop_camera_movement":
                    self._execute_stop_camera_movement(action, i)

                elif action_type == "stop_all_actions":
                    self._execute_stop_all_actions(action, i)

                elif action_type == "template":
                    if not self._execute_template_wait(action, i):
                        _safe_print(f"❌ Template não detectado, abortando sequência")
                        return False

                elif action_type == "template_detect":
                    if not self._execute_template_detect(action, i):
                        _safe_print(f"❌ Template não detectado, abortando sequência")
                        return False

                elif action_type == "click_detected":
                    self._execute_click_detected(action, i)

                elif action_type == "drag":
                    self._execute_drag(action, i)

                else:
                    _safe_print(f"⚠️ Ação #{i}: Tipo desconhecido '{action_type}'")

            _safe_print("✅ Sequência concluída com sucesso")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao executar sequência: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_click(self, action, index):
        """Executar clique(s)"""
        x = action.get("x")
        y = action.get("y")
        repeat = action.get("repeat", 1)
        interval = action.get("interval", 0.1)
        button = action.get("button", "left")

        if x is None or y is None:
            _safe_print(f"⚠️ Ação #{index}: Click sem coordenadas")
            return

        action_desc = f"click({x}, {y})"
        if repeat > 1:
            action_desc += f" × {repeat}"

        _safe_print(f"   #{index}: {action_desc}")

        # Executar cliques
        if self.input_manager:
            # Usar InputManager se disponível
            for _ in range(repeat):
                if button == "left":
                    self.input_manager.click(x, y)
                elif button == "right":
                    self.input_manager.right_click(x, y)

                if _ < repeat - 1:
                    time.sleep(interval)
        else:
            # Fallback: pyautogui direto
            for _ in range(repeat):
                pyautogui.click(x, y, button=button)
                if _ < repeat - 1:
                    time.sleep(interval)

    def _execute_wait(self, action, index):
        """Executar espera"""
        duration = action.get("duration", 1.0)

        _safe_print(f"   #{index}: wait({duration}s)")
        time.sleep(duration)

    def _execute_key(self, action, index):
        """Executar pressionamento de tecla"""
        key = action.get("key")

        if not key:
            _safe_print(f"⚠️ Ação #{index}: Key sem tecla especificada")
            return

        _safe_print(f"   #{index}: key({key})")

        # Executar tecla
        if self.input_manager and hasattr(self.input_manager, 'press_key'):
            self.input_manager.press_key(key)
        else:
            # Fallback: keyboard direto
            keyboard.press_and_release(key)

    def _execute_template_wait(self, action, index) -> bool:
        """
        Executar espera por template

        Returns:
            True se detectado, False se timeout
        """
        name = action.get("name")
        timeout = action.get("timeout", 5)
        confidence = action.get("confidence", 0.8)

        if not name:
            _safe_print(f"⚠️ Ação #{index}: Template sem nome")
            return False

        if not self.template_engine:
            _safe_print(f"⚠️ TemplateEngine não disponível, pulando detecção")
            return True  # Continuar mesmo assim

        _safe_print(f"   #{index}: template({name}, timeout={timeout}s)")

        # Aguardar detecção
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.template_engine.detect_template(name, confidence)

            if result and result.found:
                _safe_print(f"      ✅ Detectado (confidence: {result.confidence:.2f})")
                return True

            time.sleep(0.1)

        _safe_print(f"      ❌ Não detectado após {timeout}s")
        return False

    def _execute_drag(self, action, index):
        """Executar arraste"""
        from_x = action.get("from_x")
        from_y = action.get("from_y")
        to_x = action.get("to_x")
        to_y = action.get("to_y")
        duration = action.get("duration", 0.5)

        if None in [from_x, from_y, to_x, to_y]:
            _safe_print(f"⚠️ Ação #{index}: Drag sem coordenadas completas")
            return

        _safe_print(f"   #{index}: drag({from_x},{from_y} → {to_x},{to_y})")

        # Executar drag
        pyautogui.moveTo(from_x, from_y)
        time.sleep(0.1)
        pyautogui.drag(to_x - from_x, to_y - from_y, duration=duration)

    def _execute_click_right(self, action, index):
        """Executar clique direito"""
        x = action.get("x")
        y = action.get("y")

        if x is None or y is None:
            _safe_print(f"⚠️ Ação #{index}: Click_right sem coordenadas")
            return

        _safe_print(f"   #{index}: click_right({x}, {y})")

        if self.input_manager and hasattr(self.input_manager, 'right_click'):
            self.input_manager.right_click(x, y)
        else:
            pyautogui.click(x, y, button='right')

    def _execute_key_press(self, action, index):
        """Executar pressionar+soltar tecla"""
        key = action.get("key")
        duration = action.get("duration", 0.1)

        if not key:
            _safe_print(f"⚠️ Ação #{index}: Key_press sem tecla especificada")
            return

        _safe_print(f"   #{index}: key_press({key})")

        if self.input_manager and hasattr(self.input_manager, 'press_key'):
            self.input_manager.press_key(key)
        else:
            keyboard.press(key)
            time.sleep(duration)
            keyboard.release(key)

    def _execute_key_down(self, action, index):
        """Executar segurar tecla"""
        key = action.get("key")

        if not key:
            _safe_print(f"⚠️ Ação #{index}: Key_down sem tecla especificada")
            return

        _safe_print(f"   #{index}: key_down({key})")

        if self.input_manager and hasattr(self.input_manager, 'key_down'):
            self.input_manager.key_down(key)
        else:
            keyboard.press(key)

    def _execute_key_up(self, action, index):
        """Executar soltar tecla"""
        key = action.get("key")

        if not key:
            _safe_print(f"⚠️ Ação #{index}: Key_up sem tecla especificada")
            return

        _safe_print(f"   #{index}: key_up({key})")

        if self.input_manager and hasattr(self.input_manager, 'key_up'):
            self.input_manager.key_up(key)
        else:
            keyboard.release(key)

    def _execute_move_camera(self, action, index):
        """Executar movimento de câmera (relativo)"""
        dx = action.get("dx")
        dy = action.get("dy")

        if dx is None or dy is None:
            _safe_print(f"⚠️ Ação #{index}: Move_camera sem dx/dy")
            return

        _safe_print(f"   #{index}: move_camera(dx={dx}, dy={dy})")

        if self.input_manager and hasattr(self.input_manager, 'move_relative'):
            self.input_manager.move_relative(dx, dy)
        else:
            # Fallback: movimento relativo com pyautogui
            pyautogui.moveRel(dx, dy)

    def _execute_mouse_down_relative(self, action, index):
        """Executar mouse down sem mover cursor"""
        button = action.get("button", "left")

        _safe_print(f"   #{index}: mouse_down_relative({button})")

        if self.input_manager and hasattr(self.input_manager, 'mouse_down'):
            self.input_manager.mouse_down(button)
        else:
            pyautogui.mouseDown(button=button)

    def _execute_mouse_up(self, action, index):
        """Executar mouse up"""
        button = action.get("button", "left")

        _safe_print(f"   #{index}: mouse_up({button})")

        if self.input_manager and hasattr(self.input_manager, 'mouse_up'):
            self.input_manager.mouse_up(button)
        else:
            pyautogui.mouseUp(button=button)

    def _execute_force_release_key(self, action, index):
        """Executar force release de tecla (via Arduino)"""
        key = action.get("key")

        if not key:
            _safe_print(f"⚠️ Ação #{index}: Force_release_key sem tecla especificada")
            return

        _safe_print(f"   #{index}: force_release_key({key})")

        # Force release via Arduino (se disponível)
        if self.input_manager and hasattr(self.input_manager, 'force_release_key'):
            self.input_manager.force_release_key(key)
        else:
            # Fallback: release normal
            keyboard.release(key)

    def _execute_stop_continuous_clicking(self, action, index):
        """Parar cliques contínuos"""
        _safe_print(f"   #{index}: stop_continuous_clicking()")

        if self.input_manager and hasattr(self.input_manager, 'stop_continuous_clicking'):
            self.input_manager.stop_continuous_clicking()
        elif self.fishing_engine and hasattr(self.fishing_engine, 'stop_continuous_clicking'):
            self.fishing_engine.stop_continuous_clicking()

    def _execute_stop_camera_movement(self, action, index):
        """Parar movimentos de câmera (A/D)"""
        _safe_print(f"   #{index}: stop_camera_movement()")

        if self.input_manager and hasattr(self.input_manager, 'stop_camera_movement'):
            self.input_manager.stop_camera_movement()
        elif self.fishing_engine and hasattr(self.fishing_engine, 'stop_camera_movement'):
            self.fishing_engine.stop_camera_movement()

    def _execute_stop_all_actions(self, action, index):
        """Parar todas as ações"""
        _safe_print(f"   #{index}: stop_all_actions()")

        self._execute_stop_continuous_clicking(action, index)
        self._execute_stop_camera_movement(action, index)

    def _execute_template_detect(self, action, index) -> bool:
        """
        Executar detecção de template e salvar resultado

        Returns:
            True se detectado, False caso contrário
        """
        name = action.get("name")
        confidence = action.get("confidence", 0.8)

        if not name:
            _safe_print(f"⚠️ Ação #{index}: Template_detect sem nome")
            return False

        if not self.template_engine:
            _safe_print(f"⚠️ TemplateEngine não disponível")
            return False

        _safe_print(f"   #{index}: template_detect({name})")

        result = self.template_engine.detect_template(name, confidence)

        if result and result.found:
            self.last_detected = result.location
            _safe_print(f"      ✅ Detectado em ({result.location[0]}, {result.location[1]})")
            return True
        else:
            _safe_print(f"      ❌ Não detectado")
            return False

    def _execute_click_detected(self, action, index):
        """Clicar na última posição detectada"""
        if not self.last_detected:
            _safe_print(f"⚠️ Ação #{index}: Click_detected sem detecção anterior")
            return

        x, y = self.last_detected
        repeat = action.get("repeat", 1)
        interval = action.get("interval", 0.1)

        action_desc = f"click_detected({x}, {y})"
        if repeat > 1:
            action_desc += f" × {repeat}"

        _safe_print(f"   #{index}: {action_desc}")

        for _ in range(repeat):
            if self.input_manager:
                self.input_manager.click(x, y)
            else:
                pyautogui.click(x, y)

            if _ < repeat - 1:
                time.sleep(interval)


# ═══════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Exemplo de sequência recebida do servidor
    feeding_sequence = [
        {"type": "key", "key": "esc"},
        {"type": "wait", "duration": 1.5},
        {"type": "click", "x": 1306, "y": 858},
        {"type": "wait", "duration": 0.8},
        {"type": "click", "x": 1083, "y": 373, "repeat": 5, "interval": 0.3},
        {"type": "wait", "duration": 0.5},
        {"type": "key", "key": "esc"}
    ]

    # Criar executor
    executor = ActionExecutor()

    # Executar sequência
    _safe_print("\n🎮 Teste do ActionExecutor")
    _safe_print("="*60)
    success = executor.execute_sequence(feeding_sequence)

    if success:
        _safe_print("\n✅ Teste concluído com sucesso!")
    else:
        _safe_print("\n❌ Teste falhou!")

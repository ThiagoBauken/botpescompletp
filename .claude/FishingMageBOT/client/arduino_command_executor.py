"""
Arduino Command Executor - Executor genérico de comandos do servidor

Este módulo TRADUZ comandos JSON do servidor para protocolo Arduino e executa.

ARQUITETURA:
1. SERVIDOR decide O QUE fazer (limpeza, alimentação, manutenção)
2. SERVIDOR envia comando específico JSON
3. CLIENTE traduz JSON → protocolo Arduino
4. ARDUINO executa fisicamente (HID)

IMPORTANTE:
- Cliente NÃO sabe o que está fazendo
- Cliente apenas EXECUTA comandos cegamente
- Toda lógica está no SERVIDOR

Comandos suportados:
- move: Mover mouse
- click: Clicar
- key_press: Pressionar tecla
- drag: Arrastar item
- sequence: Sequência de ações
- wait: Aguardar tempo
"""

import time
import re
from typing import Optional, Dict, List, Any


def _safe_print(text):
    """Print seguro para Unicode/emoji"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class ArduinoCommandExecutor:
    """
    Executor genérico de comandos do servidor via Arduino

    Cliente NÃO sabe o significado dos comandos!
    Apenas traduz JSON → Arduino e executa.
    """

    def __init__(self, arduino_input_manager):
        """
        Inicializar executor

        Args:
            arduino_input_manager: Instância do ArduinoInputManager
        """
        self.arduino = arduino_input_manager
        self.execution_log = []  # Log de execuções para debug

    def execute_command(self, command: Dict[str, Any]) -> bool:
        """
        Executar comando do servidor

        Args:
            command: Comando JSON do servidor

        Formato:
        {
            "cmd": "move" | "click" | "key_press" | "drag" | "sequence" | "wait",
            ...parâmetros específicos...
        }

        Returns:
            True se executado com sucesso, False caso contrário
        """
        try:
            cmd_type = command.get("cmd")

            _safe_print(f"")
            _safe_print(f"{'='*70}")
            _safe_print(f"🤖 [EXECUTOR] Recebeu comando do servidor: {cmd_type}")
            _safe_print(f"{'='*70}")

            if cmd_type == "move":
                return self._execute_move(command)
            elif cmd_type == "click":
                return self._execute_click(command)
            elif cmd_type == "key_press":
                return self._execute_key_press(command)
            elif cmd_type == "drag":
                return self._execute_drag(command)
            elif cmd_type == "sequence":
                return self._execute_sequence(command)
            elif cmd_type == "wait":
                return self._execute_wait(command)
            else:
                _safe_print(f"❌ [EXECUTOR] Comando desconhecido: {cmd_type}")
                return False

        except Exception as e:
            _safe_print(f"❌ [EXECUTOR] Erro ao executar comando: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_move(self, command: Dict[str, Any]) -> bool:
        """
        Executar movimento de mouse

        Formato:
        {
            "cmd": "move",
            "x": 1083,
            "y": 373
        }
        """
        x = command.get("x")
        y = command.get("y")

        if x is None or y is None:
            _safe_print(f"❌ [EXECUTOR] Movimento sem coordenadas: {command}")
            return False

        _safe_print(f"🖱️  [EXECUTOR] Movendo mouse para ({x}, {y})...")
        success = self.arduino.move_to(x, y)

        if success:
            _safe_print(f"✅ [EXECUTOR] Mouse movido com sucesso!")
        else:
            _safe_print(f"❌ [EXECUTOR] Falha ao mover mouse!")

        return success

    def _execute_click(self, command: Dict[str, Any]) -> bool:
        """
        Executar clique(s) de mouse

        Formato:
        {
            "cmd": "click",
            "x": 1083,  // opcional - se fornecido, move antes
            "y": 373,   // opcional
            "button": "left" | "right",
            "repeat": 5,  // opcional - quantas vezes clicar
            "interval": 0.3  // opcional - intervalo entre cliques
        }
        """
        x = command.get("x")
        y = command.get("y")
        button = command.get("button", "left")
        repeat = command.get("repeat", 1)
        interval = command.get("interval", 0.3)

        _safe_print(f"🖱️  [EXECUTOR] Clique:")
        _safe_print(f"   Posição: {(x, y) if x and y else 'atual'}")
        _safe_print(f"   Botão: {button}")
        _safe_print(f"   Repetições: {repeat}")
        _safe_print(f"   Intervalo: {interval}s")

        # Mover se coordenadas fornecidas
        if x is not None and y is not None:
            _safe_print(f"   ➡️  Movendo para ({x}, {y})...")
            if not self.arduino.move_to(x, y):
                _safe_print(f"   ❌ Falha ao mover!")
                return False
            time.sleep(0.1)

        # Executar cliques
        _safe_print(f"   🖱️  Executando {repeat} clique(s)...")
        for i in range(repeat):
            _safe_print(f"      Clique {i+1}/{repeat}...")

            if button == "left":
                success = self.arduino.click_left()
            elif button == "right":
                success = self.arduino.click_right()
            else:
                _safe_print(f"      ❌ Botão inválido: {button}")
                return False

            if not success:
                _safe_print(f"      ❌ Falha no clique {i+1}!")
                return False

            # Intervalo entre cliques (exceto no último)
            if i < repeat - 1:
                time.sleep(interval)

        _safe_print(f"✅ [EXECUTOR] {repeat} clique(s) executado(s)!")
        return True

    def _execute_key_press(self, command: Dict[str, Any]) -> bool:
        """
        Executar tecla pressionada

        Formato:
        {
            "cmd": "key_press",
            "key": "e",
            "duration": 0.1  // opcional
        }
        """
        key = command.get("key")
        duration = command.get("duration", 0.05)

        if not key:
            _safe_print(f"❌ [EXECUTOR] Tecla não especificada!")
            return False

        _safe_print(f"⌨️  [EXECUTOR] Pressionando tecla '{key}' por {duration}s...")
        success = self.arduino.press_key(key, duration)

        if success:
            _safe_print(f"✅ [EXECUTOR] Tecla pressionada!")
        else:
            _safe_print(f"❌ [EXECUTOR] Falha ao pressionar tecla!")

        return success

    def _execute_drag(self, command: Dict[str, Any]) -> bool:
        """
        Executar arrasto de item

        Formato:
        {
            "cmd": "drag",
            "start_x": 709,
            "start_y": 700,
            "end_x": 1400,
            "end_y": 500,
            "duration": 1.0  // opcional
        }
        """
        start_x = command.get("start_x")
        start_y = command.get("start_y")
        end_x = command.get("end_x")
        end_y = command.get("end_y")
        duration = command.get("duration", 1.0)

        if None in [start_x, start_y, end_x, end_y]:
            _safe_print(f"❌ [EXECUTOR] Drag sem coordenadas completas: {command}")
            return False

        _safe_print(f"🖱️  [EXECUTOR] Arrastando:")
        _safe_print(f"   De: ({start_x}, {start_y})")
        _safe_print(f"   Para: ({end_x}, {end_y})")
        _safe_print(f"   Duração: {duration}s")

        success = self.arduino.drag(start_x, start_y, end_x, end_y, duration)

        if success:
            _safe_print(f"✅ [EXECUTOR] Arrasto concluído!")
        else:
            _safe_print(f"❌ [EXECUTOR] Falha no arrasto!")

        return success

    def _execute_sequence(self, command: Dict[str, Any]) -> bool:
        """
        Executar sequência de ações

        Formato:
        {
            "cmd": "sequence",
            "actions": [
                {"cmd": "move", "x": 1083, "y": 373},
                {"cmd": "click", "button": "left", "repeat": 5, "interval": 0.3},
                {"cmd": "wait", "duration": 1.0},
                {"cmd": "key_press", "key": "e"}
            ]
        }
        """
        actions = command.get("actions", [])

        if not actions:
            _safe_print(f"❌ [EXECUTOR] Sequência vazia!")
            return False

        _safe_print(f"📋 [EXECUTOR] Executando sequência de {len(actions)} ações...")

        for i, action in enumerate(actions):
            _safe_print(f"")
            _safe_print(f"   ▶️  Ação {i+1}/{len(actions)}: {action.get('cmd')}")

            success = self.execute_command(action)

            if not success:
                _safe_print(f"   ❌ Falha na ação {i+1}! Abortando sequência.")
                return False

            _safe_print(f"   ✅ Ação {i+1} concluída!")

        _safe_print(f"")
        _safe_print(f"✅ [EXECUTOR] Sequência completa executada com sucesso!")
        return True

    def _execute_wait(self, command: Dict[str, Any]) -> bool:
        """
        Executar espera (delay)

        Formato:
        {
            "cmd": "wait",
            "duration": 1.5
        }
        """
        duration = command.get("duration", 0)

        if duration <= 0:
            _safe_print(f"⚠️  [EXECUTOR] Wait com duração inválida: {duration}")
            return True  # Não é erro crítico

        _safe_print(f"⏳ [EXECUTOR] Aguardando {duration}s...")
        time.sleep(duration)
        _safe_print(f"✅ [EXECUTOR] Espera concluída!")

        return True

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Obter log de execuções"""
        return self.execution_log.copy()

    def clear_execution_log(self):
        """Limpar log de execuções"""
        self.execution_log.clear()


# ===== TESTE =====

def test_executor():
    """Testar executor com comandos simulados"""
    _safe_print("="*70)
    _safe_print("🧪 TESTE DO EXECUTOR DE COMANDOS")
    _safe_print("="*70)

    # Mock do ArduinoInputManager para teste
    class MockArduino:
        def move_to(self, x, y):
            _safe_print(f"   [MOCK] move_to({x}, {y})")
            return True

        def click_left(self):
            _safe_print(f"   [MOCK] click_left()")
            return True

        def click_right(self):
            _safe_print(f"   [MOCK] click_right()")
            return True

        def press_key(self, key, duration):
            _safe_print(f"   [MOCK] press_key({key}, {duration})")
            return True

        def drag(self, sx, sy, ex, ey, duration):
            _safe_print(f"   [MOCK] drag({sx}, {sy}, {ex}, {ey}, {duration})")
            return True

    executor = ArduinoCommandExecutor(MockArduino())

    # Teste 1: Move
    _safe_print("\n📍 Teste 1: MOVE")
    executor.execute_command({"cmd": "move", "x": 1083, "y": 373})

    # Teste 2: Click
    _safe_print("\n🖱️  Teste 2: CLICK")
    executor.execute_command({
        "cmd": "click",
        "x": 1083,
        "y": 373,
        "button": "left",
        "repeat": 5,
        "interval": 0.3
    })

    # Teste 3: Sequence
    _safe_print("\n📋 Teste 3: SEQUENCE")
    executor.execute_command({
        "cmd": "sequence",
        "actions": [
            {"cmd": "move", "x": 1306, "y": 858},
            {"cmd": "click", "button": "left"},
            {"cmd": "wait", "duration": 0.5},
            {"cmd": "move", "x": 1083, "y": 373},
            {"cmd": "click", "button": "left", "repeat": 3, "interval": 0.3}
        ]
    })

    _safe_print("\n✅ TESTES CONCLUÍDOS!")


if __name__ == "__main__":
    test_executor()

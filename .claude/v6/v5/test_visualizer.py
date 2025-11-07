#!/usr/bin/env python3
"""
Teste do GameWindowVisualizer
"""

def test_dependencies():
    """Testar dependências necessárias"""
    print("🔧 Testando dependências...")
    
    # Testar PIL/Pillow
    try:
        from PIL import Image, ImageTk
        print("✅ PIL/Pillow disponível")
    except ImportError:
        print("❌ PIL/Pillow não encontrado")
        print("   Execute: pip install Pillow")
        return False
    
    # Testar win32gui
    try:
        import win32gui
        print("✅ win32gui disponível")
    except ImportError:
        print("❌ win32gui não encontrado")
        print("   Execute: pip install pywin32")
        return False
    
    # Testar mss
    try:
        import mss
        print("✅ mss disponível")
    except ImportError:
        print("❌ mss não encontrado")
        print("   Execute: pip install mss")
        return False
    
    # Testar cv2
    try:
        import cv2
        print("✅ cv2 disponível")
    except ImportError:
        print("❌ cv2 não encontrado")
        print("   Execute: pip install opencv-python")
        return False
    
    return True

def test_window_detection():
    """Testar detecção de janelas"""
    try:
        import win32gui
        
        print("\n🔍 Testando detecção de janelas...")
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if len(title) > 3:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        print(f"✅ Encontradas {len(windows)} janelas")
        
        # Procurar por Rust especificamente
        rust_windows = [w for w in windows if any(x in w[1].lower() for x in ['rust', 'facepunch'])]
        if rust_windows:
            print(f"🎮 Encontradas {len(rust_windows)} janelas do Rust:")
            for hwnd, title in rust_windows:
                print(f"   - {title}")
        else:
            print("⚠️ Nenhuma janela do Rust encontrada")
            print("   Janelas disponíveis (primeiras 10):")
            for i, (hwnd, title) in enumerate(windows[:10]):
                print(f"   - {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na detecção de janelas: {e}")
        return False

def test_visualizer():
    """Testar GameWindowVisualizer"""
    try:
        print("\n🎮 Testando GameWindowVisualizer...")
        
        from core.game_window_visualizer import GameWindowVisualizer
        from core.template_engine import TemplateEngine
        from core.config_manager import ConfigManager
        
        # Criar componentes
        config = ConfigManager()
        template_engine = TemplateEngine(config_manager=config)
        
        # Criar visualizador
        visualizer = GameWindowVisualizer(
            template_engine=template_engine,
            config_manager=config
        )
        
        # Testar informações
        info = visualizer.get_window_info()
        print(f"✅ Janela detectada: {info['window_title']}")
        print(f"✅ Região de captura: {info['capture_region']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no GameWindowVisualizer: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Teste do GameWindowVisualizer\n")
    
    if not test_dependencies():
        print("❌ Dependências não estão disponíveis")
        exit(1)
    
    if not test_window_detection():
        print("❌ Falha na detecção de janelas")
        exit(1)
    
    if not test_visualizer():
        print("❌ Falha no GameWindowVisualizer")
        exit(1)
    
    print("\n✅ Todos os testes passaram!")
    print("🎮 O visualizador deve funcionar corretamente")
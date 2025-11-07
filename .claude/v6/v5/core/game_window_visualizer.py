#!/usr/bin/env python3
"""
🎮 GameWindowVisualizer - Visualizador da Janela do Jogo Rust
Ultimate Fishing Bot v4.0

Captura e exibe feed em tempo real da janela do jogo para debugging e monitoramento.
Baseado na lógica do botpesca.py mas otimizado para o v4.
"""

import cv2
import numpy as np
import mss
import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable, Tuple
import win32gui
import win32con
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class GameWindowVisualizer:
    """
    🎮 Visualizador da Janela do Jogo
    
    Funcionalidades:
    - Detectar automaticamente janela do Rust
    - Capturar região específica da janela
    - Exibir feed em tempo real
    - Overlay de detecções de template
    - Configuração de região de captura
    """
    
    def __init__(self, template_engine=None, config_manager=None):
        """Inicializar visualizador"""
        self.template_engine = template_engine
        self.config_manager = config_manager
        
        # Estado da janela do jogo
        self.game_window = None
        self.game_window_title = None
        self.window_rect = None
        
        # Configurações de captura
        self.capture_region = None
        self.capture_active = False
        self.capture_thread = None
        self.capture_fps = 10  # FPS do visualizador
        
        # Interface do visualizador
        self.viewer_window = None
        self.video_label = None
        self.status_label = None
        
        # Callbacks
        self.on_template_detected: Optional[Callable] = None
        
        # Buscar janela do jogo automaticamente
        self._find_game_window()
        
        _safe_print("🎮 GameWindowVisualizer inicializado")
    
    def _find_game_window(self):
        """Encontrar janela do Rust automaticamente"""
        try:
            _safe_print("🔍 Procurando janela do jogo Rust...")
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    
                    # Palavras-chave para identificar Rust (incluir mais variações)
                    rust_keywords = [
                        'Rust', 'rust', 'RUST',
                        'Facepunch', 'facepunch',
                        'Unity', 'unity',  # Rust usa Unity
                        'RustClient.exe', 'RustClient'
                    ]
                    
                    # Verificar por palavras-chave primeiro
                    for keyword in rust_keywords:
                        if keyword in window_title and len(window_title) > 3:
                            windows.append((hwnd, window_title))
                            break
                    else:
                        # Se não encontrou por palavra-chave, adicionar janelas que podem ser jogos
                        if (len(window_title) > 5 and 
                            not any(x in window_title.lower() for x in ['explorer', 'desktop', 'taskbar', 'start menu', 'microsoft', 'windows']) and
                            win32gui.GetClassName(hwnd) not in ['Shell_TrayWnd', 'DV2ControlHost']):
                            windows.append((hwnd, window_title))
                
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # Se encontrou janelas, usar a primeira que tem palavra-chave do Rust
                # ou a primeira da lista se nenhuma for específica do Rust
                rust_windows = [(hwnd, title) for hwnd, title in windows 
                              if any(keyword in title for keyword in ['Rust', 'rust', 'RUST', 'Facepunch'])]
                
                if rust_windows:
                    self.game_window, self.game_window_title = rust_windows[0]
                    _safe_print(f"✅ Janela do Rust detectada: '{self.game_window_title}'")
                else:
                    self.game_window, self.game_window_title = windows[0]
                    _safe_print(f"⚠️ Usando primeira janela encontrada: '{self.game_window_title}'")
                
                # Obter dimensões da janela
                self.window_rect = win32gui.GetWindowRect(self.game_window)
                
                _safe_print(f"✅ Janela do jogo encontrada: '{self.game_window_title}'")
                _safe_print(f"📐 Dimensões: {self.window_rect}")
                
                # Configurar região de captura padrão (janela inteira)
                self._setup_default_capture_region()
                
                return True
            else:
                _safe_print("❌ Nenhuma janela do Rust encontrada")
                return False
                
        except Exception as e:
            _safe_print(f"❌ Erro ao procurar janela do jogo: {e}")
            return False
    
    def _setup_default_capture_region(self):
        """Configurar região de captura padrão"""
        if self.window_rect:
            left, top, right, bottom = self.window_rect
            
            # Região padrão: janela inteira menos bordas
            border_offset = 10
            self.capture_region = {
                'left': left + border_offset,
                'top': top + 30,  # Compensar barra de título
                'width': (right - left) - (border_offset * 2),
                'height': (bottom - top) - 40  # Compensar barra de título e borda
            }
            
            _safe_print(f"📐 Região de captura configurada: {self.capture_region}")
    
    def refresh_game_window(self):
        """Atualizar detecção da janela do jogo"""
        return self._find_game_window()
    
    def set_capture_region(self, left: int, top: int, width: int, height: int):
        """Definir região específica de captura"""
        self.capture_region = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        _safe_print(f"📐 Nova região de captura: {self.capture_region}")
    
    def start_capture(self):
        """Iniciar captura da janela do jogo"""
        try:
            if not self.game_window:
                _safe_print("❌ Nenhuma janela do jogo detectada")
                return False
            
            if self.capture_active:
                _safe_print("⚠️ Captura já está ativa")
                return False
            
            self.capture_active = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            _safe_print("🎥 Captura iniciada")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar captura: {e}")
            return False
    
    def stop_capture(self):
        """Parar captura da janela do jogo"""
        try:
            if not self.capture_active:
                _safe_print("⚠️ Captura não está ativa")
                return False
            
            self.capture_active = False
            
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2)
            
            _safe_print("🛑 Captura parada")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao parar captura: {e}")
            return False
    
    def _capture_loop(self):
        """Loop principal de captura"""
        try:
            with mss.mss() as sct:
                frame_time = 1.0 / self.capture_fps
                
                while self.capture_active:
                    start_time = time.time()
                    
                    try:
                        # Capturar frame da região
                        if self.capture_region:
                            screenshot = sct.grab(self.capture_region)
                            frame = np.array(screenshot)
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                            
                            # Processar frame (overlay de templates se disponível)
                            processed_frame = self._process_frame(frame)
                            
                            # Atualizar interface se existir
                            if self.viewer_window and self.video_label:
                                self._update_video_display(processed_frame)
                        
                        # Controlar FPS
                        elapsed = time.time() - start_time
                        sleep_time = max(0, frame_time - elapsed)
                        time.sleep(sleep_time)
                        
                    except Exception as frame_error:
                        _safe_print(f"❌ Erro no frame: {frame_error}")
                        time.sleep(0.1)
                        continue
            
        except Exception as e:
            _safe_print(f"❌ Erro no loop de captura: {e}")
        finally:
            self.capture_active = False
    
    def _process_frame(self, frame):
        """Processar frame com overlay de detecções"""
        try:
            processed_frame = frame.copy()
            
            # Se template engine disponível, detectar templates
            if self.template_engine:
                # Templates importantes para overlay
                important_templates = ['catch', 'VARANOBAUCI', 'enbausi', 'varaquebrada']
                
                for template_name in important_templates:
                    # Verificar se template existe no cache
                    if hasattr(self.template_engine, 'template_cache') and template_name in self.template_engine.template_cache:
                        result = self.template_engine.detect_template(
                            template_name, 
                            screenshot=frame
                        )
                        
                        if result and result.found:
                            # Desenhar retângulo ao redor da detecção
                            x, y = result.location
                            w, h = result.size
                            
                            # Cor baseada no template
                            color_map = {
                                'catch': (0, 255, 0),        # Verde para peixe
                                'VARANOBAUCI': (0, 255, 255), # Amarelo para vara com isca
                                'enbausi': (255, 255, 0),     # Ciano para vara sem isca
                                'varaquebrada': (0, 0, 255)   # Vermelho para vara quebrada
                            }
                            
                            color = color_map.get(template_name, (255, 255, 255))
                            
                            # Desenhar retângulo
                            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), color, 2)
                            
                            # Desenhar label
                            label = f"{template_name}: {result.confidence:.2f}"
                            cv2.putText(processed_frame, label, (x, y - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            
                            # Callback se disponível
                            if self.on_template_detected:
                                self.on_template_detected(template_name, result)
            
            # Adicionar informações de status
            self._add_status_overlay(processed_frame)
            
            return processed_frame
            
        except Exception as e:
            _safe_print(f"❌ Erro ao processar frame: {e}")
            return frame
    
    def _add_status_overlay(self, frame):
        """Adicionar overlay de status no frame"""
        try:
            # Informações de status
            status_text = [
                f"Janela: {self.game_window_title or 'N/A'}",
                f"Regiao: {self.capture_region['width']}x{self.capture_region['height']}" if self.capture_region else "N/A",
                f"FPS: {self.capture_fps}",
                f"Templates: {len(self.template_engine.template_cache) if self.template_engine and hasattr(self.template_engine, 'template_cache') else 0}"
            ]
            
            # Desenhar fundo semi-transparente
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Desenhar texto
            for i, text in enumerate(status_text):
                y_pos = 30 + (i * 25)
                cv2.putText(frame, text, (20, y_pos), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                          
        except Exception as e:
            _safe_print(f"❌ Erro ao adicionar status overlay: {e}")
    
    def _update_video_display(self, frame):
        """Atualizar display de vídeo na interface"""
        try:
            if not self.video_label:
                return
            
            # Redimensionar frame para display
            display_height = 480
            aspect_ratio = frame.shape[1] / frame.shape[0]
            display_width = int(display_height * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (display_width, display_height))
            
            # Converter para formato do tkinter
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Converter para PIL/tkinter
            try:
                from PIL import Image, ImageTk
                pil_image = Image.fromarray(rgb_frame)
                tk_image = ImageTk.PhotoImage(image=pil_image)
            except ImportError:
                _safe_print("❌ PIL não encontrado. Execute: pip install Pillow")
                return
            
            # Atualizar label (thread-safe)
            def update_label():
                if self.video_label:
                    self.video_label.configure(image=tk_image)
                    self.video_label.image = tk_image  # Manter referência
            
            if self.viewer_window:
                self.viewer_window.after(0, update_label)
                
        except Exception as e:
            _safe_print(f"❌ Erro ao atualizar display: {e}")
    
    def show_viewer_window(self):
        """Exibir janela do visualizador"""
        try:
            if self.viewer_window:
                self.viewer_window.lift()
                return
            
            # Criar janela
            self.viewer_window = tk.Toplevel()
            self.viewer_window.title("🎮 Rust Game Visualizer - Ultimate Fishing Bot v4")
            self.viewer_window.geometry("800x600")
            self.viewer_window.configure(bg='#1a1a1a')
            
            # Frame principal
            main_frame = tk.Frame(self.viewer_window, bg='#1a1a1a')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Controles superiores
            control_frame = tk.Frame(main_frame, bg='#1a1a1a')
            control_frame.pack(fill='x', pady=(0, 10))
            
            # Botões de controle
            tk.Button(control_frame, text="🔍 Encontrar Janela", 
                     command=self.refresh_game_window, bg='#333333', fg='white').pack(side='left', padx=5)
            
            tk.Button(control_frame, text="📋 Selecionar Janela", 
                     command=self.show_window_selector, bg='#333333', fg='white').pack(side='left', padx=5)
            
            tk.Button(control_frame, text="▶️ Iniciar Captura", 
                     command=self.start_capture, bg='#2d7d2d', fg='white').pack(side='left', padx=5)
            
            tk.Button(control_frame, text="⏹️ Parar Captura", 
                     command=self.stop_capture, bg='#7d2d2d', fg='white').pack(side='left', padx=5)
            
            # Status
            self.status_label = tk.Label(control_frame, 
                                       text=f"Janela: {self.game_window_title or 'Não encontrada'}", 
                                       bg='#1a1a1a', fg='white')
            self.status_label.pack(side='right', padx=10)
            
            # Área de vídeo
            video_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='sunken', bd=2)
            video_frame.pack(fill='both', expand=True)
            
            self.video_label = tk.Label(video_frame, 
                                      text="🎮 Game Window Preview\nPressione 'Iniciar Captura' para começar", 
                                      bg='#2d2d2d', fg='white', font=('Arial', 12))
            self.video_label.pack(fill='both', expand=True)
            
            # Protocolo de fechamento
            def on_closing():
                self.stop_capture()
                self.viewer_window.destroy()
                self.viewer_window = None
                self.video_label = None
                self.status_label = None
            
            self.viewer_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            _safe_print("🎮 Janela do visualizador criada")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao criar janela do visualizador: {e}")
    
    def get_current_frame(self):
        """Obter frame atual da captura"""
        try:
            if not self.capture_region:
                return None
            
            with mss.mss() as sct:
                screenshot = sct.grab(self.capture_region)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
                
        except Exception as e:
            _safe_print(f"❌ Erro ao obter frame atual: {e}")
            return None
    
    def set_template_detection_callback(self, callback: Callable):
        """Definir callback para detecção de templates"""
        self.on_template_detected = callback
        _safe_print("✅ Callback de detecção configurado")
    
    def show_window_selector(self):
        """Mostrar seletor de janela"""
        try:
            # Obter todas as janelas disponíveis
            def enum_all_windows(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and len(win32gui.GetWindowText(hwnd)) > 3:
                    windows.append((hwnd, win32gui.GetWindowText(hwnd)))
                return True
            
            all_windows = []
            win32gui.EnumWindows(enum_all_windows, all_windows)
            
            if not all_windows:
                _safe_print("❌ Nenhuma janela encontrada")
                return
            
            # Criar janela de seleção
            selector = tk.Toplevel(self.viewer_window if self.viewer_window else None)
            selector.title("📋 Selecionar Janela do Jogo")
            selector.geometry("600x400")
            selector.configure(bg='#1a1a1a')
            
            # Lista de janelas
            frame = tk.Frame(selector, bg='#1a1a1a')
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="Selecione a janela do jogo:", 
                    bg='#1a1a1a', fg='white', font=('Arial', 12)).pack(pady=5)
            
            # Listbox com scrollbar
            list_frame = tk.Frame(frame, bg='#1a1a1a')
            list_frame.pack(fill='both', expand=True, pady=5)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side='right', fill='y')
            
            listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                               bg='#2d2d2d', fg='white', font=('Arial', 10))
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Preencher lista
            window_map = {}
            for i, (hwnd, title) in enumerate(all_windows):
                display_text = f"{title}"
                listbox.insert(i, display_text)
                window_map[i] = (hwnd, title)
            
            def select_window():
                selection = listbox.curselection()
                if selection:
                    hwnd, title = window_map[selection[0]]
                    self.game_window = hwnd
                    self.game_window_title = title
                    self.window_rect = win32gui.GetWindowRect(hwnd)
                    self._setup_default_capture_region()
                    
                    _safe_print(f"✅ Janela selecionada: '{title}'")
                    
                    # Atualizar status se janela do viewer estiver aberta
                    if self.status_label:
                        self.status_label.config(text=f"Janela: {title}")
                    
                    selector.destroy()
            
            # Botões
            button_frame = tk.Frame(frame, bg='#1a1a1a')
            button_frame.pack(fill='x', pady=5)
            
            tk.Button(button_frame, text="Selecionar", command=select_window,
                     bg='#2d7d2d', fg='white').pack(side='left', padx=5)
            
            tk.Button(button_frame, text="Cancelar", command=selector.destroy,
                     bg='#7d2d2d', fg='white').pack(side='left', padx=5)
            
        except Exception as e:
            _safe_print(f"❌ Erro ao mostrar seletor de janela: {e}")

    def get_window_info(self):
        """Obter informações da janela do jogo"""
        return {
            'window_title': self.game_window_title,
            'window_rect': self.window_rect,
            'capture_region': self.capture_region,
            'capture_active': self.capture_active
        }
# 🚀 PLANO COMPLETO DE REESTRUTURAÇÃO - ULTIMATE FISHING BOT v4.0

## 📋 VISÃO GERAL

Transformar o bot monolítico atual (27,127 linhas caóticas) em sistema distribuído modular, limpo e escalável com:

1. **📱 CLIENTE PC** - UI + Detecção (Python)
2. **🖥️ SERVIDOR** - Lógica + IA (Python/FastAPI) 
3. **🤖 ARDUINO** - Execução Física (C++)

---

## 🏗️ ARQUITETURA DISTRIBUÍDA FINAL

```
┌─────────────────────────────────────────────────────────────────┐
│                        SERVIDOR CENTRAL                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  LOGIC ENGINE   │  │   USER MANAGER  │  │   ANALYTICS     │  │
│  │ • Fishing Logic │  │ • Autenticação  │  │ • Statistics    │  │
│  │ • Decision AI   │  │ • Multi-tenant  │  │ • Monitoring    │  │
│  │ • Anti-Detection│  │ • Licensing     │  │ • Optimization  │  │
│  │ • Coordination  │  │ • Configurations│  │ • Logs          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
          ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
          │ CLIENTE 1   │ │ CLIENTE 2   │ │ CLIENTE N   │
          │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
          │ │   PC    │◄┼─┼─│   PC    │◄┼─┼─│   PC    │ │
          │ │ UI +    │ │ │ │ UI +    │ │ │ │ UI +    │ │
          │ │ Detection│ │ │ │ Detection│ │ │ │ Detection│ │
          │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
          │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
          │ │ ARDUINO │ │ │ │ ARDUINO │ │ │ │ ARDUINO │ │
          │ │ Physical│ │ │ │ Physical│ │ │ │ Physical│ │
          │ │ Control │ │ │ │ Control │ │ │ │ Control │ │
          │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
          └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 📁 ESTRUTURA DE ARQUIVOS COMPLETA

### 🖥️ COMPONENTE 1: CLIENTE PC

```
📁 fishing_bot_client/
├── 📁 core/
│   ├── __init__.py
│   ├── client_manager.py       # Gerenciador principal do cliente
│   ├── template_engine.py      # Engine unificado de template matching
│   ├── screen_capture.py       # Captura otimizada MSS
│   ├── detection_processor.py  # Processamento de detecções
│   └── cache_manager.py        # Cache local de templates/results
├── 📁 ui/
│   ├── __init__.py
│   ├── main_window.py         # Janela principal Tkinter
│   ├── control_panel.py       # Painel de controle
│   ├── config_panel.py        # Painel de configurações
│   ├── confidence_panel.py    # Configuração de confiança
│   ├── status_panel.py        # Status em tempo real
│   └── widgets/
│       ├── __init__.py
│       ├── custom_widgets.py  # Widgets customizados
│       └── charts.py          # Gráficos de performance
├── 📁 communication/
│   ├── __init__.py
│   ├── websocket_client.py    # Cliente WebSocket
│   ├── arduino_serial.py      # Comunicação Serial Arduino
│   ├── protocol.py            # Protocolo de comunicação
│   └── heartbeat.py           # Keep-alive
├── 📁 templates/              # 40 templates essenciais
│   ├── detection/
│   │   ├── catch.png          # CRÍTICO
│   │   ├── VARANOBAUCI.png    # CRÍTICO
│   │   ├── enbausi.png        # CRÍTICO
│   │   ├── varaquebrada.png   # CRÍTICO
│   │   ├── inventory.png      # CRÍTICO
│   │   └── loot.png           # CRÍTICO
│   ├── rods/
│   │   ├── comiscavara.png
│   │   ├── semiscavara.png
│   │   ├── namaocomisca.png
│   │   └── namaosemisca.png
│   ├── baits/
│   │   ├── crocodilo.png      # Prioridade 1
│   │   ├── carneurso.png      # Prioridade 2
│   │   ├── wolfmeat.png       # Prioridade 3
│   │   ├── smalltrout.png     # Prioridade 4
│   │   ├── grub.png           # Prioridade 5
│   │   └── worm.png           # Prioridade 6
│   ├── fish/
│   │   ├── salmon.png
│   │   ├── sardine.png
│   │   ├── anchovy.png
│   │   ├── shark.png
│   │   └── yellowperch.png
│   └── food/
│       ├── eat.png
│       ├── salmonbox.png
│       └── grubbox.png
├── 📁 config/
│   ├── __init__.py
│   ├── config_manager.py      # Gerenciador de configurações
│   ├── default_config.py      # Configurações padrão
│   └── template_config.py     # Configurações de templates
├── 📁 utils/
│   ├── __init__.py
│   ├── logging_manager.py     # Sistema de logs
│   ├── hotkey_manager.py      # Sistema de hotkeys
│   ├── i18n_manager.py        # Sistema i18n (reutilizar existente)
│   ├── license_validator.py   # Validação de licença
│   └── performance_monitor.py # Monitor de performance
├── 📁 data/
│   ├── config.json           # Configuração principal
│   ├── template_confidence.json
│   ├── user_settings.json
│   └── logs/
├── main.py                   # Entry point
├── requirements.txt
└── README.md
```

### 🌐 COMPONENTE 2: SERVIDOR

```
📁 fishing_bot_server/
├── 📁 core/
│   ├── __init__.py
│   ├── server_manager.py      # Gerenciador principal do servidor
│   ├── fishing_engine.py      # Engine principal de pesca
│   ├── decision_engine.py     # Motor de decisões IA
│   ├── state_manager.py       # Gerenciamento de estado
│   ├── coordination_engine.py # Coordenação de operações
│   └── anti_detection.py      # Sistema anti-ban
├── 📁 logic/
│   ├── __init__.py
│   ├── fishing_logic.py       # Lógica principal de pesca
│   ├── rod_logic.py           # Lógica de gerenciamento de varas
│   ├── inventory_logic.py     # Lógica de inventário/baú
│   ├── feeding_logic.py       # Lógica de alimentação
│   ├── auto_clean_logic.py    # Lógica de limpeza automática
│   └── emergency_logic.py     # Lógica de emergência
├── 📁 ai/
│   ├── __init__.py
│   ├── pattern_recognition.py # Reconhecimento de padrões
│   ├── optimization_ai.py     # IA de otimização
│   ├── behavior_analysis.py   # Análise de comportamento
│   └── adaptive_learning.py   # Aprendizado adaptativo
├── 📁 communication/
│   ├── __init__.py
│   ├── websocket_server.py    # Servidor WebSocket
│   ├── client_handler.py      # Handler de clientes
│   ├── arduino_bridge.py      # Bridge para Arduino
│   ├── protocol_handler.py    # Handler de protocolo
│   └── session_manager.py     # Gerenciamento de sessões
├── 📁 database/
│   ├── __init__.py
│   ├── models.py             # Modelos SQLAlchemy
│   ├── database.py           # Configuração DB
│   ├── user_repository.py    # Repository de usuários
│   ├── session_repository.py # Repository de sessões
│   ├── analytics_repository.py # Repository de analytics
│   └── migrations/           # Migrações DB
├── 📁 auth/
│   ├── __init__.py
│   ├── auth_manager.py       # Gerenciamento de autenticação
│   ├── jwt_handler.py        # Handler JWT
│   ├── license_manager.py    # Gerenciamento de licenças
│   └── subscription_manager.py # Gerenciamento de assinaturas
├── 📁 api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py    # Rotas de autenticação
│   │   ├── user_routes.py    # Rotas de usuário
│   │   ├── session_routes.py # Rotas de sessão
│   │   └── analytics_routes.py # Rotas de analytics
│   ├── middleware.py         # Middlewares
│   └── dependencies.py       # Dependências FastAPI
├── 📁 analytics/
│   ├── __init__.py
│   ├── metrics_collector.py  # Coletor de métricas
│   ├── performance_analyzer.py # Analisador de performance
│   ├── user_analytics.py     # Analytics por usuário
│   └── global_analytics.py   # Analytics globais
├── 📁 utils/
│   ├── __init__.py
│   ├── logging.py            # Sistema de logs
│   ├── cache_manager.py      # Cache Redis
│   ├── config_loader.py      # Carregador de configurações
│   └── security.py           # Utilitários de segurança
├── 📁 config/
│   ├── __init__.py
│   ├── settings.py           # Configurações do servidor
│   ├── database_config.py    # Configuração de banco
│   └── redis_config.py       # Configuração Redis
├── main.py                   # Entry point FastAPI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 🤖 COMPONENTE 3: ARDUINO

```
📁 fishing_bot_arduino/
├── main/
│   ├── main.ino              # Programa principal
│   ├── config.h              # Configurações
│   ├── commands.h            # Definições de comandos
│   └── states.h              # Estados do sistema
├── modules/
│   ├── mouse_controller.h    # Controle do mouse
│   ├── mouse_controller.cpp
│   ├── keyboard_controller.h # Controle do teclado
│   ├── keyboard_controller.cpp
│   ├── macro_executor.h      # Executor de macros
│   ├── macro_executor.cpp
│   ├── serial_handler.h      # Handler de comunicação serial
│   ├── serial_handler.cpp
│   ├── safety_manager.h      # Gerenciador de segurança
│   └── safety_manager.cpp
├── macros/
│   ├── fishing_macros.h      # Macros de pesca
│   ├── fishing_macros.cpp
│   ├── inventory_macros.h    # Macros de inventário
│   ├── inventory_macros.cpp
│   ├── feeding_macros.h      # Macros de alimentação
│   └── feeding_macros.cpp
├── utils/
│   ├── utils.h               # Utilitários gerais
│   ├── utils.cpp
│   ├── timer.h               # Gerenciamento de timers
│   └── timer.cpp
├── tests/
│   ├── hardware_test.ino     # Teste de hardware
│   └── communication_test.ino # Teste de comunicação
├── circuit/
│   ├── schematic.png         # Esquemático
│   └── breadboard.png        # Layout breadboard
├── README.md
└── INSTALL.md
```

---

## 🔄 PROTOCOLOS DE COMUNICAÇÃO

### 📡 CLIENTE ↔ SERVIDOR (WebSocket JSON)

#### Cliente → Servidor (Detecções)
```json
{
  "type": "detection_data",
  "session_id": "user123_session_456",
  "client_id": "client_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "detections": [
    {
      "type": "fish_caught",
      "confidence": 0.95,
      "position": {"x": 960, "y": 540},
      "template": "catch.png",
      "timestamp": "2024-01-15T10:30:00.123Z"
    },
    {
      "type": "rod_broken",
      "confidence": 0.87,
      "position": {"x": 1092, "y": 1005},
      "template": "varaquebrada.png",
      "rod_slot": 5
    }
  ],
  "game_state": {
    "fishing_active": true,
    "current_rod": 5,
    "inventory_open": false,
    "chest_open": false
  }
}
```

#### Servidor → Cliente (Comandos)
```json
{
  "type": "arduino_command",
  "session_id": "user123_session_456",
  "command_id": "cmd_789",
  "timestamp": "2024-01-15T10:30:01Z",
  "action": {
    "type": "restart_fishing",
    "priority": "high",
    "delay": 2.0,
    "parameters": {}
  },
  "arduino_commands": [
    "RIGHT_CLICK_RELEASE",
    "DELAY_2000", 
    "RIGHT_CLICK_HOLD"
  ]
}
```

### 🔌 SERVIDOR ↔ ARDUINO (Serial)

#### Comandos do Servidor para Arduino
```
# Comandos básicos
START_FISHING\n
STOP_FISHING\n
EMERGENCY_STOP\n

# Comandos de interface
PRESS_TAB\n
PRESS_ESC\n
PRESS_KEY:E\n

# Comandos de mouse
CLICK_LEFT:X:Y\n
CLICK_RIGHT:X:Y\n
MOVE_MOUSE:X:Y\n

# Macros complexos
EXECUTE_CHEST_MACRO\n
EXECUTE_FEED_MACRO\n
EXECUTE_ROD_REPLACE:SLOT\n
EXECUTE_AUTO_CLEAN\n

# Controle de vara
SWITCH_ROD:1\n
SWITCH_ROD:2\n
...
SWITCH_ROD:6\n

# Alimentação
FEED_CHARACTER:SLOT1\n
FEED_CHARACTER:SLOT2\n
```

#### Respostas do Arduino para Servidor
```
# Status
ARDUINO_READY\n
ARDUINO_BUSY\n
ARDUINO_IDLE\n

# Confirmações
FISHING_STARTED\n
FISHING_STOPPED\n
COMMAND_EXECUTED:cmd_id\n
MACRO_COMPLETED:macro_name\n

# Emergência
EMERGENCY_ACTIVATED\n
TIMEOUT_DETECTED\n
HARDWARE_ERROR\n

# Heartbeat
HEARTBEAT:timestamp\n
```

---

## 🧩 MÓDULOS PRINCIPAIS

### 📱 CLIENTE PC - MÓDULOS CORE

#### 1. ClientManager (core/client_manager.py)
```python
class ClientManager:
    """Gerenciador principal do cliente"""
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.websocket_client = WebSocketClient()
        self.arduino_serial = ArduinoSerial()
        self.ui_manager = UIManager()
        
    async def start(self):
        """Iniciar cliente completo"""
        await self.connect_to_server()
        await self.connect_to_arduino()
        await self.start_detection_loop()
        
    async def detection_loop(self):
        """Loop principal de detecção"""
        while self.running:
            screenshot = self.capture_screen()
            detections = self.template_engine.detect_all(screenshot)
            await self.send_detections(detections)
            await self.process_server_commands()
```

#### 2. TemplateEngine (core/template_engine.py)
```python
class TemplateEngine:
    """Engine unificado de template matching"""
    def __init__(self):
        self.templates = self.load_templates()
        self.confidence_thresholds = self.load_confidence_config()
        
    def detect_all(self, screenshot):
        """Detectar todos os objetos críticos"""
        detections = []
        for template_name, template_data in self.templates.items():
            result = self.match_template(screenshot, template_data)
            if result.found:
                detections.append(result)
        return detections
        
    def match_template(self, screenshot, template_data):
        """Fazer matching de um template específico"""
        # Implementação OpenCV otimizada
        pass
```

### 🌐 SERVIDOR - MÓDULOS CORE

#### 1. FishingEngine (core/fishing_engine.py)
```python
class FishingEngine:
    """Engine principal de pesca - lógica consolidada"""
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.state_manager = StateManager()
        self.coordination_engine = CoordinationEngine()
        
    async def process_detections(self, session_id: str, detections: List[Detection]):
        """Processar detecções e tomar decisões"""
        # Atualizar estado
        state = self.state_manager.update_state(session_id, detections)
        
        # Decidir próxima ação
        action = await self.decision_engine.decide(state, detections)
        
        # Coordenar execução
        if action:
            await self.coordination_engine.execute_action(session_id, action)
```

#### 2. DecisionEngine (core/decision_engine.py)
```python
class DecisionEngine:
    """Motor de decisões IA"""
    def __init__(self):
        self.fishing_logic = FishingLogic()
        self.rod_logic = RodLogic()
        self.inventory_logic = InventoryLogic()
        self.feeding_logic = FeedingLogic()
        
    async def decide(self, state: GameState, detections: List[Detection]) -> Optional[Action]:
        """Decidir próxima ação baseada em IA"""
        # Priority 1: Emergências
        emergency_action = self.check_emergencies(detections)
        if emergency_action:
            return emergency_action
            
        # Priority 2: Pesca
        fishing_action = self.fishing_logic.analyze(state, detections)
        if fishing_action:
            return fishing_action
            
        # Priority 3: Manutenção
        maintenance_action = self.check_maintenance(state)
        return maintenance_action
```

### 🤖 ARDUINO - MÓDULOS CORE

#### 1. Programa Principal (main/main.ino)
```cpp
#include "modules/mouse_controller.h"
#include "modules/keyboard_controller.h"
#include "modules/macro_executor.h"
#include "modules/serial_handler.h"
#include "modules/safety_manager.h"

// Gerenciadores globais
MouseController mouseCtrl;
KeyboardController keyboardCtrl;
MacroExecutor macroExec;
SerialHandler serialHandler;
SafetyManager safetyMgr;

// Estados
bool fishing_active = false;
bool emergency_stop = false;
unsigned long last_command_time = 0;

void setup() {
    Serial.begin(9600);
    Mouse.begin();
    Keyboard.begin();
    
    safetyMgr.init();
    serialHandler.init();
    
    Serial.println("ARDUINO_READY");
}

void loop() {
    // Processar comandos
    serialHandler.processCommands();
    
    // Verificar segurança
    safetyMgr.checkSafety();
    
    // Atualizar estado
    updateState();
    
    delay(10);
}
```

#### 2. Mouse Controller (modules/mouse_controller.cpp)
```cpp
void MouseController::startFishing() {
    if (!emergency_stop) {
        Mouse.press(MOUSE_RIGHT);
        fishing_active = true;
        Serial.println("FISHING_STARTED");
    }
}

void MouseController::stopFishing() {
    Mouse.release(MOUSE_RIGHT);
    fishing_active = false;
    Serial.println("FISHING_STOPPED");
}

void MouseController::clickAt(int x, int y, int button) {
    // Implementar clique em posição específica
    // (Arduino Leonardo não suporta posição absoluta nativamente)
    // Usar movimento relativo baseado em calibração
}
```

---

## 🌍 SISTEMA DE INTERNACIONALIZAÇÃO (I18N)

### 📋 SUPORTE COMPLETO A 3 IDIOMAS

#### Idiomas Suportados:
- 🇧🇷 **Português (Brasil)** - pt_BR (padrão)
- 🇺🇸 **English** - en_US  
- 🇷🇺 **Русский** - ru_RU

### 📁 Estrutura I18N

```
📁 fishing_bot_client/locales/
├── pt_BR/
│   ├── ui.json              # Interface principal
│   ├── messages.json        # Mensagens do sistema
│   ├── errors.json          # Mensagens de erro
│   ├── tooltips.json        # Tooltips e ajuda
│   └── status.json          # Status e logs
├── en_US/
│   ├── ui.json
│   ├── messages.json
│   ├── errors.json
│   ├── tooltips.json
│   └── status.json
├── ru_RU/
│   ├── ui.json
│   ├── messages.json
│   ├── errors.json
│   ├── tooltips.json
│   └── status.json
└── i18n_manager.py          # Gerenciador de traduções
```

### 🔧 I18N Manager (utils/i18n_manager.py)

```python
import json
import locale
import os
from typing import Dict, Optional

class I18NManager:
    """Gerenciador completo de internacionalização"""
    
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
                if system_locale.startswith('pt_BR'):
                    return 'pt_BR'
                elif system_locale.startswith('en'):
                    return 'en_US'
                elif system_locale.startswith('ru'):
                    return 'ru_RU'
        except:
            pass
        return 'pt_BR'  # Padrão
        
    def load_all_translations(self):
        """Carregar todas as traduções"""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            self.translations[lang_code] = {}
            lang_dir = f"locales/{lang_code}"
            
            # Carregar cada arquivo de tradução
            for file_name in ['ui.json', 'messages.json', 'errors.json', 'tooltips.json', 'status.json']:
                file_path = os.path.join(lang_dir, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        category = file_name.replace('.json', '')
                        self.translations[lang_code][category] = json.load(f)
                        
    def set_language(self, language_code: str):
        """Definir idioma atual"""
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            
    def translate(self, key: str, category: str = 'ui', **kwargs) -> str:
        """Traduzir chave com suporte a parâmetros"""
        try:
            # Buscar na linguagem atual
            text = self.translations[self.current_language][category][key]
            
            # Aplicar parâmetros se fornecidos
            if kwargs:
                text = text.format(**kwargs)
                
            return text
            
        except (KeyError, IndexError):
            # Fallback para inglês
            try:
                text = self.translations['en_US'][category][key]
                if kwargs:
                    text = text.format(**kwargs)
                return text
            except:
                # Fallback final - retornar a chave
                return f"[{key}]"
                
    def get_available_languages(self) -> Dict[str, str]:
        """Obter lista de idiomas disponíveis"""
        return self.SUPPORTED_LANGUAGES.copy()

# Instância global
i18n = I18NManager()

# Função helper para uso rápido
def _(key: str, category: str = 'ui', **kwargs) -> str:
    """Função helper para tradução rápida"""
    return i18n.translate(key, category, **kwargs)
```

### 📝 Arquivos de Tradução

#### 🇧🇷 pt_BR/ui.json
```json
{
  "main_window": {
    "title": "Ultimate Fishing Bot v4.0",
    "tabs": {
      "control": "Controle",
      "config": "Configuração", 
      "confidence": "Confiança",
      "feeding": "Alimentação",
      "analytics": "Análises"
    },
    "buttons": {
      "start": "Iniciar Bot",
      "stop": "Parar Bot",
      "pause": "Pausar",
      "emergency": "EMERGÊNCIA",
      "connect": "Conectar Servidor",
      "disconnect": "Desconectar",
      "save_config": "Salvar Configuração",
      "load_config": "Carregar Configuração"
    }
  },
  "status": {
    "fishing_active": "Pescando Ativo",
    "bot_idle": "Bot Inativo",
    "connecting": "Conectando...",
    "connected": "Conectado",
    "disconnected": "Desconectado",
    "fish_caught": "Peixes Capturados: {count}",
    "session_time": "Tempo de Sessão: {time}",
    "current_rod": "Vara Atual: {rod}",
    "bait_count": "Iscas: {count}"
  },
  "config": {
    "detection_settings": "Configurações de Detecção",
    "template_confidence": "Confiança dos Templates",
    "coordinates": "Coordenadas",
    "bait_priority": "Prioridade de Iscas",
    "feeding_settings": "Configurações de Alimentação",
    "auto_clean": "Limpeza Automática",
    "language": "Idioma"
  }
}
```

#### 🇺🇸 en_US/ui.json
```json
{
  "main_window": {
    "title": "Ultimate Fishing Bot v4.0",
    "tabs": {
      "control": "Control",
      "config": "Configuration",
      "confidence": "Confidence", 
      "feeding": "Feeding",
      "analytics": "Analytics"
    },
    "buttons": {
      "start": "Start Bot",
      "stop": "Stop Bot", 
      "pause": "Pause",
      "emergency": "EMERGENCY",
      "connect": "Connect Server",
      "disconnect": "Disconnect",
      "save_config": "Save Configuration",
      "load_config": "Load Configuration"
    }
  },
  "status": {
    "fishing_active": "Fishing Active",
    "bot_idle": "Bot Idle",
    "connecting": "Connecting...",
    "connected": "Connected",
    "disconnected": "Disconnected", 
    "fish_caught": "Fish Caught: {count}",
    "session_time": "Session Time: {time}",
    "current_rod": "Current Rod: {rod}",
    "bait_count": "Baits: {count}"
  },
  "config": {
    "detection_settings": "Detection Settings",
    "template_confidence": "Template Confidence",
    "coordinates": "Coordinates",
    "bait_priority": "Bait Priority",
    "feeding_settings": "Feeding Settings", 
    "auto_clean": "Auto Clean",
    "language": "Language"
  }
}
```

#### 🇷🇺 ru_RU/ui.json
```json
{
  "main_window": {
    "title": "Ultimate Fishing Bot v4.0",
    "tabs": {
      "control": "Управление",
      "config": "Настройки",
      "confidence": "Точность",
      "feeding": "Питание", 
      "analytics": "Аналитика"
    },
    "buttons": {
      "start": "Запустить Бота",
      "stop": "Остановить Бота",
      "pause": "Пауза",
      "emergency": "АВАРИЙНАЯ ОСТАНОВКА",
      "connect": "Подключить Сервер",
      "disconnect": "Отключить",
      "save_config": "Сохранить Настройки",
      "load_config": "Загрузить Настройки"
    }
  },
  "status": {
    "fishing_active": "Рыбалка Активна",
    "bot_idle": "Бот Неактивен",
    "connecting": "Подключение...",
    "connected": "Подключено",
    "disconnected": "Отключено",
    "fish_caught": "Поймано Рыб: {count}",
    "session_time": "Время Сессии: {time}",
    "current_rod": "Текущая Удочка: {rod}",
    "bait_count": "Приманки: {count}"
  },
  "config": {
    "detection_settings": "Настройки Обнаружения",
    "template_confidence": "Точность Шаблонов",
    "coordinates": "Координаты",
    "bait_priority": "Приоритет Приманок",
    "feeding_settings": "Настройки Питания",
    "auto_clean": "Автоочистка",
    "language": "Язык"
  }
}
```

### 🎨 UI Internacionalizada

#### Main Window com I18N (ui/main_window.py)
```python
import tkinter as tk
from tkinter import ttk
from utils.i18n_manager import _, i18n

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interface com suporte a I18N"""
        # Título da janela
        self.root.title(_("main_window.title"))
        
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        
        # Tabs
        self.control_tab = self.create_control_tab()
        self.config_tab = self.create_config_tab()
        self.confidence_tab = self.create_confidence_tab()
        self.feeding_tab = self.create_feeding_tab()
        self.analytics_tab = self.create_analytics_tab()
        
        # Adicionar tabs com textos traduzidos
        self.notebook.add(self.control_tab, text=_("main_window.tabs.control"))
        self.notebook.add(self.config_tab, text=_("main_window.tabs.config"))
        self.notebook.add(self.confidence_tab, text=_("main_window.tabs.confidence"))
        self.notebook.add(self.feeding_tab, text=_("main_window.tabs.feeding"))
        self.notebook.add(self.analytics_tab, text=_("main_window.tabs.analytics"))
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Language selector
        self.create_language_selector()
        
    def create_control_tab(self):
        """Criar tab de controle"""
        frame = ttk.Frame(self.notebook)
        
        # Botões principais
        ttk.Button(frame, text=_("main_window.buttons.start"), 
                  command=self.start_bot).pack(pady=5)
        ttk.Button(frame, text=_("main_window.buttons.stop"), 
                  command=self.stop_bot).pack(pady=5)
        ttk.Button(frame, text=_("main_window.buttons.pause"), 
                  command=self.pause_bot).pack(pady=5)
        
        # Botão de emergência
        emergency_btn = tk.Button(frame, text=_("main_window.buttons.emergency"),
                                 bg='red', fg='white', font=('Arial', 12, 'bold'),
                                 command=self.emergency_stop)
        emergency_btn.pack(pady=10)
        
        # Status
        self.status_label = ttk.Label(frame, text=_("status.bot_idle"))
        self.status_label.pack(pady=5)
        
        # Estatísticas
        self.fish_count_label = ttk.Label(frame, text=_("status.fish_caught", count=0))
        self.fish_count_label.pack(pady=2)
        
        self.session_time_label = ttk.Label(frame, text=_("status.session_time", time="00:00:00"))
        self.session_time_label.pack(pady=2)
        
        return frame
        
    def create_language_selector(self):
        """Criar seletor de idioma"""
        lang_frame = ttk.Frame(self.root)
        lang_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(lang_frame, text=_("config.language") + ":").pack(side=tk.LEFT)
        
        # Combobox com idiomas
        self.language_var = tk.StringVar(value=i18n.current_language)
        self.language_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=list(i18n.SUPPORTED_LANGUAGES.keys()),
            state="readonly",
            width=10
        )
        self.language_combo.pack(side=tk.LEFT, padx=5)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Exibir nome do idioma atual
        self.language_name_label = ttk.Label(
            lang_frame, 
            text=i18n.SUPPORTED_LANGUAGES[i18n.current_language]
        )
        self.language_name_label.pack(side=tk.LEFT, padx=5)
        
    def on_language_changed(self, event=None):
        """Callback para mudança de idioma"""
        new_language = self.language_var.get()
        i18n.set_language(new_language)
        
        # Atualizar nome do idioma
        self.language_name_label.config(
            text=i18n.SUPPORTED_LANGUAGES[new_language]
        )
        
        # Recriar interface com novo idioma
        self.refresh_ui()
        
    def refresh_ui(self):
        """Atualizar interface com novo idioma"""
        # Título da janela
        self.root.title(_("main_window.title"))
        
        # Atualizar textos das tabs
        for i, tab_key in enumerate(['control', 'config', 'confidence', 'feeding', 'analytics']):
            self.notebook.tab(i, text=_(f"main_window.tabs.{tab_key}"))
            
        # Atualizar todos os widgets recursivamente
        self.update_widget_texts(self.root)
        
    def update_widget_texts(self, widget):
        """Atualizar textos de todos os widgets recursivamente"""
        # Implementar atualização de textos baseada em tags ou referencias
        pass
```

### 📊 Analytics Tab Multilíngue

#### Analytics Panel (ui/analytics_panel.py)
```python
class AnalyticsPanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.setup_analytics_ui()
        
    def setup_analytics_ui(self):
        """Configurar painel de analytics"""
        # Título
        title_label = ttk.Label(self.frame, text=_("analytics.title"), 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Estatísticas de sessão
        session_frame = ttk.LabelFrame(self.frame, text=_("analytics.session_stats"))
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid de estatísticas
        stats_data = [
            ("analytics.total_fish", "0"),
            ("analytics.session_duration", "00:00:00"),
            ("analytics.fish_per_hour", "0.0"),
            ("analytics.success_rate", "0%"),
            ("analytics.rod_changes", "0"),
            ("analytics.auto_cleans", "0")
        ]
        
        for i, (label_key, value) in enumerate(stats_data):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(session_frame, text=_(label_key) + ":").grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            ttk.Label(session_frame, text=value, font=('Arial', 10, 'bold')).grid(
                row=row, column=col+1, sticky=tk.W, padx=5, pady=2
            )
            
        # Gráficos
        charts_frame = ttk.LabelFrame(self.frame, text=_("analytics.performance_charts"))
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Placeholder para gráficos
        ttk.Label(charts_frame, text=_("analytics.charts_placeholder")).pack(pady=20)
```

### 🔄 Configuração de Idioma Persistente

#### Config Manager com I18N (config/config_manager.py)
```python
class ConfigManager:
    def __init__(self):
        self.config_file = "data/config.json"
        self.load_config()
        
    def load_config(self):
        """Carregar configuração incluindo idioma"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Configurar idioma salvo
            saved_language = config.get('language', 'pt_BR')
            i18n.set_language(saved_language)
            
        except FileNotFoundError:
            self.create_default_config()
            
    def save_config(self):
        """Salvar configuração incluindo idioma atual"""
        config = {
            'language': i18n.current_language,
            # ... outras configurações
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
```

---

## 📋 PLANO DE IMPLEMENTAÇÃO

### 🎯 **ORDEM CORRETA DE IMPLEMENTAÇÃO**

**IMPORTANTE**: Começamos pela **UI primeiro** usando componentes reutilizáveis, depois lógica modular.

#### **🔄 COMPONENTES TOTALMENTE REUTILIZÁVEIS**

✅ **DO CÓDIGO ATUAL - MANTER INTEGRALMENTE**:

1. **📁 i18n.py** (449 linhas) - **PERFEITO, NÃO ALTERAR**
   - Sistema completo de internacionalização PT/EN
   - Função `_()` helper funcionando
   - Detecção automática de idioma
   - **APENAS ADICIONAR RUSSO** ao existente

2. **📁 Templates Essenciais** (40 de 50 arquivos)
   - `catch.png`, `VARANOBAUCI.png`, `enbausi.png`, `varaquebrada.png`
   - `inventory.png`, `loot.png`
   - Templates de iscas e peixes organizados

3. **⚙️ Configurações Funcionais**:
   ```json
   // Coordenadas CORRETAS já testadas
   "slot_positions": {
     "1": [709, 1005], "2": [805, 1005], "3": [899, 1005],
     "4": [992, 1005], "5": [1092, 1005], "6": [1188, 1005]
   },
   "feeding_positions": {
     "slot1": [1306, 858], "slot2": [1403, 877], "eat": [1083, 373]
   }
   ```

4. **🔐 Sistema de Licenciamento**
   - `license.key` + validação online
   - Hardware fingerprinting
   - **FUNCIONA - manter lógica**

#### **🚀 FASE 1: UI MODERNA PRIMEIRO (1-2 semanas)**

**Objetivo**: Interface limpa e funcional **ANTES** da lógica complexa

##### **Estrutura UI Modular**:
```
📁 fishing_bot_v4/
├── 📁 ui/                      # UI PRIMEIRO
│   ├── main_window.py          # Janela principal Tkinter moderna
│   ├── control_panel.py        # Painel de controle
│   ├── config_panel.py         # Configurações
│   ├── confidence_panel.py     # Confiança de templates
│   ├── analytics_panel.py      # Estatísticas
│   └── widgets/                # Widgets customizados
├── 📁 utils/                   # Utilitários básicos
│   ├── i18n_manager.py         # REUTILIZAR i18n.py existente
│   ├── config_manager.py       # Gerenciador de configurações
│   └── logging_manager.py      # Sistema de logs
├── 📁 templates/               # REUTILIZAR 40 templates
├── 📁 locales/                 # Traduções PT/EN/RU
├── 📁 config/                  # Configurações
│   └── default_config.json     # REUTILIZAR coordenadas funcionais
└── main.py                     # Entry point
```

##### **UI Principal (ui/main_window.py)**:
```python
import tkinter as tk
from tkinter import ttk
import threading
import json
from utils.i18n_manager import _, i18n  # REUTILIZAR i18n existente

class FishingBotUI:
    """Interface principal moderna do Ultimate Fishing Bot v4.0"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.load_existing_config()  # REUTILIZAR configurações
        
    def setup_window(self):
        """Configurar janela principal"""
        self.root.title(_("main_window.title"))
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Icon se existir
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
    def setup_ui(self):
        """Configurar interface modular"""
        # Estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        
        # Menu principal
        self.create_menu()
        
        # Toolbar
        self.create_toolbar()
        
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        
        # Criar tabs
        self.control_tab = ControlPanel(self.notebook)
        self.config_tab = ConfigPanel(self.notebook)
        self.confidence_tab = ConfidencePanel(self.notebook)
        self.analytics_tab = AnalyticsPanel(self.notebook)
        
        # Adicionar tabs
        self.notebook.add(self.control_tab.frame, text=_("tabs.control"))
        self.notebook.add(self.config_tab.frame, text=_("tabs.config"))
        self.notebook.add(self.confidence_tab.frame, text=_("tabs.confidence"))
        self.notebook.add(self.analytics_tab.frame, text=_("tabs.analytics"))
        
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.create_status_bar()
        
        # Language selector
        self.create_language_selector()
        
    def create_toolbar(self):
        """Toolbar com botões principais"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Botões principais
        ttk.Button(toolbar, text=_("buttons.start"), 
                  command=self.start_bot, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=_("buttons.stop"), 
                  command=self.stop_bot, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=_("buttons.pause"), 
                  command=self.pause_bot, width=12).pack(side=tk.LEFT, padx=2)
                  
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Emergency button
        emergency_btn = tk.Button(toolbar, text=_("buttons.emergency"),
                                 bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                                 relief=tk.RAISED, bd=2,
                                 command=self.emergency_stop)
        emergency_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        self.status_indicator = tk.Label(toolbar, text="●", fg="gray", font=('Arial', 16))
        self.status_indicator.pack(side=tk.RIGHT, padx=5)
        
        self.status_text = ttk.Label(toolbar, text=_("status.idle"))
        self.status_text.pack(side=tk.RIGHT, padx=5)
```

##### **Control Panel (ui/control_panel.py)**:
```python
class ControlPanel:
    """Painel de controle principal"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.setup_control_ui()
        
    def setup_control_ui(self):
        """Interface do painel de controle"""
        # Status atual
        status_frame = ttk.LabelFrame(self.frame, text=_("control.current_status"))
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid de status
        self.status_labels = {}
        status_items = [
            ("fishing_active", _("status.fishing_inactive")),
            ("current_rod", _("status.rod_none")),
            ("fish_count", "0"),
            ("session_time", "00:00:00"),
            ("last_action", _("status.no_action"))
        ]
        
        for i, (key, default_value) in enumerate(status_items):
            ttk.Label(status_frame, text=_(f"status.{key}") + ":").grid(
                row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=2
            )
            self.status_labels[key] = ttk.Label(status_frame, text=default_value,
                                              font=('Arial', 9, 'bold'))
            self.status_labels[key].grid(
                row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2
            )
            
        # Controles manuais
        manual_frame = ttk.LabelFrame(self.frame, text=_("control.manual_controls"))
        manual_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botões manuais em grid
        manual_buttons = [
            ("open_inventory", self.open_inventory),
            ("open_chest", self.open_chest),
            ("feed_character", self.feed_character),
            ("switch_rod", self.show_rod_selector),
            ("auto_clean", self.auto_clean),
            ("test_detection", self.test_detection)
        ]
        
        for i, (button_key, callback) in enumerate(manual_buttons):
            ttk.Button(manual_frame, text=_(f"manual.{button_key}"),
                      command=callback).grid(
                row=i//3, column=i%3, padx=5, pady=5, sticky=tk.EW
            )
            
        # Configurar colunas para expandir
        for col in range(3):
            manual_frame.columnconfigure(col, weight=1)
            
        # Log de ações
        log_frame = ttk.LabelFrame(self.frame, text=_("control.action_log"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text widget com scroll
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD,
                               font=('Consolas', 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                 command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
```

#### **🔧 FASE 2: LÓGICA MODULAR (2-3 semanas)**

**Objetivo**: Extrair e modularizar a lógica funcional do código atual

##### **Componentes a Extrair do botpesca.py**:

1. **🎣 FishingEngine** - Lógica principal de pesca
   ```python
   # EXTRAIR de botpesca.py (linhas que funcionam)
   class FishingEngine:
       def __init__(self):
           self.template_engine = TemplateEngine()
           self.state = GameState()
           
       def detect_fish_caught(self):
           # REUTILIZAR lógica de detecção de catch.png que funciona
           pass
           
       def handle_fish_caught(self):
           # REUTILIZAR sequência: soltar botão → aguardar → pressionar
           pass
   ```

2. **🎯 TemplateEngine** - Sistema unificado
   ```python
   # CONSOLIDAR os 10+ sistemas em 1 só
   class TemplateEngine:
       def __init__(self):
           self.load_working_templates()  # REUTILIZAR templates que funcionam
           self.confidence_config = self.load_confidence_config()
           
       def detect_all_critical(self, screenshot):
           # UNIFICAR detecção: catch, rod, inventory, chest
           pass
   ```

3. **🔄 RodManager** - Gestão de varas
   ```python
   # EXTRAIR lógica funcional de troca de varas
   class RodManager:
       def __init__(self):
           self.current_rod = 1
           self.rod_pairs = [(1,2), (3,4), (5,6)]  # MANTER lógica
           self.bait_priority = self.load_bait_priority()  # REUTILIZAR
           
       def switch_to_next_rod(self):
           # REUTILIZAR lógica de troca que funciona
           pass
   ```

#### **🤖 FASE 3: ARDUINO INTEGRATION (2-3 semanas)**

##### **Arduino Leonardo Setup**:
```cpp
// main.ino - CÓDIGO LIMPO
#include <Mouse.h>
#include <Keyboard.h>

// Estados essenciais
bool fishing_active = false;
bool emergency_stop = false;

void setup() {
    Serial.begin(9600);
    Mouse.begin();
    Keyboard.begin();
    Serial.println("ARDUINO_READY");
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        executeCommand(command);
    }
    delay(10);
}

void executeCommand(String cmd) {
    if (cmd == "START_FISHING") {
        startFishing();
    } else if (cmd == "STOP_FISHING") {
        stopFishing();
    } else if (cmd == "OPEN_CHEST") {
        executeChestMacro();
    }
    // ... comandos essenciais
}

void startFishing() {
    Mouse.press(MOUSE_RIGHT);  // FÍSICO - impossível detectar
    fishing_active = true;
    Serial.println("FISHING_STARTED");
}

void executeChestMacro() {
    // REUTILIZAR sequência ALT+movimento+E que funciona
    Keyboard.press(KEY_LEFT_ALT);
    delay(500);
    Mouse.move(-400, 0);  // Movimento físico
    delay(300);
    Keyboard.press('e');
    delay(100);
    Keyboard.release('e');
    Keyboard.release(KEY_LEFT_ALT);
    Serial.println("CHEST_OPENED");
}
```

### 🎯 **ESTRATÉGIA DE REUTILIZAÇÃO**

#### **✅ MANTER 100% (não alterar)**:
1. **i18n.py** - Sistema perfeito, apenas adicionar russo
2. **Templates funcionais** - 40 arquivos testados
3. **Coordenadas funcionais** - slots, feeding, áreas
4. **Configurações de confiança** - thresholds testados
5. **Sistema de licenciamento** - funciona perfeitamente

#### **🔄 EXTRAIR E LIMPAR**:
1. **Lógica de pesca** - extrair partes que funcionam
2. **Template matching** - consolidar em 1 sistema
3. **Gestão de varas** - simplificar mas manter conceito
4. **Auto-clean** - manter lógica, limpar implementação
5. **Feeding** - manter triggers, limpar execução

#### **❌ REESCREVER COMPLETAMENTE**:
1. **Estrutura de classes** - SimpleFishingUI com 7000 linhas
2. **Coordenação de operações** - 8 sistemas conflitantes
3. **Estado global** - variáveis espalhadas
4. **Thread management** - caos de locks

### 🚀 **PRIMEIRO PASSO PRÁTICO**

**COMEÇAR AGORA**: UI moderna reutilizando i18n.py existente

```bash
# 1. Criar estrutura base
mkdir fishing_bot_v4
cd fishing_bot_v4

# 2. COPIAR componentes funcionais
cp ../i18n.py utils/i18n_manager.py
cp -r ../templates/ ./
cp ../config.json config/default_config.json

# 3. Criar UI moderna
touch ui/main_window.py
touch ui/control_panel.py
touch main.py

# 4. Começar implementação modular
```

**Resultado**: Interface funcional em 1 semana, depois migrar lógica gradualmente.

Esta abordagem garante **progressão contínua** sem quebrar funcionalidades existentes! 🎯

## 🔍 **REVISÃO COMPLETA DA UI - TODOS OS SISTEMAS**

### 📋 **PAINÉIS FALTANTES IDENTIFICADOS**

Baseado na análise completa do código atual, preciso adicionar os seguintes painéis/funcionalidades:

#### **🎮 TAB ADICIONAL: ROD MANAGEMENT**
```python
class RodManagementPanel:
    """Painel dedicado ao gerenciamento de varas"""
    
    def setup_rod_ui(self):
        # Rod Status Grid (6 varas)
        rod_frame = ttk.LabelFrame(self.frame, text=_("rod.current_status"))
        
        # Grid 3x2 para as 6 varas
        self.rod_widgets = {}
        for rod_num in range(1, 7):
            row = (rod_num - 1) // 3
            col = (rod_num - 1) % 3
            
            # Frame individual da vara
            rod_individual = ttk.Frame(rod_frame)
            rod_individual.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            
            # Indicador visual da vara
            self.rod_widgets[f"rod_{rod_num}"] = {
                'status': tk.Label(rod_individual, text=f"Vara {rod_num}", 
                                 bg='gray', fg='white', width=12),
                'bait_count': ttk.Label(rod_individual, text="Iscas: 0"),
                'usage_count': ttk.Label(rod_individual, text="Usos: 0/20"),
                'switch_btn': ttk.Button(rod_individual, text=_("rod.switch"),
                                       command=lambda r=rod_num: self.switch_to_rod(r))
            }
            
            # Pack widgets
            for widget in self.rod_widgets[f"rod_{rod_num}"].values():
                widget.pack(pady=1)
                
        # Rod Pairs Configuration
        pairs_frame = ttk.LabelFrame(self.frame, text=_("rod.pair_configuration"))
        
        # Configuração dos pares: (1,2), (3,4), (5,6)
        self.pair_config = {}
        pairs = [(1,2), (3,4), (5,6)]
        
        for i, (rod1, rod2) in enumerate(pairs):
            pair_frame = ttk.Frame(pairs_frame)
            pair_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(pair_frame, text=f"Par {i+1}: Varas {rod1}-{rod2}").pack(side=tk.LEFT)
            
            # Switch limit para o par
            ttk.Label(pair_frame, text="Limite trocas:").pack(side=tk.LEFT, padx=(20,5))
            switch_limit = tk.Spinbox(pair_frame, from_=10, to=50, value=20, width=5)
            switch_limit.pack(side=tk.LEFT)
            
            self.pair_config[f"pair_{i+1}"] = switch_limit
            
        # Auto Rod Replacement
        auto_frame = ttk.LabelFrame(self.frame, text=_("rod.auto_replacement"))
        
        self.auto_replace_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text=_("rod.enable_auto_replace"),
                       variable=self.auto_replace_var).pack(anchor=tk.W)
                       
        # Broken rod action
        ttk.Label(auto_frame, text=_("rod.broken_action")).pack(anchor=tk.W, pady=(10,0))
        self.broken_action_var = tk.StringVar(value="save")
        
        action_frame = ttk.Frame(auto_frame)
        action_frame.pack(fill=tk.X, padx=20)
        
        ttk.Radiobutton(action_frame, text=_("rod.action_save"),
                       variable=self.broken_action_var, value="save").pack(anchor=tk.W)
        ttk.Radiobutton(action_frame, text=_("rod.action_discard"),
                       variable=self.broken_action_var, value="discard").pack(anchor=tk.W)
```

#### **🍖 FEEDING PANEL COMPLETO**
```python
class FeedingPanel:
    """Painel completo de alimentação"""
    
    def setup_feeding_ui(self):
        # Feeding Mode Selection
        mode_frame = ttk.LabelFrame(self.frame, text=_("feeding.mode_selection"))
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.feeding_mode_var = tk.StringVar(value="detecao_auto")
        
        ttk.Radiobutton(mode_frame, text=_("feeding.mode_auto"),
                       variable=self.feeding_mode_var, value="detecao_auto").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=_("feeding.mode_manual"),
                       variable=self.feeding_mode_var, value="manual").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=_("feeding.mode_disabled"),
                       variable=self.feeding_mode_var, value="disabled").pack(anchor=tk.W)
        
        # Trigger Configuration
        trigger_frame = ttk.LabelFrame(self.frame, text=_("feeding.trigger_config"))
        trigger_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Trigger mode
        self.trigger_mode_var = tk.StringVar(value="catches")
        
        trigger_mode_frame = ttk.Frame(trigger_frame)
        trigger_mode_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(trigger_mode_frame, text=_("feeding.trigger_catches"),
                       variable=self.trigger_mode_var, value="catches").pack(side=tk.LEFT)
        self.trigger_catches = tk.Spinbox(trigger_mode_frame, from_=1, to=20, value=2, width=5)
        self.trigger_catches.pack(side=tk.LEFT, padx=5)
        ttk.Label(trigger_mode_frame, text=_("feeding.catches_label")).pack(side=tk.LEFT)
        
        trigger_time_frame = ttk.Frame(trigger_frame)
        trigger_time_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(trigger_time_frame, text=_("feeding.trigger_time"),
                       variable=self.trigger_mode_var, value="time").pack(side=tk.LEFT)
        self.trigger_minutes = tk.Spinbox(trigger_time_frame, from_=5, to=60, value=20, width=5)
        self.trigger_minutes.pack(side=tk.LEFT, padx=5)
        ttk.Label(trigger_time_frame, text=_("feeding.minutes_label")).pack(side=tk.LEFT)
        
        # Slot Configuration
        slots_frame = ttk.LabelFrame(self.frame, text=_("feeding.slot_configuration"))
        slots_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Slot 1
        slot1_frame = ttk.Frame(slots_frame)
        slot1_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(slot1_frame, text=_("feeding.slot1_position")).pack(side=tk.LEFT)
        self.slot1_x = tk.Spinbox(slot1_frame, from_=0, to=1920, value=1306, width=6)
        self.slot1_x.pack(side=tk.LEFT, padx=(10,2))
        self.slot1_y = tk.Spinbox(slot1_frame, from_=0, to=1080, value=858, width=6)
        self.slot1_y.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(slot1_frame, text=_("feeding.test_position"),
                  command=lambda: self.test_position(1)).pack(side=tk.LEFT, padx=10)
        
        # Slot 2
        slot2_frame = ttk.Frame(slots_frame)
        slot2_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(slot2_frame, text=_("feeding.slot2_position")).pack(side=tk.LEFT)
        self.slot2_x = tk.Spinbox(slot2_frame, from_=0, to=1920, value=1403, width=6)
        self.slot2_x.pack(side=tk.LEFT, padx=(10,2))
        self.slot2_y = tk.Spinbox(slot2_frame, from_=0, to=1080, value=877, width=6)
        self.slot2_y.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(slot2_frame, text=_("feeding.test_position"),
                  command=lambda: self.test_position(2)).pack(side=tk.LEFT, padx=10)
        
        # Eat button position
        eat_frame = ttk.Frame(slots_frame)
        eat_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(eat_frame, text=_("feeding.eat_position")).pack(side=tk.LEFT)
        self.eat_x = tk.Spinbox(eat_frame, from_=0, to=1920, value=1083, width=6)
        self.eat_x.pack(side=tk.LEFT, padx=(10,2))
        self.eat_y = tk.Spinbox(eat_frame, from_=0, to=1080, value=373, width=6)
        self.eat_y.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(eat_frame, text=_("feeding.test_position"),
                  command=lambda: self.test_position('eat')).pack(side=tk.LEFT, padx=10)
        
        # Usage limits
        usage_frame = ttk.LabelFrame(self.frame, text=_("feeding.usage_limits"))
        usage_frame.pack(fill=tk.X, padx=10, pady=5)
        
        max_uses_frame = ttk.Frame(usage_frame)
        max_uses_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(max_uses_frame, text=_("feeding.max_uses_per_slot")).pack(side=tk.LEFT)
        self.max_uses = tk.Spinbox(max_uses_frame, from_=10, to=50, value=20, width=5)
        self.max_uses.pack(side=tk.LEFT, padx=10)
        
        feeds_per_session_frame = ttk.Frame(usage_frame)
        feeds_per_session_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(feeds_per_session_frame, text=_("feeding.feeds_per_session")).pack(side=tk.LEFT)
        self.feeds_per_session = tk.Spinbox(feeds_per_session_frame, from_=1, to=10, value=5, width=5)
        self.feeds_per_session.pack(side=tk.LEFT, padx=10)
```

#### **🧹 AUTO-CLEAN PANEL DETALHADO**
```python
class AutoCleanPanel:
    """Painel detalhado de limpeza automática"""
    
    def setup_autoclean_ui(self):
        # Enable/Disable
        enable_frame = ttk.Frame(self.frame)
        enable_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_clean_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(enable_frame, text=_("autoclean.enable"),
                       variable=self.auto_clean_enabled).pack(side=tk.LEFT)
        
        # Interval Configuration
        interval_frame = ttk.LabelFrame(self.frame, text=_("autoclean.interval_config"))
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        interval_config_frame = ttk.Frame(interval_frame)
        interval_config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interval_config_frame, text=_("autoclean.clean_every")).pack(side=tk.LEFT)
        self.clean_interval = tk.Spinbox(interval_config_frame, from_=1, to=50, value=1, width=5)
        self.clean_interval.pack(side=tk.LEFT, padx=5)
        ttk.Label(interval_config_frame, text=_("autoclean.catches")).pack(side=tk.LEFT)
        
        # Chest Selection
        chest_frame = ttk.LabelFrame(self.frame, text=_("autoclean.chest_selection"))
        chest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.chest_side_var = tk.StringVar(value="right")
        
        ttk.Radiobutton(chest_frame, text=_("autoclean.chest_left"),
                       variable=self.chest_side_var, value="left").pack(anchor=tk.W)
        ttk.Radiobutton(chest_frame, text=_("autoclean.chest_right"),
                       variable=self.chest_side_var, value="right").pack(anchor=tk.W)
        
        # Fish Selection for Transfer
        fish_frame = ttk.LabelFrame(self.frame, text=_("autoclean.fish_selection"))
        fish_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable frame for fish checkboxes
        canvas = tk.Canvas(fish_frame)
        scrollbar = ttk.Scrollbar(fish_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Fish types with checkboxes
        self.fish_selection = {}
        fish_types = [
            ("salmon", _("fish.salmon")),
            ("sardine", _("fish.sardine")),
            ("anchovy", _("fish.anchovy")),
            ("shark", _("fish.shark")),
            ("yellowperch", _("fish.yellowperch")),
            ("herring", _("fish.herring")),
            ("smalltrout", _("fish.smalltrout")),
            ("rawfish", _("fish.rawfish"))
        ]
        
        for i, (fish_key, fish_name) in enumerate(fish_types):
            var = tk.BooleanVar(value=True)
            self.fish_selection[fish_key] = var
            
            ttk.Checkbutton(scrollable_frame, text=fish_name,
                           variable=var).grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Macro Configuration
        macro_frame = ttk.LabelFrame(self.frame, text=_("autoclean.macro_config"))
        macro_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Chest opening method
        self.chest_method_var = tk.StringVar(value="macro")
        
        ttk.Radiobutton(macro_frame, text=_("autoclean.use_recorded_macro"),
                       variable=self.chest_method_var, value="macro").pack(anchor=tk.W)
        ttk.Radiobutton(macro_frame, text=_("autoclean.use_alt_movement"),
                       variable=self.chest_method_var, value="alt_movement").pack(anchor=tk.W)
        
        # Test buttons
        test_frame = ttk.Frame(macro_frame)
        test_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(test_frame, text=_("autoclean.test_chest_opening"),
                  command=self.test_chest_opening).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text=_("autoclean.record_new_macro"),
                  command=self.record_new_macro).pack(side=tk.LEFT, padx=5)
```

#### **📊 ANALYTICS PANEL EXPANDIDO**
```python
class AnalyticsPanel:
    """Painel expandido de análises e estatísticas"""
    
    def setup_analytics_ui(self):
        # Session Statistics
        session_frame = ttk.LabelFrame(self.frame, text=_("analytics.session_stats"))
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid de estatísticas em tempo real
        self.stats_labels = {}
        stats_layout = [
            [("total_fish", "0"), ("session_duration", "00:00:00"), ("fish_per_hour", "0.0")],
            [("success_rate", "0%"), ("rod_changes", "0"), ("auto_cleans", "0")],
            [("feeding_count", "0"), ("template_matches", "0"), ("average_catch_time", "0s")]
        ]
        
        for row, row_stats in enumerate(stats_layout):
            for col, (stat_key, default_value) in enumerate(row_stats):
                # Label
                ttk.Label(session_frame, text=_(f"analytics.{stat_key}") + ":").grid(
                    row=row*2, column=col*2, sticky=tk.W, padx=5, pady=2
                )
                # Value
                self.stats_labels[stat_key] = ttk.Label(session_frame, text=default_value,
                                                       font=('Arial', 10, 'bold'), foreground='blue')
                self.stats_labels[stat_key].grid(
                    row=row*2+1, column=col*2, sticky=tk.W, padx=5
                )
                
        # Performance Charts
        charts_frame = ttk.LabelFrame(self.frame, text=_("analytics.performance_charts"))
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chart selection
        chart_selection_frame = ttk.Frame(charts_frame)
        chart_selection_frame.pack(fill=tk.X, pady=5)
        
        self.chart_type_var = tk.StringVar(value="fish_per_time")
        chart_types = [
            ("fish_per_time", _("analytics.chart_fish_per_time")),
            ("template_confidence", _("analytics.chart_template_confidence")),
            ("rod_usage", _("analytics.chart_rod_usage")),
            ("system_performance", _("analytics.chart_system_performance"))
        ]
        
        for chart_key, chart_name in chart_types:
            ttk.Radiobutton(chart_selection_frame, text=chart_name,
                           variable=self.chart_type_var, value=chart_key,
                           command=self.update_chart).pack(side=tk.LEFT, padx=5)
        
        # Chart area (placeholder for matplotlib or similar)
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Placeholder
        ttk.Label(self.chart_frame, text=_("analytics.chart_placeholder"),
                 font=('Arial', 12)).pack(expand=True)
        
        # Export options
        export_frame = ttk.LabelFrame(self.frame, text=_("analytics.export_options"))
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(export_buttons_frame, text=_("analytics.export_csv"),
                  command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_buttons_frame, text=_("analytics.export_json"),
                  command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_buttons_frame, text=_("analytics.reset_session"),
                  command=self.reset_session_stats).pack(side=tk.LEFT, padx=5)
```

#### **⚙️ ADVANCED CONFIG PANEL**
```python
class AdvancedConfigPanel:
    """Painel de configurações avançadas"""
    
    def setup_advanced_config_ui(self):
        # Performance Settings
        performance_frame = ttk.LabelFrame(self.frame, text=_("config.performance_settings"))
        performance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Detection interval
        detection_frame = ttk.Frame(performance_frame)
        detection_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(detection_frame, text=_("config.detection_interval")).pack(side=tk.LEFT)
        self.detection_interval = tk.Spinbox(detection_frame, from_=50, to=1000, value=100, width=6)
        self.detection_interval.pack(side=tk.LEFT, padx=10)
        ttk.Label(detection_frame, text="ms").pack(side=tk.LEFT)
        
        # Screenshot region
        region_frame = ttk.Frame(performance_frame)
        region_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(region_frame, text=_("config.screenshot_region")).pack(side=tk.LEFT)
        self.region_x = tk.Spinbox(region_frame, from_=0, to=1920, value=0, width=6)
        self.region_x.pack(side=tk.LEFT, padx=2)
        self.region_y = tk.Spinbox(region_frame, from_=0, to=1080, value=0, width=6)
        self.region_y.pack(side=tk.LEFT, padx=2)
        self.region_w = tk.Spinbox(region_frame, from_=800, to=1920, value=1920, width=6)
        self.region_w.pack(side=tk.LEFT, padx=2)
        self.region_h = tk.Spinbox(region_frame, from_=600, to=1080, value=1080, width=6)
        self.region_h.pack(side=tk.LEFT, padx=2)
        
        # Anti-Detection Settings
        anti_detect_frame = ttk.LabelFrame(self.frame, text=_("config.anti_detection"))
        anti_detect_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.anti_detect_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(anti_detect_frame, text=_("config.enable_anti_detection"),
                       variable=self.anti_detect_enabled,
                       command=self.toggle_anti_detection).pack(anchor=tk.W)
        
        # Click variation
        click_var_frame = ttk.Frame(anti_detect_frame)
        click_var_frame.pack(fill=tk.X, pady=2)
        
        self.click_variation = tk.BooleanVar(value=False)
        ttk.Checkbutton(click_var_frame, text=_("config.click_variation"),
                       variable=self.click_variation).pack(side=tk.LEFT)
        
        ttk.Label(click_var_frame, text=_("config.delay_range")).pack(side=tk.LEFT, padx=(20,5))
        self.click_delay_min = tk.Spinbox(click_var_frame, from_=50, to=500, value=80, width=5)
        self.click_delay_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(click_var_frame, text="-").pack(side=tk.LEFT)
        self.click_delay_max = tk.Spinbox(click_var_frame, from_=100, to=1000, value=150, width=5)
        self.click_delay_max.pack(side=tk.LEFT, padx=2)
        ttk.Label(click_var_frame, text="ms").pack(side=tk.LEFT)
        
        # Movement variation
        movement_var_frame = ttk.Frame(anti_detect_frame)
        movement_var_frame.pack(fill=tk.X, pady=2)
        
        self.movement_variation = tk.BooleanVar(value=True)
        ttk.Checkbutton(movement_var_frame, text=_("config.movement_variation"),
                       variable=self.movement_variation).pack(side=tk.LEFT)
        
        # Natural breaks
        breaks_frame = ttk.Frame(anti_detect_frame)
        breaks_frame.pack(fill=tk.X, pady=2)
        
        self.natural_breaks = tk.BooleanVar(value=True)
        ttk.Checkbutton(breaks_frame, text=_("config.natural_breaks"),
                       variable=self.natural_breaks).pack(side=tk.LEFT)
        
        # Break configuration
        break_config_frame = ttk.Frame(anti_detect_frame)
        break_config_frame.pack(fill=tk.X, pady=2, padx=20)
        
        self.break_mode_var = tk.StringVar(value="catches")
        ttk.Radiobutton(break_config_frame, text=_("config.break_every"),
                       variable=self.break_mode_var, value="catches").pack(side=tk.LEFT)
        self.break_catches = tk.Spinbox(break_config_frame, from_=20, to=100, value=50, width=5)
        self.break_catches.pack(side=tk.LEFT, padx=2)
        ttk.Label(break_config_frame, text=_("config.catches")).pack(side=tk.LEFT)
        
        break_time_frame = ttk.Frame(anti_detect_frame)
        break_time_frame.pack(fill=tk.X, pady=2, padx=20)
        
        ttk.Radiobutton(break_time_frame, text=_("config.break_every"),
                       variable=self.break_mode_var, value="time").pack(side=tk.LEFT)
        self.break_minutes = tk.Spinbox(break_time_frame, from_=30, to=180, value=45, width=5)
        self.break_minutes.pack(side=tk.LEFT, padx=2)
        ttk.Label(break_time_frame, text=_("config.minutes")).pack(side=tk.LEFT)
        
        # Logging Settings
        logging_frame = ttk.LabelFrame(self.frame, text=_("config.logging_settings"))
        logging_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.enable_logging = tk.BooleanVar(value=True)
        ttk.Checkbutton(logging_frame, text=_("config.enable_logging"),
                       variable=self.enable_logging).pack(anchor=tk.W)
        
        log_level_frame = ttk.Frame(logging_frame)
        log_level_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(log_level_frame, text=_("config.log_level")).pack(side=tk.LEFT)
        self.log_level_var = tk.StringVar(value="INFO")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        self.log_level_combo = ttk.Combobox(log_level_frame, textvariable=self.log_level_var,
                                          values=log_levels, state="readonly", width=10)
        self.log_level_combo.pack(side=tk.LEFT, padx=10)
```

#### **🌐 SERVER CONNECTION PANEL**
```python
class ServerConnectionPanel:
    """Painel para conexão com servidor (Fase 2/3)"""
    
    def setup_server_ui(self):
        # Connection Status
        status_frame = ttk.LabelFrame(self.frame, text=_("server.connection_status"))
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_indicator_frame = ttk.Frame(status_frame)
        status_indicator_frame.pack(fill=tk.X, pady=5)
        
        self.connection_indicator = tk.Label(status_indicator_frame, text="●", 
                                           fg="red", font=('Arial', 16))
        self.connection_indicator.pack(side=tk.LEFT)
        
        self.connection_status_label = ttk.Label(status_indicator_frame, 
                                               text=_("server.disconnected"))
        self.connection_status_label.pack(side=tk.LEFT, padx=5)
        
        # Server Configuration
        config_frame = ttk.LabelFrame(self.frame, text=_("server.configuration"))
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Server URL
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(url_frame, text=_("server.url")).pack(side=tk.LEFT)
        self.server_url = tk.StringVar(value="ws://localhost:8765")
        ttk.Entry(url_frame, textvariable=self.server_url, width=30).pack(side=tk.LEFT, padx=10)
        
        # Authentication
        auth_frame = ttk.Frame(config_frame)
        auth_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(auth_frame, text=_("server.username")).pack(side=tk.LEFT)
        self.username = tk.StringVar()
        ttk.Entry(auth_frame, textvariable=self.username, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(auth_frame, text=_("server.password")).pack(side=tk.LEFT, padx=(10,5))
        self.password = tk.StringVar()
        ttk.Entry(auth_frame, textvariable=self.password, show="*", width=15).pack(side=tk.LEFT, padx=5)
        
        # Connection buttons
        buttons_frame = ttk.Frame(config_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text=_("server.connect"),
                  command=self.connect_to_server).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text=_("server.disconnect"),
                  command=self.disconnect_from_server).pack(side=tk.LEFT, padx=5)
        
        # Operating Mode
        mode_frame = ttk.LabelFrame(self.frame, text=_("server.operating_mode"))
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.operating_mode_var = tk.StringVar(value="local")
        
        ttk.Radiobutton(mode_frame, text=_("server.mode_local"),
                       variable=self.operating_mode_var, value="local",
                       command=self.change_operating_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=_("server.mode_hybrid"),
                       variable=self.operating_mode_var, value="hybrid",
                       command=self.change_operating_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text=_("server.mode_full_server"),
                       variable=self.operating_mode_var, value="server",
                       command=self.change_operating_mode).pack(anchor=tk.W)
        
        # Arduino Connection
        arduino_frame = ttk.LabelFrame(self.frame, text=_("server.arduino_connection"))
        arduino_frame.pack(fill=tk.X, padx=10, pady=5)
        
        arduino_status_frame = ttk.Frame(arduino_frame)
        arduino_status_frame.pack(fill=tk.X, pady=5)
        
        self.arduino_indicator = tk.Label(arduino_status_frame, text="●", 
                                        fg="gray", font=('Arial', 16))
        self.arduino_indicator.pack(side=tk.LEFT)
        
        self.arduino_status_label = ttk.Label(arduino_status_frame, 
                                            text=_("arduino.not_connected"))
        self.arduino_status_label.pack(side=tk.LEFT, padx=5)
        
        # COM port selection
        port_frame = ttk.Frame(arduino_frame)
        port_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(port_frame, text=_("arduino.com_port")).pack(side=tk.LEFT)
        self.com_port_var = tk.StringVar(value="COM3")
        com_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]
        self.com_port_combo = ttk.Combobox(port_frame, textvariable=self.com_port_var,
                                         values=com_ports, width=10)
        self.com_port_combo.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(port_frame, text=_("arduino.scan_ports"),
                  command=self.scan_com_ports).pack(side=tk.LEFT, padx=5)
        
        # Arduino buttons
        arduino_buttons_frame = ttk.Frame(arduino_frame)
        arduino_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(arduino_buttons_frame, text=_("arduino.connect"),
                  command=self.connect_arduino).pack(side=tk.LEFT, padx=5)
        ttk.Button(arduino_buttons_frame, text=_("arduino.test_connection"),
                  command=self.test_arduino).pack(side=tk.LEFT, padx=5)
        ttk.Button(arduino_buttons_frame, text=_("arduino.emergency_stop"),
                  command=self.arduino_emergency_stop).pack(side=tk.LEFT, padx=5)
```

### 🎯 **ESTRUTURA FINAL COMPLETA DA UI**

```python
# main_window.py - Estrutura final com TODOS os sistemas
class FishingBotUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_ui()
        
    def setup_ui(self):
        # Criar notebook com TODAS as tabs
        self.notebook = ttk.Notebook(self.root)
        
        # TODAS as tabs necessárias
        self.control_tab = ControlPanel(self.notebook)           # Controle principal
        self.rod_tab = RodManagementPanel(self.notebook)         # Gestão de varas
        self.config_tab = ConfigPanel(self.notebook)             # Configurações básicas
        self.confidence_tab = ConfidencePanel(self.notebook)     # Confiança templates
        self.feeding_tab = FeedingPanel(self.notebook)           # Sistema alimentação
        self.autoclean_tab = AutoCleanPanel(self.notebook)       # Limpeza automática
        self.analytics_tab = AnalyticsPanel(self.notebook)       # Estatísticas
        self.advanced_tab = AdvancedConfigPanel(self.notebook)   # Config avançadas
        self.server_tab = ServerConnectionPanel(self.notebook)   # Conexão servidor
        
        # Adicionar todas as tabs
        tabs = [
            (self.control_tab, "tabs.control"),
            (self.rod_tab, "tabs.rod_management"), 
            (self.config_tab, "tabs.config"),
            (self.confidence_tab, "tabs.confidence"),
            (self.feeding_tab, "tabs.feeding"),
            (self.autoclean_tab, "tabs.autoclean"),
            (self.analytics_tab, "tabs.analytics"),
            (self.advanced_tab, "tabs.advanced"),
            (self.server_tab, "tabs.server")
        ]
        
        for tab_panel, tab_key in tabs:
            self.notebook.add(tab_panel.frame, text=_(tab_key))
```

### ✅ **CONFIRMAÇÃO: TODOS OS SISTEMAS INCLUÍDOS**

**Sistemas do código atual ✅ COBERTOS na UI planejada**:

1. ✅ **Fishing Control** - ControlPanel
2. ✅ **Rod Management** - RodManagementPanel (6 varas, pares, auto-replace)
3. ✅ **Template Matching** - ConfidencePanel (todos os templates)
4. ✅ **Feeding System** - FeedingPanel (slots, triggers, coordenadas)
5. ✅ **Auto-Clean** - AutoCleanPanel (peixes, intervalos, macros)
6. ✅ **Analytics** - AnalyticsPanel (estatísticas, gráficos, export)
7. ✅ **Configuration** - ConfigPanel + AdvancedConfigPanel
8. ✅ **I18N** - Integrado em todos os painéis (PT/EN/RU)
9. ✅ **Server Connection** - ServerConnectionPanel (Fase 2/3)
10. ✅ **Arduino Control** - Integrado no ServerConnectionPanel
11. ✅ **Anti-Detection** - AdvancedConfigPanel
12. ✅ **Logging** - AdvancedConfigPanel
13. ✅ **Licensing** - Integrado no sistema

**NENHUM sistema foi esquecido** - a UI está completa e abrangente! 🎯

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Criar plano completo de reestrutura\u00e7\u00e3o do c\u00f3digo", "status": "completed", "activeForm": "Completado plano detalhado"}, {"content": "Definir arquitetura modular para 3 componentes (PC + Servidor + Arduino)", "status": "completed", "activeForm": "Arquitetura definida"}, {"content": "Especificar estrutura de arquivos e m\u00f3dulos", "status": "completed", "activeForm": "Estrutura especificada"}, {"content": "Criar guia de implementa\u00e7\u00e3o passo a passo", "status": "in_progress", "activeForm": "Criando guia passo a passo"}, {"content": "Definir protocolos de comunica\u00e7\u00e3o entre componentes", "status": "completed", "activeForm": "Protocolos definidos"}]
#!/usr/bin/env python3
"""
🔐 Validador de Licença
Reutiliza sistema de licenciamento existente
"""

import os
import hashlib
import platform
import uuid
import json
from typing import Optional

class LicenseValidator:
    """Validador de licença reutilizando sistema existente"""
    
    def __init__(self):
        self.license_file = "data/license.key"
        self.license_info_file = "data/license_info.json"
        
    def get_hardware_fingerprint(self) -> str:
        """Gerar fingerprint do hardware (mesmo método do código atual)"""
        try:
            # Informações do sistema
            system_info = [
                platform.system(),
                platform.release(),
                platform.machine(),
                str(uuid.getnode()),  # MAC address
                platform.processor()
            ]
            
            # Criar hash das informações
            fingerprint_data = "|".join(system_info)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
            
            return fingerprint
            
        except Exception as e:
            print(f"Erro ao gerar fingerprint: {e}")
            return "DEFAULT_FINGERPRINT"
    
    def validate_license(self) -> bool:
        """Validar licença (versão simplificada para desenvolvimento)"""
        try:
            # Para desenvolvimento, sempre permitir se não houver licença
            if not os.path.exists(self.license_file):
                return self.create_development_license()
                
            # Ler arquivo de licença
            with open(self.license_file, 'r') as f:
                license_key = f.read().strip()
                
            # Validação básica (expandir conforme necessário)
            if len(license_key) >= 32:  # Mínimo de caracteres
                return True
                
            return False
            
        except Exception as e:
            print(f"Erro na validação de licença: {e}")
            return False
    
    def create_development_license(self) -> bool:
        """Criar licença de desenvolvimento temporária"""
        try:
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            
            # Gerar licença de desenvolvimento
            fingerprint = self.get_hardware_fingerprint()
            dev_license = f"DEV_{fingerprint}_{hashlib.md5(b'development').hexdigest()}"
            
            # Salvar licença
            with open(self.license_file, 'w') as f:
                f.write(dev_license)
                
            # Salvar informações da licença
            license_info = {
                "type": "development",
                "fingerprint": fingerprint,
                "created": "2024-01-01",
                "expires": "2025-12-31",
                "features": {
                    "fishing_bot": True,
                    "template_matching": True,
                    "auto_clean": True,
                    "feeding_system": True,
                    "rod_management": True
                }
            }
            
            with open(self.license_info_file, 'w') as f:
                json.dump(license_info, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Erro ao criar licença de desenvolvimento: {e}")
            return False
    
    def get_license_info(self) -> Optional[dict]:
        """Obter informações da licença"""
        try:
            if os.path.exists(self.license_info_file):
                with open(self.license_info_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao ler informações da licença: {e}")
            
        return None
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Verificar se uma feature está habilitada na licença"""
        license_info = self.get_license_info()
        if license_info and "features" in license_info:
            return license_info["features"].get(feature, False)
        return True  # Para desenvolvimento, habilitar tudo
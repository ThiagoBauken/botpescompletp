#!/usr/bin/env python3
"""
🔐 Ultimate Fishing Bot v4.0 - License Manager
Sistema de licenciamento com verificação online e hardware fingerprinting
"""

import os
import json
import hashlib
import platform
import requests
import psutil
from typing import Dict, Tuple, Optional
from datetime import datetime

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

class LicenseManager:
    """Gerenciador de licenças com validação online"""
    
    def __init__(self):
        self.license_file = "license.key"
        self.server_url = "https://private-keygen.pbzgje.easypanel.host"
        self.project_id = "67a4a76a-d71b-4d07-9ba8-f7e794ce0578"
        self.hardware_id = self.get_hardware_id()
        self.licensed = False
        self.license_data = {}

        _safe_print(f"Hardware ID: {self.hardware_id}")
    
    def get_hardware_id(self) -> str:
        """Gerar ID único e consistente da máquina"""
        try:
            machine_info = {
                'node': platform.node(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'system': platform.system(),
                'cpu_count': psutil.cpu_count(),
                'memory': psutil.virtual_memory().total
            }
            combined = json.dumps(machine_info, sort_keys=True)
            return hashlib.sha256(combined.encode()).hexdigest()[:32]
        except Exception as e:
            _safe_print(f"⚠️ Erro ao gerar Hardware ID: {e}")
            return "UNKNOWN-HARDWARE-ID"
    
    def load_license(self) -> Optional[str]:
        """Carregar licença salva do arquivo"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    license_key = f.read().strip()
                return license_key if license_key else None
        except Exception as e:
            _safe_print(f"⚠️ Erro ao carregar licença: {e}")
        return None
    
    def save_license(self, key: str) -> bool:
        """Salvar licença no arquivo"""
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                f.write(key)
            _safe_print("💾 Licença salva com sucesso!")
            return True
        except Exception as e:
            _safe_print(f"❌ Erro ao salvar licença: {e}")
            return False
    
    def validate_license(self, key: str) -> Tuple[bool, Dict]:
        """Validar licença no servidor"""
        _safe_print(f"🔍 Validando chave: {key[:10]}...")
        
        try:
            data = {
                'activation_key': key,
                'hardware_id': self.hardware_id,
                'project_id': self.project_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'UltimateFishingBot/4.0'
            }
            
            _safe_print(f"📤 Enviando dados para: {self.server_url}/validate")
            _safe_print(f"📋 Hardware ID: {self.hardware_id}")
            
            response = requests.post(
                f"{self.server_url}/validate",
                json=data,
                headers=headers,
                timeout=15
            )
            
            _safe_print(f"📥 Status Code: {response.status_code}")
            _safe_print(f"📄 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    is_valid = result.get('valid', False)
                    _safe_print(f"✅ Validação: {'Válida' if is_valid else 'Inválida'}")

                    if is_valid:
                        _safe_print(f"📅 Expira em: {result.get('expires_at', 'N/A')}")
                        _safe_print(f"📊 Status: {result.get('status', 'N/A')}")
                        _safe_print(f"🎯 Plano: {result.get('plan_name', 'N/A')}")
                        _safe_print(f"⏰ Dias restantes: {result.get('days_remaining', 'N/A')}")

                    return is_valid, result
                except ValueError as e:
                    _safe_print(f"❌ Erro JSON: {e}")
                    return False, {'message': 'Resposta inválida do servidor'}
            else:
                # Lógica do v3: retornar erro com status code e texto completo
                error_msg = f'Servidor retornou {response.status_code}: {response.text}'
                _safe_print(f"❌ {error_msg}")
                return False, {'message': error_msg}
                
        except requests.exceptions.ConnectionError:
            error_msg = "Erro de conexão - Verifique sua internet"
            _safe_print(f"❌ {error_msg}")
            return False, {'message': error_msg}
        except requests.exceptions.Timeout:
            error_msg = "Timeout - Servidor demorou para responder"
            _safe_print(f"❌ {error_msg}")
            return False, {'message': error_msg}
        except Exception as e:
            error_msg = f'Erro de validação: {str(e)}'
            _safe_print(f"❌ {error_msg}")
            return False, {'message': error_msg}
    
    def activate_license(self, key: str) -> Tuple[bool, Dict]:
        """Ativar nova licença no servidor"""
        _safe_print(f"🔐 Ativando chave: {key[:10]}...")
        
        try:
            data = {
                'activation_key': key,
                'hardware_id': self.hardware_id,
                'project_id': self.project_id
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'UltimateFishingBot/4.0'
            }
            
            _safe_print(f"📤 Enviando para: {self.server_url}/activate")
            _safe_print(f"📋 Hardware ID: {self.hardware_id}")

            response = requests.post(f"{self.server_url}/activate",
                                   json=data, headers=headers, timeout=15)

            _safe_print(f"📥 Status Code: {response.status_code}")
            _safe_print(f"📄 Response: {response.text[:200]}...")

            if response.status_code == 200:
                try:
                    result = response.json()
                    # Corrigido: verificar 'valid' ao invés de 'success'
                    if result.get('valid', False):
                        self.save_license(key)
                        _safe_print("✅ Ativação bem-sucedida!")
                        return True, "Ativação realizada com sucesso!"
                    else:
                        error_msg = result.get('message', 'Erro desconhecido na ativação')
                        _safe_print(f"❌ Falha na ativação: {error_msg}")
                        return False, error_msg
                except ValueError as e:
                    _safe_print(f"❌ Erro JSON na ativação: {e}")
                    return False, "Resposta inválida do servidor"
            elif response.status_code == 403:
                error_msg = "Chave inválida, expirada ou já usada em outro dispositivo"
                _safe_print(f"❌ {error_msg}")
                return False, error_msg
            elif response.status_code == 400:
                error_msg = "Dados de ativação inválidos"
                _safe_print(f"❌ {error_msg}")
                return False, error_msg
            else:
                error_msg = f"Servidor retornou {response.status_code}: {response.text}"
                _safe_print(f"❌ {error_msg}")
                return False, error_msg

        except requests.exceptions.ConnectionError:
            error_msg = "Erro de conexão - Verifique sua internet"
            _safe_print(f"❌ {error_msg}")
            return False, error_msg
        except requests.exceptions.Timeout:
            error_msg = "Timeout - Servidor demorou para responder"
            _safe_print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro na ativação: {str(e)}"
            _safe_print(f"❌ {error_msg}")
            return False, error_msg
    
    def check_license(self) -> bool:
        """Verificar licença existente ou solicitar nova"""
        _safe_print("\n🔐 Verificando licença...")
        
        # Tentar carregar licença existente
        saved_key = self.load_license()
        
        if saved_key:
            _safe_print("🔑 Licença encontrada, validando...")
            valid, data = self.validate_license(saved_key)
            
            if valid:
                _safe_print("✅ Licença válida!")
                return True
            else:
                _safe_print(f"❌ Licença inválida: {data.get('message', 'Erro desconhecido')}")
                # Remover licença inválida
                try:
                    os.remove(self.license_file)
                except:
                    pass
        
        # Licença não encontrada ou inválida
        _safe_print("🔐 Licença necessária para continuar.")
        _safe_print("📄 Solicite sua licença do Ultimate Fishing Bot v4.0")
        _safe_print(f"🆔 Hardware ID: {self.hardware_id}")
        _safe_print("💡 Entre em contato para obter sua chave de licença.")
        
        return False
    
    def get_license_info(self) -> Dict:
        """Obter informações da licença atual"""
        return self.license_data.copy() if self.licensed else {}
    
    def is_licensed(self) -> bool:
        """Verificar se o sistema está licenciado"""
        return self.licensed
    
    def get_hardware_id_display(self) -> str:
        """Obter Hardware ID formatado para exibição"""
        return f"{self.hardware_id[:8]}-{self.hardware_id[8:16]}-{self.hardware_id[16:24]}-{self.hardware_id[24:32]}"
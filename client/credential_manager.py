#!/usr/bin/env python3
"""
🔐 Credential Manager
Gerencia salvamento/carregamento de credenciais (login/senha/license_key)

✅ CORREÇÃO: Usa AppData para salvar credenciais (persistente em .exe)
"""

import json
import os
import sys
import base64
import re
from pathlib import Path

# 🔐 CORREÇÃO DE SEGURANÇA: Importar AES-256 para criptografia forte
try:
    from utils.crypto_manager import CryptoManager
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def _safe_print(text):
    """Print com fallback para caracteres Unicode/emoji"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class CredentialManager:
    """
    Gerenciador de credenciais

    Salva credenciais localmente de forma ofuscada (base64)
    Armazena: login, senha, license_key
    """

    def __init__(self, credentials_file=None):
        """
        Inicializar gerenciador

        Args:
            credentials_file: Caminho do arquivo de credenciais (None = usar AppData)

        ✅ CORREÇÃO: Por padrão usa AppData (persistente em .exe compilado)
        """
        if credentials_file is None:
            # ✅ Usar AppData para persistência (funciona em .exe compilado)
            appdata = Path(os.getenv('APPDATA', os.path.expanduser('~')))
            data_dir = appdata / "FishingMageBot"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.credentials_file = str(data_dir / "credentials.dat")
            _safe_print(f"🔐 Credenciais serão salvas em: {self.credentials_file}")
        else:
            # Usar path customizado (para testes)
            self.credentials_file = credentials_file
            credentials_path = Path(credentials_file)
            credentials_path.parent.mkdir(parents=True, exist_ok=True)

        # 🔐 CORREÇÃO DE SEGURANÇA: Inicializar criptografia AES-256
        if CRYPTO_AVAILABLE:
            self.crypto = CryptoManager()
            _safe_print("🔐 Criptografia AES-256 ativada para credenciais")
        else:
            self.crypto = None
            _safe_print("⚠️ Criptografia não disponível, usando fallback")

    def save_credentials(self, username: str = None, password: str = None, license_key: str = None, login: str = None) -> bool:
        """
        Salvar credenciais localmente

        Args:
            username: Username (compatibilidade novo AuthDialog)
            password: Senha do usuário
            license_key: License key
            login: Login (compatibilidade versão antiga)

        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # ✅ CORREÇÃO: Validar que todos os campos obrigatórios foram passados
            if not password or not license_key:
                raise ValueError("password e license_key são obrigatórios")

            # Aceitar username OU login (compatibilidade)
            user_login = username or login
            if not user_login:
                raise ValueError("username ou login é obrigatório")

            # Criar dicionário de credenciais
            credentials = {
                "login": user_login,
                "username": user_login,  # Duplicar para compatibilidade
                "password": password,
                "license_key": license_key
            }

            # 🔐 CORREÇÃO DE SEGURANÇA: Usar AES-256 ao invés de Base64
            if self.crypto:
                # ✅ NOVO: Criptografar com AES-256
                encrypted = self.crypto.encrypt_dict(credentials)
                with open(self.credentials_file, 'w') as f:
                    f.write(encrypted)
                _safe_print(f"✅ Credenciais salvas com AES-256: {self.credentials_file}")
            else:
                # ⚠️ FALLBACK: Base64 (compatibilidade)
                json_str = json.dumps(credentials)
                encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                with open(self.credentials_file, 'w') as f:
                    f.write(encoded)
                _safe_print(f"⚠️ Credenciais salvas com Base64 (fallback): {self.credentials_file}")

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao salvar credenciais: {e}")
            return False

    def load_credentials(self) -> dict:
        """
        Carregar credenciais salvas

        🔐 COMPATIBILIDADE RETROATIVA:
        - Tenta descriptografar AES-256 primeiro (novo formato)
        - Se falhar, tenta Base64 (formato antigo)
        - Converte automaticamente para AES-256 no próximo save

        Returns:
            dict ou None:
                {
                    "login": str,
                    "password": str,
                    "license_key": str
                }
        """
        try:
            # Verificar se arquivo existe
            if not os.path.exists(self.credentials_file):
                _safe_print(f"ℹ️ Arquivo de credenciais não encontrado: {self.credentials_file}")
                return None

            # Ler arquivo
            with open(self.credentials_file, 'r') as f:
                stored_data = f.read().strip()

            if not stored_data:
                return None

            credentials = None

            # 🔐 TENTATIVA 1: Descriptografar AES-256 (formato novo)
            if self.crypto:
                try:
                    credentials = self.crypto.decrypt_dict(stored_data)
                    _safe_print(f"✅ Credenciais carregadas (AES-256): {credentials.get('login', 'N/A')}")
                except Exception as e:
                    _safe_print(f"⚠️ Não é AES-256, tentando Base64 (formato antigo)...")
                    credentials = None

            # ⚠️ TENTATIVA 2: Decodificar Base64 (formato antigo - compatibilidade)
            if credentials is None:
                try:
                    json_str = base64.b64decode(stored_data.encode('utf-8')).decode('utf-8')
                    credentials = json.loads(json_str)
                    _safe_print(f"✅ Credenciais carregadas (Base64 antigo): {credentials.get('login', 'N/A')}")
                    _safe_print("💡 Recomendado: Faça logout e login novamente para converter para AES-256")
                except Exception as e:
                    _safe_print(f"❌ Formato desconhecido: {e}")
                    return None

            # Validar campos obrigatórios
            if credentials:
                required_fields = ["login", "password", "license_key"]
                for field in required_fields:
                    if field not in credentials:
                        _safe_print(f"❌ Campo ausente nas credenciais: {field}")
                        return None

                return credentials

            return None

        except Exception as e:
            _safe_print(f"❌ Erro ao carregar credenciais: {e}")
            return None

    def delete_credentials(self) -> bool:
        """
        Deletar credenciais salvas

        Returns:
            bool: True se deletou com sucesso
        """
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                _safe_print(f"✅ Credenciais deletadas: {self.credentials_file}")
                return True
            else:
                _safe_print(f"ℹ️ Arquivo de credenciais não existe")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao deletar credenciais: {e}")
            return False

    def has_saved_credentials(self) -> bool:
        """
        Verificar se existem credenciais salvas

        Returns:
            bool: True se existe arquivo de credenciais
        """
        return os.path.exists(self.credentials_file)


# ═══════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    manager = CredentialManager()

    # Teste 1: Salvar credenciais
    print("\n=== TESTE 1: Salvar credenciais ===")
    manager.save_credentials(
        login="usuario@teste.com",
        password="senha123",
        license_key="TEST-KEY-12345"
    )

    # Teste 2: Carregar credenciais
    print("\n=== TESTE 2: Carregar credenciais ===")
    credentials = manager.load_credentials()
    if credentials:
        print(f"Login: {credentials['login']}")
        print(f"Senha: {'*' * len(credentials['password'])}")
        print(f"License: {credentials['license_key'][:10]}...")

    # Teste 3: Verificar se existe
    print("\n=== TESTE 3: Verificar se existe ===")
    print(f"Tem credenciais salvas? {manager.has_saved_credentials()}")

    # Teste 4: Deletar
    print("\n=== TESTE 4: Deletar credenciais ===")
    manager.delete_credentials()
    print(f"Tem credenciais salvas? {manager.has_saved_credentials()}")

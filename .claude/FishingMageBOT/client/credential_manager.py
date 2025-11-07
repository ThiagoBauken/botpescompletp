#!/usr/bin/env python3
"""
🔐 Credential Manager
Gerencia salvamento/carregamento de credenciais (login/senha/license_key)
"""

import json
import os
import base64
from pathlib import Path


class CredentialManager:
    """
    Gerenciador de credenciais

    Salva credenciais localmente de forma ofuscada (base64)
    Armazena: login, senha, license_key
    """

    def __init__(self, credentials_file="data/credentials.dat"):
        """
        Inicializar gerenciador

        Args:
            credentials_file: Caminho do arquivo de credenciais
        """
        self.credentials_file = credentials_file

        # Criar diretório data/ se não existir
        credentials_path = Path(credentials_file)
        credentials_path.parent.mkdir(parents=True, exist_ok=True)

    def save_credentials(self, login: str, password: str, license_key: str) -> bool:
        """
        Salvar credenciais localmente

        Args:
            login: Login do usuário
            password: Senha do usuário
            license_key: License key

        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Criar dicionário de credenciais
            credentials = {
                "login": login,
                "password": password,
                "license_key": license_key
            }

            # Converter para JSON
            json_str = json.dumps(credentials)

            # Ofuscar com base64 (simples mas funcional)
            encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

            # Salvar em arquivo
            with open(self.credentials_file, 'w') as f:
                f.write(encoded)

            print(f"✅ Credenciais salvas: {self.credentials_file}")
            return True

        except Exception as e:
            print(f"❌ Erro ao salvar credenciais: {e}")
            return False

    def load_credentials(self) -> dict:
        """
        Carregar credenciais salvas

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
                print(f"ℹ️ Arquivo de credenciais não encontrado: {self.credentials_file}")
                return None

            # Ler arquivo
            with open(self.credentials_file, 'r') as f:
                encoded = f.read()

            # Decodificar base64
            json_str = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')

            # Parsear JSON
            credentials = json.loads(json_str)

            # Validar campos obrigatórios
            required_fields = ["login", "password", "license_key"]
            for field in required_fields:
                if field not in credentials:
                    print(f"❌ Campo ausente nas credenciais: {field}")
                    return None

            print(f"✅ Credenciais carregadas: {credentials['login']}")
            return credentials

        except Exception as e:
            print(f"❌ Erro ao carregar credenciais: {e}")
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
                print(f"✅ Credenciais deletadas: {self.credentials_file}")
                return True
            else:
                print(f"ℹ️ Arquivo de credenciais não existe")
                return False

        except Exception as e:
            print(f"❌ Erro ao deletar credenciais: {e}")
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

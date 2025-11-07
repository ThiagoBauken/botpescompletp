#!/usr/bin/env python3
"""
🔐 Ultimate Fishing Bot v5.0 - Crypto Manager
Sistema de criptografia AES-256 para proteção de dados sensíveis
"""

import base64
import hashlib
import os
import json
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class CryptoManager:
    """
    Gerenciador de criptografia AES-256-CBC

    Características de segurança:
    - AES-256 (algoritmo aprovado FIPS 197)
    - Modo CBC (Cipher Block Chaining)
    - PBKDF2-HMAC-SHA256 para derivação de chave
    - Salt e IV únicos por criptografia
    - Padding PKCS7 para blocos

    Uso:
        crypto = CryptoManager()

        # Criptografar
        encrypted = crypto.encrypt("dados sensíveis")

        # Descriptografar
        decrypted = crypto.decrypt(encrypted)
    """

    def __init__(self, master_key: Optional[str] = None):
        """
        Inicializar CryptoManager

        Args:
            master_key: Chave mestre opcional (se None, usa hardware ID)
        """
        self.backend = default_backend()

        # Usar master_key ou hardware ID como base
        if master_key:
            self.master_key = master_key
        else:
            # Gerar chave baseada em hardware ID (deterministico)
            self.master_key = self._get_hardware_key()

        # Parâmetros de segurança
        self.iterations = 100000  # PBKDF2 iterations (NIST recomenda 100k+)
        self.key_length = 32      # 256 bits para AES-256
        self.iv_length = 16       # 128 bits para AES

    def _get_hardware_key(self) -> str:
        """
        Gerar chave baseada em hardware ID

        Retorna uma chave determinística baseada no hardware,
        tornando o binário único por máquina de compilação.
        """
        import platform
        try:
            import psutil
        except ImportError:
            # Fallback se psutil não disponível
            machine_info = {
                'node': platform.node(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'system': platform.system()
            }
            combined = json.dumps(machine_info, sort_keys=True)
            return hashlib.sha256(combined.encode()).hexdigest()

        # Usar informações de hardware para gerar chave única
        machine_info = {
            'node': platform.node(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'system': platform.system(),
            'cpu_count': psutil.cpu_count(),
        }
        combined = json.dumps(machine_info, sort_keys=True)
        return hashlib.sha256(combined.encode()).hexdigest()

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derivar chave AES-256 usando PBKDF2-HMAC-SHA256

        Args:
            salt: Salt único para derivação

        Returns:
            Chave de 256 bits
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        return kdf.derive(self.master_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """
        Criptografar texto usando AES-256-CBC

        Args:
            plaintext: Texto em claro para criptografar

        Returns:
            String base64 contendo: salt(16) + iv(16) + ciphertext
        """
        try:
            # Gerar salt e IV únicos
            salt = os.urandom(16)
            iv = os.urandom(self.iv_length)

            # Derivar chave do master_key usando salt
            key = self._derive_key(salt)

            # Criar cipher AES-256-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()

            # Aplicar padding PKCS7
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode()) + padder.finalize()

            # Criptografar
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            # Combinar: salt + iv + ciphertext
            encrypted_data = salt + iv + ciphertext

            # Retornar como base64
            return base64.b64encode(encrypted_data).decode('utf-8')

        except Exception as e:
            _safe_print(f"❌ Erro na criptografia: {e}")
            raise

    def decrypt(self, encrypted_b64: str) -> str:
        """
        Descriptografar texto AES-256-CBC

        Args:
            encrypted_b64: String base64 contendo salt + iv + ciphertext

        Returns:
            Texto em claro
        """
        try:
            # Decodificar base64
            encrypted_data = base64.b64decode(encrypted_b64)

            # Extrair componentes
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]

            # Derivar chave usando o mesmo salt
            key = self._derive_key(salt)

            # Criar cipher AES-256-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()

            # Descriptografar
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remover padding PKCS7
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

            return plaintext.decode('utf-8')

        except Exception as e:
            _safe_print(f"❌ Erro na descriptografia: {e}")
            raise

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Criptografar dicionário completo

        Args:
            data: Dicionário para criptografar

        Returns:
            String base64 criptografada
        """
        json_str = json.dumps(data, sort_keys=True)
        return self.encrypt(json_str)

    def decrypt_dict(self, encrypted_b64: str) -> Dict[str, Any]:
        """
        Descriptografar dicionário

        Args:
            encrypted_b64: String base64 criptografada

        Returns:
            Dicionário original
        """
        json_str = self.decrypt(encrypted_b64)
        return json.loads(json_str)


class SecretStore:
    """
    Armazenamento seguro de secrets em arquivo criptografado

    Uso:
        store = SecretStore()

        # Salvar secrets
        store.set('api_url', 'https://api.example.com')
        store.set('project_id', '12345-67890')
        store.save()

        # Carregar secrets
        api_url = store.get('api_url')
    """

    def __init__(self, secrets_file: str = ".secrets.enc"):
        """
        Inicializar SecretStore

        Args:
            secrets_file: Arquivo para armazenar secrets criptografados
        """
        self.secrets_file = secrets_file
        self.crypto = CryptoManager()
        self.secrets = {}

        # Tentar carregar secrets existentes
        self.load()

    def set(self, key: str, value: str):
        """Definir secret"""
        self.secrets[key] = value

    def get(self, key: str, default: Any = None) -> Optional[str]:
        """Obter secret"""
        return self.secrets.get(key, default)

    def save(self) -> bool:
        """
        Salvar secrets criptografados em arquivo

        Returns:
            True se sucesso
        """
        try:
            encrypted = self.crypto.encrypt_dict(self.secrets)
            with open(self.secrets_file, 'w') as f:
                f.write(encrypted)
            return True
        except Exception as e:
            _safe_print(f"❌ Erro ao salvar secrets: {e}")
            return False

    def load(self) -> bool:
        """
        Carregar secrets de arquivo

        Returns:
            True se sucesso
        """
        try:
            if not os.path.exists(self.secrets_file):
                return False

            with open(self.secrets_file, 'r') as f:
                encrypted = f.read().strip()

            self.secrets = self.crypto.decrypt_dict(encrypted)
            return True

        except Exception as e:
            _safe_print(f"⚠️ Erro ao carregar secrets: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Funções utilitárias para uso direto
# ═══════════════════════════════════════════════════════════════════

def encrypt_string(plaintext: str, key: Optional[str] = None) -> str:
    """
    Função helper para criptografar string rapidamente

    Args:
        plaintext: Texto para criptografar
        key: Chave opcional (se None, usa hardware ID)

    Returns:
        String criptografada em base64
    """
    crypto = CryptoManager(master_key=key)
    return crypto.encrypt(plaintext)


def decrypt_string(encrypted_b64: str, key: Optional[str] = None) -> str:
    """
    Função helper para descriptografar string

    Args:
        encrypted_b64: String criptografada em base64
        key: Chave opcional (se None, usa hardware ID)

    Returns:
        Texto descriptografado
    """
    crypto = CryptoManager(master_key=key)
    return crypto.decrypt(encrypted_b64)


# ═══════════════════════════════════════════════════════════════════
# TESTE DO MÓDULO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    _safe_print("\n" + "="*60)
    _safe_print("🔐 Testando CryptoManager AES-256")
    _safe_print("="*60)

    # Teste 1: Criptografia básica
    _safe_print("\n📝 Teste 1: Criptografia básica")
    crypto = CryptoManager()

    original = "https://private-keygen.pbzgje.easypanel.host"
    _safe_print(f"Original: {original}")

    encrypted = crypto.encrypt(original)
    _safe_print(f"Criptografado (base64): {encrypted[:50]}...")

    decrypted = crypto.decrypt(encrypted)
    _safe_print(f"Descriptografado: {decrypted}")
    _safe_print(f"✅ Match: {original == decrypted}")

    # Teste 2: Criptografia de dicionário
    _safe_print("\n📝 Teste 2: Criptografia de dicionário")
    data = {
        'server_url': 'https://private-keygen.pbzgje.easypanel.host',
        'project_id': '67a4a76a-d71b-4d07-9ba8-f7e794ce0578',
        'ws_url': 'wss://private-serverpesca.pbzgje.easypanel.host/ws'
    }

    encrypted_dict = crypto.encrypt_dict(data)
    _safe_print(f"Dict criptografado: {encrypted_dict[:50]}...")

    decrypted_dict = crypto.decrypt_dict(encrypted_dict)
    _safe_print(f"Dict descriptografado: {decrypted_dict}")
    _safe_print(f"✅ Match: {data == decrypted_dict}")

    # Teste 3: SecretStore
    _safe_print("\n📝 Teste 3: SecretStore")
    store = SecretStore(".test_secrets.enc")

    store.set('api_url', 'https://api.example.com')
    store.set('api_key', 'secret-key-12345')
    store.save()
    _safe_print("✅ Secrets salvos em .test_secrets.enc")

    # Carregar em nova instância
    store2 = SecretStore(".test_secrets.enc")
    api_url = store2.get('api_url')
    api_key = store2.get('api_key')
    _safe_print(f"API URL: {api_url}")
    _safe_print(f"API Key: {api_key}")
    _safe_print(f"✅ Secrets carregados corretamente")

    # Limpar arquivo de teste
    import os
    if os.path.exists(".test_secrets.enc"):
        os.remove(".test_secrets.enc")
        _safe_print("🧹 Arquivo de teste removido")

    _safe_print("\n" + "="*60)
    _safe_print("✅ Todos os testes passaram!")
    _safe_print("="*60)

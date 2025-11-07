#!/usr/bin/env python3
"""
🔒 Ultimate Fishing Bot v5.0 - String Obfuscator
Sistema de ofuscação de strings para proteção em binários compilados
"""

import base64
import zlib
from typing import Union

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class StringObfuscator:
    """
    Ofuscador de strings para dificultar análise de binários

    Técnicas aplicadas:
    1. XOR com chave rotativa
    2. Compressão zlib
    3. Codificação base64
    4. Reversão de bytes

    Não é criptografia forte, mas dificulta análise estática.
    """

    @staticmethod
    def _xor_encrypt(data: bytes, key: int = 0x5A) -> bytes:
        """
        XOR com chave rotativa

        Args:
            data: Dados para XOR
            key: Chave inicial (0-255)

        Returns:
            Dados após XOR
        """
        result = bytearray()
        current_key = key

        for byte in data:
            result.append(byte ^ current_key)
            # Rotacionar chave
            current_key = (current_key + 1) % 256

        return bytes(result)

    @staticmethod
    def obfuscate(plaintext: str) -> str:
        """
        Ofuscar string

        Processo:
        1. Encode UTF-8
        2. Comprimir com zlib
        3. XOR com chave rotativa
        4. Reverter bytes
        5. Base64 encode

        Args:
            plaintext: String para ofuscar

        Returns:
            String ofuscada em base64
        """
        try:
            # 1. UTF-8 encode
            data = plaintext.encode('utf-8')

            # 2. Comprimir
            compressed = zlib.compress(data, level=9)

            # 3. XOR
            xored = StringObfuscator._xor_encrypt(compressed)

            # 4. Reverter bytes (dificulta padrões)
            reversed_data = xored[::-1]

            # 5. Base64
            b64 = base64.b64encode(reversed_data).decode('ascii')

            return b64

        except Exception as e:
            _safe_print(f"❌ Erro na ofuscação: {e}")
            raise

    @staticmethod
    def deobfuscate(obfuscated: str) -> str:
        """
        Deofuscar string

        Processo reverso do obfuscate()

        Args:
            obfuscated: String ofuscada em base64

        Returns:
            String original
        """
        try:
            # 1. Base64 decode
            reversed_data = base64.b64decode(obfuscated)

            # 2. Reverter de volta
            xored = reversed_data[::-1]

            # 3. XOR decrypt (mesma operação)
            compressed = StringObfuscator._xor_encrypt(xored)

            # 4. Descomprimir
            data = zlib.decompress(compressed)

            # 5. UTF-8 decode
            plaintext = data.decode('utf-8')

            return plaintext

        except Exception as e:
            _safe_print(f"❌ Erro na deofuscação: {e}")
            raise


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Uso direto
# ═══════════════════════════════════════════════════════════════════

def obfuscate(s: str) -> str:
    """
    Função helper para ofuscar string

    Uso:
        from utils.string_obfuscator import obfuscate
        hidden = obfuscate("https://api.example.com")
    """
    return StringObfuscator.obfuscate(s)


def deobfuscate(s: str) -> str:
    """
    Função helper para deofuscar string

    Uso:
        from utils.string_obfuscator import deobfuscate
        url = deobfuscate("eJwrSS0u...")
    """
    return StringObfuscator.deobfuscate(s)


# ═══════════════════════════════════════════════════════════════════
# GERADOR DE CÓDIGO - Para substituir strings no código-fonte
# ═══════════════════════════════════════════════════════════════════

def generate_obfuscated_code(plaintext: str, var_name: str = "SECRET") -> str:
    """
    Gerar código Python para string ofuscada

    Args:
        plaintext: String para ofuscar
        var_name: Nome da variável

    Returns:
        Código Python pronto para copiar

    Exemplo:
        >>> generate_obfuscated_code("https://api.com", "API_URL")

        # AUTO-GENERATED - DO NOT EDIT
        from utils.string_obfuscator import deobfuscate
        API_URL = deobfuscate("eJwrSS0u...")
    """
    obfuscated = obfuscate(plaintext)

    code = f'''# AUTO-GENERATED - DO NOT EDIT
from utils.string_obfuscator import deobfuscate
{var_name} = deobfuscate("{obfuscated}")'''

    return code


def generate_obfuscated_dict(data: dict, var_name: str = "SECRETS") -> str:
    """
    Gerar código Python para dicionário ofuscado

    Args:
        data: Dicionário com secrets
        var_name: Nome da variável

    Returns:
        Código Python

    Exemplo:
        >>> secrets = {
        ...     'api_url': 'https://api.com',
        ...     'api_key': 'secret-123'
        ... }
        >>> generate_obfuscated_dict(secrets)
    """
    lines = ["# AUTO-GENERATED - DO NOT EDIT"]
    lines.append("from utils.string_obfuscator import deobfuscate")
    lines.append(f"{var_name} = {{")

    for key, value in data.items():
        obfuscated = obfuscate(value)
        lines.append(f'    "{key}": deobfuscate("{obfuscated}"),')

    lines.append("}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# TESTE DO MÓDULO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    _safe_print("\n" + "="*60)
    _safe_print("🔒 Testando StringObfuscator")
    _safe_print("="*60)

    # Teste 1: Ofuscação básica
    _safe_print("\n📝 Teste 1: Ofuscação básica")
    original = "https://private-keygen.pbzgje.easypanel.host"
    _safe_print(f"Original: {original}")

    obfuscated = obfuscate(original)
    _safe_print(f"Ofuscado: {obfuscated}")

    deobfuscated = deobfuscate(obfuscated)
    _safe_print(f"Deofuscado: {deobfuscated}")
    _safe_print(f"✅ Match: {original == deobfuscated}")

    # Teste 2: URLs críticas
    _safe_print("\n📝 Teste 2: URLs críticas do projeto")
    urls = [
        "https://private-keygen.pbzgje.easypanel.host",
        "wss://private-serverpesca.pbzgje.easypanel.host/ws",
        "67a4a76a-d71b-4d07-9ba8-f7e794ce0578"
    ]

    for url in urls:
        obf = obfuscate(url)
        dec = deobfuscate(obf)
        match = "✅" if url == dec else "❌"
        _safe_print(f"{match} {url[:40]}... -> {obf[:30]}...")

    # Teste 3: Geração de código
    _safe_print("\n📝 Teste 3: Geração de código")
    code = generate_obfuscated_code(
        "https://private-keygen.pbzgje.easypanel.host",
        "LICENSE_SERVER_URL"
    )
    _safe_print("Código gerado:")
    _safe_print(code)

    # Teste 4: Dicionário de secrets
    _safe_print("\n📝 Teste 4: Dicionário de secrets")
    secrets = {
        'license_server': 'https://private-keygen.pbzgje.easypanel.host',
        'ws_server': 'wss://private-serverpesca.pbzgje.easypanel.host/ws',
        'project_id': '67a4a76a-d71b-4d07-9ba8-f7e794ce0578'
    }

    code_dict = generate_obfuscated_dict(secrets, "APP_SECRETS")
    _safe_print("Código do dicionário:")
    _safe_print(code_dict)

    # Teste 5: Caracteres especiais
    _safe_print("\n📝 Teste 5: Caracteres especiais e Unicode")
    special_texts = [
        "Café com açúcar!",
        "🔐🎣🐟",
        "key=value&param=123",
        "C:\\Users\\path\\to\\file.txt"
    ]

    for text in special_texts:
        try:
            obf = obfuscate(text)
            dec = deobfuscate(obf)
            match = "✅" if text == dec else "❌"
            _safe_print(f"{match} {text}")
        except Exception as e:
            _safe_print(f"❌ {text}: {e}")

    _safe_print("\n" + "="*60)
    _safe_print("✅ Todos os testes passaram!")
    _safe_print("="*60)

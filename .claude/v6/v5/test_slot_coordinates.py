"""
Script de teste para calibrar coordenadas dos slots de vara

USO:
1. Abra o jogo e pressione "I" para abrir inventário
2. Execute este script: python test_slot_coordinates.py
3. O mouse vai se mover para cada slot
4. Observe se o mouse está no CENTRO do slot
5. Anote as coordenadas corretas se necessário
"""

import time
import pyautogui
import json

# Carregar configuração
with open('config/default_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

slot_positions = config['coordinates']['slot_positions']

print("=" * 60)
print("🎯 TESTE DE COORDENADAS DOS SLOTS")
print("=" * 60)
print("\n📋 INSTRUÇÕES:")
print("1. Abra o jogo e pressione 'I' para abrir inventário")
print("2. O mouse vai se mover para cada slot (1, 2, 3, 4, 5, 6)")
print("3. Observe se o mouse está NO CENTRO do slot")
print("4. Se estiver ERRADO, anote a posição correta\n")

input("Pressione ENTER quando estiver pronto...")

print("\n🖱️ Movendo mouse para os slots...")
print("-" * 60)

for slot_num in ['1', '2', '3', '4', '5', '6']:
    x, y = slot_positions[slot_num]

    print(f"\n📍 SLOT {slot_num}: ({x}, {y})")
    print(f"   Movendo mouse...")

    # Mover mouse para o slot
    pyautogui.moveTo(x, y, duration=0.5)

    # Aguardar para visualização
    time.sleep(2)

    # Perguntar se está correto
    resposta = input(f"   ✅ Mouse está NO CENTRO do Slot {slot_num}? (s/n): ").strip().lower()

    if resposta == 'n':
        print(f"   ❌ Slot {slot_num} está INCORRETO!")
        print(f"   📝 Mova o mouse MANUALMENTE para o centro do Slot {slot_num}")
        input(f"   Pressione ENTER quando o mouse estiver posicionado corretamente...")

        # Ler posição atual do mouse
        correct_x, correct_y = pyautogui.position()
        print(f"   ✅ Nova coordenada: ({correct_x}, {correct_y})")

        # Atualizar configuração
        slot_positions[slot_num] = [correct_x, correct_y]
        print(f"   💾 Coordenada salva!")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO!")
print("=" * 60)

# Perguntar se quer salvar
salvar = input("\n💾 Salvar coordenadas corrigidas no config? (s/n): ").strip().lower()

if salvar == 's':
    config['coordinates']['slot_positions'] = slot_positions

    with open('config/default_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("✅ Configuração salva em config/default_config.json")
    print("\n📋 NOVAS COORDENADAS:")
    for slot_num in ['1', '2', '3', '4', '5', '6']:
        x, y = slot_positions[slot_num]
        print(f"   Slot {slot_num}: ({x}, {y})")
else:
    print("❌ Configuração NÃO foi salva")

print("\n🎯 Coordenadas finais:")
print(json.dumps(slot_positions, indent=2))

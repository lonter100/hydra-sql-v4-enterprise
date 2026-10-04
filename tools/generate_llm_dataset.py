#!/usr/bin/env python3
"""
================================================================================
  GENERATOR I KONWERTER DUŻEGO ZBIORU DANYCH JSON DLA MODELI LLM ➔ HYDRA-SQL BINARY
================================================================================
"""

import json
import os
import struct
import time

JSON_FILE = "duzy_llm_dataset.json"
BIN_FILE = "baza_llm.bin"

# HYDRA-SQL Binary Record Format for LLM Dataset (128 Bytes per record):
# Pack format: uint32(id), 32s(prompt_topic), 48s(prompt_preview), 32s(model_name), uint16(tokens), uint16(score), uint8(cat)
# 4 + 32 + 48 + 32 + 2 + 2 + 1 + 7(pad) = 128 Bytes
STRUCT_FORMAT = "<I32s48s32sHHB"
RECORD_SIZE = 128

def generate_llm_json(filename=JSON_FILE, num_records=100000):
    print(f"\033[1;33m[1/3] Generowanie dużego pliku JSON dla LLM ('{filename}') z {num_records:,} promptami...\033[0m")
    
    prompts_templates = [
        ("Napisz kod w Pythonie do sortowania", "Oto czysty kod sortowania złożoności O(n log n) z opisem."),
        ("Jak działa pamięć cache L3 w CPU", "Pamięć cache L3 jest współdzielonym buforem SRAM blisko rdzeni."),
        ("Wyjaśnij pojęcie Zero-Copy mmap", "Zero-Copy polega na bezpośrednim mapowaniu stron z SSD do rejestrów."),
        ("Napisz skrypt do analizy danych SQL", "Użyj zapytań GROUP BY i agregacji SUM oraz AVG do podsumowania."),
        ("Jak wytrenować model językowy LLM", "Trening LLM wymaga fazy Pre-training na wielkich korpusach i SFT.")
    ]
    
    models = ["Qwen-2.5-7B-Instruct", "Llama-3-70B-Instruct", "DeepSeek-V3-MoE", "Claude-3.5-Sonnet", "GPT-4o-Turbo"]
    
    t0 = time.perf_counter()
    data = []
    for i in range(1, num_records + 1):
        tmpl = prompts_templates[i % len(prompts_templates)]
        model = models[i % len(models)]
        tokens = 128 + (i % 2048)
        score = 800 + (i % 200)
        
        data.append({
            "id": i,
            "topic": f"{tmpl[0]} #{i}",
            "response_preview": f"{tmpl[1]} (id: {i})",
            "model_name": model,
            "tokens": tokens,
            "score": score,
            "category": i % 8
        })
        
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    t1 = time.perf_counter()
    
    json_size_mb = os.path.getsize(filename) / (1024.0 * 1024.0)
    print(f"  \033[1;31m[!] Plik JSON dla LLM został utworzony: {json_size_mb:.2f} MB na dysku (Czas: {t1-t0:.2f}s)\033[0m")
    return filename

def convert_json_to_hydra_binary(json_filename=JSON_FILE, bin_filename=BIN_FILE):
    print(f"\n\033[1;33m[2/3] Konwersja JSON ➔ HYDRA-SQL Zero-Copy Binary ('{bin_filename}')...\033[0m")
    
    t0 = time.perf_counter()
    with open(json_filename, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    with open(bin_filename, "wb") as f_out:
        for r in records:
            r_id = int(r["id"])
            topic = r["topic"].encode("utf-8")[:31]
            response = r["response_preview"].encode("utf-8")[:47]
            model = r["model_name"].encode("utf-8")[:31]
            tokens = int(r["tokens"])
            score = int(r["score"])
            cat = int(r["category"])
            
            # Pack fixed 128-byte binary struct payload
            raw_struct = struct.pack(STRUCT_FORMAT, r_id, topic, response, model, tokens, score, cat)
            pad_needed = RECORD_SIZE - len(raw_struct)
            if pad_needed > 0:
                raw_struct += b'\x00' * pad_needed
                
            f_out.write(raw_struct)
            
    t1 = time.perf_counter()
    
    json_mb = os.path.getsize(json_filename) / (1024.0 * 1024.0)
    bin_mb = os.path.getsize(bin_filename) / (1024.0 * 1024.0)
    pct = (1.0 - (bin_mb / json_mb)) * 100.0
    
    print(f"  \033[1;32m[+] Sukces! Konwersja zakończona w {t1-t0:.3f} sekundy.\033[0m")
    print(f"      Rozmiar wejściowy JSON : \033[1;31m{json_mb:.2f} MB\033[0m")
    print(f"      Rozmiar HYDRA Binary   : \033[1;32m{bin_mb:.2f} MB\033[0m")
    print(f"      \033[1;33m➔ Redukcja rozmiaru na dysku: {pct:.1f}% MNIEJSZY PLIK!\033[0m\n")

def main():
    print("=" * 80)
    print("   GENERATOR DUŻEGO ZBIORU DANYCH LLM I KONWERTER DO HYDRA-SQL BINARY")
    print("=" * 80 + "\n")
    
    generate_llm_json()
    convert_json_to_hydra_binary()

if __name__ == "__main__":
    main()

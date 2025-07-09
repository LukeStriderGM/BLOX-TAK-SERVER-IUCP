#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === PREFERENCE FILE (.pref) GENERATOR ===
# === GENERATOR PLIKU PREFERENCJI (.pref) ===
# =====================================================================================

import os
import time
import yaml


# =====================================================================================
# === HELPER FUNCTIONS ===
# === FUNKCJE POMOCNICZE ===
# =====================================================================================

def load_config(path="config.yaml"):
    """
    Loads and returns the configuration from a YAML file.

    Wczytuje i zwraca konfigurację z pliku YAML.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{path}' nie został znaleziony!")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}")
        print(f"BŁĄD: Nie udało się wczytać pliku konfiguracyjnego: {e}")
        return None


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def generate_pref_file():
    """
    The main function that generates the .pref file.

    Główna funkcja generująca plik .pref.
    """
    print("*********************************")
    print("* Generating: 'PREF' File       *")
    print("* Generowanie pliku 'PREF'      *")
    print("*********************************")
    time.sleep(2)

    # --- Step 1: Load configuration ---
    # --- Krok 1: Wczytanie konfiguracji ---
    config = load_config()
    if not config:
        return

    try:
        external_ip = config['network']['external_ip']
        pref_output_path = config['paths']['preferences_output']
    except KeyError as e:
        print(f"ERROR: Missing key in config.yaml: {e}")
        print(f"BŁĄD: Brakujący klucz w config.yaml: {e}")
        return

    # --- Step 2: Define XML content ---
    # --- Krok 2: Zdefiniowanie treści XML ---
    config_pref_content = f"""<?xml version="1.0" standalone="yes"?>
<preferences>
    <preference version="1" name="cot_streams">
        <entry key="count" class="class java.lang.Integer">1</entry>
        <entry key="description0" class="class java.lang.String">BLOX-TAK-SERVER</entry>
        <entry key="enabled0" class="class java.lang.Boolean">true</entry>
        <entry key="connectString0" class="class java.lang.String">{external_ip}:8089:ssl</entry>
    </preference>
    <preference version="1" name="com.atakmap.app_preferences">
        <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
    </preference>
</preferences>
"""

    # --- Step 3: Build the full output path and save the file ---
    # --- Krok 3: Zbudowanie pełnej ścieżki i zapis pliku ---
    output_file_path = os.path.join(pref_output_path, "config.pref")

    try:
        # Ensure the output directory exists
        # Upewnij się, że katalog wyjściowy istnieje
        os.makedirs(pref_output_path, exist_ok=True)

        with open(output_file_path, "w", encoding='utf-8') as file:
            file.write(config_pref_content)

        print("*********************************")
        print("* 'PREF' File Generated         *")
        print("* Plik 'PREF' wygenerowany      *")
        print("*********************************")
        print(f"File saved to: {output_file_path}")
        print(f"Plik zapisano w: {output_file_path}")
        time.sleep(3)
        os.system("clear || cls")

    except Exception as e:
        print(f"ERROR: Failed to write .pref file: {e}")
        print(f"BŁĄD: Nie udało się zapisać pliku .pref: {e}")


if __name__ == "__main__":
    generate_pref_file()
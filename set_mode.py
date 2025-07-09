#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === SCRIPT TO INTERACTIVELY SET THE EXECUTION MODE (local/remote) ===
# === SKRYPT DO INTERAKTYWNEGO USTAWIANIA TRYBU PRACY (local/remote) ===
# =====================================================================================

import os
import yaml

# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def set_execution_mode(config_path: str = "config.yaml"):
    """
    Interactively prompts the user to select an execution mode ('local' or 'remote')
    and updates the corresponding value in the YAML configuration file.

    Interaktywnie pyta użytkownika o wybór trybu wykonania ('local' lub 'remote')
    i aktualizuje odpowiednią wartość w pliku konfiguracyjnym YAML.
    """
    # --- Step 1: Check for the existence of the configuration file ---
    # --- Krok 1: Sprawdzenie dostępności pliku konfiguracyjnego ---
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file '{config_path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{config_path}' nie został znaleziony!")
        return

    # --- Step 2: Interactive loop for user mode selection ---
    # --- Krok 2: Pętla interaktywnego wyboru trybu przez użytkownika ---
    while True:
        print("\n" + "="*60)
        print("=== SCRIPT EXECUTION MODE SELECTION ===")
        print("=== WYBÓR TRYBU PRACY SKRYPTÓW ===")
        print("="*60)
        print("  [1] Local Mode - Operations will be performed on this machine.")
        print("      Tryb LOKALNY - Operacje będą wykonywane na tej maszynie.\n")
        print("  [2] Remote Mode - Operations will be performed on a remote server via SSH.")
        print("      Tryb ZDALNY - Operacje będą wykonywane na zdalnym serwerze przez SSH.")
        print("="*60)

        print("Choose mode [1 or 2]:")
        choice = input("Wybierz tryb [1 lub 2]: ").strip()

        if choice == '1':
            selected_mode = 'local'
            break
        elif choice == '2':
            selected_mode = 'remote'
            break
        else:
            print("\nINVALID CHOICE! Please enter '1' or '2'.")
            print("BŁĘDNY WYBÓR! Proszę wprowadzić '1' lub '2'.")

    # --- Step 3: Load, update, and save the YAML file ---
    # --- Krok 3: Wczytanie, aktualizacja i zapis pliku YAML ---
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)

        # Update the value in the dictionary
        # Aktualizacja wartości w słowniku
        if 'execution' in config_data and isinstance(config_data['execution'], dict):
            config_data['execution']['mode'] = selected_mode
        else:
            # If the 'execution' section does not exist, it can be added
            # Jeśli sekcja 'execution' nie istnieje, można ją dodać
            config_data['execution'] = {'mode': selected_mode}
            print(f"\nWARNING: 'execution' section missing in the file. It has been added.")
            print(f"OSTRZEŻENIE: Brak sekcji 'execution' w pliku. Została ona dodana.")

        # Save the updated configuration back to the file
        # Zapisanie zaktualizowanej konfiguracji z powrotem do pliku
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print("\n" + "*"*60)
        print(f"SUCCESS! Execution mode has been set to: '{selected_mode}'.")
        print(f"SUKCES! Tryb pracy został ustawiony na: '{selected_mode}'.")
        print("*"*60 + "\n")

    except yaml.YAMLError as e:
        print(f"\nERROR: Problem parsing the file '{config_path}': {e}")
        print(f"BŁĄD: Problem z parsowaniem pliku '{config_path}': {e}")
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred during the file operation: {e}")
        print(f"BŁĄD: Wystąpił nieoczekiwany problem podczas operacji na pliku: {e}")


if __name__ == "__main__":
    # Call the main function of the script
    # Wywołanie głównej funkcji skryptu
    set_execution_mode()
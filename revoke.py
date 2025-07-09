#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === CERTIFICATE REVOCATION ORCHESTRATOR ===
# === ORKIESTRATOR ODWOŁYWANIA CERTYFIKATÓW ===
# =====================================================================================

import os
import time
import pandas as pd
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
        print("ERROR: Configuration file '{path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{path}' nie został znaleziony!")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}")
        print(f"BŁĄD: Nie udało się wczytać pliku konfiguracyjnego: {e}")
        return None


def save_config(data, path="config.yaml"):
    """
    Saves the configuration dictionary to a YAML file.

    Zapisuje słownik konfiguracyjny do pliku YAML.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save config file: {e}")
        print(f"BŁĄD: Nie udało się zapisać pliku konfiguracyjnego: {e}")
        return False


def set_language():
    """
    Prompts the user to select a language and saves the choice to config.yaml.

    Pyta użytkownika o wybór języka i zapisuje go w pliku config.yaml.
    """
    while True:
        print("---")
        print("Select User Type:")
        print("Wybierz Typ Użytkownika:")
        print("[1] English")
        print("[2] Polski")
        print("---")

        prompt = "Choose and press Enter: "
        prompt_pl = "Wybierz i naciśnij Enter: "
        print(prompt)
        choice = input(prompt_pl).strip()

        if choice == "1":
            user_type = "EN"
            break
        elif choice == "2":
            user_type = "PL"
            break
        else:
            os.system("clear || cls")
            print("Invalid Choice")
            print("Niepoprawny Wybór")

    os.system("clear || cls")
    print(f"Selected: {user_type}")
    print(f"Wybrano: {user_type}")
    time.sleep(2)
    os.system("clear || cls")

    config = load_config()
    if config:
        config['user_management']['state']['user_type'] = user_type
        if save_config(config):
            return True
    return False


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def run_revocation_process():
    """
    The main function that orchestrates the entire certificate revocation process.

    Główna funkcja orkiestrująca całym procesem odwoływania certyfikatów.
    """
    if not set_language():
        exit(1)

    config = load_config()
    if not config:
        exit(1)

    user_type = config['user_management']['state']['user_type']
    data_sources = config['user_management']['data_sources']
    csv_path = data_sources.get(user_type.lower())

    if not csv_path:
        print(f"ERROR: No data source defined for language '{user_type}'.")
        print(f"BŁĄD: Brak zdefiniowanego źródła danych dla języka '{user_type}'.")
        exit(1)

    print("Loading user list for certificate revocation...")
    print("Wczytuję listę użytkowników do odwołania certyfikatów...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"ERROR: Failed to load data from CSV: {e}")
        print(f"BŁĄD: Nie udało się wczytać danych z CSV: {e}")
        exit(1)

    if user_type == "EN":
        column_name = 'Username:'
        print("\n--- Users to revoke ---")
    else:  # PL
        column_name = 'Nazwa Użytkownika:'
        print("\n--- Lista użytkowników do odwołania ---")

    print(df[column_name].to_string(index=False))
    print(f"\nNumber Of Users: {len(df)}")
    print(f"Liczba Użytkowników: {len(df)}")
    time.sleep(4)
    os.system("clear || cls")

    # --- Main revocation loop ---
    # --- Główna pętla odwoływania ---
    for index, row in df.iterrows():
        client_name = row[column_name]

        print(f"Revoking certificate for: {client_name} ({index + 1} of {len(df)})...")
        print(f"Odwołuję certyfikat dla: {client_name} ({index + 1} z {len(df)})...")

        # Save the current user's name to config.yaml so that revoke_cert.sh
        # knows who to act upon.
        # Zapisz nazwę bieżącego użytkownika do config.yaml, aby skrypt revoke_cert.sh
        # wiedział, dla kogo ma działać.
        current_config = load_config()
        if not current_config:
            print("CRITICAL ERROR: Lost access to config file during loop. Skipping user.")
            print("BŁĄD KRYTYCZNY: Utracono dostęp do pliku konfiguracyjnego w trakcie pętli. Pomijam użytkownika.")
            continue

        current_config['user_management']['state']['client_name'] = str(client_name)
        save_config(current_config)

        # Call the shell script to perform the revocation
        # Wywołaj skrypt powłoki, aby przeprowadzić odwołanie
        os.system("./revoke_cert.sh")
        os.system("clear || cls")
        time.sleep(1)

    print("---")
    print("Certificate revocation process finished.")
    print("Proces odwoływania certyfikatów zakończony.")


if __name__ == "__main__":
    run_revocation_process()
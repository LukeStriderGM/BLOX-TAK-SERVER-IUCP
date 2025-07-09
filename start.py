#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === MAIN ORCHESTRATION SCRIPT ===
# === GŁÓWNY SKRYPT ORKIESTRUJĄCY ===
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

        print("Choose and press Enter:")
        choice = input("Wybierz i naciśnij Enter: ").strip()

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
# === MAIN EXECUTION FUNCTION ===
# === GŁÓWNA FUNKCJA WYKONAWCZA ===
# =====================================================================================

def run_orchestration():
    """
    The main function that orchestrates the entire process.
    Główna funkcja orkiestrująca całym procesem.
    """
    # --- Step 1: Configuration questions for the user ---
    # --- Krok 1: Pytania konfiguracyjne do użytkownika ---
    if not set_language():
        exit(1)

    print("---")
    print("Select the operating mode (local/remote)...")
    print("Wybierz tryb pracy (local/remote)...")
    os.system("python3 set_mode.py")
    os.system("clear || cls")

    # --- Step 2: Running preparation scripts ---
    # --- Krok 2: Uruchomienie skryptów przygotowawczych ---
    print("---")
    print("Running preparation scripts...")
    print("Uruchamiam skrypty przygotowawcze...")
    os.system("python3 check_ip.py")
    os.system("python3 config_pref.py")
    os.system("clear || cls")

    # --- Step 3: Loading data and preparing for the loop ---
    # --- Krok 3: Wczytanie danych i przygotowanie do pętli ---
    config = load_config()
    if not config:
        exit(1)

    user_type = config['user_management']['state']['user_type']
    data_sources = config['user_management']['data_sources']
    csv_path = data_sources.get(user_type.lower())

    if not csv_path:
        print(f"ERROR: No data source for language '{user_type}'.")
        print(f"BŁĄD: Brak źródła danych dla języka '{user_type}'.")
        exit(1)

    print("---")
    print("Loading user list...")
    print("Wczytuję listę użytkowników...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"ERROR: Failed to load data from CSV: {e}")
        print(f"BŁĄD: Nie udało się wczytać danych z CSV: {e}")
        exit(1)

    if user_type == "EN":
        column_name = 'Username:'
        column_name1 = 'E-Mail Address:'
        column_name2 = 'Timestamp:'
        print("\n--- Users List ---")
    else:  # PL
        column_name = 'Nazwa Użytkownika:'
        column_name1 = 'Adres E-Mail:'
        column_name2 = 'Sygnatura czasowa:'
        print("\n--- Lista Użytkowników ---")

    number_users = len(df)
    print(df[column_name].to_string(index=False))
    print(f"\nNumber Of Users: {number_users}")
    print(f"Liczba Użytkowników: {number_users}")
    time.sleep(3)
    os.system("clear || cls")

    config['user_management']['state']['number_users'] = number_users
    save_config(config)

    # --- Step 4: Main processing loop ---
    # --- Krok 4: Główna pętla przetwarzania ---
    for index, row in df.iterrows():
        print("---")
        print(f"Processing user {index + 1} of {number_users}...")
        print(f"Przetwarzam użytkownika {index + 1} z {number_users}...")

        client_name = row[column_name]
        email_address = row[column_name1]
        registration_date = row[column_name2]

        print(f"Client: {client_name}")
        print(f"Klient: {client_name}")
        time.sleep(2)

        config['user_management']['state']['client_name'] = str(client_name)
        config['user_management']['state']['email_address'] = str(email_address)
        config['user_management']['state']['registration_date'] = str(registration_date)
        save_config(config)

        # Call scripts for the current user
        # Wywołanie skryptów dla bieżącego użytkownika
        os.system("./make_cert.sh")
        os.system("clear || cls")
        os.system("./package.sh")
        time.sleep(3)
        os.system("clear || cls")
        os.system("python3 email_sender.py")
        time.sleep(6)
        os.system("clear || cls")

    print("---")
    print("Script has finished.")
    print("Skrypt zakończył działanie.")


# =====================================================================================
# === SCRIPT ENTRY POINT ===
# === PUNKT WEJŚCIA DO SKRYPTU ===
# =====================================================================================

if __name__ == "__main__":
    run_orchestration()
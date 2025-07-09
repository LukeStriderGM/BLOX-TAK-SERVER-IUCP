#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === SCRIPT TO CHECK AND UPDATE EXTERNAL IP ADDRESS ===
# === SKRYPT DO SPRAWDZANIA I AKTUALIZACJI ZEWNĘTRZNEGO ADRESU IP ===
# =====================================================================================

import os
import time
import requests
import yaml
import subprocess


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def check_and_update_ip(config_path: str = "config.yaml"):
    """
    Checks the public IP of the local or remote machine depending on the mode
    set in the configuration file and updates that file accordingly.

    Sprawdza publiczny adres IP maszyny lokalnej lub zdalnej w zależności od trybu
    ustawionego w pliku konfiguracyjnym i aktualizuje ten plik.
    """
    # --- Step 1: Loading configuration and execution mode ---
    # --- Krok 1: Wczytanie konfiguracji i trybu pracy ---
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)

        mode = config_data.get('execution', {}).get('mode')
        if not mode:
            raise KeyError("Execution mode 'mode' is not defined in the 'execution' section.")

        sudo_pswd = config_data['security']['sudo_pswd']
        remote_user = config_data['network']['remote_server']['user']
        remote_host = config_data['network']['remote_server']['host']

    except FileNotFoundError:
        print(f"ERROR: Configuration file '{config_path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{config_path}' nie został znaleziony!")
        return
    except KeyError as e:
        print(f"ERROR: Invalid structure in '{config_path}'. Check missing key: {e}")
        print(f"BŁĄD: Nieprawidłowa struktura pliku '{config_path}'. Sprawdź brakujący klucz: {e}")
        return

    # --- Step 2: Fetching the IP address according to the loaded mode ---
    # --- Krok 2: Pobranie adresu IP zgodnie z wczytanym trybem ---
    ip_address = None
    ip_service_url = "https://api.ipify.org"
    print("---")

    if mode == 'local':
        print("LOCAL mode read. Checking this machine's IP address...")
        print("Odczytano tryb LOKALNY. Sprawdzam adres IP tej maszyny...")
        try:
            response = requests.get(ip_service_url, timeout=10)
            response.raise_for_status()
            ip_address = response.text.strip()
        except requests.exceptions.RequestException as e:
            print(f"\nNETWORK ERROR: Could not get IP from {ip_service_url}. {e}")
            print(f"BŁĄD SIECIOWY: Nie można pobrać IP z {ip_service_url}. {e}")
            return

    elif mode == 'remote':
        print(f"REMOTE mode read. Checking server's IP address: {remote_host}...")
        print(f"Odczytano tryb ZDALNY. Sprawdzam adres IP serwera: {remote_host}...")
        try:
            command = f"sshpass -p '{sudo_pswd}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 {remote_user}@{remote_host} 'curl -s {ip_service_url}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, timeout=15)
            ip_address = result.stdout.strip()
            if not ip_address:
                raise ValueError("Received an empty response from the remote server.")
        except subprocess.CalledProcessError as e:
            print("\nSSH ERROR: Problem executing command. Check password or connection.")
            print(f"BŁĄD SSH: Problem z wykonaniem polecenia. Sprawdź hasło lub połączenie.")
            print(f"Stderr: {e.stderr}")
            return
        except Exception as e:
            print(f"\nERROR: {e}")
            print(f"BŁĄD: {e}")
            return
    else:
        print(f"\nERROR: Unknown mode '{mode}' in the configuration file.")
        print(f"BŁĄD: Nieznany tryb '{mode}' w pliku konfiguracyjym.")
        return

    # --- Step 3: Displaying and saving the IP address ---
    # --- Krok 3: Wyświetlenie i zapis adresu IP ---
    print("********************************")
    print(f"* EXTERNAL-IP: {ip_address} *")
    print("********************************")
    time.sleep(3)
    os.system("clear || cls")

    try:
        print("---")
        print(f"Updating '{config_path}' with the new IP address...")
        print(f"Aktualizuję plik '{config_path}' nowym adresem IP...")

        config_data['network']['external_ip'] = ip_address

        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print("The configuration file has been successfully updated.")
        print("Plik konfiguracyjny został pomyślnie zaktualizowany.")
        print("---\n")

    except Exception as e:
        print(f"\nERROR: An unexpected error occurred while writing to the file: {e}")
        print(f"BŁĄD: Wystąpił nieoczekiwany problem podczas zapisu do pliku: {e}")


if __name__ == "__main__":
    check_and_update_ip()
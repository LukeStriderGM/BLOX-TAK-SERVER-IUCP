#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === SCRIPT TO UPDATE WIREGUARD ENDPOINT AND RESTART THE SERVICE ===
# === SKRYPT DO AKTUALIZACJI ENDPOINTU WIREGUARD I RESTARTU USŁUGI ===
# =====================================================================================

import os
import re
import subprocess
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
        with open(path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{path}' nie został znaleziony!")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}")
        print(f"BŁĄD: Nie udało się wczytać pliku konfiguracyjnego: {e}")
        return None

def run_sudo_command(command: str, password: str) -> bool:
    """
    Runs a command with sudo, piping the password to it.
    Uruchamia komendę z sudo, przekazując do niej hasło.

    Returns:
        bool: True if the command was successful, False otherwise.
              True, jeśli polecenie się powiodło, w przeciwnym razie False.
    """
    print(f"Executing: sudo {command}")
    print(f"Wykonuję: sudo {command}")
    try:
        # We use a pipe to safely pass the password to 'sudo -S'
        # Używamy potoku, aby bezpiecznie przekazać hasło do 'sudo -S'
        process = subprocess.run(
            ['sudo', '-S'] + command.split(),
            input=password + '\n',
            text=True,
            capture_output=True,
            check=True  # Will raise an exception if the command fails
        )
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(f"Stderr: {process.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print("\nERROR: An error occurred while executing a sudo command.")
        print("BŁĄD: Wystąpił błąd podczas wykonywania komendy sudo.")
        print(f"Command / Polecenie: {e.cmd}")
        print(f"Exit Code / Kod wyjścia: {e.returncode}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"\nERROR: Command '{command.split()[0]}' not found. Make sure it is installed.")
        print(f"BŁĄD: Polecenie '{command.split()[0]}' nie zostało znalezione. Upewnij się, że jest zainstalowane.")
        return False

# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def update_wireguard_endpoint(config_path: str = "config.yaml"):
    """
    Updates the Endpoint in the WireGuard configuration file and restarts the service.
    Aktualizuje Endpoint w pliku konfiguracyjnym WireGuard i restartuje usługę.
    """
    wg_config_path = "/etc/wireguard/wg0-client.conf"
    temp_wg_config_path = "/tmp/wg0-client.conf.temp"

    # --- Step 1: Load configuration from YAML ---
    # --- Krok 1: Wczytanie konfiguracji z YAML ---
    print("---")
    print("Loading configuration from YAML file...")
    print("Wczytuję konfigurację z pliku YAML...")
    config_data = load_config(config_path)
    if not config_data:
        return

    try:
        sudo_pswd = config_data['security']['sudo_pswd']
        new_ip = config_data['network']['external_ip']
    except KeyError as e:
        print(f"ERROR: Missing key in config.yaml: {e}")
        print(f"BŁĄD: Brakujący klucz w config.yaml: {e}")
        return

    # --- Step 2: Read WireGuard configuration using sudo ---
    # --- Krok 2: Odczytanie konfiguracji WireGuard za pomocą sudo ---
    print(f"\nReading WireGuard configuration file: {wg_config_path}")
    print(f"Odczytuję plik konfiguracyjny WireGuard: {wg_config_path}")
    try:
        read_process = subprocess.run(
            ['sudo', '-S', 'cat', wg_config_path],
            input=sudo_pswd + '\n', text=True, capture_output=True, check=True
        )
        original_content = read_process.stdout
    except Exception:
        print(f"\nERROR: Failed to read {wg_config_path}. Check permissions and password.")
        print(f"BŁĄD: Nie udało się odczytać pliku {wg_config_path}. Sprawdź uprawnienia i hasło.")
        return

    # --- Step 3: Modify the IP address in memory ---
    # --- Krok 3: Modyfikacja adresu IP w pamięci ---
    print("\nReplacing the IP address in the 'Endpoint' line...")
    print("Podmieniam adres IP w linii 'Endpoint'...")
    modified_content = re.sub(
        r'(^\s*Endpoint\s*=\s*)[\d\.]+',
        fr'\g<1>{new_ip}',
        original_content,
        flags=re.MULTILINE
    )

    if original_content == modified_content:
        print("\nWarning: 'Endpoint' line not found for update, or the IP address is already current.")
        print("Ostrzeżenie: Nie znaleziono linii 'Endpoint' do aktualizacji lub adres IP jest już aktualny.")
        # We can continue to the restart just in case
        # Możemy kontynuować do restartu na wszelki wypadek

    # --- Step 4: Write to a temporary file and move it into place with sudo ---
    # --- Krok 4: Zapis do pliku tymczasowego i przeniesienie go z sudo ---
    print(f"\nSaving changes and updating {wg_config_path}...")
    print(f"Zapisuję zmiany i aktualizuję plik {wg_config_path}...")
    try:
        with open(temp_wg_config_path, "w") as f:
            f.write(modified_content)
    except IOError as e:
        print(f"ERROR: Could not write to temporary file {temp_wg_config_path}: {e}")
        print(f"BŁĄD: Nie można było zapisać do pliku tymczasowego {temp_wg_config_path}: {e}")
        return

    # We use sudo to move the file, set the owner, and set permissions
    # Używamy sudo do przeniesienia pliku, ustawienia właściciela i uprawnień
    if not run_sudo_command(f"mv {temp_wg_config_path} {wg_config_path}", sudo_pswd): return
    if not run_sudo_command(f"chown root:root {wg_config_path}", sudo_pswd): return
    if not run_sudo_command(f"chmod 600 {wg_config_path}", sudo_pswd): return

    # --- Step 5: Restart the WireGuard service ---
    # --- Krok 5: Restart usługi WireGuard ---
    print("\nRestarting WireGuard interface (wg0-client)...")
    print("Restartuję interfejs WireGuard (wg0-client)...")
    if not run_sudo_command("wg-quick down wg0-client", sudo_pswd):
        print("\nWarning: Failed to bring the interface down (it may have already been down). Continuing...")
        print("Ostrzeżenie: Nie udało się wyłączyć interfejsu (możliwe, że był już wyłączony). Kontynuuję...")

    if not run_sudo_command("wg-quick up wg0-client", sudo_pswd):
        print("\nCRITICAL ERROR: Failed to bring up the WireGuard interface! Check the configuration.")
        print("BŁĄD KRYTYCZNY: Nie udało się podnieść interfejsu WireGuard! Sprawdź konfigurację.")
        return

    # --- Step 6: Verification ---
    # --- Krok 6: Weryfikacja ---
    print("\nVerifying connection status...")
    print("Weryfikuję status połączenia...")
    run_sudo_command("wg show wg0-client", sudo_pswd)

    print("\n---")
    print("Process completed successfully!")
    print("Proces zakończony pomyślnie!")
    print("---")

if __name__ == "__main__":
    update_wireguard_endpoint()
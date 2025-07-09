#!/bin/bash

# =====================================================================================
# === REVOKE TAK CLIENT CERTIFICATE - Handles local/remote mode ===
# === ODWOŁYWANIE CERTYFIKATU KLIENTA TAK - Obsługa trybu local/remote ===
# =====================================================================================

set -e
# Stop the script on any error
# Zatrzymaj skrypt w przypadku błędu

# --- Configuration ---
# --- Konfiguracja ---
CONFIG_FILE="config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found!"
    echo "BŁĄD: Plik konfiguracyjny '$CONFIG_FILE' nie został znaleziony!"
    exit 1
fi

echo "---"
echo "Loading configuration..."
echo "Wczytuję konfigurację..."

# Read data from the nested YAML structure
# Odczyt danych z zagnieżdżonej struktury YAML
sudo_pswd=$(yq '.security.sudo_pswd' "$CONFIG_FILE")
client_name=$(yq '.user_management.state.client_name' "$CONFIG_FILE")
mode=$(yq '.execution.mode' "$CONFIG_FILE")
remote_user=$(yq '.network.remote_server.user' "$CONFIG_FILE")
remote_host=$(yq '.network.remote_server.host' "$CONFIG_FILE")

# --- Command Definitions ---
# --- Definicje Poleceń ---
# The same set of commands is used for local and remote mode
# Ten sam zestaw komend jest używany dla trybu lokalnego i zdalnego
commands_to_execute="
    set -e;
    echo '--- (REMOTE/LOCAL) Revoking certificate for: ${client_name} ---';
    echo '--- (ZDALNY/LOKALNY) Odwoływanie certyfikatu dla: ${client_name} ---';

    echo '--> Changing directory to /home/tak/tak-server/tak/certs';
    echo '--> Zmiana katalogu na /home/tak/tak-server/tak/certs';
    cd /home/tak/tak-server/tak/certs;

    echo '--> Running revokeCert.sh...';
    echo '--> Uruchamiam revokeCert.sh...';
    ./revokeCert.sh '${client_name}' root-ca-do-not-share root-ca;

    echo '--> Changing directory to .../certs/files';
    echo '--> Zmiana katalogu na .../certs/files';
    cd /home/tak/tak-server/tak/certs/files;

    echo '--> Deleting client certificate files (.p12, .pem, .key)...';
    echo '--> Usuwanie plików certyfikatów (.p12, .pem, .key) dla klienta...';
    rm -f '${client_name}'.*;

    echo '--- Operation finished successfully. ---';
    echo '--- Operacja zakończona pomyślnie. ---';
"

# ======================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# ======================================================

echo "---"
if [ "$mode" == "remote" ]; then
    # --- REMOTE MODE ---
    # --- TRYB ZDALNY ---
    echo "REMOTE MODE read. Executing operations on host: $remote_host"
    echo "Odczytano TRYB ZDALNY. Wykonuję operacje na hoście: $remote_host"
    echo "---"

    # Execute remote commands using the established pattern
    # Wykonaj zdalne komendy, używając ustalonego wzorca
    sshpass -p "$sudo_pswd" ssh -t "${remote_user}@${remote_host}" "echo '$sudo_pswd' | sudo -S bash -c \"$commands_to_execute\""

elif [ "$mode" == "local" ]; then
    # --- LOCAL MODE ---
    # --- TRYB LOKALNY ---
    echo "LOCAL MODE read. Executing operations on this machine."
    echo "Odczytano TRYB LOKALNY. Wykonuję operacje na tej maszynie."
    echo "---"

    # Execute the same commands locally with sudo
    # Wykonaj te same komendy lokalnie z sudo
    echo "$sudo_pswd" | sudo -S bash -c "$commands_to_execute"

else
    echo "ERROR: Invalid mode '$mode' in config.yaml. Use 'local' or 'remote'." >&2
    echo "BŁĄD: Nieprawidłowy tryb '$mode' w pliku konfiguracyjnym. Użyj 'local' lub 'remote'." >&2
    exit 1
fi

echo "---"
echo "Certificate revocation process completed successfully!"
echo "Proces odwoływania certyfikatu zakończony pomyślnie!"
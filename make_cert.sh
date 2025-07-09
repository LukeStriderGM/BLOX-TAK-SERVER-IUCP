#!/bin/bash

# =====================================================================================
# === GENERATING TAK CLIENT CERTIFICATE - Handling local/remote mode ===
# === GENEROWANIE CERTYFIKATU KLIENTA TAK - Obsługa trybu local/remote ===
# =====================================================================================

set -e
# Stop the script on any error
# Zatrzymaj skrypt w przypadku błędu

# --- Configuration ---
# --- Konfiguracja ---
config_file="config.yaml"
echo "---"
echo "Wczytuję konfigurację..."
echo "Loading configuration..."

# Read data from the nested YAML structure
# Odczyt danych z zagnieżdżonej struktury YAML
sudo_pswd=$(yq '.security.sudo_pswd' "$config_file")
client_name=$(yq '.user_management.state.client_name' "$config_file")
mode=$(yq '.execution.mode' "$config_file")
remote_user=$(yq '.network.remote_server.user' "$config_file")
remote_host=$(yq '.network.remote_server.host' "$config_file")

# Use the path from config.yaml as the destination
# Użyj ścieżki z config.yaml jako docelowej
destination_dir=$(yq -r '.paths.preferences_output' "$config_file")

# --- Paths and Commands Definitions ---
# --- Definicje Ścieżek i Poleceń ---
tak_certs_dir="/home/tak/tak-server/tak/certs"
tak_certs_files_dir="${tak_certs_dir}/files"

# Define paths for the client certificate
# Zdefiniuj ścieżki dla certyfikatu klienta
remote_temp_cert_path="/home/${remote_user}/${client_name}.p12"
local_final_cert_path="${destination_dir}${client_name}.p12"

# Define paths for the root certificate
# Zdefiniuj ścieżki dla certyfikatu roota
remote_temp_root_path="/home/${remote_user}/truststore-root.p12"
local_final_root_path="${destination_dir}truststore-root.p12"


# Commands to be executed on the server (remote or local)
# Polecenia do wykonania na serwerze (zdalnym lub lokalnym)
commands_to_execute="
    set -e;
    echo '--- (REMOTE/LOCAL) Generating client certificate for: ${client_name} ---';
    echo '--- (ZDALNY/LOKALNY) Generowanie certyfikatu klienta dla: ${client_name} ---';
    cd ${tak_certs_dir};
    ./makeCert.sh client \"${client_name}\";
"

# ======================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# ======================================================

echo "---"
if [ "$mode" == "remote" ]; then
    # ### REMOTE MODE ###
    # ### TRYB ZDALNY ###
    echo "Odczytano TRYB ZDALNY."
    echo "Wykonuję operacje na hoście: $remote_host"
    echo "REMOTE MODE read."
    echo "Executing operations on host: $remote_host"
    echo "---"

    # Additional commands for remote mode (copying to /home)
    # Dodatkowe komendy dla trybu zdalnego (kopiowanie do /home)
    remote_commands="
        ${commands_to_execute}
        echo '--- (REMOTE) Copying certificates (client and root) to /home for download ---';
        echo '--- (ZDALNY) Kopiowanie certyfikatów (klient i root) do /home w celu pobrania ---';
        cp ${tak_certs_files_dir}/${client_name}.p12 ${remote_temp_cert_path};
        chown ${remote_user}:${remote_user} ${remote_temp_cert_path};
        cp ${tak_certs_files_dir}/truststore-root.p12 ${remote_temp_root_path};
        chown ${remote_user}:${remote_user} ${remote_temp_root_path};
    "
    # Execute remote commands
    # Wykonaj zdalne komendy
    sshpass -p "$sudo_pswd" ssh -t "$remote_user@$remote_host" "echo '$sudo_pswd' | sudo -S bash -c \"$remote_commands\""

    # Copy files from the server to the local machine
    # Kopiuj pliki z serwera na maszynę lokalną
    echo "---"
    echo "Kopiuję certyfikat klienta (.p12) na maszynę lokalną..."
    echo "Copying client certificate (.p12) to the local machine..."
    sshpass -p "$sudo_pswd" scp -o StrictHostKeyChecking=no "$remote_user@$remote_host:$remote_temp_cert_path" "$local_final_cert_path"

    echo "Kopiuję certyfikat roota (truststore-root.p12) na maszynę lokalną..."
    echo "Copying root certificate (truststore-root.p12) to the local machine..."
    sshpass -p "$sudo_pswd" scp -o StrictHostKeyChecking=no "$remote_user@$remote_host:$remote_temp_root_path" "$local_final_root_path"

    # Cleanup on the remote server
    # Sprzątanie na serwerze zdalnym
    echo "---"
    echo "Sprzątam pliki tymczasowe na serwerze zdalnym..."
    echo "Cleaning up temporary files on the remote server..."
    sshpass -p "$sudo_pswd" ssh "$remote_user@$remote_host" "rm ${remote_temp_cert_path} ${remote_temp_root_path}"

elif [ "$mode" == "local" ]; then
    # ### LOCAL MODE ###
    # ### TRYB LOKALNY ###
    echo "Odczytano TRYB LOKALNY."
    echo "Wykonuję operacje na tej maszynie."
    echo "LOCAL MODE read."
    echo "Executing operations on this machine."
    echo "---"

    # Additional commands for local mode (copying to the project directory)
    # Dodatkowe komendy dla trybu lokalnego (kopiowanie do katalogu projektu)
    local_commands="
        ${commands_to_execute}
        echo '--- (LOCAL) Copying certificates (client and root) to the project directory... ---';
        echo '--- (LOKALNY) Kopiowanie certyfikatów (klient i root) do katalogu projektu... ---';
        cp ${tak_certs_files_dir}/${client_name}.p12 ${local_final_cert_path};
        cp ${tak_certs_files_dir}/truststore-root.p12 ${local_final_root_path};
    "
    # Execute commands locally with sudo
    # Wykonaj komendy lokalnie z sudo
    echo "$sudo_pswd" | sudo -S bash -c "$local_commands"

else
    echo "BŁĄD: Nieprawidłowy tryb '$mode' w pliku konfiguracyjnym. Użyj 'local' lub 'remote'." >&2
    echo "ERROR: Invalid mode '$mode' in config.yaml. Use 'local' or 'remote'." >&2
    exit 1
fi

# --- Finalization ---
# --- Finalizacja ---
echo "---"
echo "Ustawiam uprawnienia dla pobranych plików..."
echo "Setting permissions for the downloaded files..."
chmod 644 "$local_final_cert_path"
chmod 644 "$local_final_root_path"

echo "---"
echo "Proces generowania certyfikatów zakończony pomyślnie!"
echo "Certificate generation process completed successfully!"
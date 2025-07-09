#!/bin/bash

# =====================================================================================
# === GENERATE AND COPY MUMBLE CERTIFICATE ===
# === GENEROWANIE I KOPIOWANIE CERTYFIKATU MUMBLE ===
#
# This script generates an SSL certificate for the Mumble server. It operates
# automatically in local or remote mode. In remote mode, it copies the certificate
# to the local machine.
#
# Skrypt generuje certyfikat SSL dla serwera Mumble. Działa automatycznie
# w trybie lokalnym lub zdalnym. W trybie zdalnym kopiuje certyfikat na maszynę lokalną.
# =====================================================================================

# --- Path Definitions ---
# --- Definicje ścieżek ---
config_file="config.yaml"
# Target directory on the local machine
# Docelowy katalog na lokalnej maszynie
cert_dir="/home/luke_blue_lox/PycharmProjects/BLOX-TAK-SERVER-IUCP/IUCP-IPPU_PACKAGE/certs"
mkdir -p "$cert_dir"

# --- Loading configuration ---
# --- Wczytanie konfiguracji ---
echo "---"
echo "Loading configuration from '$config_file'..."
echo "Wczytuję konfigurację z pliku '$config_file'..."
sudo_pswd=$(yq '.security.sudo_pswd' "$config_file")
ex_ip=$(yq '.network.external_ip' "$config_file")
mode=$(yq '.execution.mode' "$config_file")
remote_host=$(yq '.network.remote_server.host' "$config_file")
remote_user=$(yq '.network.remote_server.user' "$config_file")

# --- Definition of commands to be executed on the server ---
# --- Definicja poleceń do wykonania na serwerze ---
commands_to_execute="
    echo '---'
    echo 'Starting certificate and key generation...'
    echo 'Rozpoczynam generowanie certyfikatu i klucza...'
    openssl req -x509 -sha256 -nodes -days 1080 -newkey rsa:2048 \
        -keyout /etc/mumble.key \
        -out /etc/mumble.cer \
        -subj \\"/CN=$ex_ip\\" \
        -addext \\"subjectAltName=IP:$ex_ip,IP:192.168.1.17,IP:10.0.0.1\\" \
        -addext \\"extendedKeyUsage=serverAuth\\" &&

    echo 'Setting permissions for the generated files...'
    echo 'Ustawiam uprawnienia dla wygenerowanych plików...'
    chmod 755 /etc/mumble.key
    chmod 755 /etc/mumble.cer &&

    echo 'Restarting the mumble-server service...'
    echo 'Restartuję usługę mumble-server...'
    systemctl restart mumble-server &&

    echo 'Checking the mumble-server service status...'
    echo 'Sprawdzam status usługi mumble-server...'
    systemctl status mumble-server
"

# ======================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# ======================================================
echo "---"
if [ "$mode" == "remote" ]; then
    # ---------- REMOTE MODE ----------
    # ---------- TRYB ZDALNY ----------
    echo "REMOTE MODE read. Executing operations on host: $remote_host"
    echo "Odczytano TRYB ZDALNY. Wykonuję operacje na hoście: $remote_host"
    echo "---"

    # Execute certificate generation commands on the remote server
    # Wykonanie poleceń generujących certyfikat na zdalnym serwerze
    sshpass -p "$sudo_pswd" ssh -t "$remote_user@$remote_host" "
        echo '$sudo_pswd' | sudo -S bash -c \"$commands_to_execute\"
    "

    # <<< ADDED COPY LOGIC >>>
    # <<< DODANA LOGIKA KOPIOWANIA >>>
    echo "---"
    echo "Copying mumble.cer certificate from the remote server..."
    echo "Kopiuję certyfikat mumble.cer z serwera zdalnego..."

    sshpass -p "$sudo_pswd" scp -o StrictHostKeyChecking=no "$remote_user@$remote_host:/etc/mumble.cer" "$cert_dir/mumble.cer"

    echo "Certificate copied to '$cert_dir'."
    echo "Certyfikat skopiowany do '$cert_dir'."
    chmod 755 "$cert_dir/mumble.cer"


elif [ "$mode" == "local" ]; then
    # ---------- LOCAL MODE ----------
    # ---------- TRYB LOKALNY ----------
    echo "LOCAL MODE read. Executing operations on this machine."
    echo "Odczytano TRYB LOKALNY. Wykonuję operacje na tej maszynie."
    echo "---"

    # Execute commands locally
    # Wykonanie poleceń lokalnie
    echo "$sudo_pswd" | sudo -S bash -c "$commands_to_execute"

    # Copy the certificate from /etc/ to the project directory
    # Kopiowanie certyfikatu z /etc/ do katalogu projektu
    echo "---"
    echo "Copying local mumble.cer certificate..."
    echo "Kopiuję lokalny certyfikat mumble.cer..."
    echo "$sudo_pswd" | sudo -S cp "/etc/mumble.cer" "$cert_dir/mumble.cer"
    echo "$sudo_pswd" | sudo -S chmod 755 "$cert_dir/mumble.cer"
    echo "Certificate copied to '$cert_dir'."
    echo "Certyfikat skopiowany do '$cert_dir'."

else
    echo "ERROR: Invalid mode '$mode' in the configuration file."
    echo "BŁĄD: Nieprawidłowy tryb '$mode' w pliku konfiguracyjnym."
    exit 1
fi

echo "---"
echo "Process completed successfully!"
echo "Proces zakończony pomyślnie!"
sleep 5
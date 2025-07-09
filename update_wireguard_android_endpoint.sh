#!/bin/bash

# =====================================================================================
# === UNIFIED WIREGUARD UPDATE (ANDROID) - Handles local/remote mode ===
# === ZUNIFIKOWANA AKTUALIZACJA WIREGUARD (ANDROID) - Obsługa trybu local/remote ===
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
new_ip=$(yq '.network.external_ip' "$CONFIG_FILE")
remote_user=$(yq '.network.remote_server.user' "$CONFIG_FILE")
remote_host=$(yq '.network.remote_server.host' "$CONFIG_FILE")
local_project_root=$(yq -r '.paths.project_root' "$CONFIG_FILE")
mode=$(yq '.execution.mode' "$CONFIG_FILE")
modifier_script="modify_android_conf.py"

# --- Path Definitions ---
# --- Definicje Ścieżek ---
wg_config_path="/etc/wireguard/android.conf"
local_qr_destination="${local_project_root}android_wireguard_qr.png"

# =====================================================================================
# --- MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

echo "---"
if [ "$mode" == "remote" ]; then
    # ####################
    # ### REMOTE MODE ###
    # ####################
    echo "REMOTE MODE read. Executing operations on host: $remote_host"
    echo "Odczytano TRYB ZDALNY. Wykonuję operacje na hoście: $remote_host"

    # --- Path definitions for remote mode ---
    # --- Definicje ścieżek dla trybu zdalnego ---
    local_temp_conf="./android.conf.temp"
    remote_temp_conf="/tmp/android.conf.temp"

    # --- Step 1 (Remote): Download the original config file ---
    # --- Krok 1 (Zdalny): Pobranie oryginalnego pliku konfiguracyjnego ---
    echo "---"
    echo "Downloading original config file from the server..."
    echo "Pobieram oryginalny plik konfiguracyjny z serwera..."
    sshpass -p "$sudo_pswd" ssh "${remote_user}@${remote_host}" "echo '$sudo_pswd' | sudo -S cat $wg_config_path" > "$local_temp_conf"

    if [ ! -s "$local_temp_conf" ]; then
        echo "ERROR: Failed to download the config file content." >&2
        echo "BŁĄD: Nie udało się pobrać treści pliku konfiguracyjnego." >&2
        exit 1
    fi

    # --- Step 2 (Remote): Modify the file locally ---
    # --- Krok 2 (Zdalny): Modyfikacja pliku lokalnie ---
    echo "---"
    echo "Modifying config file locally..."
    echo "Modyfikuję plik konfiguracyjny lokalnie..."
    python3 "$modifier_script" "$local_temp_conf" "$new_ip"

    # --- Step 3 (Remote): Generate QR code LOCALLY ---
    # --- Krok 3 (Zdalny): Generowanie kodu QR LOKALNIE ---
    echo "---"
    echo "Generating QR code from the local, modified file..."
    echo "Generuję kod QR z lokalnego, zmodyfikowanego pliku..."
    qrencode -o "$local_qr_destination" < "$local_temp_conf"
    echo "QR code PNG image successfully saved to: $local_qr_destination"
    echo "Obraz PNG z kodem QR został pomyślnie zapisany w: $local_qr_destination"

    # --- Step 4 (Remote): Upload the modified file back to the server ---
    # --- Krok 4 (Zdalny): Wysłanie zmodyfikowanego pliku z powrotem na serwer ---
    echo "---"
    echo "Uploading modified file to the server..."
    echo "Wysyłam zmodyfikowany plik na serwer..."
    sshpass -p "$sudo_pswd" scp "$local_temp_conf" "${remote_user}@${remote_host}:${remote_temp_conf}"

    # --- Step 5 (Remote): Perform final operations on the server ---
    # --- Krok 5 (Zdalny): Wykonanie finalnych operacji na serwerze ---
    echo "---"
    echo "Performing final operations on the server..."
    echo "Wykonuję finalne operacje na serwerze..."
    # CORRECTED BLOCK - with standard spaces
    # POPRAWIONY BLOK - ze standardowymi spacjami
    remote_commands="
        set -e;
        echo '--- (REMOTE) Replacing the configuration file... ---';
        echo '--- (ZDALNY) Podmiana pliku konfiguracyjnego... ---';
        mv ${remote_temp_conf} ${wg_config_path};
        chown root:root ${wg_config_path};
        chmod 600 ${wg_config_path};
        echo '--- (REMOTE) Restarting WireGuard interface (wg0)... ---';
        echo '--- (ZDALNY) Restart interfejsu WireGuard (wg0)... ---';
        wg-quick down wg0 || true;
        wg-quick up wg0;
    "
    sshpass -p "$sudo_pswd" ssh -t "${remote_user}@${remote_host}" "echo '$sudo_pswd' | sudo -S bash -c \"$remote_commands\""

    # --- Step 6 (Remote): Cleanup ---
    # --- Krok 6 (Zdalny): Sprzątanie ---
    echo "---"
    echo "Cleaning up local temporary file..."
    echo "Sprzątam lokalny plik tymczasowy..."
    rm "$local_temp_conf"

elif [ "$mode" == "local" ]; then
    # ###################
    # ### LOCAL MODE ###
    # ###################
    echo "LOCAL MODE read. Executing operations on this machine."
    echo "Odczytano TRYB LOKALNY. Wykonuję operacje na tej maszynie."

    # --- Commands to be executed LOCALLY ---
    # --- Polecenia do wykonania LOKALNIE ---
    local_commands="
        set -e;
        echo '--- (LOCAL) Modifying the configuration file... ---';
        echo '--- (LOKALNY) Modyfikacja pliku konfiguracyjnego... ---';
        echo '$sudo_pswd' | sudo -S python3 '$modifier_script' '$wg_config_path' '$new_ip';

        echo '--- (LOCAL) Restarting WireGuard interface (wg0)... ---';
        echo '--- (LOKALNY) Restart interfejsu WireGuard (wg0)... ---';
        echo '$sudo_pswd' | sudo -S wg-quick down wg0 || true;
        echo '$sudo_pswd' | sudo -S wg-quick up wg0;
    "

    # --- Execute local commands without a new sudo pipe for each ---
    # --- Wykonanie poleceń lokalnych bez nowego potoku sudo dla każdego ---
    echo "---"
    bash -c "$local_commands"

    # --- Generate QR code locally ---
    # --- Generowanie kodu QR lokalnie ---
    echo "---"
    echo "Generating QR code locally..."
    echo "Generuję kod QR lokalnie..."
    echo "$sudo_pswd" | sudo -S cat "$wg_config_path" | qrencode -o "$local_qr_destination"
    echo "QR code PNG image successfully saved to: $local_qr_destination"
    echo "Obraz PNG z kodem QR został pomyślnie zapisany w: $local_qr_destination"

else
    echo "ERROR: Invalid mode '$mode' in config.yaml. Use 'local' or 'remote'." >&2
    echo "BŁĄD: Nieprawidłowy tryb '$mode' w pliku konfiguracyjnym. Użyj 'local' lub 'remote'." >&2
    exit 1
fi

echo "---"
echo "Process completed successfully!"
echo "Proces zakończony pomyślnie!"
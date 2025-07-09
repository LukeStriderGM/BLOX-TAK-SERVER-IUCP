#!/bin/bash

# =====================================================================================
# === PACKAGE USER BUNDLE AND CLEANUP ===
# === PAKOWANIE PACZKI UŻYTKOWNIKA I SPRZĄTANIE ===
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
client_name=$(yq '.user_management.state.client_name' "$CONFIG_FILE")
project_root=$(yq -r '.paths.project_root' "$CONFIG_FILE")
certs_dir=$(yq -r '.paths.preferences_output' "$CONFIG_FILE")
# Define the source directory for the package from the project root
# Zdefiniuj katalog źródłowy paczki na podstawie katalogu głównego projektu
package_source_dir="${project_root}IUCP-IPPU_PACKAGE"


# =====================================================================================
# --- MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

# --- Step 1: Create the .zip archive ---
# --- Krok 1: Tworzenie archiwum .zip ---
echo "---"
echo "Creating .zip archive for client: $client_name"
echo "Tworzę archiwum .zip dla klienta: $client_name"

if [ ! -d "$package_source_dir" ]; then
    echo "Error: Source directory for packaging does not exist: $package_source_dir"
    echo "BŁĄD: Katalog źródłowy do spakowania nie istnieje: $package_source_dir"
    exit 1
fi

# Navigate to the source directory to create a clean archive
# Przejdź do katalogu źródłowego, aby utworzyć czyste archiwum
cd "$package_source_dir"

archive_name="../IUCP-IPPU_PACKAGE_${client_name}.zip"

# Remove the old archive if it exists to avoid issues
# Usuń stare archiwum, jeśli istnieje, aby uniknąć problemów
rm -f "$archive_name"

# Zip the contents, excluding logs and temporary files
# Spakuj zawartość, wykluczając logi i pliki tymczasowe
zip -r "$archive_name" . -x \*.log \*.tmp

# Return to the previous directory
# Wróć do poprzedniego katalogu
cd - > /dev/null

echo "Archive '$archive_name' has been created successfully."
echo "Archiwum '$archive_name' zostało pomyślnie utworzone."


# --- Step 2: Cleanup the .p12 certificate after packaging ---
# --- Krok 2: Sprzątanie certyfikatu .p12 po spakowaniu ---
echo "---"
echo "Cleaning up the .p12 certificate from the packaging directory..."
echo "Sprzątam certyfikat .p12 z katalogu pakowania..."

certificate_path="${certs_dir}${client_name}.p12"

if [[ -f "$certificate_path" ]]; then
    rm -f "$certificate_path"
    echo "Certificate $client_name.p12 removed from: $certs_dir"
    echo "Certyfikat $client_name.p12 usunięty z katalogu: $certs_dir"
else
    echo "Warning: No certificate file found for $client_name at $certs_dir. Nothing to clean up."
    echo "Ostrzeżenie: Nie znaleziono pliku certyfikatu dla $client_name w katalogu $certs_dir. Nic do posprzątania."
fi

echo "---"
echo "Packaging process completed successfully!"
echo "Proces pakowania zakończony pomyślnie!"
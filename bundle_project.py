import os
import datetime

# =====================================================================================
# === CONFIGURATION ===
# === KONFIGURACJA ===
# =====================================================================================

# The name of the output file that will contain all the bundled files.
# Nazwa pliku wyjściowego, który będzie zawierał wszystkie spakowane pliki.
OUTPUT_FILENAME = "codebase_bundle.txt"

# List of directories to absolutely exclude from the bundling process.
# Lista katalogów do bezwzględnego wykluczenia z procesu pakowania.
DIRECTORIES_TO_EXCLUDE = {
    '.git',
    '.idea',
    '.venv',
    '__pycache__',
    # We exclude the directory with generated packages to avoid including certificates.
    # Wykluczamy katalog z wygenerowanymi paczkami, aby nie dołączyć certyfikatów.
    'IUCP-IPPU_PACKAGE'
}

# List of specific files to exclude (e.g., configuration files with passwords).
# Lista konkretnych plików do wykluczenia (np. pliki konfiguracyjne z hasłami).
FILES_TO_EXCLUDE = {
    OUTPUT_FILENAME,
    'token.json',  # Google API session token. / Token sesji Google API.
    'client_secret.json'  # Google API key. / Klucz Google API.
    'config.yaml'
}

# List of file extensions to be ignored.
# Lista rozszerzeń plików, które mają być ignorowane.
EXTENSIONS_TO_EXCLUDE = {
    '.p12',
    '.zip',
    '.png',
    '.log',
    '.tmp'
}


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def bundle_project_files():
    """
    Walks through the project directory, collects the content of all allowed
    files, and saves them into a single, large text file.

    Przechodzi przez katalog projektu, zbiera zawartość wszystkich dozwolonych
    plików i zapisuje je w jednym, dużym pliku tekstowym.
    """
    project_root = os.path.abspath(os.path.dirname(__file__))

    print("Starting project bundling...")
    print("Rozpoczynam pakowanie projektu...")
    print(f"Root directory: {project_root}")
    print(f"Katalog główny: {project_root}")
    print(f"Output file: {OUTPUT_FILENAME}\n")
    print(f"Plik wyjściowy: {OUTPUT_FILENAME}\n")

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as bundle_file:
            # Write a header to the output file
            # Zapisujemy nagłówek w pliku wyjściowym
            bundle_file.write(f"Project Bundle: {os.path.basename(project_root)}\n")
            bundle_file.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            bundle_file.write("=" * 40 + "\n\n")

            # We use os.walk to recursively browse directories
            # Używamy os.walk do rekurencyjnego przeglądania katalogów
            for root, dirs, files in os.walk(project_root, topdown=True):
                # We modify the 'dirs' list in-place to exclude unwanted directories
                # Modyfikujemy listę 'dirs' w locie, aby wykluczyć niechciane katalogi
                dirs[:] = [d for d in dirs if d not in DIRECTORIES_TO_EXCLUDE]

                for filename in sorted(files):
                    # Check if the file or its extension are on the exclusion list
                    # Sprawdzamy, czy plik lub jego rozszerzenie nie są na liście wykluczonych
                    if filename in FILES_TO_EXCLUDE or any(filename.endswith(ext) for ext in EXTENSIONS_TO_EXCLUDE):
                        print(f"--- Skipping file: {filename}")
                        print(f"--- Pomijam plik: {filename}")
                        continue

                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, project_root)

                    print(f"+++ Adding file: {relative_path}")
                    print(f"+++ Dodaję plik: {relative_path}")

                    # Write a header for each file
                    # Zapisujemy nagłówek dla każdego pliku
                    bundle_file.write(f"--- START FILE: {relative_path} ---\n")

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as source_file:
                            bundle_file.write(source_file.read())
                    except Exception as e:
                        bundle_file.write(f"\n[ERROR READING FILE / BŁĄD ODCZYTU PLIKU: {e}]\n")

                    # Write a footer for each file
                    # Zapisujemy stopkę dla każdego pliku
                    bundle_file.write(f"\n--- END FILE: {relative_path} ---\n\n")

        print("\nProject bundling completed successfully!")
        print("Pakowanie projektu zakończone pomyślnie!")
        print(f"The result has been saved to the file: {OUTPUT_FILENAME}")
        print(f"Wynik został zapisany w pliku: {OUTPUT_FILENAME}")

    except IOError as e:
        print(f"\nERROR: Could not write to the output file: {e}")
        print(f"BŁĄD: Nie można zapisać pliku wyjściowego: {e}")
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {e}")
        print(f"BŁĄD: Wystąpił nieoczekiwany problem: {e}")


if __name__ == "__main__":
    bundle_project_files()
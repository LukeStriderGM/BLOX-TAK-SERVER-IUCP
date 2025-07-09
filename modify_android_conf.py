#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === SCRIPT TO MODIFY THE 'ENDPOINT' IN A CONFIGURATION FILE ===
# === SKRYPT DO MODYFIKACJI 'ENDPOINT' W PLIKU KONFIGURACYJNYM ===
# =====================================================================================

import re
import argparse


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def modify_endpoint_in_file(file_path: str, new_ip: str):
    """
    Reads a file, replaces the IP address in the 'Endpoint' line, and saves the file.

    Wczytuje plik, zamienia adres IP w linii 'Endpoint' i zapisuje plik.

    Args:
        file_path (str): The path to the configuration file to modify.
                         Ścieżka do pliku konfiguracyjnego do modyfikacji.
        new_ip (str):    The new IP address to set for the Endpoint.
                         Nowy adres IP do ustawienia dla Endpoint.
    """
    try:
        # --- Step 1: Read the original content ---
        # --- Krok 1: Odczyt oryginalnej zawartości ---
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # --- Step 2: Use regex to find and replace the endpoint IP ---
        # --- Krok 2: Użycie regex do znalezienia i zamiany IP endpointu ---
        # The regex finds a line starting with 'Endpoint', followed by '=',
        # and captures the IP address to replace it.
        # Regex znajduje linię zaczynającą się od 'Endpoint', po której jest '=',
        # i przechwytuje adres IP w celu jego zamiany.
        modified_content, num_replacements = re.subn(
            r'(^\s*Endpoint\s*=\s*)[\d\.]+',
            fr'\g<1>{new_ip}',
            content,
            flags=re.MULTILINE
        )

        if num_replacements == 0:
            print(f"Warning: 'Endpoint' line not found in {file_path}. File was not changed.")
            print(f"Ostrzeżenie: Nie znaleziono linii 'Endpoint' w {file_path}. Plik nie został zmieniony.")
            return

        # --- Step 3: Write the modified content back to the file ---
        # --- Krok 3: Zapisanie zmodyfikowanej treści z powrotem do pliku ---
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        print(f"Success: File '{file_path}' updated with new IP: {new_ip}")
        print(f"Sukces: Plik '{file_path}' zaktualizowany nowym adresem IP: {new_ip}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print(f"Błąd: Plik '{file_path}' nie został znaleziony.")
    except Exception as e:
        print(f"Error: An unexpected error occurred while modifying the file: {e}")
        print(f"Błąd: Wystąpił nieoczekiwany błąd podczas modyfikacji pliku: {e}")


if __name__ == "__main__":
    # --- Argument Parser Setup ---
    # --- Konfiguracja parsera argumentów ---
    parser = argparse.ArgumentParser(
        description="A simple script to modify the Endpoint IP in a config file.",
        epilog="Example: python3 modify_android_conf.py /path/to/android.conf 192.168.1.100"
    )
    parser.add_argument(
        "file_path",
        help="Path to the configuration file. (Ścieżka do pliku konfiguracyjnego)"
    )
    parser.add_argument(
        "new_ip",
        help="The new IP address to set. (Nowy adres IP do ustawienia)"
    )
    args = parser.parse_args()

    # --- Run the main function ---
    # --- Uruchomienie głównej funkcji ---
    modify_endpoint_in_file(args.file_path, args.new_ip)
# BLOX-TAK-SERVER-IUCP

IUCP - Individual User Connection Profile

A suite of automation scripts designed to manage the entire lifecycle of user onboarding for a TAK (Team Awareness Kit) server from "Google Forms" or csv file. The project handles certificate generation, configuration packaging, email distribution, and various server maintenance tasks.

---

<details>
<summary>🇵🇱 Wersja Polska (kliknij, aby rozwinąć)</summary>

# BLOX-TAK-SERVER-IPPU

IPPU - Indywidualny Profil Połączeniowy Użytkownika

Zestaw skryptów automatyzujących, zaprojektowany do zarządzania całym cyklem wdrażania użytkowników na serwerze TAK (Team Awareness Kit) z "Formualrzy Google" lub pliku csv. Projekt obsługuje generowanie certyfikatów, pakowanie konfiguracji, dystrybucję e-mailem oraz różne zadania związane z konserwacją serwera.

---
</details>

## 🇺🇸 Features / 🇵🇱 Funkcjonalności

* **Automated User Onboarding**: Fetches user data from a Google Sheet to process multiple users in a batch.
* **Certificate Management**: Generates and revokes user-specific `.p12` client certificates for TAK server authentication.
* **Configuration Packaging**: Creates ATAK preference files (`.pref`) and packages all user-specific files into a single `.zip` archive.
* **Email Distribution**: Automatically sends the generated user package via email using the Gmail API.
* **Server Maintenance Scripts**: Includes helper scripts for updating server configurations like Mumble and WireGuard.
* **Flexible Execution Modes**: Can be run in `local` mode (if the script is on the same machine as the TAK server) or `remote` mode (controlling a remote server via SSH).
* **Bilingual Interface**: All scripts provide interactive prompts and status messages in both English and Polish.

---
* **Automatyczne Wdrażanie Użytkowników**: Pobiera dane użytkowników z Arkusza Google w celu wsadowego przetwarzania wielu użytkowników.
* **Zarządzanie Certyfikatami**: Generuje i odwołuje certyfikaty klienckie `.p12` specyficzne dla użytkownika, służące do uwierzytelniania na serwerze TAK.
* **Pakowanie Konfiguracji**: Tworzy pliki preferencji ATAK (`.pref`) i pakuje wszystkie pliki użytkownika w jedno archiwum `.zip`.
* **Dystrybucja E-mailem**: Automatycznie wysyła wygenerowaną paczkę dla użytkownika za pośrednictwem poczty e-mail przy użyciu Gmail API.
* **Skrypty Konserwacyjne**: Zawiera skrypty pomocnicze do aktualizacji konfiguracji serwerów, takich jak Mumble i WireGuard.
* **Elastyczne Tryby Pracy**: Może być uruchamiany w trybie `local` (gdy skrypt znajduje się na tej samej maszynie co serwer TAK) lub `remote` (sterując zdalnym serwerem przez SSH).
* **Dwujęzyczny Interfejs**: Wszystkie skrypty zapewniają interaktywne monity i komunikaty o stanie w języku angielskim i polskim.

## 🇺🇸 Prerequisites / 🇵🇱 Wymagania Wstępne

* Python 3.8+
* A working TAK Server installation.
* System dependencies: `yq`, `sshpass`, `zip`, `qrencode`.
    ```bash
    sudo apt-get update && sudo apt-get install yq sshpass zip qrencode
    ```
* A Google Cloud Platform project with the **Gmail API** enabled. You must download the `client_secret.json` credentials file.

Example "Google Form" and its sheet in "Google Sheets":
* https://forms.gle/sFrsnXiwdvajEnMw7
* https://docs.google.com/spreadsheets/d/1CM2LOH7eukbyAVMIsMpIQJ5oqltqE2DO8u90WjYsdDk

---
* Python 3.8+
* Działająca instalacja serwera TAK.
* Zależności systemowe: `yq`, `sshpass`, `zip`, `qrencode`.
    ```bash
    sudo apt-get update && sudo apt-get install yq sshpass zip qrencode
    ```
* Projekt w Google Cloud Platform z włączonym **Gmail API**. Musisz pobrać plik poświadczeń `client_secret.json`.

Przykładowy "Formularz Google" i jego arkusz w "Google Sheets":
* https://forms.gle/eXdWgruSUeK7bcXp8
* https://docs.google.com/spreadsheets/d/1RDjmTp9mFpW1pEMcim6r5MV7lYj1juzRuxsh3UYDvpU

## 🇺🇸 Setup / 🇵🇱 Konfiguracja

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/LukeStriderGM/BLOX-TAK-SERVER-IUCP.git
    cd BLOX-TAK-SERVER-IUCP
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure `config.yaml`:**
    Rename `config.example.yaml` to `config.yaml` and fill in all the required values. **This step is crucial.**

    ```yaml
    # ==============================================================================
    # === SECURITY - Sensitive data and credentials
    # === SECURITY - Wrażliwe dane i poświadczenia
    # ==============================================================================
    security:
      # WARNING: Storing a plaintext password is a significant security risk.
      # OSTRZEŻENIE: Przechowywanie hasła w postaci czystego tekstu jest znaczącym ryzykiem bezpieczeństwa.
      sudo_pswd: '*****'

      # Absolute path to the Google API client_secret.json file.
      # Absolutna ścieżka do pliku client_secret.json od Google API.
      api_creds_path: /home/*****/BLOX-TAK-SERVER-IUCP/client_secret.json

    # ==============================================================================
    # === PATHS - Paths to key project directories
    # === PATHS - Ścieżki do kluczowych katalogów projektu
    # ==============================================================================
    paths:
      # Directory where the final .zip packages for users will be saved.
      # Katalog, w którym będą zapisywane finalne paczki .zip dla użytkowników.
      attachment_output: /home/*****/BLOX-TAK-SERVER-IUCP/

      # Directory where generated .pref and certificate files are placed before packaging.
      # Katalog, w którym generowane są pliki .pref i certyfikaty przed spakowaniem.
      preferences_output: /home/*****/BLOX-TAK-SERVER-IUCP/IUCP-IPPU_PACKAGE/certs/

      # The absolute path to the project's root directory.
      # Absolutna ścieżka do głównego katalogu projektu.
      project_root: /home/*****/BLOX-TAK-SERVER-IUCP/

    # ==============================================================================
    # === USER MANAGEMENT - User data management
    # === USER MANAGEMENT - Zarządzanie danymi użytkowników
    # ==============================================================================
    user_management:
      # Public URLs to the Google Sheets (published as CSV) containing user data.
      # Publiczne URL-e do Arkuszy Google (opublikowanych jako CSV) z danymi użytkowników.
      data_sources:
        en: https://docs.google.com/spreadsheets/d/e/2PACX-1vR-r4HG3Qdelr4fqt9GxmA7pljbFRxwsQRddxF6qY6FChMMYlC_trLesLgF8ayjhWe00n7PeuUQ6TSp/pub?gid=754383885&single=true&output=csv
        pl: https://docs.google.com/spreadsheets/d/e/2PACX-1vRdndMsKWQbT6RtHunuyoizVTeNE60RTRBh8OSlGY9FDEwcmqKwPaTB96b-rBDR7aImSjHk3l9x4hV_/pub?gid=1887676185&single=true&output=csv

      # --- Runtime State ---
      # This section is managed automatically by the scripts. Do not edit manually.
      # Ta sekcja jest zarządzana automatycznie przez skrypty. Nie edytuj ręcznie.
      state:
        client_name: '*****'
        email_address: '*.*.*@gmail.com'
        registration_date: '*-*-* *:*:*'
        number_users: 0
        user_index: 0
        user_type: EN

    email:
      # Set the email address you want to send messages from.
      # Ustaw adres e-mail, z którego chcesz wysyłać wiadomości.
      sender_email: '*.*.*@gmail.com'

    # ==============================================================================
    # === NETWORK - Network configuration
    # === NETWORK - Konfiguracja sieciowa
    # ==============================================================================
    network:
      # The external IP of the server, automatically detected by check_ip.py.
      # Zewnętrzny adres IP serwera, automatycznie wykrywany przez check_ip.py.
      external_ip: '*.*.*.*'

      # Details for the remote server if 'remote' mode is used.
      # Dane zdalnego serwera, używane w trybie 'remote'.
      remote_server:
        host: '*.*.*.*'
        user: '*****'

    # ==============================================================================
    # === EXECUTION - Script execution mode
    # === EXECUTION - Tryb pracy skryptów
    # ==============================================================================
    execution:
      # The operating mode of the scripts: 'local' or 'remote'. Managed by set_mode.py.
      # Tryb pracy skryptów: 'local' lub 'remote'. Zarządzany przez set_mode.py.
      mode: remote
    ```
5.  **Make shell scripts executable:**
    ```bash
    chmod +x *.sh
    ```

---
1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/LukeStriderGM/BLOX-TAK-SERVER-IUCP.git
    cd BLOX-TAK-SERVER-IUCP
    ```
2.  **Stwórz i aktywuj wirtualne środowisko Pythona:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Zainstaluj zależności Pythona:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Skonfiguruj `config.yaml`:**
    Zmień nazwę `config.example.yaml` na `config.yaml` i uzupełnij wszystkie wymagane wartości. **Ten krok jest kluczowy.**
    *Powyżej znajduje się przykład struktury pliku.*

5.  **Nadaj skryptom powłoki uprawnienia do wykonania:**
    ```bash
    chmod +x *.sh
    ```

## 🇺🇸 Usage / 🇵🇱 Użycie

The project is designed to be run from a central orchestrator script (`start.py`) but also contains standalone helper scripts.

### Main Onboarding Process
This is the primary workflow for generating certificates and packages for new users.

1.  **Set the execution mode** (optional, as the script will ask if not set):
    ```bash
    python3 set_mode.py 
    ```
2.  **Run the main orchestrator:**
    ```bash
    python3 start.py
    ```
    The script will guide you through selecting a language and then automatically process all users from the configured Google Sheet.

### Other Scripts
* **`revoke.py`**: A master script to revoke certificates for all users in a Google Sheet.
* **`update_android_wg.sh`**: Updates the WireGuard configuration for the Android client and generates a new QR code.
* **`make_cert_mumble.sh`**: Generates and copies a certificate for a Mumble server.

---

Projekt jest zaprojektowany do uruchamiania z centralnego skryptu-orkiestratora (`start.py`), ale zawiera również samodzielne skrypty pomocnicze.

### Główny Proces Wdrażania
To główny przepływ pracy do generowania certyfikatów i paczek dla nowych użytkowników.

1.  **Ustaw tryb pracy** (opcjonalne, skrypt zapyta, jeśli nie jest ustawiony):
    ```bash
    python3 set_mode.py 
    ```
2.  **Uruchom główny skrypt-orkiestrator:**
    ```bash
    python3 start.py
    ```
    Skrypt poprowadzi Cię przez wybór języka, a następnie automatycznie przetworzy wszystkich użytkowników ze skonfigurowanego Arkusza Google.

### Inne Skrypty
* **`revoke.py`**: Główny skrypt do odwoływania certyfikatów dla wszystkich użytkowników z Arkusza Google.
* **`update_android_wg.sh`**: Aktualizuje konfigurację WireGuard dla klienta Android i generuje nowy kod QR.
* **`make_cert_mumble.sh`**: Generuje i kopiuje certyfikat dla serwera Mumble.


## 🇺🇸 License / 🇵🇱 Licencja

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Ten projekt jest udostępniany na licencji MIT. Zobacz plik `LICENSE`, aby uzyskać szczegółowe informacje.

Tłumaczenie [PL]:

Licencja MIT

Prawa autorskie (c) 2025 Łukasz "LukeStriderGM" Andruszkiewicz

Niniejszym udziela się bezpłatnej zgody każdej osobie wchodzącej w posiadanie kopii
tego oprogramowania i powiązanych z nim plików dokumentacji (dalej „Oprogramowanie”),
na obchodzenie się z Oprogramowaniem bez ograniczeń, włączając w to bez ograniczeń
prawa do używania, kopiowania, modyfikowania, łączenia, publikowania, dystrybucji,
sublicencjonowania i/lub sprzedaży kopii Oprogramowania, oraz na zezwolenie osobom,
którym Oprogramowanie jest dostarczane, aby to czyniły, pod następującymi warunkami:

Powyższa nota o prawach autorskich i ta nota o pozwoleniu muszą być dołączone do wszystkich
kopii lub istotnych części Oprogramowania.

OPROGRAMOWANIE JEST DOSTARCZANE "TAKIM, JAKIE JEST", BEZ JAKIEJKOLWIEK GWARANCJI,
WYRAŹNEJ LUB DOROZUMIANEJ, WŁĄCZAJĄC W TO, ALE NIE OGRANICZAJĄC SIĘ DO, GWARANCJI
PRZYDATNOŚCI HANDLOWEJ, PRZYDATNOŚCI DO OKREŚLONEGO CELU ORAZ NIENARUSZALNOŚCI PRAW.
W ŻADNYM WYPADKU AUTORZY LUB POSIADACZE PRAW AUTORSKICH NIE BĘDĄ ODPOWIEDZIALNI
ZA JAKIEKOLWIEK ROSZCZENIA, SZKODY LUB INNE ZOBOWIĄZANIA, CZY TO W WYNIKU DZIAŁANIA
UMOWY, DELIKTU CZY W INNY SPOSÓB, WYNIKAJĄCE Z, LUB W ZWIĄZKU Z OPROGRAMOWANIEM
LUB UŻYCIEM LUB INNYMI DZIAŁANIAMI W OPROGRAMOWANIU.


## 🇺🇸 Code of Conduct / 🇵🇱 Kodeks Postępowania

This project and everyone participating in it is governed by the Contributor Covenant. See the `CODE_OF_CONDUCT.md` file for details.

Ten projekt i wszyscy jego uczestnicy podlegają zasadom Contributor Covenant. Zobacz plik `CODE_OF_CONDUCT.md`, aby uzyskać szczegółowe informacje.

Tłumaczenie [PL]:


## Kodeks Postępowania - Contributor Covenant

### Nasza Obietnica

Jako członkinie i członkowie, współtwórczynie i współtwórcy oraz liderki i liderzy
zobowiązujemy się, że udział w naszej społeczności będzie wolny od nękania dla
każdego, bez względu na wiek, budowę ciała, widoczną lub niewidoczną
niepełnosprawność, pochodzenie etniczne, cechy płciowe, tożsamość i ekspresję
płciową, poziom doświadczenia, wykształcenie, status społeczno-ekonomiczny,
narodowość, wygląd, rasę, religię czy tożsamość i orientację seksualną.

Zobowiązujemy się do działania i interakcji w sposób, który przyczynia się do
tworzenia otwartej, przyjaznej, zróżnicowanej, inkluzywnej i zdrowej społeczności.

### Nasze Standardy

Przykłady zachowań, które przyczyniają się do tworzenia pozytywnego środowiska
dla naszej społeczności, obejmują:

* Okazywanie empatii i życzliwości wobec innych osób
* Szacunek dla odmiennych opinii, punktów widzenia i doświadczeń
* Udzielanie i taktowne przyjmowanie konstruktywnej informacji zwrotnej
* Przyjmowanie odpowiedzialności, przepraszanie osób dotkniętych naszymi
    błędami i wyciąganie z nich wniosków
* Skupianie się nie tylko na tym, co najlepsze dla nas jako jednostek, ale dla
    całej społeczności

Przykłady niedopuszczalnych zachowań obejmują:

* Używanie języka lub obrazów o charakterze seksualnym oraz wszelkiego rodzaju
    zaloty lub umizgi o charakterze seksualnym
* Trolling, obraźliwe lub uwłaczające komentarze oraz ataki osobiste lub
    polityczne
* Nękanie publiczne lub prywatne
* Publikowanie prywatnych informacji innych osób, takich jak adres fizyczny lub
    mailowy, bez ich wyraźnej zgody
* Inne zachowania, które można by uznać za niewłaściwe w środowisku
    profesjonalnym

### Obowiązki Egzekwowania Zasad

Liderki i liderzy społeczności są odpowiedzialni za wyjaśnianie i egzekwowanie
naszych standardów oraz podejmą odpowiednie i sprawiedliwe działania naprawcze w
odpowiedzi na każde zachowanie, które uznają za niestosowne, zagrażające,
obraźliwe lub szkodliwe.

Liderki i liderzy społeczności mają prawo i obowiązek usuwać, edytować lub
odrzucać komentarze, commity, kod, edycje wiki, zgłoszenia i inne formy wkładu,
które nie są zgodne z niniejszym Kodeksem Postępowania, i w razie potrzeby
przedstawią powody swoich decyzji moderacyjnych.

### Zakres

Niniejszy Kodeks Postępowania obowiązuje we wszystkich przestrzeniach
społeczności, a także wtedy, gdy dana osoba oficjalnie reprezentuje społeczność w
przestrzeni publicznej. Przykłady reprezentowania naszej społeczności obejmują
używanie oficjalnego adresu e-mail, publikowanie postów za pośrednictwem
oficjalnego konta w mediach społecznościowych lub występowanie w charakterze
wyznaczonej przedstawicielki lub przedstawiciela na wydarzeniu online lub offline.

### Egzekwowanie Zasad

Przypadki obraźliwego, nękającego lub w inny sposób niedopuszczalnego zachowania
mogą być zgłaszane liderkom i liderom społeczności odpowiedzialnym za egzekwowanie
zasad pod adresem **luke.strider.gm@gmail.com**.
Wszystkie skargi zostaną rozpatrzone i zbadane niezwłocznie i sprawiedliwie.

Wszystkie liderki i liderzy społeczności są zobowiązani do poszanowania prywatności i
bezpieczeństwa osoby zgłaszającej incydent.

### Wytyczne Dotyczące Egzekwowania Zasad

Liderki i liderzy społeczności będą postępować zgodnie z niniejszymi Wytycznymi
Dotyczącymi Wpływu na Społeczność przy określaniu konsekwencji za każde
działanie, które uznają za naruszenie niniejszego Kodeksu Postępowania:

### 1. Naprawienie

**Wpływ na Społeczność**: Używanie niestosownego języka lub inne zachowanie uznane
za nieprofesjonalne lub niemile widziane w społeczności.

**Konsekwencja**: Prywatne, pisemne upomnienie od liderek lub liderów społeczności,
wyjaśniające naturę naruszenia i powód, dla którego zachowanie było
niestosowne. Może zostać zażądane publiczne przeproszenie.

### 2. Ostrzeżenie

**Wpływ na Społeczność**: Naruszenie w wyniku pojedynczego incydentu lub serii
działań.

**Konsekwencja**: Ostrzeżenie z konsekwencjami za dalsze zachowanie. Zakaz
interakcji z osobami zaangażowanymi, w tym nieproszonych interakcji z osobami
egzekwującymi Kodeks Postępowania, przez określony czas. Obejmuje to unikanie
interakcji w przestrzeniach społeczności, jak i na kanałach zewnętrznych, takich
jak media społecznościowe. Naruszenie tych warunków może prowadzić do
tymczasowego lub stałego bana.

### 3. Tymczasowy Ban

**Wpływ na Społeczność**: Poważne naruszenie standardów społeczności, w tym
utrzymujące się niestosowne zachowanie.

**Konsekwencja**: Tymczasowy zakaz jakichkolwiek interakcji lub publicznej
komunikacji ze społecznością na określony czas. W tym okresie zabronione są
publiczne i prywatne interakcje z osobami zaangażowanymi, w tym nieproszone
interakcje z osobami egzekwującymi Kodeks Postępowania. Naruszenie tych
warunków może prowadzić do stałego bana.

### 4. Stały Ban

**Wpływ na Społeczność**: Wykazywanie wzorca naruszania standardów społeczności,
w tym utrzymujące się niestosowne zachowanie, nękanie danej osoby lub agresja
wobec lub oczernianie grup osób.

**Konsekwencja**: Stały zakaz jakichkolwiek publicznych interakcji w ramach
społeczności.

---
Atrybucja

Niniejszy Kodeks Postępowania jest adaptacją [Contributor Covenant][homepage],
wersja 2.1, dostępnej pod adresem
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html

---
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================================
# === E-MAIL SENDER SCRIPT ===
# === SKRYPT DO WYSYŁANIA WIADOMOŚCI E-MAIL ===
# =====================================================================================

import os
import mimetypes
import base64
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Google Libraries ---
# --- Biblioteki Google ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{path}' not found!")
        print(f"BŁĄD: Plik konfiguracyjny '{path}' nie został znaleziony!")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load config file: {e}")
        print(f"BŁĄD: Nie udało się wczytać pliku konfiguracyjnego: {e}")
        return None


def google_api_authenticate(credentials_file, scopes):
    """
    Performs the Google API authentication process and returns credentials.

    Przeprowadza proces autentykacji Google API i zwraca dane uwierzytelniające.
    """
    creds = None
    token_file = "token.json"

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            print("Odświeżam token dostępu...")
            creds.refresh(Request())
        else:
            print("Performing new authentication...")
            print("Przeprowadzam nową autoryzację...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as token:
            token.write(creds.to_json())
            print(f"Credentials saved to {token_file}")
            print(f"Dane uwierzytelniające zapisano w {token_file}")

    return creds


def create_message_with_attachment(sender, to, subject, message_text, file_path):
    """
    Creates an email message object with an attachment.

    Tworzy obiekt wiadomości e-mail z załącznikiem.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(message_text))

    try:
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)

        with open(file_path, 'rb') as fp:
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(fp.read())

        encoders.encode_base64(attachment)
        filename = os.path.basename(file_path)
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(attachment)

        # Return the message formatted for the Gmail API
        # Zwróć wiadomość sformatowaną dla Gmail API
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    except FileNotFoundError:
        print(f"ERROR: Attachment file not found: {file_path}")
        print(f"BŁĄD: Plik załącznika nie został znaleziony: {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to create attachment: {e}")
        print(f"BŁĄD: Nie udało się utworzyć załącznika: {e}")
        return None


# =====================================================================================
# === MAIN SCRIPT LOGIC ===
# === GŁÓWNA LOGIKA SKRYPTU ===
# =====================================================================================

def main():
    """
    The main orchestrating function for sending emails.
    Główna funkcja orkiestrująca wysyłanie e-maili.
    """
    print("---")
    print("Starting e-mail sender script...")
    print("Uruchamiam skrypt wysyłania e-mail...")

    # --- Step 1: Load configuration ---
    # --- Krok 1: Wczytanie konfiguracji ---
    config = load_config()
    if not config:
        return

    try:
        user_state = config['user_management']['state']
        client_name = user_state['client_name']
        email_address = user_state['email_address']
        registration_date = user_state['registration_date']
        user_type = user_state['user_type']

        attachment_output_path = config['paths']['attachment_output']
        api_creds_path = config['security']['api_creds_path']
        sender_email = config['email']['sender_email']
    except KeyError as e:
        print(f"ERROR: Missing key in config.yaml: {e}")
        print(f"BŁĄD: Brakujący klucz w config.yaml: {e}")
        return

    # --- Step 2: Authenticate with Google API ---
    # --- Krok 2: Autoryzacja w Google API ---
    scopes = ["https://www.googleapis.com/auth/gmail.send"]
    creds = google_api_authenticate(api_creds_path, scopes)
    if not creds:
        print("ERROR: Failed to obtain credentials.")
        print("BŁĄD: Nie udało się uzyskać danych uwierzytelniających.")
        return

    # --- Step 3: Define email content based on user type ---
    # --- Krok 3: Zdefiniowanie treści maila na podstawie typu użytkownika ---
    if user_type == "EN":
        subject = "BLOX-TAK-SERVER-IUCP"
        message_text = f"""Hello, {client_name}!

Thank you for registering on {registration_date}:
https://forms.gle/VcUSKJ5bvuJ1nuBB6

This message was generated automatically by the BLOX-TAK-SERVER-IUCP software (Individual User Connection Profile).

This is a test message - the certificates in the ZIP package were revoked immediately after generation and will not work at this stage.
Up to an hour from sending this message, I will prepare an instructional video titled '#Instruction1' in the "featured" section on my LinkedIn profile:
https://www.linkedin.com/in/lukebluelox/details/featured

Best wishes from the "Giant Mountains" in Poland (in Polish: "Karkonosze"),
Łukasz "LukeBlueLOx" Andruszkiewicz
"""
    elif user_type == "PL":
        subject = "BLOX-TAK-SERVER-IPPU"
        message_text = f"""Witaj, {client_name}!

Dziękuję za rejestrację w dniu {registration_date}:
https://forms.gle/mrz8zPWiootVLYet8

Wiadomość została wygenerowana automatycznie przy pomocy oprogramowania BLOX-TAK-SERVER-IPPU (Indywidualny Profil Połączeniowy Użytkownika).

To jest wiadomość testowa - certyfikaty w paczce ZIP zostały odwołane tuż po wygenerowaniu i nie będą działać na tym etapie.
Do godziny czasu od rozesłania wiadomości, przygotuję film instruktarzowy o tytule "#Instrukcja1" w moich "wyróżnionych" na profilu LinkedIn:
https://www.linkedin.com/in/lukebluelox/details/featured

Pozdrowienia z Karkonoszy,
Łukasz "LukeBlueLOx" Andruszkiewicz
"""
    else:
        print(f"ERROR: Unknown user type: '{user_type}'")
        print(f"BŁĄD: Nieznany typ użytkownika: '{user_type}'")
        return

    # --- Step 4: Create and send the message ---
    # --- Krok 4: Utworzenie i wysłanie wiadomości ---
    try:
        service = build("gmail", "v1", credentials=creds)

        attachment_filename = f"IUCP-IPPU_PACKAGE_{client_name}.zip"
        attachment_path = os.path.join(attachment_output_path, attachment_filename)

        print(f"Creating message for: {email_address}")
        print(f"Tworzę wiadomość dla: {email_address}")
        message_body = create_message_with_attachment(sender_email, email_address, subject, message_text,
                                                      attachment_path)

        if message_body:
            print("Sending message...")
            print("Wysyłam wiadomość...")
            message = service.users().messages().send(userId='me', body=message_body).execute()
            print(f"Message sent successfully, ID: {message['id']}")
            print(f"Wiadomość pomyślnie wysłana, ID: {message['id']}")

    except HttpError as error:
        print(f"ERROR: An API error occurred: {error}")
        print(f"BŁĄD: Wystąpił błąd API: {error}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        print(f"BŁĄD: Wystąpił nieoczekiwany błąd: {e}")


if __name__ == "__main__":
    main()
    print("---")
    print("E-mail sender script finished.")
    print("Skrypt wysyłania e-mail zakończył działanie.")
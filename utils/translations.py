"""Translation module for the Business Central Publisher application."""

TRANSLATIONS = {
    'app_title': 'Business Central Erweiterung Publisher',
    'extension_file': 'Erweiterungsdatei',
    'drop_app': 'APP-Datei hier ablegen\noder zum Durchsuchen klicken',
    'server_config': 'Server-Konfiguration',
    'drop_json':
    'Server-Konfiguration JSON hier ablegen\noder zum Durchsuchen klicken',
    'clear': 'Server löschen',
    'parse_config': 'Konfiguration Parsen',
    'server_configs': 'Server-Konfigurationen',
    'publish_button': 'Auf ausgewählte Server veröffentlichen',
    'config_editor': 'Konfigurationseditor',
    'apply_changes': 'Änderungen übernehmen',
    'open_editor': 'Editor öffnen',
    'close': 'Schließen',
    'test_connection': 'Verbindung testen',  # New
    'connection_test_progress': 'Verbindungstest Fortschritt',  # New
    'testing_connection': 'Teste Verbindung zu {server}...',  # New
    'test_summary': '=== Verbindungstest Zusammenfassung ===',  # New
    'test_complete': 'Verbindungstest Abgeschlossen',  # New
    'test_complete_with_errors': 'Verbindungstest mit {count} Fehler(n) abgeschlossen',  # New
    'all_tests_successful': 'Alle Verbindungstests erfolgreich!',  # New
    'select_server_test': 'Bitte wählen Sie mindestens einen Server für den Test aus',  # New

    # Column headers
    'col_select': 'Auswahl',
    'col_type': 'Typ',
    'col_name': 'Name',
    'col_environment': 'Umgebung / Instanz',

    # Messages
    'confirm_deployment':
    'Möchten Sie {app_name} auf {count} ausgewählte(n) Server veröffentlichen?',
    'deployment_progress': 'Veröffentlichungsfortschritt',
    'deploying_to': 'Veröffentlichung auf {server}...',
    'deployment_summary': '=== Veröffentlichungszusammenfassung ===',
    'successful': 'Erfolgreich: {count}',
    'failed': 'Fehlgeschlagen: {count}',
    'deployment_complete': 'Veröffentlichung abgeschlossen',
    'deployment_complete_with_errors':
    'Veröffentlichung mit {count} Fehler(n) abgeschlossen.\nDetails im Fortschrittsfenster prüfen.',
    'all_deployments_successful':
    'Alle Veröffentlichungen erfolgreich abgeschlossen!',

    # Errors
    'select_app': 'Bitte wählen Sie zuerst eine APP-Datei aus',
    'select_server': 'Bitte wählen Sie mindestens einen Server aus',
    'invalid_app': 'Bitte wählen Sie eine gültige .app-Datei aus',
    'invalid_json': 'Bitte geben Sie eine Konfiguration im JSON-Format ein',
    'json_format_error':
    'JSON Format Fehler:\n{error}\n\nBitte überprüfen Sie Zeile {line}, Spalte {col} Ihrer JSON-Konfiguration.',
    'config_exists':
    'Eine Konfiguration mit dem Namen "{name}" existiert bereits.\nMöchten Sie sie überschreiben?',
    'enter_config': 'Bitte geben Sie eine Konfiguration ein'
}


def get_text(key: str, **kwargs) -> str:
    """Get translated text for the given key with optional format arguments."""
    text = TRANSLATIONS.get(key,
                            key)  # Fallback to key if translation not found
    if kwargs:
        return text.format(**kwargs)
    return text
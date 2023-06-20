# milvus_backend_bot
Milvus DB backend, feeding with data to use with LLM

## VM Einrichten

Wichtig ist eine Ubuntu 22 VM mit public IP.

1. Melden Sie sich beim Azure-Portal an.
2. Geben Sie "Virtuelle Maschinen" in die Suche ein.
3. Wählen Sie unter "Dienste" die Option "Virtuelle Maschinen".
4. Wählen Sie auf der Seite "Virtuelle Maschinen" die Option "Erstellen" und dann "Virtuelle Maschine". Die Seite zum Erstellen einer virtuellen Maschine wird geöffnet.
5. Wählen Sie auf der Registerkarte "Grundeinstellungen" unter "Projektdetails" das richtige Abonnement aus und entscheiden Sie sich dann für "Neue Ressourcengruppe erstellen". Geben Sie "myResourceGroup" als Namen ein. 
6. Geben Sie unter "Instanzdetails" "myVM" als Namen der virtuellen Maschine ein und wählen Sie "Ubuntu Server 22.04 LTS - Gen2" als Ihr Image. Lassen Sie die anderen Standardwerte.
7. Wählen Sie unter "Administrator-Konto" die Option "SSH-öffentlicher Schlüssel".
8. Geben Sie "azureuser" als Benutzernamen ein.
9. Wählen Sie ein Kennwort, dass man beim Einloggen immer angeben muss.
10. Wählen Sie unter "Eingehende Portregeln > Öffentliche eingehende Ports" die Option "Ausgewählte Ports zulassen" und wählen Sie dann SSH (22) aus dem Dropdown-Menü aus.
11. Lassen Sie die restlichen Standardwerte und wählen Sie dann die Schaltfläche "Überprüfen + erstellen" am unteren Rand der Seite.
12. Auf der Seite "Virtuelle Maschine erstellen" können Sie die Details zur VM, die Sie erstellen möchten, einsehen. Wenn Sie bereit sind, wählen Sie "Erstellen".
13. Unter dem Netzwerkblade sicherstellen, dass eine Public IP genutzt wird. Hier macht es auch Sinn den Haken bei "IP löschen wenn VM gelöscht"
14. Wenn die Bereitstellung abgeschlossen ist, wählen Sie "Zur Ressource gehen".
15. Kopieren Sie auf der Seite Ihrer neuen VM die öffentliche IP-Adresse in Ihre Zwischenablage.
16. (Diese beiden Schritte können mit dem Passwort übersprungen werden) Setzen Sie die nur-Lesen-Berechtigung auf die `.pem`-Datei mit dem Befehl `chmod 400 ~/Downloads/myKey.pem`.
17. Öffnen Sie eine SSH-Verbindung zu Ihrer VM. Ersetzen Sie die IP-Adresse durch die Ihrer VM und den Pfad zur `.pem`-Datei durch den Pfad, an dem die Schlüsseldatei heruntergeladen wurde:
    ssh -i ~/Downloads/myKey.pem azureuser@<Ihre-VM-IP>


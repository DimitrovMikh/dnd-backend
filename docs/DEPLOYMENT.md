# Server Setup & Production Hardening Guide

Dieses Dokument beschreibt die Schritt-für-Schritt-Einrichtung und Härtung unseres Unmanaged Linux Cloud VPS (Ubuntu 24.04 LTS) für das Deployment der Anwendung.

---

## 1. System & Betriebssystem-Update

Nach der Erstbereitstellung des VPS wird das System vollständig aktualisiert, um aktuelle Sicherheits-Patches einzuspielen.

```bash
# Paketlisten aktualisieren und System patchen
sudo apt update && sudo apt upgrade -y
```

---

## 2. Benutzer- & Rechte-Management (Least Privilege)

Aus Sicherheitsgründen wird die direkte Arbeit als `root` unterbunden. Ein dedizierter Sudo-User übernimmt die Administration.

```bash
# 1. Non-Root Administrator anlegen
sudo adduser deployer

# 2. Sudo-Gruppe zuweisen
sudo usermod -aG sudo deployer
```

---

## 3. SSH Security Hardening & Asymmetrische Schlüssel

Der Zugriff wird ausschließlich über moderne **Ed25519**-SSH-Schlüsselpaare gewährt. Passwort-Logins und der direkte `root`-Zugriff werden auf SSH-Daemon-Ebene deaktiviert.

### 3.1. Schlüsselübertragung (vom lokalen Client)

```bash
# Schlüssel lokal in WSL erzeugen (falls nicht vorhanden)
ssh-keygen -t ed25519 -C "dnd-backend-prod"

# Öffentlichen Schlüssel auf VPS kopieren
ssh-copy-id deployer@<SERVER_IP>
```

### 3.2. SSH Daemon Konfiguration

In der SSH-Provider-Konfiguration (z. B. `/etc/ssh/sshd_config.d/50-cloud-init.conf` oder `/etc/ssh/sshd_config`) werden folgende Parameter gesetzt:

```text
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
# Konfiguration verifizieren & SSH-Dienst neu starten
sudo sshd -t
sudo systemctl restart ssh.socket ssh
```

---

## 4. Host Firewall & Intrusion Prevention

### 4.1. UFW (Uncomplicated Firewall)

Es gilt das Security-Prinzip **Default Deny** (alles Eingehende blockieren, nur explizite Ports erlauben).

```bash
# Standard-Regeln definieren
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Erforderliche Ports öffnen
sudo ufw allow 22/tcp   # SSH Administration
sudo ufw allow 80/tcp comment 'HTTP Web traffic'  # HTTP (Web-Traffic)
sudo ufw allow 443/tcp comment 'HTTPS Encrypted Web traffic' # HTTPS (TLS Encryption)

# Firewall aktivieren
sudo ufw enable
```

### 4.2. Fail2ban (Brute-Force Protection)

Automatisierte Port-Scanner und fehlerhafte Login-Versuche werden über das `sshd`-Jail in Echtzeit analysiert und auf IP-Ebene gesperrt.

```bash
# Installieren und aktivieren
sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban
```

### 4.3. Unattended Upgrades (Automatisierte Sicherheits-Patches)

Kritische Sicherheits-Patches des Betriebssystems werden täglich im Hintergrund eingespielt.

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 5. Docker Engine & Docker Compose Installation

Installation der offiziellen Docker Engine (Upstream Repository) inklusive Docker Compose V2 Plugin.

```bash
# 1. Vorbereitende Pakete installieren
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# 2. Offiziellen GPG-Schlüssel von Docker hinzufügen
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 3. Docker-Repository hinzufügen
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Engine, CLI & Compose Plugin installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. Non-Root Rechte für den deployer-User einrichten
sudo usermod -aG docker deployer
newgrp docker
```

---

## 6. UFW Web-Ports & Reverse Proxy (Caddy) Installation

Freischaltung der Web-Ports in der Firewall und Installation von Caddy über das offizielle Debian/Ubuntu-Repository für automatisches TLS/SSL-Management.

```bash
# 1. Benötigte Pakete für Repository-Einbindung installieren
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# 2. GPG-Schlüssel von Caddy hinzufügen
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

# 3. Repository-Liste anlegen
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# 4. Paketlisten aktualisieren & Caddy installieren
sudo apt update
sudo apt install -y caddy

# 5. Status prüfen
sudo systemctl status caddy
```

---

## 7. Production Container Setup & Reverse Proxy Routing

Erstellung des Projektverzeichnisses, Absicherung der Umgebungsvariablen (`.env`), Konfiguration der Produktions-`docker-compose.yml` und Anbindung von Caddy.

```bash
# 1. Projektverzeichnis anlegen & aufrufen
mkdir -p ~/dnd-backend
cd ~/dnd-backend

# 2. Produktions-.env erstellen & Rechte auf deployer-User beschränken
nano .env
chmod 600 .env

# 3. Produktions-docker-compose.yml erstellen
nano docker-compose.yml

# 4. Caddy Reverse Proxy auf Port 8000 konfigurieren & neu laden
sudo nano /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

---

## 8. Automated CI/CD Pipeline & Remote Deployment (GitHub Actions)

Vollautomatisierte Deployment-Pipeline über GitHub Actions: Nach erfolgreicher Durchleitung der CI-Tests wird bei jedem Push auf `main` ein neues Production-Image gebaut, in die GitHub Container Registry (`ghcr.io`) gepusht und per SSH nahtlos auf dem VPS aktualisiert.

### 8.1 Required GitHub Repository Secrets

Unter **Settings > Secrets and variables > Actions** im GitHub-Repository hinterlegte Geheimnisse:

- `VPS_HOST`: Öffentliche IP-Adresse des Contabo-VPS
- `VPS_USERNAME`: `deployer`
- `SSH_PRIVATE_KEY`: Privater SSH-Schlüssel des lokalen PCs (`~/.ssh/id_ed25519`)
- `SSH_PORT`: `22` (oder benutzerdefinierter SSH-Port)

### 8.2 Deployment Workflow Architecture (`.github/workflows/cd.yml`)

1. **Trigger:** Reagiert auf das Ereignis `workflow_run` und wartet den erfolgreichen Durchlauf von `CI Quality Control` auf dem `main`-Branch ab.
2. **Build & Push Job (`build-and-push`):**
   - Authentifizierung an `ghcr.io` via `${{ secrets.GITHUB_TOKEN }}`.
   - Generierung strukturierter Metadata-Tags (`latest` und SHA-Hash).
   - Build des Dockerfiles aus `./backend` und Push an GHCR.
3. **Deploy Job (`deploy`):**
   - Ausführung von `appleboy/ssh-action` für die Remote-Verbindung.
   - Aktualisierung des Setups im Verzeichnis `~/dnd-backend`:
     ```bash
     cd ~/dnd-backend
     docker compose pull
     docker compose up -d
     docker image prune -f
     ```

### 8.3 Verifizierung auf dem VPS

```bash
# Aktive Container anzeigen
docker ps

# Container-Logs zur Fehleranalyse prüfen
docker logs -f dnd_backend
```
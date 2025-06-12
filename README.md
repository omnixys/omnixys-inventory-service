# 📦 GentleCorp Inventory Service

> DE | [ENGLISH BELOW](#-omnixys-inventory-service-en)

Willkommen beim **Inventory Service** des GentleCorp-Ecosystems. Dieser Microservice verwaltet Lagerbestände, Produktverfügbarkeiten und bietet APIs zur Bestandsabfrage und -aktualisierung.

---

## 📚 Inhaltsverzeichnis

-   [🚀 Funktionen](#-funktionen)
-   [🛠️ Technologie-Stack](#️-technologie-stack)
-   [⚙️ Installation & Setup](#️-installation--setup)
-   [🔐 Lizenz](#-lizenz)
-   [📬 Kommerzielle Lizenzierung](#-kommerzielle-lizenzierung)
-   [📞 Kontakt](#-kontakt)

---

## 🚀 Funktionen

-   Verwaltung von Lagerbeständen
-   Abfrage von Produktverfügbarkeiten
-   Reservierung und Freigabe von Lagerartikeln
-   REST-API für Anbindung an andere Microservices

---

## 🛠️ Technologie-Stack

-   **Sprache:** TypeScript
-   **Framework:** NestJS
-   **Datenbank:** MySQL
-   **Protokoll:** REST

---

## ⚙️ Installation & Setup

```bash
# Repository klonen
git clone https://github.com/GentleCorp-AG/omnixys-inventory-service.git
cd omnixys-inventory-service

# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm run start:dev
```

> Hinweis: Stelle sicher, dass eine lokale MySQL-Datenbank mit den korrekten Umgebungsvariablen läuft.

---

## 🔐 Lizenz

Dieses Projekt steht unter der **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### Kommerzielle Nutzung

Für den Einsatz in kommerziellen oder proprietären Systemen ist eine kommerzielle Lizenz erforderlich. Weitere Informationen findest du unter:

-   [`COMMERCIAL-LICENSE.md`](./COMMERCIAL-LICENSE.md)
-   [https://omnixys.com/lizenz](https://omnixys.com/lizenz)
-   📧 license@omnixys.com

---

## 📞 Kontakt

Bei Fragen oder Support:

-   💼 [https://omnixys.com](https://omnixys.com)
-   📧 hello@omnixys.com

---

# 📦 GentleCorp Inventory Service (EN)

Welcome to the **Inventory Service** of the GentleCorp Ecosystem. This microservice manages inventory data, product availability, and provides APIs for stock checking and updates.

---

## 📚 Table of Contents

-   [🚀 Features](#-features)
-   [🛠️ Tech Stack](#️-tech-stack)
-   [⚙️ Installation & Setup](#️-installation--setup)
-   [🔐 License](#-license)
-   [📬 Commercial Licensing](#-commercial-licensing)
-   [📞 Contact](#-contact)

---

## 🚀 Features

-   Manage product inventory
-   Check product availability
-   Reserve and release stock
-   REST API to integrate with other microservices

---

## 🛠️ Tech Stack

-   **Language:** TypeScript
-   **Framework:** NestJS
-   **Database:** MySQL
-   **Protocol:** REST

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/GentleCorp-AG/omnixys-inventory-service.git
cd omnixys-inventory-service

# Install dependencies
npm install

# Start development server
npm run start:dev
```

> Note: Ensure a local MySQL instance is running with correct environment variables.

---

## 🔐 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### Commercial Use

For usage in commercial or proprietary systems, a commercial license is required. Learn more:

-   [`COMMERCIAL-LICENSE.md`](./COMMERCIAL-LICENSE.md)
-   [https://omnixys.com/license](https://omnixys.com/license)
-   📧 license@omnixys.com

---

## 📞 Contact

For questions or support:

-   💼 [https://omnixys.com](https://omnixys.com)
-   📧 hello@omnixys.com

# 📦 Omnixys Inventory Service

Der **Omnixys Inventory Service** ist ein modularer Microservice zur Verwaltung von Lagerbeständen innerhalb der **OmnixysSphere**. Er stellt sicher, dass Produktverfügbarkeiten stets aktuell sind, Bestandsänderungen nachverfolgbar bleiben und andere Dienste (wie der Order- oder Product-Service) über GraphQL sowie Kafka Events integriert sind.

> Powered by **OmnixysOS** – The Fabric of Modular Innovation

---

## 🚀 Features

-   📦 Verwaltung von Beständen pro Produkt und Variante
-   📉 Echtzeitverfügbarkeiten durch GraphQL-Abfragen
-   🔄 Events bei Bestandserhöhungen/-verringerungen via Kafka
-   🧾 Tracing via OpenTelemetry (Tempo)
-   📊 Monitoring via Prometheus (/metrics)
-   🧠 Zugriffsschutz über Keycloak mit Rollenprüfung (`Admin`, `helper`)
-   �� Zentrales Logging via LoggerPlus + Kafka (`logs.inventory`)

---

## 💠 Tech Stack

| Komponente | Technologie                  |
| ---------- | ---------------------------- |
| API        | FastAPI + Strawberry GraphQL |
| DB         | MongoDB + Beanie ODM         |
| Auth       | Keycloak                     |
| Messaging  | Kafka (aiokafka)             |
| Monitoring | Prometheus, Grafana          |
| Tracing    | OpenTelemetry + Tempo        |
| Logging    | LoggerPlus + Kafka           |
| Port       | `7302`                       |

---

## 🥪 Getting Started

```bash
# Klone das Repository
git clone https://github.com/omnixys/omnixys-inventory-service.git
cd omnixys-inventory-service

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten (lokal)
uvicorn src.fastapi_app:app --reload
```

Oder via Docker:

```bash
docker-compose up
```

---

## 🔐 Authentifizierung

Alle geschützten Routen erfordern ein gültiges Bearer-Token von Keycloak. Rollenbasierte Zugriffe prüfen z. B.:

```python
if not user.has_realm_role("Admin"):
    raise NotAllowedError("Only admins can perform this operation.")
```

---

## 📡 GraphQL-Schnittstelle

Erreichbar unter:
`http://localhost:7302/graphql`

Beispiel-Query:

```graphql
query {
    getInventoryByProductId(productId: "123") {
        quantity
        updatedAt
    }
}
```

---

## �� Logging & Monitoring

-   Strukturierte Logs im JSON-Format (`LoggerPlus`)
-   Kafka-Integration via `LogEventDTO`
-   Tracing automatisch via Middleware (`TraceContext`)
-   Prometheus-Metrics unter `/metrics`

---

## 📤 Kafka Topics (Events)

| Event               | Beschreibung                             |
| ------------------- | ---------------------------------------- |
| `inventory.updated` | Bestandsänderung für ein Produkt         |
| `logs.inventory`    | Strukturierte Logs für zentrales Logging |

---

## 📂 Projektstruktur

```
src/
├── api/                  # REST / GraphQL Endpunkte
├── services/             # Businesslogik
├── kafka/                # Producer & Consumer
├── graphql/              # Schema & Resolver
├── models/               # Beanie-Dokumente
├── config/               # Mongo, Kafka, Keycloak
├── logger_plus.py        # Logging-Utility
├── fastapi_app.py        # FastAPI Setup
└── __main__.py           # Entry Point
```

---

## 🤝 Beitrag leisten

Siehe [CONTRIBUTING.md](./CONTRIBUTING.md) für Guidelines, Branching und PR-Regeln.

---

## 📜 Lizenz

Veröffentlicht unter der [GNU General Public License v3.0](./LICENSE)
© 2025 [Omnixys](https://omnixys.com)

---

> _Connect Everything. Empower Everyone._

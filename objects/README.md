# NaturalNetwork Data

Dieses Verzeichnis enthält die Seed-Daten für InfraHub im Object-Format.

## Dateistruktur

| Datei | Inhalt |
|-------|--------|
| `01_base.yml` | Standorte, Hersteller, Plattformen, Device Types |
| `02_ipam.yml` | VLANs und IP Prefixe |
| `03_l3_switches.yml` | Core Switches (Layer 3) |
| `04_l2_switches.yml` | Distribution & Access Switches (Layer 2) |
| `05_endpoints.yml` | Server, Workstations, Drucker |
| `06_ip_addresses.yml` | IP-Adressen für alle Geräte |

## Daten laden

```bash
# Alle Daten in InfraHub laden (Reihenfolge beachten!)
uv run infrahubctl object load data/01_base.yml
uv run infrahubctl object load data/02_ipam.yml
uv run infrahubctl object load data/03_l3_switches.yml
uv run infrahubctl object load data/04_l2_switches.yml
uv run infrahubctl object load data/05_endpoints.yml
uv run infrahubctl object load data/06_ip_addresses.yml
```

**Wichtig:** Die Dateien müssen in der richtigen Reihenfolge geladen werden, da Abhängigkeiten bestehen:
1. `01_base.yml` - Grundlegende Objekte (Standorte, Hersteller, Plattformen)
2. `02_ipam.yml` - VLANs und Prefixe
3. `03_l3_switches.yml` - Core Switches (referenzieren Standorte, Plattformen)
4. `04_l2_switches.yml` - Distribution und Access Switches
5. `05_endpoints.yml` - Endgeräte (referenzieren Standorte)
6. `06_ip_addresses.yml` - IP-Adressen

## Netzwerk-Übersicht

### Standorte
- **Bonn (BN)** - Außenstelle: 5 Switches, 2 PCs, 1 Drucker
- **Köln (KN)** - Headquarters: 6 Switches, 3 PCs, 1 Drucker, 1 Server

### Switches
| Typ | Bonn | Köln |
|-----|------|------|
| L3 (Core) | 1 | 1 |
| L2 (Distribution) | 2 | 2 |
| L2 (Access) | 2 | 3 |

### VLANs
| VLAN ID | Name | Verwendung |
|---------|------|------------|
| 10 | Management | Switch-Management |
| 100 | Users | Benutzer-PCs |
| 200 | Printers | Netzwerkdrucker |
| 300 | Servers | Server (nur Köln) |

### IP-Adressierung
| Standort | Management | Users | Printers | Servers |
|----------|------------|-------|----------|---------|
| Bonn | 10.10.10.0/24 | 10.10.100.0/24 | 10.10.200.0/24 | - |
| Köln | 10.20.10.0/24 | 10.20.100.0/24 | 10.20.200.0/24 | 10.20.30.0/24 |
| Inter-Site | 10.0.0.0/30 | - | - | - |

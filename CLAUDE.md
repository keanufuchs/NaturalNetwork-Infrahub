# CLAUDE.md — naturalnetwork-infrahub

InfraHub-Repository des NaturalNetwork-Projekts (Bachelorarbeit Keanu Fuchs).
Single Source of Truth fuer Netzwerkobjekte der Standorte Bonn (BN) und Koeln (KN).

---

## Kritische Regeln

- **InfraHub nur ueber `make`-Targets bedienen** — nie direkt `infrahubctl` ohne Makefile aufrufen, ausser fuer lesende Befehle (`transform`, `render`, `repository list`).
- **`generated/configs/` nicht manuell bearbeiten** — ausschliesslich durch `scripts/render_ios_xe_configs.py` oder `infrahubctl transform` erzeugt.
- **Objekt-Dateien in `objects/` nicht umbenennen** — Ladereihenfolge ist numerisch und intentional (00_ vor 01_ vor 07_ etc.).
- **Keine Direkt-Writes via `infrahubctl object load`** auf dem `main`-Branch — immer auf einem Feature-Branch arbeiten.

---

## Repo-Struktur

| Pfad | Zweck |
|---|---|
| `schemas/` | YAML-Schemadefinitionen (Switch, Interface, VLAN, IP, SVI …) |
| `objects/` | Objektdaten — Reihenfolge: Sites → Switches → IPs → SVIs → Interfaces |
| `queries/` | GraphQL-Queries (registriert in `.infrahub.yml`) |
| `transforms/jinja/` | Jinja2-Templates |
| `transforms/python/` | Python-Transforms (`InfrahubTransform`-Subklassen) |
| `generators/` | InfraHub-Generatoren |
| `scripts/` | Standalone-Hilfsscripte (nicht in InfraHub registriert) |
| `generated/configs/` | Generierte IOS-XE-Configs — Artefakte, kein Quellcode |
| `tests/integration/` | Integrationstests mit Testcontainers |

---

## InfraHub-Betrieb

```bash
make help            # Alle Targets anzeigen
make load-schema     # Schema laden (aktueller Git-Branch)
make load-objects    # Objekte laden
make cleanup         # Branch loeschen, neu erstellen, Schema + Objekte laden
make reset-branch    # Alias fuer cleanup
```

InfraHub-URL: `http://localhost:8000`
Standard-Branch: `main` (Produktionsdaten), Feature-Branches fuer Aenderungen.

---

## Transforms

### ios_xe_switch_config (Python Transform — nativ in InfraHub)

Vollstaendige IOS-XE-Konfiguration pro Switch aus InfraHub-Daten.

```bash
# CLI (liest .infrahub.yml lokal, kein Sync noetig)
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-CORE-01
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-DIST-01
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-01

# REST API (benoetigt Git-Commit + InfraHub-Repo-Sync)
curl "http://localhost:8000/api/transform/python/ios_xe_switch_config?name=SW-BN-CORE-01"
curl "http://localhost:8000/api/transform/python/ios_xe_switch_config?name=SW-BN-DIST-01&branch=main"
```

Dateien:
- Query: `queries/dcim_switch_ios_xe_config.gql`
- Transform: `transforms/python/ios_xe_switch_config.py` → `IosXeSwitchConfigTransform`
- Template: `transforms/jinja/ios_xe_switch_config.j2`

### Bulk-Rendering (alle Switches eines Standorts)

```bash
uv run python scripts/render_ios_xe_configs.py              # Bonn, main
INFRAHUB_SITE=Köln uv run python scripts/render_ios_xe_configs.py
INFRAHUB_BRANCH=develop uv run python scripts/render_ios_xe_configs.py
```

Output: `generated/configs/<switch-name>.cfg` — deterministisch (gleicher InfraHub-Zustand = identische Hashes).

### Weitere Transforms

```bash
uv run infrahubctl render switch_interfaces    # Interface-Konfiguration
uv run infrahubctl render switch_hostname      # Hostnamen
uv run infrahubctl transform --list            # Alle registrierten Transforms
```

---

## Queries

| Name | Variable | Zweck |
|---|---|---|
| `dcim_switch_ios_xe_config` | `name` | Config-Daten eines einzelnen Switches (fuer Transform) |
| `dcim_switch_full_config` | `site` | Config-Daten aller Switches eines Standorts (fuer Bulk-Script) |
| `cml_lab_topology` | `site` | Topologie-Daten (Switches + Links) fuer CML |
| `dcim_switch_interfaces` | `display_label` | Interface-Daten eines Switches |
| `dcim_switch_names` | — | Alle Switch-Namen |
| `ipam_ipaddress` | — | IP-Adressen |

Queries direkt testen:
```bash
curl -s -X POST http://localhost:8000/graphql/main \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ DcimSwitch(name__value: \"SW-BN-CORE-01\") { edges { node { name { value } role { value } } } } }"}'
```

---

## Dateikonventionen

### Schemas (`schemas/*.yml`)

Dateiname: `<nummer>_<namespace>_<typ>.yml` (z.B. `2400_dcim_switch.yml`)
Namespaces: `Dcim`, `Ipam`, `Endpoints`, `Base`

### Objekte (`objects/*.yml`)

Ladereihenfolge ist kritisch — abhaengige Objekte muessen spaeter geladen werden:

```
00_  Sites, Vendors
01_  Operating Systems
02_  Platforms
03_  Models, VLANs
04_  Switches, Prefixes
05_  IP-Adressen
06_  SVIs
07_  Physical Interfaces
08_  Interface-Verbindungen (connected_endpoint)
```

### Transforms (`transforms/python/*.py`)

- Erben von `InfrahubTransform`
- `query`-Attribut muss dem Query-Namen in `.infrahub.yml` entsprechen
- `transform(self, data: dict) -> str | dict` — `str` fuer Device-Configs, `dict` fuer JSON
- Template-Zugriff ueber `self.root_directory` (Repo-Root)

### Registrierung (`.infrahub.yml`)

Neue Queries, Transforms und Generatoren muessen in `.infrahub.yml` eingetragen werden, sonst sind sie InfraHub nicht bekannt.

---

## Tests

```bash
uv run pytest tests/
uv run pytest tests/integration/   # Benoetigt Docker (Testcontainers)
```

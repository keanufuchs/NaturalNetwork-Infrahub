# NaturalNetwork InfraHub Repository

InfraHub-Repository des NaturalNetwork-Projekts. Enthält Schemas, Objekte, Queries und Transforms für die Netzwerk-Single-Source-of-Truth (SoT) der Standorte Bonn (BN) und Köln (KN).

Dieses Repository ist Teil der Bachelorarbeit:
> *Einfluss von LLM-Quantisierung auf die Zuverlässigkeit intent-basierter Netzwerkautomatisierung mit InfraHub als Single Source of Truth*

---

## Voraussetzungen

- InfraHub läuft lokal unter `http://localhost:8000`
- Python 3.11+ mit [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

---

## Repository-Struktur

| Pfad | Inhalt |
|---|---|
| `schemas/` | YAML-Schemadefinitionen (Switch, Interface, VLAN, IP, SVI …) |
| `objects/` | Objektdaten für BN/KN-Topologie |
| `queries/` | GraphQL-Queries |
| `transforms/jinja/` | Jinja2-Templates |
| `transforms/python/` | Python-Transforms (InfrahubTransform) |
| `generated/configs/` | Generierte IOS-XE-Configs (Artefakt, nicht manuell bearbeiten) |
| `scripts/` | Hilfsscripte (Bulk-Rendering) |
| `generators/` | InfraHub-Generatoren |

---

## InfraHub verwalten

Alle InfraHub-Operationen über `make`-Targets:

```bash
make help           # Alle verfügbaren Targets
make load-schema    # Schema laden
make load-objects   # Objekte laden
make cleanup        # Branch zurücksetzen und neu laden
```

---

## Verfügbare Transforms

### ios_xe_switch_config (Python Transform)

Generiert eine vollständige IOS-XE-Konfiguration für einen einzelnen Switch aus InfraHub-Daten.

**Umfang:** hostname, VTP-Modus, VLAN-Datenbank, physische Interfaces (access/trunk/routed), SVIs mit IP-Adressen, ip routing

**Query:** `dcim_switch_ios_xe_config` (filtert per `name`)

**CLI:**
```bash
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-CORE-01
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-DIST-01
uv run infrahubctl transform ios_xe_switch_config name=SW-BN-01
```

**REST API** (nach Git-Commit + InfraHub-Sync):
```bash
curl "http://localhost:8000/api/transform/python/ios_xe_switch_config?name=SW-BN-CORE-01"
curl "http://localhost:8000/api/transform/python/ios_xe_switch_config?name=SW-BN-DIST-01&branch=main"
```

---

### Bulk-Rendering aller BN-Switches

Generiert `.cfg`-Dateien für alle Switches eines Standorts und legt sie in `generated/configs/` ab:

```bash
# Standard: site=Bonn, branch=main
uv run python scripts/render_ios_xe_configs.py

# Anderer Standort oder Branch
INFRAHUB_SITE=Köln uv run python scripts/render_ios_xe_configs.py
INFRAHUB_BRANCH=develop uv run python scripts/render_ios_xe_configs.py
```

Ausgabe:
```
generated/configs/SW-BN-CORE-01.cfg
generated/configs/SW-BN-DIST-01.cfg
generated/configs/SW-BN-DIST-02.cfg
generated/configs/SW-BN-01.cfg
generated/configs/SW-BN-02.cfg
```

Deterministisch: gleicher InfraHub-Zustand → identische MD5-Hashes.

---

### switch_interfaces (Jinja2 Transform)

Rendert Interface-Konfiguration für einen Switch.

```bash
uv run infrahubctl render switch_interfaces
```

### switch_hostname (Jinja2 + Python Transform)

Gibt den Hostnamen eines Switches aus.

```bash
uv run infrahubctl render switch_hostname
uv run infrahubctl transform switch_hostname
```

---

## Verfügbare Queries

| Query | Filter | Zweck |
|---|---|---|
| `dcim_switch_ios_xe_config` | `name` | Vollständige Config-Daten pro Switch (für Transform) |
| `dcim_switch_full_config` | `site` | Vollständige Config-Daten aller Switches eines Standorts |
| `cml_lab_topology` | `site` | CML-Topologie (Switches + Links) |
| `dcim_switch_interfaces` | `display_label` | Interface-Daten eines Switches |
| `dcim_switch_names` | — | Alle Switch-Namen |
| `ipam_ipaddress` | — | IP-Adressen |

---

## Tests

```bash
uv run pytest tests/
```

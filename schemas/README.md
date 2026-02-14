# NaturalNetwork InfraHub Schemas

Dieses Verzeichnis enthält die InfraHub-Schema-Definitionen für das NaturalNetwork-Projekt.

## Schema-Dateien

| Bereich | Dateien | Beschreibung |
|---------|---------|--------------|
| Base | 1000-1300 | Standorte, Organisationen |
| DCIM | 2000-2800 | Geräte, Interfaces, Plattformen |
| IPAM | 3000-3300 | IP-Adressen, Präfixe, VLANs |
| Endpoints | 4000-4500 | Server, PCs, Drucker, IoT |

## Dateinamen-Schema

Pattern: `XXXX_CATEGORY_SCHEMANODE.yml`

| Komponente | Beschreibung |
|------------|--------------|
| XXXX | Nummer 1000-9999 (logische Reihenfolge) |
| CATEGORY | Schema-Kategorie |
| SCHEMANODE | Schema-Node Name |

## Order Weight Ranges

| Range | Kategorie | Beispiele |
|-------|-----------|-----------|
| 100-199 | Identität | name, description, status, role |
| 200-299 | Netzwerk | vlan_id, vrf, mtu, ip_addresses |
| 400-499 | Hardware | platform, device_type, serial |
| 600-699 | Standort | location, rack, timezone |
| 700-799 | Metadaten | tags |

## Schema-Hierarchie

```
┌─────────────────────────────────────────────────────────────┐
│                    base/location + organization              │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ LocationSite     │  │ OrganizationManufacturer         │ │
│  │ - Bonn (BN)      │  │ - Cisco                          │ │
│  │ - Köln (KN)      │  └──────────────────────────────────┘ │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
          │                         │
          ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         ipam/                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ IpamPrefix   │  │ IpamIPAddress│  │ IpamVLAN         │   │
│  │ - 10.10.x.0  │  │ - Gateways   │  │ - 10 Management  │   │
│  │ - 10.20.x.0  │  │ - Device IPs │  │ - 100 Users      │   │
│  └──────────────┘  └──────────────┘  │ - 200 Printers   │   │
│                                       │ - 300 Servers    │   │
│  ┌──────────────────────────────────┐└──────────────────┘   │
│  │ IpamStaticRoute                  │                        │
│  │ - Inter-Site Routes              │                        │
│  └──────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                         dcim/                                │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ DcimSwitch       │  │ DcimPhysicalInterface            │ │
│  │ - Core Layer     │  │ - GigabitEthernet Ports          │ │
│  │ - Distribution   │  │ - Access/Trunk Modes             │ │
│  │ - Access Layer   │  │ - VLAN Assignments               │ │
│  │ - L2/L3 Support  │  └──────────────────────────────────┘ │
│  └──────────────────┘                                        │
│                        ┌──────────────────────────────────┐ │
│  ┌──────────────────┐  │ DcimPlatform / DeviceType        │ │
│  │ DcimSVIInterface │  │ - IOSv, IOSvL2, IOS-XE           │ │
│  │ - VLAN Gateways  │  └──────────────────────────────────┘ │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                       endpoints/                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │
│  │ Server     │ │ Workstation│ │ Printer    │ │ Camera   │  │
│  │ Server-KN  │ │ PC-BN-01   │ │ Drucker-BN │ │ Cam-01   │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Laden der Schemas

Verwende immer das Makefile:

```bash
make load-schema
```

## Verwendung

Schemas beschreiben die Datenstruktur für Infrahub-Objekte. 
Siehe [docs/schema.md](../docs/schema.md) für Entwicklungsrichtlinien.

## Beziehungen

```
LocationSite ─────┬────> DcimSwitch ────────────> DcimPhysicalInterface
                  │                                        │
                  │                                        ├──> IpamVLAN (untagged/tagged)
                  │                                        │
                  │                                        └──> EndpointEndpoint (connected)
                  │
                  └────> IpamPrefix ────> IpamIPAddress
                              │
                              └────> IpamVLAN
```

## Referenz

Diese Schemas basieren auf der [OpsMill Schema Library](https://github.com/opsmill/schema-library) und wurden für das NaturalNetwork Lab-Szenario angepasst.


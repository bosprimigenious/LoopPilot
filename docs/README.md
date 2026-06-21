# LoopPilot Documentation

Documentation root for LoopPilot. Pick an entry by audience and language.

## Quick navigation

| Audience | Entry |
|----------|-------|
| Daily reading (Chinese) | [zh/README.md](zh/README.md) |
| Chinese doc policy (authoritative) | [zh/10-中英文文档管理.md](zh/10-中英文文档管理.md) |
| English interface spec (AI / CI) | [en-core.md](en-core.md) |
| Full development specs (numbered) | [development/README.md](development/README.md) |
| Repository layout (Chinese) | [zh/06-仓库目录说明.md](zh/06-仓库目录说明.md) |

## Structure

```text
docs/
├── README.md              # this file
├── en-core.md             # English minimal interface spec
├── zh/                    # Chinese cognitive layer (00–10)
└── development/           # English numbered specs (00–42) + logs/
```

## Bilingual index (high level)

| Topic | Chinese | English |
|-------|---------|---------|
| Version roadmap | [zh/03-版本路线图.md](zh/03-版本路线图.md) | [development/34-version-roadmap-0x.md](development/34-version-roadmap-0x.md) |
| 0.3 acceptance | [zh/07-0.3-Adapter验收说明.md](zh/07-0.3-Adapter验收说明.md) | [development/36-adapter-mvp-0.3-acceptance.md](development/36-adapter-mvp-0.3-acceptance.md) |
| 0.4 personal daily loop | [zh/08-0.4-个人日用闭环.md](zh/08-0.4-个人日用闭环.md) | [development/40-personal-daily-loop-0.4-spec.md](development/40-personal-daily-loop-0.4-spec.md) |
| 1.x personal → collaboration | [zh/09-1.x-个人到协作.md](zh/09-1.x-个人到协作.md) | [development/42-1x-roadmap-personal-to-collaboration.md](development/42-1x-roadmap-personal-to-collaboration.md) |
| Doc management policy | [zh/10-中英文文档管理.md](zh/10-中英文文档管理.md) | [development/README.md](development/README.md) (mapping table) |

Full zh ↔ en mapping: [development/README.md#中文认知层对应关系](development/README.md).

## Language convention

- **Chinese (`docs/zh/`)**: understand what the system is, how to run it, where things live.
- **English (`docs/en-core.md`, `docs/development/`)**: authoritative contracts for code, CLI, schemas, and acceptance.
- **Mixed (`prompts/`)**: Chinese goals + English constraints for AI implementation tasks.

See [zh/05-文档体系说明.md](zh/05-文档体系说明.md) for the three-layer model; maintenance rules in [zh/10-中英文文档管理.md](zh/10-中英文文档管理.md).

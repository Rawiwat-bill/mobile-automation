# Canonical Business Flow Source Documents

This directory stores the canonical business source documents for the business flows. Each flow owns its own canonical Visio diagram:

- ETB: `etb/current/Onboarding_Sequence Diagram.vsdx`
- NTB: `ntb/current/NTB_SequenceDiagram.vsdx`
- Reactivate: `reactivate/current/Reactivation_Sequence Diagram (MVPX).vsdx`

The `.vsdx` files are the business source of truth. They are not AI knowledge and must never be placed under `knowledge/`. They must not be modified by Hermes; Business / BA maintains them.

Each `archive/` directory stores previous versions of that flow's canonical Visio source only.

## AIOS Knowledge Workflow

When Hermes needs business-flow knowledge, it must first determine the active business flow and select that flow's corresponding canonical Visio source. The Visio document is read only during knowledge generation. During engineering work, Hermes must not read the raw Visio directly; it must query the AIOS Query Engine, which answers from generated knowledge.

The workflow is:

1. Business updates the Visio diagram.
2. Business replaces only the corresponding file inside that flow's `current/` directory.
3. Hermes reads the updated Visio source for the active flow.
4. Hermes generates the Flow Contract.
5. Hermes generates Markdown knowledge and Mermaid.
6. The generated knowledge is written to `knowledge/flows/<flow>/`.
7. The AIOS Query Engine consumes only the generated knowledge.

When a canonical Visio diagram changes, regenerate the Flow Contract, Mermaid, and Markdown knowledge, update the AIOS Query cache, and invalidate outdated repository answers. Engineering decisions must not be based on stale generated knowledge.

## ETB Synchronization Record

- Flow: `ETB_NEW`
- Source: `etb/current/Onboarding_Sequence Diagram.vsdx`
- Last synchronized: `2026-08-05`
- Generated contract: `knowledge/flows/etb/flow.yaml`
- Generated Markdown: `knowledge/flows/etb/flow.md`
- Generated Mermaid: `knowledge/flows/etb/diagram.mmd`

The Visio files remain the canonical business documents. The generated knowledge becomes the canonical AI knowledge.

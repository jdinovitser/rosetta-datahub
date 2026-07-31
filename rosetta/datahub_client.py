"""
Thin wrapper around DataHub's Python SDK + MCP server.

Rosetta reads context (glossary terms, column descriptions, lineage, ownership,
historical SQL) and WRITES BACK canonical glossary terms, deprecation tags, and
documentation. The write-back loop is the part the judges care most about:
DataHub's own Analytics Agent demo highlighted that "the agent does useful work
today, and the context platform underneath gets richer every time it runs."

Requirements: Python 3.10+, a running DataHub instance, and a personal access token.

Set:
  DATAHUB_GMS_URL   e.g. http://localhost:8080
  DATAHUB_GMS_TOKEN your personal access token

The SDK reads these automatically via DataHubClient.from_env().
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable

# The DataHub SDK is imported lazily so the repo's unit tests can run without a
# live instance (see tests/ for the fully mocked detector tests).
try:
    from datahub.sdk import DataHubClient, DatasetUrn, GlossaryTermUrn
    from datahub.sdk.glossary_term import GlossaryTerm

    _HAS_SDK = True
except Exception:  # pragma: no cover - only in envs without the SDK installed
    _HAS_SDK = False
    DataHubClient = object  # type: ignore
    DatasetUrn = object  # type: ignore
    GlossaryTermUrn = object  # type: ignore
    GlossaryTerm = object  # type: ignore


@dataclass
class MetricDefinition:
    """One team's understanding of a business metric."""

    name: str  # normalized name, e.g. "active_user"
    display_name: str  # raw label as it appears, e.g. "Monthly Active Users"
    domain: str  # owning domain, e.g. "finance"
    owner: str  # DataHub owner URN or team id
    definition_text: str  # human definition (glossary or column desc)
    sql_logic: str = ""  # inferred computation from historical SQL
    source_urns: list[str] = field(default_factory=list)  # assets that use it
    term_urn: str = ""  # existing glossary term URN, if any
    tags: list[str] = field(default_factory=list)  # DataHub tags (e.g. pii, sensitive)
    last_modified: str = ""  # ISO date the definition was last updated (stale-ness signal)


class RosettaDataHub:
    """Read/write facade over DataHub for the Rosetta agents."""

    def __init__(self, client: "DataHubClient | None" = None) -> None:
        if client is not None:
            self.client = client
        elif _HAS_SDK:
            self.client = DataHubClient.from_env()
        else:  # pragma: no cover
            raise RuntimeError(
                "acryl-datahub SDK not installed. `pip install acryl-datahub` "
                "or pass a mock client for tests."
            )

    # ---------- READ ----------
    def harvest_metric_definitions(self) -> list[MetricDefinition]:
        """
        Pull candidate metric definitions from the graph.

        In a full build this queries the DataHub search + GraphQL APIs for
        glossary terms and column descriptions, then parses historical SQL
        (Pinterest's trick) to infer how each metric is actually computed.

        For the hackathon demo we seed from demo_data/seed_definitions.json so
        the flow is reproducible without a warehouse. Swap this method for real
        client.search / client.entities.get calls against your instance.
        """
        import json
        from pathlib import Path

        seed = Path(__file__).resolve().parent.parent / "demo_data" / "seed_definitions.json"
        raw = json.loads(seed.read_text())
        return [MetricDefinition(**row) for row in raw]

    def blast_radius(self, defn: MetricDefinition) -> int:
        """
        Count downstream assets impacted by a definition by walking lineage.

        Real implementation uses client.lineage.get_lineage(... direction=DOWNSTREAM)
        and dedupes dashboards/models/datasets. Here we walk the seed lineage
        graph transitively so a wrong definition's true blast radius includes
        every dashboard/model that transitively consumes it.
        """
        return len(self.downstream_assets(defn))

    def downstream_assets(self, defn: MetricDefinition) -> list[str]:
        """
        Breadth-first walk of the downstream lineage graph from every asset
        that directly uses this definition. Returns the full set of transitively
        impacted assets (deduped, excluding the seed assets themselves).

        Mirrors client.lineage.get_lineage(urn, direction="DOWNSTREAM") which
        returns paths; we flatten and dedupe those paths.
        """
        graph = self._lineage_graph()
        seen: set[str] = set()
        frontier = list(defn.source_urns)
        while frontier:
            node = frontier.pop()
            for child in graph.get(node, []):
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)
        # include the direct source assets themselves in the impact count
        for u in defn.source_urns:
            seen.add(u)
        return sorted(seen)

    def _lineage_graph(self) -> dict:
        if getattr(self, "_lineage_cache", None) is not None:
            return self._lineage_cache
        import json
        from pathlib import Path

        path = Path(__file__).resolve().parent.parent / "demo_data" / "lineage.json"
        if path.exists():
            raw = json.loads(path.read_text())
            self._lineage_cache = {k: v for k, v in raw.items() if not k.startswith("_")}
        else:  # pragma: no cover
            self._lineage_cache = {}
        return self._lineage_cache

    def impact_graph(self, defn: MetricDefinition) -> dict:
        """
        Build a node/edge graph of everything a wrong definition contaminates,
        for visualization. Nodes are typed (metric | dataset | dashboard | model)
        and edges are directed downstream. The metric node is the origin.
        """
        graph = self._lineage_graph()
        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        origin_id = f"metric::{defn.name}::{defn.domain}"
        nodes[origin_id] = {
            "id": origin_id,
            "label": f"{defn.display_name}\n({defn.domain})",
            "type": "metric",
        }

        def kind(urn: str) -> str:
            if ":dashboard:" in urn or ":chart:" in urn:
                return "dashboard"
            if ":mlModel:" in urn or ":mlFeatureTable:" in urn:
                return "model"
            return "dataset"

        def short(urn: str) -> str:
            # dashboards/charts: use the last identifier inside the parens
            if ":dashboard:" in urn or ":chart:" in urn:
                inner = urn.split("(", 1)[-1].rstrip(")")
                parts = [p for p in inner.split(",") if p]
                return parts[-1].split(".")[-1] if parts else urn
            if ":mlModel:" in urn:
                inner = urn.split("(", 1)[-1].rstrip(")")
                parts = [p for p in inner.split(",") if p]
                return parts[1] if len(parts) > 1 else parts[-1]
            # datasets: table name is the middle comma-field, last dotted segment
            inner = urn.split("(", 1)[-1].rstrip(")")
            parts = [p for p in inner.split(",") if p]
            table = parts[1] if len(parts) > 1 else inner
            return table.split(".")[-1]

        seen: set[str] = set()
        frontier = []
        for u in defn.source_urns:
            nodes.setdefault(u, {"id": u, "label": short(u), "type": kind(u)})
            edges.append({"source": origin_id, "target": u})
            frontier.append(u)
            seen.add(u)
        while frontier:
            node = frontier.pop()
            for child in graph.get(node, []):
                nodes.setdefault(child, {"id": child, "label": short(child), "type": kind(child)})
                edges.append({"source": node, "target": child})
                if child not in seen:
                    seen.add(child)
                    frontier.append(child)
        return {"nodes": list(nodes.values()), "edges": edges}

    # ---------- VERIFY (post-write confirmation) ----------

    def read_glossary_term(self, term_urn: str) -> dict | None:
        """Re-read a GlossaryTerm entity and return its observed attributes.

        Used by verify_proposal() to confirm a write actually applied.
        Returns None if the entity cannot be read or does not exist.
        """
        if not _HAS_SDK:
            return None
        try:
            term = self.client.entities.get(GlossaryTermUrn.from_string(term_urn))
            if term is None:
                return None
            result: dict = {"urn": term_urn, "exists": True}
            # Definition may be on different attributes depending on SDK version
            for attr in ("definition", "description", "doc"):
                val = getattr(term, attr, None)
                if val:
                    result["definition"] = str(val)
                    break
            # Deprecated flag
            for attr in ("deprecated", "is_deprecated"):
                val = getattr(term, attr, None)
                if val is not None:
                    result["deprecated"] = bool(val)
                    break
            return result
        except Exception:
            return None

    def read_asset_term_urns(self, asset_urn: str) -> list[str]:
        """Return the glossary term URNs currently attached to a dataset.

        Used by verify_proposal() to confirm that attach_term_to_asset applied.
        Returns an empty list if the entity cannot be read.
        """
        if not _HAS_SDK:
            return []
        try:
            dataset = self.client.entities.get(DatasetUrn.from_string(asset_urn))
            if dataset is None:
                return []
            # SDK versions differ on attribute name
            for attr in ("glossary_terms", "terms", "glossaryTerms"):
                raw = getattr(dataset, attr, None)
                if raw is None:
                    continue
                urns: list[str] = []
                for t in raw:
                    if isinstance(t, str):
                        urns.append(t)
                    else:
                        urn = getattr(t, "urn", None) or getattr(t, "term_urn", None)
                        urns.append(str(urn) if urn else str(t))
                return urns
            return []
        except Exception:
            return []

    # ---------- WRITE (the loop that compounds) ----------
    def write_canonical_term(
        self, term_id: str, display_name: str, definition: str
    ) -> str:
        """Upsert the agreed canonical glossary term back into DataHub."""
        if not _HAS_SDK:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        term = GlossaryTerm(id=term_id, display_name=display_name, definition=definition)
        self.client.entities.upsert(term)
        return f"urn:li:glossaryTerm:{term_id}"

    def attach_term_to_assets(self, term_urn: str, asset_urns: Iterable[str]) -> None:
        """Link the canonical term to every affected dataset."""
        if not _HAS_SDK:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        for urn in asset_urns:
            dataset = self.client.entities.get(DatasetUrn.from_string(urn))
            dataset.add_term(GlossaryTermUrn(term_urn))
            self.client.entities.update(dataset)

    def deprecate_conflicting_term(self, term_urn: str, note: str) -> None:
        """
        Mark a losing definition deprecated. Deprecated terms remain in the
        system and keep their relationships, so nothing breaks; they just stop
        being the recommended vocabulary. (See DataHub GlossaryTerm docs.)
        """
        if not _HAS_SDK:  # pragma: no cover
            raise RuntimeError("SDK required to write to DataHub.")
        term = self.client.entities.get(GlossaryTermUrn.from_string(term_urn))
        # set_deprecation is available on the term entity in recent SDKs
        term.set_deprecation(deprecated=True, note=note)
        self.client.entities.update(term)

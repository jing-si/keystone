"""Pure canonical-source selection for inline and adjacent companion metadata."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from .adapters import Adapter, adapter_for_path, prepare_adapter
from .model import Diagnostic


COMPANION_SUFFIX = ".keystone.json"


class SourceSurface(str, Enum):
    INLINE = "inline"
    COMPANION = "companion"


@dataclass(frozen=True)
class SourceUnit:
    path: str
    adapter: Optional[Adapter]
    source_bytes: Optional[bytes]
    companion_bytes: Optional[bytes]
    surface: Optional[SourceSurface]
    diagnostics: Tuple[Diagnostic, ...] = ()
    prepared_adapter: Optional[Adapter] = None

    @property
    def parsing_adapter(self) -> Optional[Adapter]:
        return self.prepared_adapter or self.adapter

    @property
    def companion_path(self) -> str:
        return self.path + COMPANION_SUFFIX

    @property
    def generation_paths(self) -> Tuple[str, ...]:
        paths = []
        if self.source_bytes is not None:
            paths.append(self.path)
        if (
            self.surface in {SourceSurface.COMPANION, None}
            and self.companion_bytes is not None
        ):
            paths.append(self.companion_path)
        return tuple(paths)

    @property
    def generation_items(self) -> Tuple[Tuple[str, bytes], ...]:
        values = []
        if self.source_bytes is not None:
            values.append((self.path, self.source_bytes))
        if (
            self.surface in {SourceSurface.COMPANION, None}
            and self.companion_bytes is not None
        ):
            values.append((self.companion_path, self.companion_bytes))
        return tuple(values)


def resolve_source_unit(
    path: str,
    source_bytes: Optional[bytes],
    companion_bytes: Optional[bytes],
) -> SourceUnit:
    """Select exactly one canonical metadata surface without merging declarations."""
    adapter = adapter_for_path(path)
    if companion_bytes is not None:
        try:
            companion_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return SourceUnit(
                path,
                adapter,
                source_bytes,
                companion_bytes,
                None,
                (Diagnostic(
                    "unsupported_encoding",
                    "companion metadata is not UTF-8",
                    path=path + COMPANION_SUFFIX,
                ),),
            )
    if adapter is None:
        surface = SourceSurface.COMPANION if companion_bytes is not None else None
        return SourceUnit(path, None, source_bytes, companion_bytes, surface)
    if source_bytes is None:
        surface = SourceSurface.COMPANION if companion_bytes is not None else None
        return SourceUnit(path, adapter, None, companion_bytes, surface)
    try:
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError:
        if companion_bytes is not None:
            return SourceUnit(
                path,
                adapter,
                source_bytes,
                companion_bytes,
                SourceSurface.COMPANION,
            )
        return SourceUnit(
            path,
            adapter,
            source_bytes,
            None,
            None,
            (Diagnostic(
                "unsupported_encoding",
                "supported source is not UTF-8 and has no canonical companion",
                path=path,
            ),),
        )
    prepared = prepare_adapter(adapter, text)
    lexical_findings = (
        prepared.metadata_diagnostics(text)
        if hasattr(prepared, "metadata_diagnostics")
        else ()
    )
    if lexical_findings:
        return SourceUnit(
            path,
            adapter,
            source_bytes,
            companion_bytes,
            None,
            tuple(
                Diagnostic(code, message, path=path)
                for code, message in lexical_findings
            ),
        )
    if companion_bytes is None:
        return SourceUnit(path, adapter, source_bytes, None, SourceSurface.INLINE,
                          prepared_adapter=prepared)

    has_inline_declarations = any(prepared.metadata_blocks(text))
    if has_inline_declarations:
        return SourceUnit(
            path,
            adapter,
            source_bytes,
            companion_bytes,
            None,
            (Diagnostic(
                "metadata_surface_conflict",
                "source has both inline and companion Keystone declarations",
                path=path,
            ),),
        )
    return SourceUnit(
        path,
        adapter,
        source_bytes,
        companion_bytes,
        SourceSurface.COMPANION,
    )

#!/usr/bin/env python
"""Generate Pydantic models and endpoint methods from the NetDoc OpenAPI spec.

Usage:
    python scripts/generate.py

Both output files are generated artifacts — do not edit them manually.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from datamodel_code_generator import DataModelType, InputFileType, generate
from datamodel_code_generator.format import Formatter

REPO_ROOT = Path(__file__).parent
OPENAPI_PATH = REPO_ROOT / '../netdoc/docs/api/openapi.yaml'
MODELS_OUTPUT = REPO_ROOT / 'src/netdoc_sdk/models/_generated_models.py'
ENDPOINTS_OUTPUT = REPO_ROOT / 'src/netdoc_sdk/_generated_endpoints.py'

GENERATED_HEADER = """\
# GENERATED FILE — do not edit manually.
# Run: python scripts/generate.py
"""

# Explicit full overrides — applied after any suffix/prefix normalization.
# Use for action endpoints where the generated name is redundant or verbose.
_OPERATION_ID_OVERRIDES = {
    'canonical_devices_history_list': 'canonical_devices_history',
    'canonical_endpoints_history_list': 'canonical_endpoints_history',
    'collectors_heartbeat_add': 'collectors_heartbeat',
    'discoveries_cancel_add': 'discoveries_cancel',
    'discovery_jobs_claim_add': 'discovery_jobs_claim',
    'discovery_jobs_complete_add': 'discovery_jobs_complete',
    'discovery_jobs_logs_list': 'discovery_jobs_logs',
    'discovery_jobs_push_discovered_device_add': 'discovery_jobs_push_discovered_device',
    'snapshots_latest_get': 'snapshots_latest',
    'snapshots_pin_add': 'snapshots_pin',
    'snapshots_stats_get': 'snapshots_stats',
    'snapshots_unpin_add': 'snapshots_unpin',
    'tenants_current_get': 'tenants_current',
}

# Mapping from OpenAPI operationId suffix → SDK method suffix
_OPERATION_SUFFIX_MAP = {
    'create': 'add',
    'partial_update': 'update',
    'retrieve': 'get',
    'destroy': 'delete',
    # 'list' stays as-is
}


def _normalize_operation_id(operation_id: str) -> str:
    """Remap OpenAPI operationId suffixes to SDK naming conventions.

    Examples:
        canonical_devices_create        → canonical_devices_add
        canonical_devices_partial_update → canonical_devices_update
        canonical_devices_retrieve      → canonical_devices_get
        canonical_devices_destroy       → canonical_devices_delete
        canonical_devices_list          → canonical_devices_list  (unchanged)
    """
    result = operation_id

    # Step 1 — CRUD suffix remapping
    for openapi_suffix, sdk_suffix in _OPERATION_SUFFIX_MAP.items():
        # Match suffix at end of string, preceded by underscore
        if operation_id == openapi_suffix:
            result = sdk_suffix
        if operation_id.endswith(f'_{openapi_suffix}'):
            result = operation_id[: -len(openapi_suffix)] + sdk_suffix

    # Step 2 — explicit override
    if result in _OPERATION_ID_OVERRIDES:
        result = _OPERATION_ID_OVERRIDES[result]

    return result


# ---------------------------------------------------------------------------
# Step 1 — Pydantic models via datamodel-code-generator Python API
# ---------------------------------------------------------------------------


def generate_models() -> None:
    """Invoke datamodel-code-generator programmatically."""
    generate(
        input_=OPENAPI_PATH,
        input_file_type=InputFileType.OpenAPI,
        output=MODELS_OUTPUT,
        output_model_type=DataModelType.PydanticV2BaseModel,
        base_class='netdoc_sdk.models.core.APIModel',
        use_annotated=True,
        field_constraints=True,
        use_union_operator=True,
        snake_case_field=True,
        formatters=[Formatter.ISORT, Formatter.RUFF_FORMAT],
    )
    # Prepend the "do not edit" header
    original = MODELS_OUTPUT.read_text()
    MODELS_OUTPUT.write_text(GENERATED_HEADER + '\n' + original)
    print(f'[models]    written → {MODELS_OUTPUT.relative_to(REPO_ROOT)}')


# ---------------------------------------------------------------------------
# Step 2 — Endpoint methods via custom OpenAPI walker
# ---------------------------------------------------------------------------


def _extract_path_params(path: str) -> list[str]:
    return re.findall(r'\{(\w+)\}', path)


def _strip_api_prefix(path: str) -> str:
    return re.sub(r'^/api/v1/', '', path)


def _resolve_response_model(responses: dict) -> str:
    """Return the Python type name for the successful response, or 'None'."""
    for status in ('201', '200'):
        content = responses.get(status, {}).get('content', {}).get('application/json', {})
        schema = content.get('schema', {})
        if '$ref' in schema:
            return schema['$ref'].split('/')[-1]
        if schema.get('type') == 'array' and '$ref' in schema.get('items', {}):
            return f'list[{schema["items"]["$ref"].split("/")[-1]}]'
    return 'None'


def _resolve_expected_status(responses: dict, http_method: str) -> int:
    """Return the primary expected HTTP status code for an operation."""
    for status in ('201', '200', '204'):
        if status in responses:
            return int(status)
    return 200


def _extract_header_params(parameters: list[dict]) -> list[str]:
    """Return names of required custom headers declared in the operation."""
    return [p['name'] for p in parameters if p.get('in') == 'header' and p.get('required', False)]


def _build_method(
    operation_id: str,
    http_method: str,
    path: str,
    summary: str,
    responses: dict,
    parameters: list[dict],
) -> str:
    path_params = _extract_path_params(path)
    header_params = _extract_header_params(parameters)
    relative_path = _strip_api_prefix(path)

    has_body = http_method in ('post', 'patch', 'put')
    has_query = http_method == 'get' and any(p.get('in') == 'query' for p in parameters)

    return_type = _resolve_response_model(responses)
    expected_status = _resolve_expected_status(responses, http_method)
    if '204' in responses and '200' not in responses and '201' not in responses:
        return_type = 'None'

    # Build signature params
    sig_params = ['self']
    sig_params += [f'{p}: str' for p in path_params]
    # Header params become explicit keyword arguments
    sig_params += [f'{_header_to_arg(h)}: str' for h in header_params]
    if has_body:
        sig_params.append('data: JsonMapping | None = None, **fields: Any')
    elif has_query:
        sig_params.append('**params: Any')

    lines = [
        f'    def {operation_id}({", ".join(sig_params)}) -> {return_type}:',
        f'        """{summary}"""',
    ]

    # Build headers dict if needed
    if header_params:
        header_dict = '{' + ', '.join(f'{h!r}: {_header_to_arg(h)}' for h in header_params) + '}'
        lines.append(f'        headers = {header_dict}')

    lines += [
        '        return self._request(',
        f'            {http_method.upper()!r},',
        f'            {f'f"{relative_path}"' if path_params else repr(relative_path)},',
    ]
    if header_params:
        lines.append('            headers=headers,')
    if has_query:
        lines.append('            params=params,')
    if has_body:
        lines.append('            json=self._serialize_body(data, **fields),')
    lines.append(f'            expected_status={expected_status},')
    if return_type != 'None':
        lines.append(f'            response_model={return_type},')
    lines.append('        )')

    return '\n'.join(lines)


def _header_to_arg(header_name: str) -> str:
    """Convert 'X-Claim-Token' to 'claim_token'."""
    return re.sub(r'^x[-_]', '', header_name.lower()).replace('-', '_')


def generate_endpoints() -> None:
    """Walk the OpenAPI paths and emit a mixin class with one method per operation."""
    spec = yaml.safe_load(OPENAPI_PATH.read_text())

    # Collect all schema names so we can validate references later if needed
    schema_names: set[str] = set(spec.get('components', {}).get('schemas', {}).keys())

    methods: list[str] = []
    # Track all non-builtin return types so we can build the import block
    referenced_models: set[str] = set()

    for path, path_item in spec['paths'].items():
        for http_method, operation in path_item.items():
            if http_method not in ('get', 'post', 'patch', 'put', 'delete'):
                continue

            operation_id: str = operation.get('operationId', '')
            if not operation_id:
                print(f'  [warn] no operationId for {http_method.upper()} {path}', file=sys.stderr)
                continue

            operation_id = _normalize_operation_id(operation_id)

            summary = operation.get('summary', operation_id)
            parameters = operation.get('parameters', [])
            responses = operation.get('responses', {})
            header_params = _extract_header_params(parameters)

            if header_params:
                print(f'  [headers] {operation_id}: {header_params}')

            method_src = _build_method(
                operation_id=operation_id,
                http_method=http_method,
                path=path,
                summary=summary,
                responses=responses,
                parameters=parameters,
            )
            methods.append(method_src)

            # Track model references for the import block
            model = _resolve_response_model(responses)
            if model not in ('None',) and not model.startswith('list['):
                referenced_models.add(model)
            elif model.startswith('list['):
                inner = model[5:-1]
                referenced_models.add(inner)

    # Only import models that actually exist in the spec schemas
    valid_imports = sorted(referenced_models & schema_names)

    import_block = (
        'from __future__ import annotations\n\n'
        'from typing import Any\n\n'
        'from collections.abc import Mapping\n\n'
        'from pydantic import BaseModel\n\n'
    )
    if valid_imports:
        import_block += (
            'from netdoc_sdk.models._generated_models import (\n'
            + ''.join(f'    {m},\n' for m in valid_imports)
            + ')\n'
        )

    class_lines = [
        'class _GeneratedEndpoints:',
        '    """Auto-generated endpoint methods — do not edit manually.',
        '',
        '    Inherited by _NetDocClientBase. Override individual methods',
        '    in _client_base.py when custom logic is required (e.g. special',
        '    headers, dual expected_status, or non-standard request shapes).',
        '    """',
        '',
    ]

    output = (
        GENERATED_HEADER
        + '\n'
        + import_block
        + '\nJsonMapping = Mapping[str, Any] | BaseModel\n'
        + '\n\n'
        + '\n'.join(class_lines)
        + '\n\n'
        + '\n\n'.join(methods)
        + '\n'
    )

    ENDPOINTS_OUTPUT.write_text(output)
    print(
        f'[endpoints] written → {ENDPOINTS_OUTPUT.relative_to(REPO_ROOT)} ({len(methods)} methods)'
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print(f'Reading spec from {OPENAPI_PATH.relative_to(REPO_ROOT.parent)}')
    generate_models()
    generate_endpoints()
    print('Done.')

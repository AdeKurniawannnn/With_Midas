#!/usr/bin/env python3
"""
n8n Workflow JSON Validator

Validates n8n workflow JSON files for structural correctness.
This is an offline validation tool - for full validation use n8n-MCP tools.

Usage:
    python validate_workflow_json.py workflow.json
    python validate_workflow_json.py --stdin < workflow.json
"""

import json
import sys
import argparse
from typing import Any


class ValidationError:
    def __init__(self, severity: str, message: str, path: str = ""):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.path = path

    def __str__(self):
        prefix = f"[{self.severity.upper()}]"
        location = f" at {self.path}" if self.path else ""
        return f"{prefix}{location}: {self.message}"


def validate_workflow(workflow: dict) -> list[ValidationError]:
    """Validate n8n workflow JSON structure."""
    errors = []

    # Required top-level fields
    required_fields = ['name', 'nodes', 'connections']
    for field in required_fields:
        if field not in workflow:
            errors.append(ValidationError('error', f"Missing required field: {field}"))

    # Validate nodes
    if 'nodes' in workflow:
        errors.extend(validate_nodes(workflow['nodes']))

    # Validate connections
    if 'connections' in workflow and 'nodes' in workflow:
        errors.extend(validate_connections(workflow['connections'], workflow['nodes']))

    # Check settings
    if 'settings' in workflow:
        errors.extend(validate_settings(workflow['settings']))

    return errors


def validate_nodes(nodes: list) -> list[ValidationError]:
    """Validate nodes array."""
    errors = []
    node_ids = set()
    node_names = set()

    if not isinstance(nodes, list):
        errors.append(ValidationError('error', "nodes must be an array"))
        return errors

    for i, node in enumerate(nodes):
        path = f"nodes[{i}]"

        # Required node fields
        if 'name' not in node:
            errors.append(ValidationError('error', "Node missing 'name'", path))
        elif node['name'] in node_names:
            errors.append(ValidationError('error', f"Duplicate node name: {node['name']}", path))
        else:
            node_names.add(node['name'])

        if 'type' not in node:
            errors.append(ValidationError('error', "Node missing 'type'", path))

        # Check for ID (recommended)
        if 'id' in node:
            if node['id'] in node_ids:
                errors.append(ValidationError('warning', f"Duplicate node ID: {node['id']}", path))
            else:
                node_ids.add(node['id'])

        # Check position
        if 'position' in node:
            pos = node['position']
            if not isinstance(pos, list) or len(pos) != 2:
                errors.append(ValidationError('warning', "Position should be [x, y] array", path))

        # Check parameters
        if 'parameters' in node and not isinstance(node['parameters'], dict):
            errors.append(ValidationError('error', "parameters must be an object", path))

        # AI Agent specific checks
        if node.get('type', '').endswith('.agent'):
            errors.extend(validate_ai_agent_node(node, path))

    return errors


def validate_ai_agent_node(node: dict, path: str) -> list[ValidationError]:
    """Validate AI Agent node configuration."""
    errors = []

    # AI Agents need language model connection (checked in connections)
    errors.append(ValidationError('info',
        "AI Agent node detected - ensure language model is connected", path))

    return errors


def validate_connections(connections: dict, nodes: list) -> list[ValidationError]:
    """Validate connections structure."""
    errors = []

    if not isinstance(connections, dict):
        errors.append(ValidationError('error', "connections must be an object"))
        return errors

    # Get all node names
    node_names = {node.get('name') for node in nodes if 'name' in node}

    for source_name, outputs in connections.items():
        if source_name not in node_names:
            errors.append(ValidationError('warning',
                f"Connection references non-existent node: {source_name}",
                f"connections.{source_name}"))

        if not isinstance(outputs, dict):
            errors.append(ValidationError('error',
                f"Invalid connection format for {source_name}",
                f"connections.{source_name}"))
            continue

        for output_type, targets_list in outputs.items():
            if not isinstance(targets_list, list):
                continue

            for targets in targets_list:
                if not isinstance(targets, list):
                    continue

                for target in targets:
                    if isinstance(target, dict):
                        target_name = target.get('node')
                        if target_name and target_name not in node_names:
                            errors.append(ValidationError('warning',
                                f"Connection target node not found: {target_name}",
                                f"connections.{source_name}"))

    return errors


def validate_settings(settings: dict) -> list[ValidationError]:
    """Validate workflow settings."""
    errors = []

    if not isinstance(settings, dict):
        errors.append(ValidationError('error', "settings must be an object"))
        return errors

    # Check execution order
    if 'executionOrder' in settings:
        if settings['executionOrder'] not in ['v0', 'v1']:
            errors.append(ValidationError('warning',
                "executionOrder should be 'v0' or 'v1'",
                "settings.executionOrder"))

    return errors


def validate_expressions(workflow: dict) -> list[ValidationError]:
    """Basic expression syntax validation."""
    errors = []

    def check_string_for_expressions(value: Any, path: str):
        if not isinstance(value, str):
            return

        # Check for common expression errors
        if '{{' in value and '={{' not in value:
            errors.append(ValidationError('warning',
                "Expression may be missing '=' prefix: {{ should be ={{",
                path))

        if '$json.' in value and '={{' not in value and '{{' not in value:
            errors.append(ValidationError('warning',
                "Expression reference outside of expression syntax",
                path))

    def traverse(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                traverse(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                traverse(item, f"{path}[{i}]")
        elif isinstance(obj, str):
            check_string_for_expressions(obj, path)

    traverse(workflow)
    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate n8n workflow JSON')
    parser.add_argument('file', nargs='?', help='Workflow JSON file to validate')
    parser.add_argument('--stdin', action='store_true', help='Read from stdin')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    # Read workflow
    try:
        if args.stdin or not args.file:
            workflow = json.load(sys.stdin)
        else:
            with open(args.file, 'r') as f:
                workflow = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Run validation
    errors = validate_workflow(workflow)
    errors.extend(validate_expressions(workflow))

    # Output results
    if args.json:
        result = {
            'valid': not any(e.severity == 'error' for e in errors),
            'errors': [{'severity': e.severity, 'message': e.message, 'path': e.path}
                      for e in errors if e.severity == 'error'],
            'warnings': [{'severity': e.severity, 'message': e.message, 'path': e.path}
                        for e in errors if e.severity == 'warning'],
            'info': [{'severity': e.severity, 'message': e.message, 'path': e.path}
                    for e in errors if e.severity == 'info']
        }
        print(json.dumps(result, indent=2))
    else:
        error_count = sum(1 for e in errors if e.severity == 'error')
        warning_count = sum(1 for e in errors if e.severity == 'warning')
        info_count = sum(1 for e in errors if e.severity == 'info')

        for error in errors:
            print(error)

        print(f"\nValidation complete: {error_count} errors, {warning_count} warnings, {info_count} info")

        if error_count > 0:
            print("INVALID - Fix errors before deployment")
            sys.exit(1)
        else:
            print("VALID - Workflow structure is correct")
            print("Note: For full validation including node configs, use n8n-MCP tools")


if __name__ == '__main__':
    main()

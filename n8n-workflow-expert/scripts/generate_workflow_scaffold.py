#!/usr/bin/env python3
"""
n8n Workflow Scaffold Generator

Generates n8n workflow JSON scaffolds from templates.

Usage:
    python generate_workflow_scaffold.py --name "My Workflow" --type basic
    python generate_workflow_scaffold.py --name "API Handler" --type webhook
    python generate_workflow_scaffold.py --name "Chat Bot" --type ai-agent
"""

import json
import argparse
import uuid
import os
from pathlib import Path


def generate_uuid():
    """Generate a unique ID for n8n nodes."""
    return str(uuid.uuid4())[:8]


def get_template_path(template_type: str) -> Path:
    """Get the path to a template file."""
    script_dir = Path(__file__).parent
    templates_dir = script_dir.parent / 'assets' / 'templates'

    template_map = {
        'basic': 'workflow-basic.json',
        'webhook': 'workflow-webhook.json',
        'ai-agent': 'workflow-ai-agent.json',
    }

    if template_type not in template_map:
        raise ValueError(f"Unknown template type: {template_type}. Available: {list(template_map.keys())}")

    return templates_dir / template_map[template_type]


def load_template(template_type: str) -> dict:
    """Load a template file."""
    template_path = get_template_path(template_type)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, 'r') as f:
        return json.load(f)


def update_ids(workflow: dict) -> dict:
    """Update all IDs in the workflow to be unique."""
    # Generate new IDs for all nodes
    id_mapping = {}

    for node in workflow.get('nodes', []):
        old_id = node.get('id', '')
        new_id = generate_uuid()
        id_mapping[old_id] = new_id
        node['id'] = new_id

        # Update webhook IDs
        if 'webhookId' in node:
            node['webhookId'] = generate_uuid()

    return workflow


def customize_workflow(workflow: dict, name: str, **kwargs) -> dict:
    """Customize the workflow with provided options."""
    # Set workflow name
    workflow['name'] = name

    # Update meta
    if 'meta' not in workflow:
        workflow['meta'] = {}
    workflow['meta']['instanceId'] = generate_uuid()

    return workflow


def generate_scaffold(
    name: str,
    template_type: str = 'basic',
    **kwargs
) -> dict:
    """Generate a workflow scaffold from a template."""
    # Load template
    workflow = load_template(template_type)

    # Update IDs to be unique
    workflow = update_ids(workflow)

    # Customize
    workflow = customize_workflow(workflow, name, **kwargs)

    return workflow


def main():
    parser = argparse.ArgumentParser(description='Generate n8n workflow scaffold')
    parser.add_argument('--name', required=True, help='Workflow name')
    parser.add_argument('--type', default='basic',
                       choices=['basic', 'webhook', 'ai-agent'],
                       help='Template type (default: basic)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', default=True,
                       help='Pretty print JSON (default: true)')
    args = parser.parse_args()

    try:
        workflow = generate_scaffold(
            name=args.name,
            template_type=args.type
        )

        # Output
        indent = 2 if args.pretty else None
        json_output = json.dumps(workflow, indent=indent)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"Workflow saved to: {args.output}")
        else:
            print(json_output)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=os.sys.stderr)
        os.sys.exit(1)


if __name__ == '__main__':
    main()

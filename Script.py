import yaml

def load_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
    except FileNotFoundError:
        print(f"Fichier introuvable : {file_path}")
        return []


def extract_data(new_file):
    doc_files = [r"E:\The-Eye-of-Horus\yaml\core.yaml",r"E:\The-Eye-of-Horus\yaml\iam.yaml",r"E:\The-Eye-of-Horus\yaml\schemas.yaml"]
    schema_file = r"E:\The-Eye-of-Horus\yaml\schemas.yaml"
    final = {
        "openapi": "3.1.0",
        "info": {
            "title": "Zeney API Documentation",
            "description": "Zeney API documentation.",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://zn-svc-gateway.onrender.com"}
        ],
        "tags": [
            {"name": "FLOW", "description": "API following the FLOW design. Optimized for mobile use."},
            {"name": "REST", "description": "API following the REST design."},
            {"name": "RPC", "description": "Internal inter-services API"},
            {"name": "IAM", "description": "IAM microservice"}
        ]
    }

    for file_path in doc_files:
        lines = load_yaml(file_path)

        if 'paths' not in final:
            final['paths'] = {}
        if 'paths' in lines:
            final['paths'].update(lines['paths'])

    schema_data = load_yaml(schema_file)
    if 'components' not in final:
        final['components'] = {}
    if 'components' in schema_data:
        final['components'].update(schema_data['components'])

    with open(new_file, 'w', encoding='utf-8') as f:
        yaml.dump(final, f, allow_unicode=True, sort_keys=False)

    content = ''
    with open(new_file, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace("./schemas.yaml", "")

    with open(new_file, 'w', encoding='utf-8') as f:
        f.write(content)


new_file = "doc1.yaml"
files = [r"E:\The-Eye-of-Horus\yaml\core.yaml",r"E:\The-Eye-of-Horus\yaml\iam.yaml",r"E:\The-Eye-of-Horus\yaml\schemas.yaml"]
key_words = ["components","paths"]
extract_data(new_file)


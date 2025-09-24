import os
import sys

# Définition de l'arborescence à créer
tree = {
    "SIDC": {
        "DEV_SICK": {
            "DDL": {
                "version_number": {
                    "INSTALL_LOAD": {
                        "list_ddl.cfg": None,
                        "make_install_ddl.sh": None
                    },
                    "MPD": {
                        "ddl_per": None,
                        "ddl_soc": None,
                        "ddl_stg": None
                    }
                }
            },
            "VRPT": {}
        },
        "LIV_SIDC": {}
    }
}

def create_tree(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if content is None:
            # C'est un fichier
            open(path, 'w').close()
        else:
            # C'est un dossier
            os.makedirs(path, exist_ok=True)
            create_tree(path, content)

def create_file_at_path(path):
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    open(path, 'w').close()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--full-tree":
        create_tree('.', tree)
        print("Arborescence complète créée.")
    elif len(sys.argv) == 2:
        create_file_at_path(sys.argv[1])
        print(f"Fichier '{sys.argv[1]}' créé.")
    else:
        print("Usage:")
        print("  python arborescence_creator.py --full-tree   # Crée toute l'arborescence")
        print("  python arborescence_creator.py chemin/vers/fichier.ext   # Crée un fichier à l'endroit voulu")

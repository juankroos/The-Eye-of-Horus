import cv2
import numpy as np
from matplotlib import pyplot as plt

# funtion to apply a filter to an image
def load_image_as_matrix(path):
    image = plt.imread(path)
    # convert to grayscale if it's a color image
    if image.ndim == 3:
        image = np.mean(image, axis=2)
    return image

b = load_image_as_matrix('cheval.jpeg')
plt.imshow(b)
plt.imsave('aaa_cheval.png',b)
b1 = b[50:100,75:100]
plt.imsave('b1_cheval.png',b1)
plt.imshow(b1)
plt.savefig("pixeled_one_cheval")



import json
import yaml
import logging
import requests
import sqlparse
import teradatasql
from retrying import retry
import re
import fastmcp

# Configuration du logging
logging.basicConfig(level=logging.INFO, filename="mcp_server.log")
logger = logging.getLogger(_name_)

# Charger la configuration YAML
def load_mcp_config(path="mcp_config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Fichier mcp_config.yaml introuvable")
        raise SystemExit("Erreur : Fichier mcp_config.yaml introuvable")

try:
    config = load_mcp_config()
    api_url = config["intents"]["generate_sql"]["api_url"]
    api_key = config["intents"]["generate_sql"]["api_key"]
    model = config["intents"]["generate_sql"]["model"]
    max_tokens = config["intents"]["generate_sql"]["max_tokens"]
    temperature = config["intents"]["generate_sql"]["temperature"]
    prompt_template = config["intents"]["generate_sql"]["prompt_template"]
    retry_on_failure = config["intents"]["generate_sql"]["retry_on_failure"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    conn_config = config["intents"]["execute_sql"]["connection"]
except KeyError as e:
    logger.error(f"Erreur dans la configuration YAML : clé manquante {str(e)}")
    raise SystemExit(f"Erreur : Clé manquante dans mcp_config.yaml : {str(e)}")

# Initialiser le serveur MCP
app = fastmcp.FastMCP()

# Ressource : Fournir les configurations
@app.resource
def get_config():
    return {
        "api_config": {
            "api_url": api_url,
            "api_key": api_key,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "prompt_template": prompt_template,
            "retry_on_failure": retry_on_failure
        },
        "connection_config": conn_config
    }

# Outil : Nettoyer la réponse SQL
@app.tool
def clean_sql_response(query: str) -> str:
    query = re.sub(r'sql\s*|\s*|--.?\n|/\.?\/|\r\n|\n|\r', ' ', query, flags=re.MULTILINE | re.DOTALL)
    query = re.sub(r'\s+', ' ', query).strip()
    if query and not query.endswith(';'):
        query += ';'
    return query

# Outil : Validation SQL
@app.tool
def validate_sql(query: str) -> dict:
    try:
        query = clean_sql_response(query)
        logger.info(f"Requeete aprws nettoyage : {query}")
        parsed = sqlparse.parse(query)
        if not parsed:
            logger.warning(f"Échec de l'analyse SQL : aucune requwte valide trouvée dans '{query}'")
            return {"is_valid": False, "error": f"echec de l'analyse SQL : aucune requete valide trouvee dans '{query}'"}
        statement_type = parsed[0].get_type()
        valid_types = ("SELECT", "CREATE", "WITH")
        is_valid = statement_type in valid_types
        logger.info(f"Type de requete detecte : {statement_type}, Valide : {is_valid}")
        if not is_valid:
            logger.warning(f"Type de requete non supporte : {statement_type}")
            return {"is_valid": False, "error": f"Type de requete non supporte : {statement_type}"}
        return {"is_valid": True}
    except Exception as e:
        logger.error(f"Erreur de validation SQL : {str(e)}")
        return {"is_valid": False, "error": f"Erreur de validation SQL : {str(e)}"}

# Outil : Génération SQL via l’API Grok
@app.tool
@retry(stop_max_attempt_number=retry_on_failure, wait_fixed=1000)
def generate_sql(prompt: str, dialect: str) -> dict:
    formatted_prompt = prompt_template.format(user_prompt=prompt, sql_dialect=dialect)
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"Tu es un expert en {dialect} SQL. Retourne uniquement la requête SQL, sans explication ni commentaire, et sans marqueurs de bloc de code."},
            {"role": "user", "content": formatted_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        raw_query = result["choices"][0]["message"]["content"]
        logger.info(f"Réponse brute de l'API : {raw_query}")
        return {"sql": clean_sql_response(raw_query)}
    except requests.HTTPError as e:
        if response.status_code == 401:
            logger.error("Erreur d'authentification API Grok : Clé API invalide ou non autorisée")
            return {"error": "Erreur 401 : Clé API Grok invalide"}
        logger.error(f"Erreur HTTP API Grok : {str(e)}")
        return {"error": f"Erreur HTTP API Grok : {str(e)}"}
    except requests.RequestException as e:
        logger.error(f"Erreur réseau API Grok : {str(e)}")
        return {"error": f"Erreur réseau API Grok : {str(e)}"}

# Outil : Exécution SQL sur Teradata
@app.tool
def execute_sql(query: str) -> dict:
    try:
        with teradatasql.connect(
            host=conn_config["host"],
            user=conn_config["user"],
            password=conn_config["password"],
            database=conn_config.get("database")
        ) as conn:
            with conn.cursor() as cursor:
                # Vérifier si la table existe
                table_name = None
                parsed = sqlparse.parse(query)
                if parsed and parsed[0].get_type() == "SELECT":
                    for token in parsed[0].tokens:
                        if isinstance(token, sqlparse.sql.Identifier):
                            table_name = token.get_name()
                            break
                if table_name:
                    cursor.execute("SELECT COUNT(*) FROM DBC.TablesV WHERE DatabaseName = ? AND TableName = ?", 
                                  [conn_config.get("database", ""), table_name])
                    table_exists = cursor.fetchone()[0] > 0
                    if not table_exists:
                        logger.warning(f"Tableau {table_name} n'existe pas dans la base de données {conn_config.get('database', 'inconnue')}")
                        return {"error": f"Erreur : La table '{table_name}' n'existe pas dans la base de données {conn_config.get('database', 'inconnue')}"}
                
                # Exécuter la requête
                cursor.execute(query)
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                logger.info(f"Requête exécutée avec succès : {query}")
                return {"sql": query, "results": [dict(zip(columns, row)) for row in rows], "message": "Requête exécutée avec succès"}
    except teradatasql.Error as e:
        logger.error(f"Erreur Teradata : {str(e)}")
        if "Object" in str(e) and "does not exist" in str(e):
            return {"error": f"Erreur : La table ou l'objet dans la requête n'existe pas dans la base de données {conn_config.get('database', 'inconnue')}"}
        return {"error": f"Échec de l'exécution : {str(e)}"}

# Gestion des messages WebSocket
@app.on_message
def handle_message(ws, message):
    try:
        data = json.loads(message)
        if "tool" in data:
            tool = data.get("tool")
            tool_data = data.get("data", {})
            if tool in app.tools:
                result = app.tools[tool](**tool_data)
                ws.send(json.dumps(result))
            else:
                ws.send(json.dumps({"error": f"Outil {tool} non trouvé"}))
        elif "resource" in data:
            resource = data.get("resource")
            if resource in app.resources:
                result = app.resources[resource]()
                ws.send(json.dumps(result))
            else:
                ws.send(json.dumps({"error": f"Ressource {resource} non trouvée"}))
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message : {str(e)}")
        ws.send(json.dumps({"error": f"Erreur serveur : {str(e)}"}))

# Démarrer le serveur
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=8765)




    import json
import yaml
import logging
import websocket

# Configuration du logging
logging.basicConfig(level=logging.INFO, filename="agent.log")
logger = logging.getLogger(_name_)

# Charger la configuration YAML
def load_agent_config(path="agent_config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Fichier agent_config.yaml introuvable")
        raise SystemExit("Erreur : Fichier agent_config.yaml introuvable")

try:
    config = load_agent_config()
    ws_url = config["mcp"]["ws_url"]
    sql_dialect = config["mcp"]["sql_dialect"]
except KeyError as e:
    logger.error(f"Erreur dans la configuration YAML : clé manquante {str(e)}")
    raise SystemExit(f"Erreur : Clé manquante dans agent_config.yaml : {str(e)}")

# Connexion au serveur MCP
ws = None
def connect_to_mcp():
    global ws
    try:
        ws = websocket.WebSocket()
        ws.connect(ws_url)
        logger.info(f"Connecté au serveur MCP à {ws_url}")
    except Exception as e:
        logger.error(f"Erreur de connexion au MCP : {str(e)}")
        raise SystemExit(f"Erreur : Impossible de se connecter au serveur MCP : {str(e)}")

# Envoyer une requête au MCP et recevoir la réponse
def send_mcp_request(tool: str, data: dict) -> dict:
    try:
        request = {"tool": tool, "data": data}
        ws.send(json.dumps(request))
        response = json.loads(ws.recv())
        logger.info(f"Réponse du MCP pour l'outil {tool} : {response}")
        return response
    except Exception as e:
        logger.error(f"Erreur lors de la communication avec le MCP : {str(e)}")
        return {"error": f"Erreur MCP : {str(e)}"}

# Fonction principale avec boucle interactive
def main():
    connect_to_mcp()
    while True:
        print("Entrez votre prompt pour générer une requête SQL (ex. 'sélectionne tous les champs de la table utilisateurs') ou 'quit' pour sortir :")
        try:
            user_prompt = input("> ")
            if user_prompt.lower() == "quit":
                ws.close()
                break

            # Générer la requête SQL via le MCP
            generate_response = send_mcp_request("generate_sql", {"prompt": user_prompt, "sql_dialect": sql_dialect})
            if "error" in generate_response:
                print(f"Erreur de génération : {generate_response['error']}")
                logger.error(f"Erreur de génération : {generate_response['error']}")
                continue
            generated_sql = generate_response["sql"]
            logger.info(f"Requête générée : {generated_sql}")
            print(f"Requête générée ({sql_dialect}) :")
            print(generated_sql)

            # Valider la requête via le MCP
            validate_response = send_mcp_request("validate_sql", {"query": generated_sql})
            if "error" in validate_response:
                print(f"Erreur de validation : {validate_response['error']}")
                logger.error(f"Erreur de validation : {validate_response['error']}")
                continue
            if validate_response["is_valid"]:
                print("La requête est valide.")
                # Exécuter la requête via le MCP
                execute_response = send_mcp_request("execute_sql", {"query": generated_sql})
                if "error" in execute_response:
                    print(f"Erreur d'exécution : {execute_response['error']}")
                    logger.error(f"Erreur d'exécution : {execute_response['error']}")
                else:
                    print("Résultats de la requête :")
                    if execute_response["results"]:
                        for row in execute_response["results"]:
                            print(row)
                    else:
                        print("Aucun résultat retourné.")
            else:
                print("La requête est invalide.")
                logger.warning(f"Requête générée invalide : {generated_sql}")
        except Exception as e:
            logger.error(f"Erreur générale : {str(e)}")
            print(f"Erreur : {str(e)}")

if _name_ == "_main_":
    main()
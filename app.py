#!/usr/bin/env python3
import mindsdb_sdk
import logging
import time

# === CONFIG ===
LOCAL_URL = "http://127.0.0.1:47334"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === COMPATIBLE SQL WRAPPER ===
def run_sql(server, query):
    if hasattr(server, "sql"):
        return server.sql(query)
    elif hasattr(server, "query"):
        return server.query(query)
    else:
        raise AttributeError("❌ SDK does not have .sql or .query method!")

# === WAIT FOR OBJECT FUNCTION (KB / AGENT / TABLE) ===
def wait_for_object(server, name, timeout=45, object_type='TABLE'):
    """
    Wait for a MindsDB object (KB/Agent/Table) to become available.
    """
    if object_type == 'KNOWLEDGE_BASE':
        command = "SHOW KNOWLEDGE BASES"
    elif object_type == 'AGENT':
        command = "SHOW AGENTS"
    else:
        command = "SHOW TABLES"

    logging.info(f"⏳ Waiting for {object_type.lower()} '{name}' to appear...")
    for i in range(timeout):
        try:
            result = run_sql(server, command)
            names = [row['name'] for row in result.fetch()]
            if name in names:
                logging.info(f"✅ {object_type} '{name}' is now available (after {i+1}s).")
                return True
        except Exception as e:
            logging.debug(f"⏲️ {object_type} check attempt {i+1}: {e}")
        time.sleep(1)

    logging.error(f"❌ Timeout: {object_type} '{name}' did not appear in `{command}`.")
    return False

# === MAIN SCRIPT ===
def main():
    logging.info("🖥️ Connecting to local MindsDB on Docker...")
    try:
        server = mindsdb_sdk.connect(LOCAL_URL)
        logging.info("✅ Connected to MindsDB at http://127.0.0.1:47334")
    except Exception as e:
        logging.error(f"❌ Could not connect: {e}")
        return

    # === Step 1: Create KB ===
    create_kb_query = """
    CREATE KNOWLEDGE_BASE consumer_kb
    USING
        embedding_model = {
            "provider": "sentence-transformers",
            "model_name": "paraphrase-MiniLM-L6-v2"
        },
        content_columns = ['subject', 'body', 'answer'],
        metadata_columns = ['type', 'queue', 'priority', 'language', 'version'],
        id_column = 'row_id';
    """
    logging.info("📦 Creating Knowledge Base...")
    try:
        run_sql(server, create_kb_query)
        logging.info("✅ KB creation sent.")
    except Exception as e:
        logging.error(f"❌ KB creation failed: {e}")

    # === Step 2: Ingest Data ===
    ingest_query = """
    INSERT INTO consumer_kb
    SELECT row_id, subject, body, answer,
           type, queue, priority, language, version
    FROM tickets;
    """
    logging.info("📥 Ingesting data into KB...")
    try:
        run_sql(server, ingest_query)
        logging.info("✅ Ingestion command sent.")
    except Exception as e:
        logging.error(f"❌ Ingestion failed: {e}")

    # === Step 3: Wait for KB to become available ===
    if not wait_for_object(server, 'consumer_kb', timeout=60, object_type='KNOWLEDGE_BASE'):
        logging.error("❌ Aborting: KB not ready.")
        return

    # === Step 4: Semantic Search ===
    search_query = """
    SELECT chunk_content, relevance
    FROM consumer_kb
    WHERE content = 'reset password'
      AND relevance >= 0.25;
    """
    logging.info("🔍 Semantic search: 'reset password'...")
    try:
        result = run_sql(server, search_query)
        rows = result.fetch()
        if rows:
            for row in rows:
                logging.info(f"📄 Result: {row}")
        else:
            logging.info("ℹ️ No results found.")
    except Exception as e:
        logging.error(f"❌ Semantic search failed: {e}")

    # === Step 5: Create Agent ===
    create_agent_query = """
    CREATE AGENT support_agent
    USING
        knowledge_bases = ['consumer_kb'],
        prompt_template = '
            You are a multilingual customer-support assistant.
            Use the knowledge base to answer exactly and cite ticket IDs.'
    ;
    """
    logging.info("🤖 Creating AI Agent...")
    try:
        run_sql(server, create_agent_query)
        logging.info("✅ Agent creation sent.")
    except Exception as e:
        logging.error(f"❌ Agent creation failed: {e}")

    # === Step 6: Wait for Agent ===
    if not wait_for_object(server, 'support_agent', timeout=45, object_type='AGENT'):
        logging.error("❌ Aborting: Agent not ready.")
        return

    # === Step 7: Ask Agent ===
    question = "How can I reset my password?"
    ask_query = f"""
    SELECT answer FROM support_agent WHERE question = '{question}';
    """
    logging.info(f"💬 Asking: '{question}'")
    try:
        result = run_sql(server, ask_query)
        rows = result.fetch()
        if rows:
            for row in rows:
                logging.info(f"🤖 Answer: {row.get('answer')}")
        else:
            logging.info("ℹ️ No answer returned.")
    except Exception as e:
        logging.error(f"❌ Agent query failed: {e}")

    # === Step 8: Multilingual Search ===
    multilingual_query = """
    SELECT chunk_content, relevance
    FROM consumer_kb
    WHERE content = 'restablecer la contraseña'
      AND language = 'es'
      AND relevance >= 0.25;
    """
    logging.info("🌍 Spanish search: 'restablecer la contraseña'...")
    try:
        result = run_sql(server, multilingual_query)
        rows = result.fetch()
        if rows:
            for row in rows:
                logging.info(f"🌐 Result: {row}")
        else:
            logging.info("ℹ️ No Spanish results found.")
    except Exception as e:
        logging.error(f"❌ Multilingual search failed: {e}")

if __name__ == "__main__":
    main()
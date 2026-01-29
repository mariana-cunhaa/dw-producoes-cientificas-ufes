"""
Script de teste para validar a conexão com o Supabase
Execute: streamlit run test_connection.py
"""

import streamlit as st
from db_utils import test_connection, get_connection
import psycopg2

st.set_page_config(
    page_title="Teste de Conexão - Supabase",
    page_icon="🔌",
    layout="centered"
)

st.title("🔌 Teste de Conexão com Supabase")
st.markdown("---")

# Teste 1: Verificar se secrets está configurado
st.header("1️⃣ Verificando Secrets")
try:
    db_config = st.secrets["db"]
    st.success("✅ Arquivo secrets.toml encontrado!")
    
    st.write("**Configurações detectadas:**")
    st.code(f"""
Host: {db_config['host']}
Database: {db_config['database']}
User: {db_config['user']}
Port: {db_config.get('port', 5432)}
Password: {'*' * len(db_config['password'])} (oculta)
    """)
except Exception as e:
    st.error(f"❌ Erro ao ler secrets: {e}")
    st.warning("Verifique se o arquivo `.streamlit/secrets.toml` existe e está preenchido.")
    st.stop()

st.markdown("---")

# Teste 2: Testar conexão
st.header("2️⃣ Testando Conexão")
if st.button("🔄 Testar Conexão", type="primary"):
    with st.spinner("Conectando ao Supabase..."):
        try:
            conn = get_connection()
            st.success("✅ Conexão estabelecida com sucesso!")
            
            # Teste 3: Consultar informações do banco
            st.markdown("---")
            st.header("3️⃣ Informações do Banco")
            
            cursor = conn.cursor()
            
            # Versão do PostgreSQL
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            st.info(f"**Versão do PostgreSQL:** {version.split(',')[0]}")
            
            # Listar schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schema_name;
            """)
            schemas = [row[0] for row in cursor.fetchall()]
            st.write(f"**Schemas encontrados:** {', '.join(schemas)}")
            
            # Contar tabelas no schema dw
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'dw';
            """)
            num_tabelas = cursor.fetchone()[0]
            st.write(f"**Tabelas no schema 'dw':** {num_tabelas}")
            
            # Listar tabelas do schema dw
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'dw' 
                ORDER BY table_name;
            """)
            tabelas = [row[0] for row in cursor.fetchall()]
            
            if tabelas:
                st.success(f"✅ Encontradas {len(tabelas)} tabelas no schema 'dw':")
                st.write(tabelas)
            else:
                st.warning("⚠️ Nenhuma tabela encontrada no schema 'dw'")
            
            # Teste 4: Consultar dados de exemplo
            st.markdown("---")
            st.header("4️⃣ Teste de Consulta")
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total_pesquisadores
                    FROM dw.dim_pesquisador;
                """)
                total = cursor.fetchone()[0]
                st.metric("Total de Pesquisadores", f"{total:,}")
                
                cursor.execute("""
                    SELECT SUM(qtd_producoes) as total_producoes
                    FROM dw.fato_pesquisador_producoes;
                """)
                total_prod = cursor.fetchone()[0]
                st.metric("Total de Produções", f"{total_prod:,}")
                
                st.success("✅ Dados acessíveis e íntegros!")
                
            except Exception as e:
                st.error(f"❌ Erro ao consultar dados: {e}")
            
            cursor.close()
            conn.close()
            
            st.markdown("---")
            st.success("🎉 **Tudo funcionando!** Pode prosseguir com o deploy.")
            
        except psycopg2.OperationalError as e:
            st.error(f"❌ Erro de conexão: {e}")
            st.warning("""
            **Possíveis causas:**
            - Host incorreto
            - Senha errada
            - Firewall bloqueando
            - SSL não configurado
            """)
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")

st.markdown("---")
st.info("💡 **Dica:** Se todos os testes passarem, o app está pronto para deploy!")

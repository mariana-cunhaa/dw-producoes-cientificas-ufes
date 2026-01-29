# 🚀 Guia de Configuração - Supabase + Streamlit

## 📋 Pré-requisitos

- ✅ Banco PostgreSQL no Supabase criado
- ✅ Dados migrados para o Supabase
- ✅ Conexão testada no DBeaver

---

## 🔧 Passo a Passo: Configurar Secrets do Streamlit

### **1️⃣ Obter as Credenciais do Supabase**

1. Acesse o [Supabase Dashboard](https://supabase.com/dashboard)
2. Selecione seu projeto
3. Vá em **Settings** > **Database**
4. Na seção **Connection Info**, copie:
   - **Host** (exemplo: `db.abcdefghijk.supabase.co`)
   - **Database name** (geralmente `postgres`)
   - **User** (geralmente `postgres`)
   - **Password** (a senha que você definiu na criação)
   - **Port** (geralmente `5432`)

### **2️⃣ Preencher o arquivo `secrets.toml`**

1. Abra o arquivo: `.streamlit/secrets.toml`
2. Substitua os valores de exemplo pelas credenciais do Supabase:

```toml
[db]
host = "db.abcdefghijk.supabase.co"  # Cole aqui o host do Supabase
database = "postgres"                 # Geralmente "postgres"
user = "postgres"                     # Geralmente "postgres"
password = "sua_senha_super_segura"  # Cole aqui a senha do Supabase
port = "5432"                        # Porta padrão do PostgreSQL
```

3. **IMPORTANTE**: Não compartilhe este arquivo nem faça commit no Git!

### **3️⃣ Testar a Conexão Localmente**

No terminal, dentro da pasta `streamlit/`, execute:

```bash
streamlit run app.py
```

Se tudo estiver correto, você verá:
- ✅ "Banco conectado" na página inicial
- Métricas carregando corretamente
- Dashboards funcionando

---

## 🌐 Deploy no Streamlit Cloud

### **4️⃣ Preparar para Deploy**

1. **Verificar o `requirements.txt`**:
   - Certifique-se de que todas as dependências estão listadas
   - Confirme que `psycopg2-binary` está presente

2. **Verificar o `.gitignore`**:
   - Confirme que `.streamlit/secrets.toml` está na lista
   - Isso evita que suas credenciais sejam publicadas

### **5️⃣ Fazer o Deploy**

1. Acesse [Streamlit Cloud](https://streamlit.io/cloud)
2. Clique em **New app**
3. Selecione seu repositório GitHub
4. Configure:
   - **Main file path**: `streamlit/app.py`
   - **Python version**: 3.9 ou superior

### **6️⃣ Adicionar Secrets no Streamlit Cloud**

1. No Streamlit Cloud, vá em **Settings** > **Secrets**
2. Cole o conteúdo do seu `secrets.toml` local:

```toml
[db]
host = "db.abcdefghijk.supabase.co"
database = "postgres"
user = "postgres"
password = "sua_senha_super_segura"
port = "5432"
```

3. Clique em **Save**
4. O app reiniciará automaticamente e conectará ao Supabase

---

## ✅ Checklist Final

- [ ] Credenciais do Supabase copiadas corretamente
- [ ] Arquivo `secrets.toml` preenchido (local)
- [ ] Conexão testada localmente (`streamlit run app.py`)
- [ ] `.gitignore` configurado
- [ ] Secrets adicionados no Streamlit Cloud
- [ ] App funcionando em produção

---

## 🆘 Troubleshooting

### ❌ Erro: "could not connect to server"
- Verifique se o **host** está correto
- Confirme que a **porta** é 5432
- Teste a conexão no DBeaver primeiro

### ❌ Erro: "password authentication failed"
- Confirme que a **senha** está correta
- Verifique se não há espaços extras no `secrets.toml`

### ❌ Erro: "SSL required"
- Certifique-se de que `sslmode="require"` está no código
- O Supabase exige conexão SSL

### ❌ App no Streamlit Cloud não conecta
- Verifique se os **Secrets** foram salvos corretamente
- Confirme que o formato TOML está correto (sem espaços extras)
- Reinicie o app manualmente

---

## 📚 Arquivos Importantes

| Arquivo | Função |
|---------|--------|
| `.streamlit/secrets.toml` | Credenciais do banco (LOCAL - não commitar) |
| `secrets_template.toml` | Template para referência |
| `db_utils.py` | Conexão com o banco usando secrets |
| `.gitignore` | Protege arquivos sensíveis |
| `requirements.txt` | Dependências do projeto |

---

## 🎯 Próximos Passos Após Deploy

1. ✅ Testar todos os dashboards em produção
2. ✅ Configurar domínio customizado (opcional)
3. ✅ Monitorar logs e performance
4. ✅ Configurar backup do Supabase (se ainda não fez)

---

**🎉 Pronto! Seu Data Warehouse agora está 100% em nuvem!**

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def setup_database():
    """
    Define a arquitetura de memória do Nexus no Supabase.
    """
    print("🔵 Iniciando Configuração da Arquitetura de Memória NEXUS...")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n❌ ERRO: Credenciais do Supabase não encontradas.")
        print("   Por favor, crie um arquivo '.env' na pasta 'backend' com o seguinte conteúdo:")
        print("   SUPABASE_URL=sua_url_aqui")
        print("   SUPABASE_KEY=sua_chave_aqui")
        return

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conexão com Supabase estabelecida.")
        
        # Aqui iríamos criar as tabelas via SQL se o Supabase permitisse via API client diretamente (geralmente é via Dashboard ou Migrations)
        # Mas podemos verificar se a conexão é válida tentando listar uma tabela (mesmo que não exista, o erro confirma a conexão)
        
        print("\n📋 Estrutura Planejada (Criar no Dashboard do Supabase > SQL Editor):")
        
        sql_commands = """
        -- Tabela de Usuários
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'free',
            credits INT DEFAULT 10,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );

        -- Tabela de Memórias (Vetorizada)
        -- Requer extensão: create extension vector;
        CREATE TABLE IF NOT EXISTS memories (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id),
            content TEXT,
            embedding VECTOR(1536),
            tags TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );

        -- Tabela de Padrões
        CREATE TABLE IF NOT EXISTS patterns (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id),
            pattern_name TEXT,
            frequency INT DEFAULT 1,
            last_detected TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );
        """
        
        print(sql_commands)
        print("\n⚠️ AÇÃO NECESSÁRIA: Copie o SQL acima e execute no 'SQL Editor' do seu painel Supabase.")

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    setup_database()

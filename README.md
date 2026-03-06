# Auth-SNK

## 🎯 Objetivo

API para centralizar e gerenciar a autenticação no gateway da Sankhya, servindo como um ponto único de acesso para todas as soluções da empresa que necessitam de um token de autenticação.

## 🚀 Como Funciona

O `auth-snk` funciona como um serviço intermediário que armazena as credenciais das diversas aplicações (chamadas de `Soluções`) e gerencia os tokens de acesso da Sankhya.

1.  **Cadastro da Solução**: Uma nova aplicação que precisa de acesso à Sankhya é cadastrada no banco de dados do `auth-snk`, incluindo suas credenciais (`clientId`, `clientSecret`, `xToken`) e ambiente (`prd` ou `snd`).
2.  **Solicitação de Token**: A aplicação cliente faz uma requisição para a API `auth-snk`, informando seu `solucaoId` e `xToken`.
3.  **Validação e Cache**: A API verifica se já existe um token válido e não expirado para a solução solicitante em seu banco de dados.
4.  **Geração de Novo Token**:
    *   Se não houver um token válido, a API utiliza as credenciais armazenadas para realizar um novo login no endpoint da Sankhya.
    *   Após obter um novo token, ele é criptografado e salvo no banco de dados, juntamente com sua data de geração e expiração.
5.  **Retorno**: A API retorna o token de acesso para a aplicação cliente.

Este processo garante que as credenciais da Sankhya fiquem centralizadas e seguras, além de otimizar o uso de tokens, evitando logins desnecessários.

## 🛠️ Tecnologias Utilizadas

*   **Backend**: Python
*   **Banco de Dados**: PostgreSQL
*   **ORM**: SQLAlchemy (com suporte assíncrono)
*   **Criptografia**: `cryptography.fernet` para proteger dados sensíveis como tokens e segredos de cliente.
*   **Variáveis de Ambiente**: `python-dotenv` para gerenciamento de configurações.

## ⚙️ Configuração e Instalação

1.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/tieisen/auth-snk.git
    cd auth-snk
    ```

2.  **Configurar Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto conforme o arquivo `example.env`

4.  **Instalar e inicializar a aplicação:**
    Acesse a raíz do diretório do projeto e execute o comando:
    ```bash
    python .
    ```

## 📂 Estrutura do Projeto

```
auth-snk/
├── src/
│   └── authSnk/
│       ├── controllers/
│       │   ├── autenticacao.py  # Controlador de autenticação das soluções cadastradas
│       │   └── solucao.py       # Controlador de CRUD das soluções
│       ├── database/
│       │   ├── crud/            # Lógica de acesso ao banco (CRUDs)
│       │   ├── models.py        # Modelos de tabela SQLAlchemy
│       │   └── database.py      # Configuração do engine e sessão do banco
│       ├── services/
│       │   ├── autenticacao.py  # Lógica de negócio para autenticação
│       │   └── solucao.py       # Lógica de negócio para CRUD das soluções
│       └── utils/
│           ├── configLog.py     # Configuração do logger
│           ├── criptografia.py  # Funções para criptografar/descriptografar dados
│           ├── database.py      # Funções utilitárias para o banco
│           └── paths.py         # Funções para leitura do diretório
├── __main__.py                  # Arquivo principal do projeto
├── bootstrap.py                 # Rotina de inicialização do ambiente Python e do banco de dados
├── example.env                  # Arquivo modelo de variáveis de ambiente
├── pyproject.toml               # Arquivo de configuração do projeto
├── .gitignore
├── LICENSE
└── README.md
```

## 📝 API (Exemplo de Uso)

A principal funcionalidade é exposta através de um endpoint de autenticação.

**Requisição:**

`GET /autenticar/{solucaoId}`

**Headers:**

`X-Token: <seu-xtoken-cadastrado>`

**Resposta de Sucesso:**

```json
{
    "solucaoId": 1,
    "token": "ey...",
    "dhExpiracaoToken": "2023-10-27T15:30:00",
    "mensagem": "Autenticado com sucesso"
}
```


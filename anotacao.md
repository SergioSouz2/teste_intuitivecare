3. Diagrama lógico simplificado (texto)
+-----------------+        +-----------------------+        +----------------------+
|   operadoras    | 1     N|  despesas_consolidadas|        |  despesas_agregadas  |
|-----------------|--------|----------------------|        |--------------------|
| id (UUID, PK)   |<------>| operadora_id (FK)    |        | id (UUID, PK)       |
| cnpj            |        | ano                  |        | operadora_id (FK)   |
| razao_social    |        | trimestre            |        | uf                  |
| nome_fantasia   |        | valor                |        | total               |
| ...             |        |                      |        | media               |
| data_registro   |        |                      |        | desvio_padrao       |
+-----------------+        +----------------------+        +--------------------+



Opção C – Guardar em tabela “pendentes”

Cria uma tabela despesas_pendentes para despesas sem cadastro:

CREATE TABLE despesas_pendentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registro_ans INTEGER,
    ano INTEGER,
    trimestre INTEGER,
    valor_despesas NUMERIC(20,2)
);



🔀 Trade-off: Normalização
Requisito

Escolher:

Opção A: Desnormalizada

Opção B: Normalizada
E justificar

Seu status: ⚠️ IMPLEMENTADO, MAS NÃO DOCUMENTADO

Você claramente escolheu Opção B (normalizada):

operadoras

despesas_consolidadas

despesas_agregadas

📌 FALTA:
👉 Texto explicando a decisão

Sugestão de justificativa (você pode copiar):

Optou-se por uma abordagem normalizada, separando dados cadastrais das operadoras e dados financeiros, visando reduzir redundância, facilitar atualizações cadastrais e melhorar a integridade referencial.
Como o volume de dados financeiros cresce mais rapidamente que os dados cadastrais e as análises exigem agregações temporais, a normalização melhora a manutenibilidade sem impactar negativamente a performance analítica, especialmente com índices adequados.




💾 Trade-off: Tipos de dados
Requisito

Justificar:

Monetário: DECIMAL vs FLOAT vs INTEGER

Datas: DATE vs VARCHAR vs TIMESTAMP

Seu status: ⚠️ IMPLEMENTADO, MAS NÃO JUSTIFICADO

Você usou:

NUMERIC(20,2) → ✔️ excelente escolha

DATE → ✔️ correto

INTEGER para ano/trimestre → ✔️ simples e eficiente

📌 FALTA: explicação formal.

Justificativa pronta:

Valores monetários

Foi utilizado o tipo NUMERIC(20,2) para garantir precisão decimal em cálculos financeiros, evitando erros de arredondamento comuns em tipos FLOAT. INTEGER em centavos foi descartado por reduzir legibilidade e aumentar complexidade de queries analíticas.

Datas

O tipo DATE foi utilizado para campos de data por representar corretamente o domínio do dado, permitir validações nativas e facilitar operações temporais, evitando ambiguidades de VARCHAR e complexidade desnecessária do TIMESTAMP.
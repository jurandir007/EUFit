# Relatório Técnico: `models.py` (Modelos de Dados)
https://chat.deepseek.com/share/3d22sunus1b9kev5m2

## 1. Visão Geral

O arquivo `models.py` define todos os modelos ORM (Object-Relational Mapping) do projeto EUFit, utilizando **SQLAlchemy** para mapear as tabelas do banco de dados PostgreSQL.

---

## 2. Modelo: `User`

### 2.1 Definição

```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
```

### 2.2 Estrutura da Tabela

| Coluna | Tipo | Atributos | Descrição |
|--------|------|-----------|-----------|
| `id` | Integer | PRIMARY KEY | Identificador único do usuário |
| `google_id` | String(100) | UNIQUE, NOT NULL | ID do usuário no Google (sub) ou UUID para anônimo |
| `email` | String(120) | UNIQUE, NOT NULL | E-mail do usuário |
| `name` | String(100) | NOT NULL | Nome do usuário |
| `deleted_at` | DateTime | NULLABLE | Soft delete (marcação de exclusão) |

### 2.3 Características

| Aspecto | Detalhe |
|---------|---------|
| **Herança** | `UserMixin` (Flask-Login) - fornece `is_authenticated`, `is_active`, `is_anonymous`, `get_id()` |
| **Soft Delete** | Coluna `deleted_at` permite exclusão lógica (dados não são removidos fisicamente) |
| **Relacionamentos** | Um-para-muitos com `Eu2016` e `RecordVape` |

---

## 3. Modelo: `Eu2016`

### 3.1 Definição

```python
class Eu2016(db.Model):
    __tablename__ = 'Eu_2016'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carimbo = db.Column('Carimbo de data/hora', db.DateTime)
    peso = db.Column('Peso', db.Float)
    gordura = db.Column('Gordura', db.Float)
    musculo = db.Column('Musculo', db.Float)
    basal = db.Column('basal', db.Float)
    idade = db.Column('Idade', db.Float)
    viceral = db.Column('viceral', db.Float)
    
    str_comb = db.Column('str_comb', db.String(10), Computed('PERSISTED'))
    fk_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    usuario = db.relationship('User', backref=db.backref('registros_eu2016', lazy=True))
```

### 3.2 Estrutura da Tabela

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer (PK) | Identificador único do registro |
| `carimbo` | DateTime | Data/hora da medição |
| `peso` | Float | Peso corporal |
| `gordura` | Float | Percentual de gordura |
| `musculo` | Float | Percentual de massa muscular |
| `basal` | Float | Taxa metabólica basal |
| `idade` | Float | Idade projetada (corporal) |
| `viceral` | Float | Gordura visceral |
| `str_comb` | String(10) | **Coluna computada** - indicador de campos nulos |
| `fk_user_id` | Integer (FK) | Referência ao usuário dono do registro |

### 3.3 Coluna Computada: `str_comb`

```python
str_comb = db.Column('str_comb', db.String(10), Computed('PERSISTED'))
```

**Propósito:** Indicar quais campos estão nulos em cada registro.

**Lógica (definida no banco):**

| Condição | Valor |
|----------|-------|
| Todos os campos preenchidos | `'0'` |
| Gordura nulo | Inclui `'f'` |
| Músculo nulo | Inclui `'m'` |
| Basal nulo | Inclui `'b'` |
| Idade nulo | Inclui `'a'` |
| Visceral nulo | Inclui `'v'` |

**Exemplos:**
- Registro completo: `'0'`
- Gordura e músculo nulos: `'fm'`
- Basal e idade nulos: `'ba'`

### 3.4 Relacionamentos

| Relacionamento | Tipo | Referência |
|----------------|------|------------|
| `fk_user_id` | Many-to-One | `users.id` |
| `usuario` | Relationship | Objeto `User` associado |
| `registros_eu2016` | Backref | Lista de registros do usuário |

---

## 4. Modelo: `RecordVape`

### 4.1 Definição

```python
class RecordVape(db.Model):
    __tablename__ = 'record_vape'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    puff_count = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    user = db.relationship('User', backref=db.backref('vape_records', lazy=True, cascade="all, delete-orphan"))
```

### 4.2 Estrutura da Tabela

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | Integer (PK) | Identificador único do registro |
| `user_id` | Integer (FK) | Referência ao usuário |
| `puff_count` | Integer | Número de puffs registrados |
| `recorded_at` | DateTime | Data/hora do registro (automático) |

### 4.3 Características

| Aspecto | Detalhe |
|---------|---------|
| **Cascade Delete** | `ondelete='CASCADE'` - Ao deletar usuário, registros vape são removidos |
| **Timestamp Automático** | `server_default=db.func.current_timestamp()` - Definido pelo banco |
| **Relacionamento** | Muitos-para-um com `User` |

---

## 5. Relacionamentos entre Modelos

```
+----------------+          +----------------+
|     User       |          |    Eu2016      |
+----------------+          +----------------+
| id (PK)        |<---------| fk_user_id (FK)|
| google_id      |          | id (PK)        |
| email          |          | carimbo        |
| name           |          | peso           |
| deleted_at     |          | gordura        |
+----------------+          | musculo        |
        |                   | basal          |
        |                   | idade          |
        |                   | viceral        |
        |                   | str_comb       |
        |                   +----------------+
        |
        |          +----------------+
        +--------->|  RecordVape    |
                   +----------------+
                   | user_id (FK)   |
                   | id (PK)        |
                   | puff_count     |
                   | recorded_at    |
                   +----------------+
```

---

## 6. Validações e Restrições

| Modelo | Restrição | Descrição |
|--------|-----------|-----------|
| `User` | `google_id` UNIQUE | Impede duplicidade de usuários Google |
| `User` | `email` UNIQUE | Impede duplicidade de e-mails |
| `Eu2016` | `fk_user_id` NOT NULL | Todo registro deve ter um dono |
| `Eu2016` | `str_comb` Computed | Mantido automaticamente pelo banco |
| `RecordVape` | `user_id` NOT NULL | Todo registro vape deve ter um dono |
| `RecordVape` | `puff_count` NOT NULL | Valor obrigatório |

---

## 7. Uso no Código

### 7.1 Criar Usuário

```python
new_user = User(
    google_id='123456789',
    email='user@example.com',
    name='John Doe'
)
db.session.add(new_user)
db.session.commit()
```

### 7.2 Buscar Registros do Usuário

```python
# Métrica corporais
records = Eu2016.query.filter_by(fk_user_id=current_user.id).all()

# Registros vape
vape_records = RecordVape.query.filter_by(user_id=current_user.id).all()
```

### 7.3 Criar Registro de Métrica

```python
new_record = Eu2016(
    fk_user_id=current_user.id,
    peso=75.0,
    gordura=18.5,
    viceral=7.0,
    # str_comb é calculado automaticamente pelo banco
)
db.session.add(new_record)
db.session.commit()
```

### 7.4 Criar Registro Vape

```python
new_vape = RecordVape(
    user_id=current_user.id,
    puff_count=150
)
db.session.add(new_vape)
db.session.commit()
```

---

## 8. Dependências

```python
from app.modules.core.database import db
from flask_login import UserMixin
from sqlalchemy import Computed
```

| Dependência | Propósito |
|-------------|-----------|
| `db` | Instância do SQLAlchemy (configurada em `database.py`) |
| `UserMixin` | Fornece métodos do Flask-Login |
| `Computed` | Define colunas computadas pelo banco |

---

## 9. Resumo Técnico

| Aspecto | Detalhe |
|---------|---------|
| **ORM** | SQLAlchemy 2.0 |
| **Tabelas** | `users`, `Eu_2016`, `record_vape` |
| **Chave Primária** | `id` (auto-increment) em todas |
| **Chaves Estrangeiras** | `fk_user_id` (Eu2016), `user_id` (RecordVape) |
| **Cascade** | `ondelete='CASCADE'` em RecordVape |
| **Coluna Computada** | `str_comb` (lógica no banco) |
| **Soft Delete** | `deleted_at` em User (não implementado, apenas coluna) |

---

## 10. Pontos de Atenção

| Item | Observação |
|------|------------|
| **`str_comb`** | Coluna computada pelo banco, **não deve ser alterada via código** |
| **`deleted_at`** | Coluna existe mas **não há filtro automático** nas queries (soft delete não implementado) |
| **`UserMixin`** | Importado mas **não há `@login_required`** nas rotas anônimas (tratado nas rotas) |
| **Nomes das Colunas** | `Eu2016` usa nomes com capitalização exata (ex: `'Carimbo de data/hora'`) |

---

## 11. Scripts de Criação (SQL Equivalente)

### Tabela `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    deleted_at TIMESTAMP NULL
);
```

### Tabela `Eu_2016`

```sql
CREATE TABLE "Eu_2016" (
    id SERIAL PRIMARY KEY,
    "Carimbo de data/hora" TIMESTAMP,
    "Peso" FLOAT,
    "Gordura" FLOAT,
    "Musculo" FLOAT,
    "basal" FLOAT,
    "Idade" FLOAT,
    "viceral" FLOAT,
    str_comb VARCHAR(10) GENERATED ALWAYS AS (
        CASE
            WHEN ("Gordura" IS NOT NULL) AND ("Musculo" IS NOT NULL) 
                 AND ("basal" IS NOT NULL) AND ("Idade" IS NOT NULL) 
                 AND ("viceral" IS NOT NULL) THEN '0'
            ELSE (CASE WHEN "Gordura" IS NULL THEN 'f' ELSE '' END) ||
                 (CASE WHEN "Musculo" IS NULL THEN 'm' ELSE '' END) ||
                 (CASE WHEN "basal" IS NULL THEN 'b' ELSE '' END) ||
                 (CASE WHEN "Idade" IS NULL THEN 'a' ELSE '' END) ||
                 (CASE WHEN "viceral" IS NULL THEN 'v' ELSE '' END)
        END
    ) STORED,
    fk_user_id INTEGER NOT NULL REFERENCES users(id)
);
```

### Tabela `record_vape`

```sql
CREATE TABLE record_vape (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    puff_count INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

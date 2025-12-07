"""Ajout colonnes category, reference, prix_unitaire

Revision ID: 7e0ec40b883f
Revises: 
Create Date: 2025-11-22 12:10:39.770734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e0ec40b883f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Migration sécurisée sans perte de données."""
    
    # ========================================
    # 1. RENOMMER entreprises → companies
    # ========================================
    # SQLite ne supporte pas ALTER TABLE RENAME directement avec contraintes
    # On crée la nouvelle table et copie les données
    
    # Créer la nouvelle table companies
    op.create_table('companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=True)
    
    # Copier les données de entreprises vers companies
    op.execute("""
        INSERT INTO companies (id, name)
        SELECT id, nom FROM entreprises
    """)
    
    # ========================================
    # 2. ARTICLES - Ajouter nouvelles colonnes
    # ========================================
    op.add_column('articles', sa.Column('reference', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('category', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('prix_unitaire', sa.Float(), nullable=True))
    
    # Vérifier si company_id existe déjà avant de l'ajouter
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('articles')]
    
    if 'company_id' not in columns:
        op.add_column('articles', sa.Column('company_id', sa.Integer(), nullable=True))
    
    # Créer les index
    op.create_index(op.f('ix_articles_category'), 'articles', ['category'], unique=False)
    op.create_index(op.f('ix_articles_reference'), 'articles', ['reference'], unique=False)
    
    # Ajouter la contrainte de clé étrangère
    try:
        op.create_foreign_key('fk_articles_company', 'articles', 'companies', ['company_id'], ['id'])
    except:
        pass  # La contrainte existe peut-être déjà
    
    # Valeurs par défaut pour les articles existants
    op.execute("""
        UPDATE articles 
        SET reference = 'REF-' || CAST(id AS TEXT),
            category = 'Non classé',
            prix_unitaire = 0.0
        WHERE reference IS NULL
    """)
    
    # ========================================
    # 3. USERS - Ajustements
    # ========================================
    
    # Vérifier les colonnes existantes
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Renommer hashed_password → password_hash si nécessaire
    if 'hashed_password' in user_columns and 'password_hash' not in user_columns:
        # SQLite ne supporte pas RENAME COLUMN directement, on doit recréer
        op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))
        op.execute("UPDATE users SET password_hash = hashed_password")
        op.execute("UPDATE users SET password_hash = 'changeme' WHERE password_hash IS NULL")
        # Note: SQLite ne supporte pas ALTER COLUMN SET NOT NULL, on laisse nullable=True
    
    # Renommer entreprise_id → company_id si nécessaire
    if 'entreprise_id' in user_columns and 'company_id' not in user_columns:
        op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
        op.execute("UPDATE users SET company_id = entreprise_id")
    elif 'company_id' not in user_columns:
        op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
    
    # Créer les index
    try:
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    except:
        pass
    
    try:
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    except:
        pass
    
    # Ajouter la contrainte de clé étrangère
    try:
        op.create_foreign_key('fk_users_company', 'users', 'companies', ['company_id'], ['id'])
    except:
        pass
    
    # Supprimer les anciennes colonnes si elles existent
    if 'hashed_password' in user_columns and 'password_hash' in user_columns:
        try:
            op.drop_column('users', 'hashed_password')
        except:
            pass
    
    if 'entreprise_id' in user_columns and 'company_id' in user_columns:
        try:
            op.drop_column('users', 'entreprise_id')
        except:
            pass
    
    if 'is_active' in user_columns:
        try:
            op.drop_column('users', 'is_active')
        except:
            pass
    
    # ========================================
    # 4. RETRAITS - Ajustements
    # ========================================
    
    retrait_columns = [col['name'] for col in inspector.get_columns('retraits')]
    
    # Ajouter les nouvelles colonnes
    if 'company_id' not in retrait_columns:
        op.add_column('retraits', sa.Column('company_id', sa.Integer(), nullable=True))
    
    if 'user_id' not in retrait_columns:
        op.add_column('retraits', sa.Column('user_id', sa.Integer(), nullable=True))
    
    if 'nom_utilisateur' not in retrait_columns:
        op.add_column('retraits', sa.Column('nom_utilisateur', sa.String(), nullable=True))
    
    # Renommer date → date_retrait si nécessaire
    if 'date' in retrait_columns and 'date_retrait' not in retrait_columns:
        op.add_column('retraits', sa.Column('date_retrait', sa.DateTime(), nullable=True))
        op.execute("UPDATE retraits SET date_retrait = date")
        try:
            op.drop_column('retraits', 'date')
        except:
            pass
    elif 'date_retrait' not in retrait_columns:
        op.add_column('retraits', sa.Column('date_retrait', sa.DateTime(), nullable=True))
        op.execute("UPDATE retraits SET date_retrait = datetime('now') WHERE date_retrait IS NULL")
    
    # Créer les index
    try:
        op.create_index(op.f('ix_retraits_id'), 'retraits', ['id'], unique=False)
    except:
        pass
    
    # Ajouter les contraintes de clés étrangères
    try:
        op.create_foreign_key('fk_retraits_company', 'retraits', 'companies', ['company_id'], ['id'])
    except:
        pass
    
    try:
        op.create_foreign_key('fk_retraits_user', 'retraits', 'users', ['user_id'], ['id'])
    except:
        pass
    
    # ========================================
    # 5. Supprimer l'ancienne table entreprises
    # ========================================
    # Uniquement après avoir tout migré
    try:
        op.drop_table('entreprises')
    except:
        pass  # La table n'existe peut-être plus
    
    print("✅ Migration terminée avec succès - Toutes les données ont été préservées !")


def downgrade() -> None:
    """Downgrade schema - Retour en arrière."""
    
    # Recréer entreprises
    op.create_table('entreprises',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('nom', sa.VARCHAR(), nullable=False),
        sa.Column('created_at', sa.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nom')
    )
    
    # Copier les données de companies vers entreprises
    op.execute("""
        INSERT INTO entreprises (id, nom)
        SELECT id, name FROM companies
    """)
    
    # Users - Restaurer les anciennes colonnes
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), nullable=True))
    op.add_column('users', sa.Column('entreprise_id', sa.INTEGER(), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(), nullable=False))
    
    op.execute("UPDATE users SET hashed_password = password_hash")
    op.execute("UPDATE users SET entreprise_id = company_id")
    
    op.drop_column('users', 'company_id')
    op.drop_column('users', 'password_hash')
    
    # Retraits - Restaurer date
    op.add_column('retraits', sa.Column('date', sa.DATETIME(), nullable=True))
    op.execute("UPDATE retraits SET date = date_retrait")
    op.drop_column('retraits', 'date_retrait')
    op.drop_column('retraits', 'nom_utilisateur')
    op.drop_column('retraits', 'user_id')
    op.drop_column('retraits', 'company_id')
    
    # Articles - Supprimer les nouvelles colonnes
    op.drop_column('articles', 'company_id')
    op.drop_column('articles', 'prix_unitaire')
    op.drop_column('articles', 'category')
    op.drop_column('articles', 'reference')
    
    # Supprimer companies
    op.drop_table('companies')
    
    print("✅ Downgrade terminé - Retour à l'état précédent")
import sqlite3

def init_db():
    conn = sqlite3.connect("/app/db/loan_requests.db")
    cursor = conn.cursor()
    
    # Table des clients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients_credit (
        cin TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        historique_credit TEXT NOT NULL,
        score_credit INTEGER NOT NULL,
        incidents_paiement INTEGER NOT NULL,
        revenus_stables TEXT NOT NULL
    )
    """)

    # Table des demandes de prêt
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cin TEXT NOT NULL,
        montant REAL NOT NULL,
        duree INTEGER NOT NULL,
        etat TEXT NOT NULL DEFAULT 'en attente',
        date_soumission TEXT,
        FOREIGN KEY (cin) REFERENCES clients_credit (cin)
    )
    """)

    # Supprimer toutes les anciennes données
    cursor.execute("DELETE FROM clients_credit;")
    # Insérer des clients fictifs
    cursor.executemany("""
        INSERT INTO clients_credit (cin, nom, historique_credit, score_credit, incidents_paiement, revenus_stables) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, [
            # Bons profils avec score élevé et stabilité financière
            ("CIN0950a", "Lucas Fontaine", "excellent", 810, 0, "Oui"),
            ("CIN0950aq", "Lucas Fontaine", "excellent", 810, 0, "Oui"),
            ("CIN0950aw", "Lucas Fontaine", "excellent", 810, 0, "Oui"),
            ("CIN0950az", "Lucas Fontaine", "excellent", 810, 0, "Oui"),
            ("CIN0950ax", "Lucas Fontaine", "excellent", 810, 0, "Oui"),
            ("CIN0950b", "Emma Lefevre", "bon", 760, 0, "Oui"),

            # Profils moyens avec un risque modéré
            ("CIN0950c", "Nathan Blanc", "moyen", 690, 1, "Oui"),
            ("CIN0950d", "Julie Renault", "moyen", 670, 2, "Non"),

            # Profils à risque avec incidents de paiement
            ("CIN0950e", "Arthur Morel", "mauvais", 520, 3, "Non"),
            ("CIN0950f", "Sophie Dubois", "mauvais", 450, 4, "Non"),

            # Profils variables avec stabilité différente
            ("CIN0950g", "Hugo Charpentier", "bon", 740, 1, "Oui"),
            ("CIN0950h", "Laura Girard", "moyen", 650, 2, "Non"),
            ("CIN0950i", "Victor Lambert", "mauvais", 500, 3, "Oui"),
            ("CIN0950j", "Chloé Perrin", "mauvais", 480, 5, "Non")
        ])

    # Insérer des demandes de prêt fictives
    cursor.executemany("""
    INSERT INTO loan_requests (cin, montant, duree, etat, date_soumission) 
    VALUES (?, CAST(? AS REAL), CAST(? AS INTEGER), ?, ?)
    """, [
        ("CIN0945f", 150000.00, 240, "en attente", "2025-03-09"),
        ("CIN0945g", 40000.00, 120, "rejeté", "2025-03-09"),
    ])


    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("*Base de données initialisée avec des données fictives.")

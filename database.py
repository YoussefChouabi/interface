# database.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Hotel (
        Id_Hotel INTEGER PRIMARY KEY AUTOINCREMENT,
        Ville TEXT,
        Pays TEXT,
        Code_postal INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Client (
        Id_Client INTEGER PRIMARY KEY AUTOINCREMENT,
        Adresse TEXT,
        Ville TEXT,
        Code_postal INTEGER,
        Email TEXT,
        Telephone TEXT,
        Nom_complet TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Prestation (
        Id_Prestation INTEGER PRIMARY KEY AUTOINCREMENT,
        Prix REAL,
        Description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Type_Chambre (
        Id_Type INTEGER PRIMARY KEY AUTOINCREMENT,
        Type TEXT,
        Tarif REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Chambre (
        Id_Chambre INTEGER PRIMARY KEY AUTOINCREMENT,
        Numero INTEGER,
        Etage INTEGER,
        Fumeur INTEGER,  # 0 pour non-fumeur, 1 pour fumeur
        Id_Hotel INTEGER,
        Id_Type INTEGER,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
        FOREIGN KEY (Id_Type) REFERENCES Type_Chambre(Id_Type)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservation (
        Id_Reservation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_arrivee DATE,
        Date_depart DATE,
        Id_Client INTEGER,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Evaluation (
        Id_Evaluation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date DATE,
        Note INTEGER,
        Commentaire TEXT,
        Id_Client INTEGER,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Chambre_Reservation (
        Id_Chambre INTEGER,
        Id_Reservation INTEGER,
        PRIMARY KEY (Id_Chambre, Id_Reservation),
        FOREIGN KEY (Id_Chambre) REFERENCES Chambre(Id_Chambre),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation)
    )
    ''')

    # Insertion des données initiales
    # Hotels
    hotels = [
        (1, 'Paris', 'France', 75001),
        (2, 'Lyon', 'France', 69002)
    ]
    cursor.executemany('INSERT INTO Hotel VALUES (?, ?, ?, ?)', hotels)

    # Clients
    clients = [
        (1, '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678', 'Jean Dupont'),
        (2, '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789', 'Marie Leroy'),
        (3, '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890', 'Paul Moreau'),
        (4, '27 Rue Nationale', 'Lille', 59800, 'Lucie.martin@email.fr', '0645678901', 'Lucie Martin'),
        (5, '3 Rue des Fleurs', 'Nice', 6000, 'emma.giraud@email.fr', '0656789012', 'Emma Giraud')
    ]
    cursor.executemany('INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)', clients)

    # Prestations
    prestations = [
        (1, 15, 'Petit-déjeuner'),
        (2, 30, 'Navette aéroport'),
        (3, 0, 'Wi-Fi gratuit'),
        (4, 50, 'Spa et bien-être'),
        (5, 20, 'Parking sécurisé')
    ]
    cursor.executemany('INSERT INTO Prestation VALUES (?, ?, ?)', prestations)

    # Types de chambre
    types_chambre = [
        (1, 'Simple', 80),
        (2, 'Double', 120)
    ]
    cursor.executemany('INSERT INTO Type_Chambre VALUES (?, ?, ?)', types_chambre)

    # Chambres
    chambres = [
        (1, 201, 2, 0, 1, 1),
        (2, 502, 5, 1, 1, 2),
        (3, 305, 3, 0, 2, 1),
        (4, 410, 4, 0, 2, 2),
        (5, 104, 1, 1, 2, 2),
        (6, 202, 2, 0, 1, 1),
        (7, 307, 3, 1, 1, 2),
        (8, 101, 1, 0, 1, 1)
    ]
    cursor.executemany('INSERT INTO Chambre VALUES (?, ?, ?, ?, ?, ?)', chambres)

    # Réservations
    reservations = [
        (1, '2025-06-15', '2025-06-18', 1),
        (2, '2025-07-01', '2025-07-05', 2),
        (7, '2025-11-12', '2025-11-14', 2),
        (10, '2026-02-01', '2026-02-05', 2),
        (3, '2025-08-10', '2025-08-14', 3),
        (4, '2025-09-05', '2025-09-07', 4),
        (9, '2026-01-15', '2026-01-18', 4),
        (5, '2025-09-20', '2025-09-25', 5)
    ]
    cursor.executemany('INSERT INTO Reservation VALUES (?, ?, ?, ?)', reservations)

    # Évaluations
    evaluations = [
        (1, '2025-06-15', 5, 'Excellent séjour, personnel très accueillant.', 1),
        (2, '2025-07-01', 4, 'Chambre propre, bon rapport qualité/prix.', 2),
        (3, '2025-08-10', 3, 'Séjour correct mais bruyant la nuit.', 3),
        (4, '2025-09-05', 5, 'Service impeccable, je recommande.', 4),
        (5, '2025-09-20', 4, 'Très bon petit-déjeuner, hôtel bien situé.', 5)
    ]
    cursor.executemany('INSERT INTO Evaluation VALUES (?, ?, ?, ?, ?)', evaluations)

    # Chambres réservées (relation Chambre_Reservation)
    chambre_reservations = [
        (1, 1),  # Chambre 1 réservée pour réservation 1
        (2, 2),  # Chambre 2 réservée pour réservation 2
        (3, 3),  # etc.
        (4, 4),
        (5, 5),
        (6, 7),
        (7, 10),
        (8, 9)
    ]
    cursor.executemany('INSERT INTO Chambre_Reservation VALUES (?, ?)', chambre_reservations)

    conn.commit()
    conn.close()

if __name__ == '_main_':
    init_db()
    print("Base de données initialisée avec succès!")
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection with error handling
def get_db_connection():
    try:
        conn = sqlite3.connect('hotel.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        st.stop()

# Initialize database with sample data
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Hotel (
        Id_Hotel INTEGER PRIMARY KEY,
        Ville TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS Type_Chambre (
        Id_Type INTEGER PRIMARY KEY,
        Type TEXT NOT NULL,
        Tarif REAL NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS Client (
        Id_Client INTEGER PRIMARY KEY,
        Nom_complet TEXT NOT NULL,
        Adresse TEXT,
        Ville TEXT,
        Code_postal INTEGER,
        Email TEXT,
        Telephone TEXT
    );
    
    CREATE TABLE IF NOT EXISTS Chambre (
        Id_Chambre INTEGER PRIMARY KEY,
        Numero INTEGER NOT NULL,
        Etage INTEGER NOT NULL,
        Fumeur INTEGER DEFAULT 0,
        Id_Hotel INTEGER,
        Id_Type INTEGER,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel (Id_Hotel),
        FOREIGN KEY (Id_Type) REFERENCES Type_Chambre (Id_Type)
    );
    
    CREATE TABLE IF NOT EXISTS Reservation (
        Id_Reservation INTEGER PRIMARY KEY,
        Date_arrivee TEXT NOT NULL,
        Date_depart TEXT NOT NULL,
        Id_Client INTEGER,
        FOREIGN KEY (Id_Client) REFERENCES Client (Id_Client)
    );
    
    CREATE TABLE IF NOT EXISTS Chambre_Reservation (
        Id_Chambre INTEGER,
        Id_Reservation INTEGER,
        PRIMARY KEY (Id_Chambre, Id_Reservation),
        FOREIGN KEY (Id_Chambre) REFERENCES Chambre (Id_Chambre),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation (Id_Reservation)
    );
    ''')
    
    # Insert sample data if tables are empty
    if not cursor.execute("SELECT COUNT(*) FROM Hotel").fetchone()[0]:
        cursor.executemany("INSERT INTO Hotel (Ville) VALUES (?)", 
                         [("Paris",), ("Lyon",), ("Marseille",)])
        
    if not cursor.execute("SELECT COUNT(*) FROM Type_Chambre").fetchone()[0]:
        cursor.executemany(
            "INSERT INTO Type_Chambre (Type, Tarif) VALUES (?, ?)",
            [("Simple", 80), ("Double", 120), ("Suite", 250)]
        )
    
    if not cursor.execute("SELECT COUNT(*) FROM Chambre").fetchone()[0]:
        cursor.executemany(
            "INSERT INTO Chambre (Numero, Etage, Id_Hotel, Id_Type) VALUES (?, ?, ?, ?)",
            [(101, 1, 1, 1), (102, 1, 1, 2), (201, 2, 1, 2), (301, 3, 1, 3)]
        )
    
    conn.commit()
    conn.close()

# Home page
def home_page():
    st.title("Système de gestion hôtelière")
    st.write("Bienvenue dans le système de gestion de l'hôtel. Utilisez le menu de gauche pour naviguer.")

# View reservations
def view_reservations():
    st.title("Liste des réservations")
    
    conn = get_db_connection()
    query = '''
    SELECT r.Id_Reservation, c.Nom_complet, h.Ville, r.Date_arrivee, r.Date_depart
    FROM Reservation r
    JOIN Client c ON r.Id_Client = c.Id_Client
    JOIN Chambre_Reservation cr ON r.Id_Reservation = cr.Id_Reservation
    JOIN Chambre ch ON cr.Id_Chambre = ch.Id_Chambre
    JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
    ORDER BY r.Date_arrivee DESC
    '''
    reservations = conn.execute(query).fetchall()
    conn.close()
    
    if reservations:
        df = pd.DataFrame(reservations, columns=["ID", "Client", "Ville", "Arrivée", "Départ"])
        df['Arrivée'] = pd.to_datetime(df['Arrivée']).dt.date
        df['Départ'] = pd.to_datetime(df['Départ']).dt.date
        st.dataframe(df)
    else:
        st.write("Aucune réservation trouvée.")

# View clients
def view_clients():
    st.title("Liste des clients")
    
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM Client ORDER BY Nom_complet').fetchall()
    conn.close()
    
    if clients:
        st.dataframe(pd.DataFrame(clients, columns=["ID", "Nom complet", "Adresse", "Ville", "Code postal", "Email", "Téléphone"]))
    else:
        st.write("Aucun client trouvé.")

# View available rooms
def view_available_rooms():
    st.title("Recherche de chambres disponibles")
    
    col1, col2 = st.columns(2)
    with col1:
        date_arrivee = st.date_input("Date d'arrivée", min_value=datetime.today())
    with col2:
        date_depart = st.date_input("Date de départ", min_value=date_arrivee)
    
    if st.button("Rechercher"):
        conn = get_db_connection()
        
        # Convert dates to strings
        date_arrivee_str = date_arrivee.strftime("%Y-%m-%d")
        date_depart_str = date_depart.strftime("%Y-%m-%d")
        
        # Find reserved rooms
        reserved_rooms = conn.execute('''
        SELECT DISTINCT cr.Id_Chambre
        FROM Chambre_Reservation cr
        JOIN Reservation r ON cr.Id_Reservation = r.Id_Reservation
        WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
           OR (r.Date_arrivee BETWEEN ? AND ?)
           OR (r.Date_depart BETWEEN ? AND ?)
        ''', (date_depart_str, date_arrivee_str, 
              date_arrivee_str, date_depart_str,
              date_arrivee_str, date_depart_str)).fetchall()
        
        reserved_ids = [room['Id_Chambre'] for room in reserved_rooms]
        
        # Find available rooms
        if reserved_ids:
            query = '''
            SELECT ch.Id_Chambre, ch.Numero, ch.Etage, 
                   CASE ch.Fumeur WHEN 1 THEN 'Oui' ELSE 'Non' END as Fumeur,
                   h.Ville, tc.Type, tc.Tarif
            FROM Chambre ch
            JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
            JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type
            WHERE ch.Id_Chambre NOT IN ({})
            '''.format(','.join(['?']*len(reserved_ids)))
            available_rooms = conn.execute(query, reserved_ids).fetchall()
        else:
            query = '''
            SELECT ch.Id_Chambre, ch.Numero, ch.Etage, 
                   CASE ch.Fumeur WHEN 1 THEN 'Oui' ELSE 'Non' END as Fumeur,
                   h.Ville, tc.Type, tc.Tarif
            FROM Chambre ch
            JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
            JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type
            '''
            available_rooms = conn.execute(query).fetchall()
        
        conn.close()
        
        if available_rooms:
            df = pd.DataFrame(available_rooms, 
                            columns=["ID", "Numéro", "Étage", "Fumeur", "Ville", "Type", "Tarif"])
            st.dataframe(df)
        else:
            st.warning("Aucune chambre disponible pour cette période.")

# Add client
def add_client():
    st.title("Ajouter un nouveau client")
    
    with st.form("client_form"):
        nom = st.text_input("Nom complet*", max_chars=100)
        adresse = st.text_input("Adresse", max_chars=200)
        ville = st.text_input("Ville", max_chars=50)
        code_postal = st.number_input("Code postal", min_value=0, max_value=99999, step=1)
        email = st.text_input("Email", max_chars=100)
        telephone = st.text_input("Téléphone", max_chars=20)
        
        submitted = st.form_submit_button("Enregistrer")
        
        if submitted:
            if not nom:
                st.error("Le nom complet est obligatoire")
                return
                
            conn = get_db_connection()
            try:
                conn.execute('''
                INSERT INTO Client (Nom_complet, Adresse, Ville, Code_postal, Email, Telephone)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (nom, adresse, ville, code_postal, email, telephone))
                conn.commit()
                st.success("Client ajouté avec succès!")
                st.balloons()
            except sqlite3.Error as e:
                st.error(f"Erreur lors de l'ajout du client: {e}")
            finally:
                conn.close()

# Add reservation
def add_reservation():
    st.title("Ajouter une nouvelle réservation")
    
    conn = get_db_connection()
    clients = conn.execute('SELECT Id_Client, Nom_complet FROM Client ORDER BY Nom_complet').fetchall()
    conn.close()
    
    if not clients:
        st.warning("Aucun client disponible. Veuillez d'abord ajouter un client.")
        return
    
    client_options = {f"{client['Nom_complet']} (ID: {client['Id_Client']})": client['Id_Client'] for client in clients}
    
    with st.form("reservation_form"):
        # Client selection
        selected_client = st.selectbox("Client*", options=list(client_options.keys()))
        
        # Date selection
        col1, col2 = st.columns(2)
        with col1:
            date_arrivee = st.date_input("Date d'arrivée*", min_value=datetime.today())
        with col2:
            date_depart = st.date_input("Date de départ*", min_value=date_arrivee)
        
        # Convert dates to strings for SQLite
        date_arrivee_str = date_arrivee.strftime("%Y-%m-%d")
        date_depart_str = date_depart.strftime("%Y-%m-%d")
        
        # Find available rooms
        conn = get_db_connection()
        available_rooms = conn.execute('''
        SELECT ch.Id_Chambre, ch.Numero, ch.Etage, tc.Type, tc.Tarif, h.Ville
        FROM Chambre ch
        JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type
        JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
        WHERE ch.Id_Chambre NOT IN (
            SELECT DISTINCT cr.Id_Chambre
            FROM Chambre_Reservation cr
            JOIN Reservation r ON cr.Id_Reservation = r.Id_Reservation
            WHERE (
                (r.Date_arrivee <= ? AND r.Date_depart >= ?) OR
                (r.Date_arrivee BETWEEN ? AND ?) OR
                (r.Date_depart BETWEEN ? AND ?)
            )
        )
        ORDER BY ch.Numero
        ''', (date_depart_str, date_arrivee_str, 
              date_arrivee_str, date_depart_str,
              date_arrivee_str, date_depart_str)).fetchall()
        
        conn.close()
        
        # Create room options
        room_options = {
            f"{room['Numero']} - {room['Type']} (Étage {room['Etage']}, {room['Ville']}) - {room['Tarif']}€/nuit": 
            room['Id_Chambre'] for room in available_rooms
        }
        
        # Room selection
        selected_rooms = st.multiselect(
            "Chambres à réserver*", 
            options=list(room_options.keys()),
            help="Sélectionnez une ou plusieurs chambres disponibles"
        )
        
        submitted = st.form_submit_button("Enregistrer la réservation")
        
        if submitted:
            if not selected_rooms:
                st.error("Veuillez sélectionner au moins une chambre")
                return
                
            conn = get_db_connection()
            try:
                # Add reservation
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client)
                VALUES (?, ?, ?)
                ''', (date_arrivee_str, date_depart_str, client_options[selected_client]))
                reservation_id = cursor.lastrowid
                
                # Link selected rooms
                for room_display in selected_rooms:
                    room_id = room_options[room_display]
                    cursor.execute('''
                    INSERT INTO Chambre_Reservation (Id_Chambre, Id_Reservation)
                    VALUES (?, ?)
                    ''', (room_id, reservation_id))
                
                conn.commit()
                st.success(f"Réservation #{reservation_id} créée pour {len(selected_rooms)} chambre(s)!")
                st.balloons()
            except sqlite3.Error as e:
                conn.rollback()
                st.error(f"Erreur de base de données: {e}")
            finally:
                conn.close()

# Main app
def main():
    # Initialize database on first run
    init_db()
    
    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Navigation", [
        "Accueil",
        "Consulter les réservations",
        "Consulter les clients",
        "Rechercher chambres disponibles",
        "Ajouter un client",
        "Ajouter une réservation"
    ])
    
    if app_mode == "Accueil":
        home_page()
    elif app_mode == "Consulter les réservations":
        view_reservations()
    elif app_mode == "Consulter les clients":
        view_clients()
    elif app_mode == "Rechercher chambres disponibles":
        view_available_rooms()
    elif app_mode == "Ajouter un client":
        add_client()
    elif app_mode == "Ajouter une réservation":
        add_reservation()

if __name__ == "__main__":
    main()
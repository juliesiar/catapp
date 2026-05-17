import streamlit as st
import pandas as pd

# ============================================================
# CONFIG DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="CatApp 🐱",
    page_icon="🐱",
    layout="wide"
)

# ============================================================
# CHARGEMENT / SAUVEGARDE DU CSV
# ============================================================

CSV_PATH = "users.csv"

def load_users():
    """Lit le fichier CSV et retourne un DataFrame."""
    return pd.read_csv(CSV_PATH)

def save_users(df):
    """Sauvegarde le DataFrame dans le fichier CSV."""
    df.to_csv(CSV_PATH, index=False)


# ============================================================
# INITIALISATION DU SESSION STATE
# (permet de mémoriser l'état de connexion entre les pages)
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "page" not in st.session_state:
    st.session_state.page = "🏠 Accueil"


# ============================================================
# PAGE DE CONNEXION
# ============================================================

def page_login():
    """Affiche le formulaire de connexion."""

    # Centrage visuel
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🐱 CatApp")
        st.subheader("Connexion")

        with st.form("form_login"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit   = st.form_submit_button("Se connecter", use_container_width=True)

        if submit:
            df = load_users()

            # Vérification si l'utilisateur existe
            user_row = df[df["name"] == username]

            if user_row.empty:
                st.error("❌ Utilisateur introuvable.")

            else:
                user = user_row.iloc[0]  # On prend la première ligne correspondante

                # Vérification : compte bloqué après 3 tentatives
                if user["failed_login_attemps"] >= 3:
                    st.error("🔒 Compte bloqué (trop de tentatives échouées). Contactez un admin.")

                # Vérification du mot de passe
                elif user["password"] == password:
                    # Connexion réussie !
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.session_state.role      = user["role"]

                    # Mise à jour du CSV : logged_in = True + remise à zéro des tentatives
                    df.loc[df["name"] == username, "logged_in"]            = True
                    df.loc[df["name"] == username, "failed_login_attemps"] = 0
                    save_users(df)

                    st.rerun()  # Rechargement de l'app pour afficher la page principale

                else:
                    # Mauvais mot de passe → on incrémente le compteur d'échecs
                    df.loc[df["name"] == username, "failed_login_attemps"] += 1
                    save_users(df)

                    tentatives_restantes = 3 - int(df.loc[df["name"] == username, "failed_login_attemps"].values[0])
                    st.error(f"❌ Mot de passe incorrect. ({max(0, tentatives_restantes)} tentative(s) restante(s))")


# ============================================================
# SIDEBAR (menu latéral)
# ============================================================

def afficher_sidebar():
    """Affiche la barre latérale avec navigation, bienvenue et déconnexion."""

    with st.sidebar:
        # Message de bienvenue
        st.markdown(f"## 👋 Bienvenue {st.session_state.username}")
        st.caption(f"Rôle : `{st.session_state.role}`")
        st.divider()

        # Menu de navigation
        choix = st.radio(
            "Navigation",
            options=["🏠 Accueil", "📸 Album Photos"],
            key="page"
        )

        st.divider()

        # Bouton de déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True):
            # Mise à jour du CSV : logged_in = False
            df = load_users()
            df.loc[df["name"] == st.session_state.username, "logged_in"] = False
            save_users(df)

            # Réinitialisation du session state
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.role      = ""
            st.session_state.page      = "🏠 Accueil"
            st.rerun()

    return choix


# ============================================================
# PAGE D'ACCUEIL
# ============================================================

def page_accueil():
    """Affiche la page d'accueil après connexion."""
    st.title("🏠 Page d'accueil")
    st.write(f"Bonjour **{st.session_state.username}** ! Bienvenue sur CatApp 🐱")
    st.info("Utilise le menu à gauche pour naviguer vers l'album photos.")


# ============================================================
# PAGE ALBUM PHOTOS (3 images par ligne)
# ============================================================

def page_album():
    """Affiche un album de photos de chats, 3 par ligne."""
    st.title("📸 Album Photos — Les chats")
    st.write("Des chats, encore des chats, toujours des chats 🐱")
    st.divider()

    # Liste d'URLs de photos de chats
    # On utilise placekitten.com avec des dimensions différentes pour varier les images
    cat_images = [
    ("https://loremflickr.com/400/300/cat?lock=1", "Minou"),
    ("https://loremflickr.com/400/300/cat?lock=2", "Filou"),
    ("https://loremflickr.com/400/300/cat?lock=3", "Tigrou"),
    ("https://loremflickr.com/400/300/cat?lock=4", "Câline"),
    ("https://loremflickr.com/400/300/cat?lock=5", "Minette"),
    ("https://loremflickr.com/400/300/cat?lock=6", "Félix"),
    ("https://loremflickr.com/400/300/cat?lock=7", "Caramel"),
    ("https://loremflickr.com/400/300/cat?lock=8", "Noisette"),
    ("https://loremflickr.com/400/300/cat?lock=9", "Perle"),
]

    # Affichage 3 images par ligne avec st.columns
    for i in range(0, len(cat_images), 3):

        # On crée 3 colonnes pour chaque ligne
        cols = st.columns(3)

        for j, col in enumerate(cols):
            index = i + j
            if index < len(cat_images):  # On vérifie qu'on ne dépasse pas la liste
                url, nom = cat_images[index]
                with col:
                    st.image(url, caption=nom, use_container_width=True)


# ============================================================
# LOGIQUE PRINCIPALE
# ============================================================

if not st.session_state.logged_in:
    # L'utilisateur n'est pas connecté → on affiche le formulaire de login
    page_login()

else:
    # L'utilisateur est connecté → on affiche la sidebar + la page choisie
    page_choisie = afficher_sidebar()

    if page_choisie == "🏠 Accueil":
        page_accueil()

    elif page_choisie == "📸 Album Photos":
        page_album()

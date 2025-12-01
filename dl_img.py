#!/usr/bin/env python3
"""
Script pour télécharger, convertir et renommer les images du site Paris-Lille
Crée les dossiers /images/full et /images/thumb avec les images en WebP
"""

import os
import re
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import unicodedata

def remove_accents(text):
    """Supprime les accents d'une chaîne de caractères"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def sanitize_filename(text):
    """Convertit un titre en nom de fichier valide sans accent"""
    # Enlever les accents
    text = remove_accents(text)
    # Convertir en minuscules
    text = text.lower()
    # Remplacer les espaces et caractères spéciaux par des tirets
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def download_and_convert_image(url, output_path, max_size=2000):
    """Télécharge une image et la convertit en WebP"""
    try:
        # Télécharger l'image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Ouvrir l'image
        img = Image.open(BytesIO(response.content))
        
        # Convertir en RGB si nécessaire (pour WebP)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionner si nécessaire (max 2000px en largeur ou hauteur)
        width, height = img.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Sauvegarder en WebP
        img.save(output_path, 'WEBP', quality=85, method=6)
        print(f"✓ Converti: {output_path.name}")
        return True
        
    except Exception as e:
        print(f"✗ Erreur pour {url}: {str(e)}")
        return False

def create_thumbnail(source_path, thumb_path, thumb_size=400):
    """Crée une miniature à partir d'une image"""
    try:
        img = Image.open(source_path)
        img.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
        img.save(thumb_path, 'WEBP', quality=80, method=6)
        print(f"  → Miniature créée: {thumb_path.name}")
        return True
    except Exception as e:
        print(f"✗ Erreur création miniature: {str(e)}")
        return False

# Liste des images avec leurs titres (extraits du HTML)
images = [
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2246-scaled.jpg", "La mini"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/image00011-copie-rotated.jpeg", "Jupette en dentelle"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/image00005-scaled.jpeg", "La robette rayée"),
    ("https://paris-lille.com/wp-content/uploads/2021/03/image00015-rotated.jpeg", "La blouse anti-loose"),
    ("https://paris-lille.com/wp-content/uploads/2021/03/image00011-2-rotated.jpeg", "Le pluvieux"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/chemise-monsieur-parislille2.jpg", "La chemise Monsieur Madame"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/image00001-copie.jpeg", "Le bandana rayé"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/carre-leo-parislille.jpg", "Le bandana léo"),
    ("https://paris-lille.com/wp-content/uploads/2021/05/sweat-parislille9.jpg", "Le sweat qui a la frite gris"),
    ("https://paris-lille.com/wp-content/uploads/2021/04/tshirt-prems-parislille7-scaled.jpeg", "Tshirt Preum's"),
    ("https://paris-lille.com/wp-content/uploads/2021/04/hot-culotte-parislille2-rotated.jpeg", "La hot culotte"),
    ("https://paris-lille.com/wp-content/uploads/2021/03/taie-d-oreiller-paris-lille6.jpg", "Taies rayées"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/taie-leo-paris-lille3.jpeg", "Taies léo"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/6B034307-5834-410C-996E-222F7232841F-1-scaled.jpg", "Blouse claudine Léo"),
    ("https://paris-lille.com/wp-content/uploads/2021/06/image00002-copie.jpeg", "Robette en broderie anglaise"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/4J2A1218-scaled.jpg", "Robette en velour rose"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/IMG_7520-scaled.jpg", "Robette en velour vert"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/4J2A1289-scaled.jpg", "Blouse anti-loose carreaux"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/IMG_7705-scaled.jpg", "Blouse anti-loose liberty"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/IMG_7806-scaled.jpg", "Veste froufrou"),
    ("https://paris-lille.com/wp-content/uploads/2021/09/4J2A1353-1-scaled.jpg", "Le frileux"),
    ("https://paris-lille.com/wp-content/uploads/2021/10/FA748953-CD7F-4105-9DBB-F7055AD3E98F-scaled.jpeg", "Le sweat qui a la frite marine"),
    ("https://paris-lille.com/wp-content/uploads/2022/02/PARIS-LILLE13-scaled.jpg", "La robe libérée libérée délivrée"),
    ("https://paris-lille.com/wp-content/uploads/2022/02/PARIS-LILLE84-scaled.jpg", "La jupe en jean fiz"),
    ("https://paris-lille.com/wp-content/uploads/2022/02/PARIS-LILLE132-scaled.jpg", "La blouse claudine à carreaux"),
    ("https://paris-lille.com/wp-content/uploads/2022/02/PARIS-LILLE154-scaled.jpg", "Le blazer Prosper"),
    ("https://paris-lille.com/wp-content/uploads/2022/03/PARIS_LILLE5.jpg", "La combi Paris-Lille"),
    ("https://paris-lille.com/wp-content/uploads/2022/03/PARIS_LILLE77.jpg", "Le top Noeud Noeud"),
    ("https://paris-lille.com/wp-content/uploads/2022/03/PARIS_LILLE110.jpg", "La robe Noeud Noeud"),
    ("https://paris-lille.com/wp-content/uploads/2022/05/PARIS_LILLE135-scaled.jpg", "Le Tshirt basique blanc"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2211-scaled.jpg", "Les chemises madame petits carreaux"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2237-scaled.jpg", "Les chemises madame grands carreaux"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2251-scaled.jpg", "Les chemises madame lurex"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH22164-scaled.jpg", "Blazer Prince de Galles"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2270-scaled.jpg", "La robette en jean"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2297-scaled.jpg", "Le pluvieux numéro 2"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH22116-scaled.jpg", "La blouse frida"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH22157-scaled.jpg", "Le manteau Daddy"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/PARIS-LILLEAH2286-scaled.jpg", "Le bonnet René"),
    ("https://paris-lille.com/wp-content/uploads/2022/09/image00015-2-scaled.jpeg", "La maille canaille"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE5-2-scaled.jpg", "La jupe Nauzan"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE19-2-scaled.jpg", "La blouse Claudette à rayures"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE45-2-scaled.jpg", "La blouse Claudette en broderie anglaise"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE83-2-scaled.jpg", "La chemise Madame rayée jaune"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE92-2-scaled.jpg", "Le short Ponta"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE114-2-scaled.jpg", "Le jupon Ninon"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE123-2-scaled.jpg", "Le blazer écru"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE139-2-scaled.jpg", "Le basique gris"),
    ("https://paris-lille.com/wp-content/uploads/2023/03/PARIS-LILLE102-2-scaled.jpg", "Le marcel blanc"),
    ("https://paris-lille.com/wp-content/uploads/2023/10/image00001-scaled-1.jpeg", "Le sweat pépite"),
    ("https://paris-lille.com/wp-content/uploads/2024/03/image00002-2-scaled.jpeg", "La robe Sarah vichy noir"),
    ("https://paris-lille.com/wp-content/uploads/2024/03/image00005-3-scaled.jpeg", "La blouse Violette vichy noir"),
    ("https://paris-lille.com/wp-content/uploads/2024/04/image00003-4-scaled.jpeg", "La robe louison"),
    ("https://paris-lille.com/wp-content/uploads/2024/04/image00004-2-scaled.jpeg", "Le marcel marine"),
    ("https://paris-lille.com/wp-content/uploads/2024/04/image00004-4-scaled.jpeg", "La robe Sarah Osaka"),
    ("https://paris-lille.com/wp-content/uploads/2024/10/image00007-1-scaled.jpeg", "La robe Sarah vichy tangerine"),
    ("https://paris-lille.com/wp-content/uploads/2024/10/image00001-3-scaled.jpeg", "La blouse Pauline Bonbon"),
    ("https://paris-lille.com/wp-content/uploads/2024/12/image00007-scaled.jpeg", "Le cabas Paula"),
    ("https://paris-lille.com/wp-content/uploads/2024/10/image00003-2-scaled.jpeg", "La jupe Sharleen"),
    ("https://paris-lille.com/wp-content/uploads/2024/03/image00021-scaled.jpeg", "Le basique noir"),
    ("https://paris-lille.com/wp-content/uploads/2025/03/image00004-4-scaled.jpeg", "La jupe BB vichy rouge"),
    ("https://paris-lille.com/wp-content/uploads/2025/03/image00009-9-scaled.jpeg", "La jupe Bohème Porto"),
    ("https://paris-lille.com/wp-content/uploads/2025/05/image00004-scaled.jpeg", "Le Tshirt Malo"),
    ("https://paris-lille.com/wp-content/uploads/2025/05/image00002-1-scaled.jpeg", "La robe Portofino"),
]

def main():
    # Créer les dossiers
    Path("images/full").mkdir(parents=True, exist_ok=True)
    Path("images/thumb").mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Téléchargement et conversion des images Paris-Lille")
    print("=" * 60)
    print()
    
    success_count = 0
    total = len(images)
    
    for i, (url, title) in enumerate(images, 1):
        filename = sanitize_filename(title)
        full_path = Path(f"images/full/{filename}.webp")
        thumb_path = Path(f"images/thumb/{filename}.webp")
        
        print(f"[{i}/{total}] {title}")
        
        # Télécharger et convertir l'image full
        if download_and_convert_image(url, full_path):
            # Créer la miniature
            create_thumbnail(full_path, thumb_path)
            success_count += 1
        
        print()
    
    print("=" * 60)
    print(f"Terminé! {success_count}/{total} images traitées avec succès")
    print("=" * 60)

if __name__ == "__main__":
    main()
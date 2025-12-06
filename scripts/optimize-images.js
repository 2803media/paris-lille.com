const sharp = require("sharp");
const fs = require("fs-extra");
const path = require("path");
const glob = require("glob");

// Configuration des dossiers
const IMG_DIR = path.join(__dirname, "../images");
const BACKUP_DIR = path.join(__dirname, "../images-original");

// Création du dossier d'images s'il n'existe pas
if (!fs.existsSync(IMG_DIR)) {
  fs.mkdirSync(IMG_DIR, { recursive: true });
}

async function optimizeImages() {
  console.log("🖼️  Optimisation des images...");

  // Si le backup existe, les images sont déjà optimisées
  if (fs.existsSync(BACKUP_DIR)) {
    console.log("✅ Images déjà optimisées (backup existe)");
    console.log("💡 Pour ré-optimiser, supprimez le dossier img-original");
    return;
  }

  // Vérifier s'il y a des images à optimiser
  const images = glob.sync(`${IMG_DIR}/**/*.{jpg,jpeg,png,webp}`, {
    nodir: true,
  });

  if (images.length === 0) {
    console.log("ℹ️  Aucune image trouvée à optimiser");
    return;
  }

  console.log(`📸 ${images.length} images trouvées`);

  // Créer le backup des originales
  console.log("📦 Création du backup des images originales...");
  await fs.ensureDir(BACKUP_DIR);
  await fs.copy(IMG_DIR, BACKUP_DIR);

  let optimized = 0;
  let skipped = 0;

  for (const imagePath of images) {
    try {
      const ext = path.extname(imagePath).toLowerCase();
      const stats = await fs.stat(imagePath);
      const originalSize = stats.size;

      // Ignorer les images trop petites
      if (originalSize < 1024 * 5) {
        // Moins de 5KB
        console.log(`  ⏩ ${path.basename(imagePath)} - Trop petite, ignorée`);
        skipped++;
        continue;
      }

      // Lire l'image avec sharp
      let image = sharp(imagePath);
      const metadata = await image.metadata();

      // Si l'image est plus large que 1920px, on la redimensionne
      if (metadata.width > 1920) {
        image = image.resize(1920);
      }

      // Optimiser selon le format
      if (ext === ".jpg" || ext === ".jpeg") {
        image = image.jpeg({
          quality: 80,
          progressive: true,
          mozjpeg: true,
        });
      } else if (ext === ".png") {
        image = image.png({
          quality: 80,
          compressionLevel: 9,
        });
      } else if (ext === ".webp") {
        image = image.webp({
          quality: 80,
          lossless: false,
          alphaQuality: 80,
        });
      }

      // Sauvegarder (écrase l'original)
      await image.toFile(imagePath + ".tmp");
      await fs.move(imagePath + ".tmp", imagePath, { overwrite: true });

      const newStats = await fs.stat(imagePath);
      const newSize = newStats.size;
      const saved = (((originalSize - newSize) / originalSize) * 100).toFixed(
        1
      );

      if (newSize < originalSize) {
        console.log(
          `  ✓ ${path.basename(imagePath)} - ${saved}% réduit (${(
            originalSize / 1024
          ).toFixed(1)}KB → ${(newSize / 1024).toFixed(1)}KB)`
        );
        optimized++;
      } else {
        // Si l'image optimisée est plus grosse, restaurer l'originale
        await fs.copy(
          path.join(BACKUP_DIR, path.relative(IMG_DIR, imagePath)),
          imagePath,
          { overwrite: true }
        );
        console.log(
          `  ! ${path.basename(imagePath)} - Aucune réduction, image conservée`
        );
        skipped++;
      }
    } catch (error) {
      console.error(
        `  ✗ Erreur sur ${path.basename(imagePath)}:`,
        error.message
      );
    }
  }

  console.log(`\n✅ Terminé : ${optimized} optimisées, ${skipped} conservées`);
  if (optimized > 0) {
    console.log(`💾 Backup des originaux dans : ${BACKUP_DIR}`);
  }
}

optimizeImages().catch(console.error);

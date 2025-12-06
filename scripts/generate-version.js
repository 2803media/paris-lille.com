const fs = require("fs");
const path = require("path");

function generateVersionFile() {
  try {
    // Lire le fichier package.json
    const packageJsonPath = path.join(__dirname, "../package.json");
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));

    // Créer le dossier de destination s'il n'existe pas
    const outputDir = path.join(__dirname, "../js");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Écrire le fichier ligne par ligne
    const outputPath = path.join(outputDir, "version.js");
    const file = fs.openSync(outputPath, "w");

    fs.writeSync(file, "// Auto-generated file - do not edit\n");
    fs.writeSync(file, `const APP_VERSION = '${packageJson.version}';\n`);
    fs.writeSync(file, "window.APP_VERSION = APP_VERSION;\n");

    fs.closeSync(file);

    console.log(`Version ${packageJson.version} written to ${outputPath}`);
    return true;
  } catch (error) {
    console.error("Error generating version file:", error.message);
    process.exit(1);
  }
}

generateVersionFile();

# Journal des changements

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnage [SemVer](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté

- `SpecError` et `FontError` s'importent depuis `blog_image` directement, et
  restent exposées par `blog_image.fonts` et `blog_image.spec` : on ne peut pas
  utiliser `resolve_fonts` ou `load_spec` en bibliothèque sans pouvoir les
  rattraper.

### Corrigé

- Un chapeau long ne sort plus de la marge droite : il n'était borné par
  aucune mesure et se faisait couper par le bord de l'image. Son corps
  rétrécit maintenant jusqu'à un plancher de lisibilité, puis le texte est
  coupé sur une ellipse. Un chapeau qui tenait déjà rend le même fichier,
  octet pour octet.
- Le point d'accent du titre entre dans la mesure : dessiné après la dernière
  ligne sans être compté par l'ajustement, il pouvait mordre dans la marge
  droite quand la ligne frôlait la largeur utile.

### Modifié

- Le paquet passe en disposition `src/`, et chaque responsabilité devient un
  module : `spec/` lit la description, `fonts/` résout les polices, `draw/`
  dessine la carte, `schema/` ne porte que les types et `errors.py` les deux
  erreurs que la CLI rattrape. L'API du premier niveau et les fichiers
  produits ne changent pas ; les chemins profonds bougent (`blog_image.config`
  devient `blog_image.spec`). Une copie de travail déjà installée demande un
  `uv sync`, le chemin du paquet ayant bougé.
- 86 tests au lieu de 29 : la CLI, les polices et les motifs en avaient zéro.

## [0.1.0] - 2026-10-24

Première version.

### Ajouté

- Génération des images de couverture d'un article dans plusieurs rapports
  d'image à partir d'un fichier YAML, pour ne plus entretenir à la main trois
  fichiers qui divergent au premier changement de titre.
- Trois formats par défaut — 16:9 (1600×900) pour Open Graph et l'en-tête du
  billet, 4:3 (1600×1200) pour l'emplacement Discover, 1:1 (1200×1200) pour les
  recadrages sociaux. Les ratios `3x2`, `2x1`, `4x5` et `9x16` sont connus, et
  toute taille s'écrit en pixels (`1240x700`).
- Clés de description en français ou en anglais (`titre` ou `title`, `fond` ou
  `background`). Une clé inconnue est une erreur plutôt qu'un silence.
- Coupe automatique du titre sur la largeur mesurée de la police, avec
  réduction du corps tant que le compte de lignes ou la largeur dépasse. Une
  seule description sert les trois formats.
- Respect des espaces insécables : un `?` ou un `:` français ne part pas seul à
  la ligne.
- Motifs `particules` et `grille`, ou `aucun`, dimensionnés sur l'unité
  typographique et non sur la bande qu'ils occupent.
- Résolution de police multi-plateforme : une famille, un gabarit de chemin
  contenant `%s`, ou une paire de fichiers explicite. À défaut, repli sur IBM
  Plex Mono, DejaVu puis Arial, avec un message qui dit où l'outil a cherché.
- Interface en ligne de commande (`-o`, `-f`, `-n`, `--dry-run`, `-q`) et API
  Python (`load_spec`, `resolve_fonts`, `render`).

### Notes

- Le rendu est reproductible : les mêmes descriptions produisent les mêmes
  fichiers, octet pour octet, de Pillow 11.3 à Pillow 13.0.
- 29 tests, exécutés en intégration continue sur Python 3.10, 3.12 et 3.14.
- Publié sur PyPI : `uv tool install blog-image`, ou
  `uvx --from blog-image blog-image image.yml` sans rien installer de permanent.

[0.1.0]: https://github.com/foverseas/blog-image/releases/tag/v0.1.0

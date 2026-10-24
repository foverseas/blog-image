# blog-image

[![CI](https://github.com/foverseas/blog-image/actions/workflows/ci.yml/badge.svg)](https://github.com/foverseas/blog-image/actions/workflows/ci.yml)

Génère les images de couverture d'un article dans plusieurs formats, à partir
d'un fichier YAML de trois lignes.

```yaml
# image.yml
titre: "Combien coûte une application mobile"
accent: "#00ff99"
fond:   "#1c1c22"
```

```console
$ blog-image image.yml
  -> article-16x9.png   1600x900
  -> article-4x3.png    1600x1200
  -> article-1x1.png    1200x1200
```

![Exemple de carte 16:9](https://raw.githubusercontent.com/foverseas/blog-image/v0.1.0/docs/exemple-16x9.png)

Trois formats parce qu'un article en a besoin de trois : le 16:9 pour Open
Graph et l'en-tête du billet, le 4:3 pour l'emplacement Discover, le 1:1 pour
les recadrages sociaux. Les générer séparément, c'est trois fichiers qui
divergent au premier changement de titre.

## Installation

Avec [uv](https://docs.astral.sh/uv/), sans rien installer de permanent :

```console
$ uvx --from blog-image blog-image image.yml
```

Pour l'avoir sous la main partout :

```console
$ uv tool install blog-image      # ou : pipx install blog-image
```

Et en développement, depuis les sources :

```console
$ git clone https://github.com/foverseas/blog-image
$ cd blog-image
$ uv sync --extra dev             # crée .venv d'après uv.lock
$ uv run blog-image examples/image.yml
```

`pip install blog-image` fonctionne aussi : c'est un paquet ordinaire, uv n'est
pas une dépendance.

Il faut Python 3.10, Pillow et PyYAML. La police par défaut est JetBrains
Mono ; si elle n'est pas installée, le programme retombe sur IBM Plex Mono,
DejaVu puis Arial, et dit où il a cherché s'il ne trouve rien.

## Le fichier de description

Seul `titre` est obligatoire. Les clés s'écrivent en français ou en anglais.

| Clé | Alias | Défaut | Rôle |
| --- | --- | --- | --- |
| `titre` | `title` | — | le titre, coupé automatiquement sur la largeur réelle de la police |
| `sous-titre` | `subtitle` | vide | une ligne sous le titre ; une liste devient autant de lignes |
| `chapeau` | `eyebrow` | vide | surtitre en capitales espacées, dans la couleur d'accent |
| `pied` | `footer` | vide | le pied de carte, précédé d'une pastille |
| `fond` | `background` | `#1c1c22` | fond de la carte |
| `texte` | `foreground` | `#ffffff` | couleur du texte |
| `accent` | — | `#00ff99` | pastille, surtitre, point final, motif |
| `motif` | — | `particules` | `particules`, `grille` ou `aucun` |
| `graine` | `seed` | `0` | change la disposition du motif sans rien toucher d'autre |
| `police` | `font` | JetBrains Mono | nom de famille, gabarit de chemin contenant `%s`, ou `{regular:, bold:}` |
| `formats` | — | `[16x9, 4x3, 1x1]` | ratios connus ou tailles explicites en pixels |
| `nom` | `name` | `article` | base du nom de fichier |
| `sortie` | `out` | `.` | dossier de sortie, relatif au fichier YAML |
| `point` | `dot` | `true` | le point d'accent après le titre |
| `lignes-max` | `max_lines` | `4` | au-delà, le titre rapetisse au lieu de déborder |

Les couleurs s'écrivent `#rgb`, `#rrggbb` ou `[28, 28, 34]`. Une clé inconnue
est une erreur : une faute de frappe dans un nom de clé ne se voit sinon qu'une
fois la carte terminée.

Ratios connus : `16x9`, `4x3`, `3x2`, `2x1`, `1x1`, `4x5`, `9x16`. Pour tout
autre besoin, écrivez la taille en pixels — `1240x700`.

Voir [`examples/complet.yml`](examples/complet.yml) pour un fichier avec toutes
les clés.

## En ligne de commande

```console
$ blog-image image.yml                      # formats du fichier
$ blog-image image.yml -o public/blog       # ailleurs
$ blog-image image.yml -f 16x9 -f 1200x628  # autres formats
$ blog-image image.yml --dry-run            # ce qui serait écrit, sans écrire
```

`-n/--name` remplace la base du nom de fichier, `-q/--quiet` coupe la sortie.
Une erreur de description sort en code 2 avec un message en clair, pas une
trace.

## Comme bibliothèque

```python
from pathlib import Path
from blog_image import load_spec, render, resolve_fonts

spec = load_spec(Path("image.yml"))
fonts = resolve_fonts(spec.font)
for fmt in spec.formats:
    render(spec, fonts, fmt, spec.path_for(fmt))
```

## Trois décisions qui expliquent le reste du code

**Tout est dessiné à 3× puis réduit en Lanczos.** C'est ce qui tient les
filets d'un pixel et le petit corps, pas l'anticrénelage du rastériseur, qui
est inégal à ces tailles. La réduction est suivie d'une quantification sur 256
couleurs : sur un aplat, elle ne se voit pas et divise le poids du fichier par
deux.

**Le corps du texte est calculé sur une unité, pas sur la largeur.** Une carte
1:1 n'est pas plus large qu'une 4:3 mais elle a bien plus de place ; dimensionner
sur la largeur seule la laisse creuse. L'unité corrige la largeur par l'écart
entre le ratio demandé et le 16:9 :

```python
unit = width * (1 + max(0.0, height / width - 0.5625) * 0.34)
```

**Le titre est coupé sur la largeur mesurée de la police**, pas sur un nombre
de caractères, et le corps diminue tant que le compte de lignes dépasse
`lignes-max`. C'est ce qui évite d'écrire une coupe différente par format.

Le motif, lui, est dimensionné sur la même unité et non sur la bande qu'il
occupe : en 16:9 cette bande fait quelques centaines de pixels, en 1:1 cinq
fois plus, et un décor calé sur la bande disparaît dans le premier cas et
écrase le second. Seul le nombre de marques dépend de la place disponible.

## Tests

```console
$ uv run pytest
```

Le rendu est reproductible : les mêmes descriptions donnent les mêmes fichiers,
octet pour octet, d'une version de Pillow à l'autre. `uv.lock` est versionné
pour que ce soit vrai d'une machine à l'autre aussi.

## Journal des changements

Voir [CHANGELOG.md](CHANGELOG.md).

## Contact

Une question d'usage, un titre qui se coupe mal, une idée de format : le
[Discord](https://discord.gg/FS2xqJ4QT6) est le chemin le plus court. Les questions posées dans les
[Discussions](https://github.com/foverseas/blog-image/discussions/categories/q-a) y gagnent une réponse qui
reste trouvable, et les bugs vont dans les [issues](https://github.com/foverseas/blog-image/issues).

## Licence

MIT.

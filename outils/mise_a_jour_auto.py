"""Mise à jour automatique du site pour le référencement (tâche planifiée tous les deux jours).

Demande du propriétaire du 2026-11-08 : « automatise cette tâche pour s'exécuter tous les deux jours,
pour un meilleur référencement ».

Étapes :
  1. catalogue relu dans Clover (nouveaux produits, noms, prix, photos) -> data/produits*.json
  2. pages du site et sitemap.xml refaits
  3. contrôles : assez de produits (Clover a bien répondu), pas de description en double
  4. s'il y a des changements : commit + push sur main -> GitHub Actions met le site en ligne (FTPS)
  5. fin de la mise en ligne attendue, puis pages changées signalées à IndexNow (Bing, Yandex, Seznam…)
  6. audit SEO (E:/claude code/Agent_SEO) ; rapport par courriel si le mot de passe SMTP est enregistré

Journal : deploiement/journal_mise_a_jour.log (non publié).

    python outils/mise_a_jour_auto.py                 # tout
    python outils/mise_a_jour_auto.py --sans-publier  # tout refaire et contrôler, sans commit ni push
    python outils/mise_a_jour_auto.py --planifier     # tâche Windows tous les deux jours à 5 h
    python outils/mise_a_jour_auto.py --deplanifier
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
AGENT_SEO = Path(r"E:\claude code\Agent_SEO")
SYNC = Path(r"E:\claude code\MVOGMBI_Sync_2026.1")
URL = "https://www.marchemvogmbi.com/"
HOTE = "www.marchemvogmbi.com"
JOURNAL = SITE / "deploiement" / "journal_mise_a_jour.log"
VERROU = SITE / "deploiement" / "mise_a_jour.verrou"
TACHE = "Marche Mvog-Mbi - mise a jour du site (referencement)"
BAISSE_MAX = 0.20          # plus de 20 % de produits en moins = Clover a mal répondu : rien n'est publié


def noter(texte: str) -> None:
    ligne = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {texte}"
    print(ligne.encode(sys.stdout.encoding or "utf-8", "replace").decode(sys.stdout.encoding or "utf-8"), flush=True)
    JOURNAL.parent.mkdir(exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(ligne + "\n")


def lancer(commande: list[str], dossier: Path = SITE, delai: int = 1800) -> str:
    r = subprocess.run(commande, cwd=dossier, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=delai, env=os.environ | {"PYTHONIOENCODING": "utf-8"})
    sortie = (r.stdout + r.stderr).strip()
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(commande)} : code {r.returncode}\n{sortie[-2000:]}")
    return sortie


def nb_produits() -> int:
    fichier = SITE / "data" / "produits.json"
    if not fichier.exists():
        return 0
    d = json.loads(fichier.read_text(encoding="utf-8"))
    return len(d if isinstance(d, list) else d["produits"])


def controler() -> list[str]:
    """Descriptions et titres en double parmi les pages produits (une langue après l'autre)."""
    problemes = []
    for dossier in [SITE] + [SITE / c for c in ("en", "es", "pt", "it", "de")]:
        descriptions, titres = Counter(), Counter()
        for p in dossier.glob("produit-*.html"):
            t = p.read_text(encoding="utf-8", errors="ignore")
            if m := re.search(r'<meta name="description" content="([^"]*)"', t):
                descriptions[m.group(1)] += 1
            if m := re.search(r"<title>(.*?)</title>", t, re.S):
                titres[m.group(1)] += 1
        doubles_d = sum(n for n in descriptions.values() if n > 1)
        doubles_t = sum(n for n in titres.values() if n > 1)
        if doubles_d or doubles_t:
            problemes.append(f"{dossier.name or 'fr'} : {doubles_d} descriptions et {doubles_t} titres en double")
    return problemes


def adresse(chemin: str) -> str | None:
    """Fichier du site -> adresse publique (pages HTML seulement)."""
    parties = chemin.replace("\\", "/").split("/")
    if not chemin.endswith(".html") or len(parties) > 2 or (len(parties) == 2 and parties[0] not in
                                                             ("en", "es", "pt", "it", "de")):
        return None
    return URL + "/".join(parties).removesuffix("index.html")


def cle_indexnow() -> str | None:
    cles = [p.stem for p in SITE.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    return cles[0] if cles else None


def signaler_indexnow(adresses: list[str]) -> None:
    cle = cle_indexnow()
    if not cle or not adresses:
        return
    for i in range(0, len(adresses), 10000):
        corps = json.dumps({"host": HOTE, "key": cle, "keyLocation": f"{URL}{cle}.txt",
                            "urlList": adresses[i:i + 10000]}).encode()
        demande = urllib.request.Request("https://api.indexnow.org/indexnow", data=corps, method="POST",
                                         headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(demande, timeout=60) as r:
                noter(f"IndexNow : {len(adresses[i:i + 10000])} adresses signalées (réponse {r.status})")
        except Exception as e:  # noqa: BLE001 — IndexNow n'est jamais bloquant
            noter(f"IndexNow refusé : {e}")


def attendre_mise_en_ligne(commit: str) -> bool:
    """Attend la fin de l'action « Mise en ligne » du commit (3 h au plus). Vrai si réussie."""
    fin = time.time() + 3 * 3600
    while time.time() < fin:
        time.sleep(60)
        try:
            runs = json.loads(lancer(["gh", "run", "list", "--workflow", "mise-en-ligne.yml", "--limit", "10",
                                      "--json", "headSha,status,conclusion"], delai=120))
        except Exception as e:  # noqa: BLE001
            noter(f"Suivi de la mise en ligne impossible : {e}")
            return False
        run = next((r for r in runs if r["headSha"] == commit), None)
        if run and run["status"] == "completed":
            return run["conclusion"] == "success"
    return False


def auditer() -> None:
    """Audit SEO du site ; rapport HTML dans Agent_SEO/rapports, par courriel si le mot de passe SMTP est connu."""
    if not AGENT_SEO.exists():
        return
    sys.path.insert(0, str(AGENT_SEO))
    try:
        from agent_seo import secrets_seo
        avec_ia = bool(secrets_seo.lire(secrets_seo.CLE_API))
        courriel = bool(secrets_seo.lire(secrets_seo.COURRIEL))
    except Exception:  # noqa: BLE001
        avec_ia = courriel = False
    commande = [sys.executable, "-m", "agent_seo", "auditer", "--site", "marche", "--pas-ouvrir"]
    commande += [] if avec_ia else ["--sans-ia"]
    commande += ["--courriel"] if courriel else []
    try:
        try:
            sortie = lancer(commande, dossier=AGENT_SEO, delai=3600)
        except RuntimeError as e:
            if not avec_ia:
                raise
            # analyse par Claude impossible (crédit Anthropic épuisé…) : audit technique seul, rapport quand même
            raison = "crédit Anthropic épuisé" if "credit balance" in str(e) else "erreur de l'agent"
            noter(f"Analyse IA impossible ({raison}) : audit sans IA")
            avec_ia = False
            sortie = lancer([c for c in commande] + ["--sans-ia"], dossier=AGENT_SEO, delai=3600)
        note = re.findall(r"(\d+)\s*/\s*100", sortie)
        noter(f"Audit SEO {'avec' if avec_ia else 'sans'} IA terminé"
              f"{f' : note {note[-1]}/100' if note else ''}{' ; rapport envoyé par courriel' if courriel else ''}")
    except Exception as e:  # noqa: BLE001
        noter(f"Audit SEO en échec : {e}")


def mettre_a_jour(publier: bool) -> None:
    avant = nb_produits()
    noter("Lecture du catalogue Clover…")
    lancer([sys.executable, "outils/exporter_catalogue.py", "--sync", str(SYNC), "--garder-articles"])
    apres = nb_produits()
    noter(f"Produits publiés : {avant} -> {apres}")
    if avant and apres < avant * (1 - BAISSE_MAX):
        lancer(["git", "checkout", "--", "data"])
        raise RuntimeError(f"Trop de produits en moins ({avant} -> {apres}) : Clover a sans doute mal répondu, "
                           "rien n'est publié.")
    noter("Construction des pages et du sitemap…")
    lancer([sys.executable, "outils/construire_site.py"])
    lancer([sys.executable, "outils/generer_sitemap.py"])
    for probleme in controler():
        noter(f"À vérifier : {probleme}")

    lancer(["git", "add", "-A"])
    changes = [l for l in lancer(["git", "diff", "--cached", "--name-only"]).splitlines() if l]
    if not changes:
        noter("Aucun changement : rien à publier.")
        return
    noter(f"{len(changes)} fichiers changés")
    if not publier:
        lancer(["git", "reset", "-q"])
        noter("--sans-publier : changements laissés dans le dossier, sans commit.")
        return
    lancer(["git", "commit", "-q", "-m", f"Mise à jour automatique du catalogue et des pages ({datetime.now():%Y-%m-%d})"])
    lancer(["git", "push", "-q", "origin", "main"], delai=600)
    commit = lancer(["git", "rev-parse", "HEAD"])
    noter(f"Envoyé sur GitHub ({commit[:8]}) : mise en ligne en cours…")
    if attendre_mise_en_ligne(commit):
        noter("Mise en ligne terminée.")
        adresses = sorted({a for c in changes if (a := adresse(c))} | {URL + "sitemap.xml"})
        signaler_indexnow(adresses)
    else:
        noter("Mise en ligne non confirmée : IndexNow sauté (voir l'onglet Actions sur GitHub).")


def planifier() -> None:
    lanceur = SITE / "deploiement" / "mise_a_jour_auto.cmd"
    lanceur.parent.mkdir(exist_ok=True)
    lanceur.write_text(f'@echo off\r\ncd /d "{SITE}"\r\n"{sys.executable}" outils\\mise_a_jour_auto.py '
                       f'>> "{JOURNAL.with_name('console_mise_a_jour.log')}" 2>&1\r\n', encoding="utf-8")
    lancer(["schtasks", "/Create", "/F", "/TN", TACHE, "/SC", "DAILY", "/MO", "2", "/ST", "05:00",
            "/TR", f'"{lanceur}"'])
    print(f"Tâche « {TACHE} » créée : tous les deux jours à 5 h (session Windows ouverte, même verrouillée).")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sans-publier", action="store_true")
    p.add_argument("--sans-audit", action="store_true")
    p.add_argument("--planifier", action="store_true")
    p.add_argument("--deplanifier", action="store_true")
    a = p.parse_args()
    if a.planifier:
        return planifier()
    if a.deplanifier:
        lancer(["schtasks", "/Delete", "/F", "/TN", TACHE])
        return print("Tâche retirée.")
    if VERROU.exists() and time.time() - VERROU.stat().st_mtime < 6 * 3600:
        return noter("Une mise à jour est déjà en cours : arrêt.")
    VERROU.parent.mkdir(exist_ok=True)
    VERROU.write_text(str(os.getpid()))
    try:
        noter("=== Début de la mise à jour automatique ===")
        mettre_a_jour(publier=not a.sans_publier)
    except Exception as e:  # noqa: BLE001
        noter(f"ÉCHEC : {e}")
    finally:
        if not a.sans_audit:
            auditer()
        VERROU.unlink(missing_ok=True)
        noter("=== Fin ===")


if __name__ == "__main__":
    main()

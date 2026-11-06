<?php
/*
 * Formulaire « Envoyez-nous un message » (pages Contact et Carrière, toutes les langues du site).
 * Envoie le message à contact@marchemvogmbi.com, avec la pièce jointe (PDF ou Word, 10 Mo au plus),
 * puis renvoie la personne sur la page d'où elle vient avec ?envoye=1 (ou ?erreur=…).
 * Hébergement : PHP avec la fonction mail() (WHC, cPanel). Rien n'est gardé sur le serveur.
 */
declare(strict_types=1);

const DESTINATAIRE = 'contact@marchemvogmbi.com';
const EXPEDITEUR = 'site@marchemvogmbi.com';          // adresse du domaine : sinon le courriel part en indésirables
const TAILLE_MAX = 10 * 1024 * 1024;
const EXTENSIONS = ['pdf' => 'application/pdf', 'doc' => 'application/msword',
    'docx' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
const SUJETS = [
    'produit' => 'Question sur un produit', 'commande' => 'Commande ou livraison',
    'prix' => 'Garantie du meilleur prix', 'candidature' => 'Candidature (CV)',
    'fournisseur' => 'Fournisseur ou partenariat', 'autre' => 'Autre demande',
];

function retour(string $page, array $params): void {
    $pages = ['contact.html', 'carriere.html'];
    foreach (['en', 'es', 'pt', 'it', 'de'] as $l) { $pages[] = "$l/contact.html"; $pages[] = "$l/carriere.html"; }
    if (!in_array($page, $pages, true)) { $page = 'contact.html'; }
    header('Location: /' . $page . '?' . http_build_query($params) . '#formulaire', true, 303);
    exit;
}

function ligne(string $texte, int $max): string {       // une ligne, sans saut (pas d'injection d'en-tête)
    $texte = trim(preg_replace('/[\r\n\t]+/', ' ', $texte) ?? '');
    return mb_substr($texte, 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { retour('contact.html', []); }
$page = (string)($_POST['page'] ?? 'contact.html');

// Robots : champ caché rempli, ou formulaire envoyé en moins de 3 secondes
if (!empty($_POST['site_web']) || (time() - (int)($_POST['debut'] ?? 0)) < 3) { retour($page, ['envoye' => 1]); }

$nom = ligne((string)($_POST['nom'] ?? ''), 120);
$courriel = ligne((string)($_POST['courriel'] ?? ''), 160);
$sujet = (string)($_POST['sujet'] ?? 'autre');
$message = trim(mb_substr((string)($_POST['message'] ?? ''), 0, 8000));
if ($nom === '' || $message === '' || !filter_var($courriel, FILTER_VALIDATE_EMAIL)) { retour($page, ['erreur' => 'champs']); }
if (!isset(SUJETS[$sujet])) { $sujet = 'autre'; }

// Pièce jointe facultative
$piece = null;
if (!empty($_FILES['piece']) && $_FILES['piece']['error'] !== UPLOAD_ERR_NO_FILE) {
    $f = $_FILES['piece'];
    if ($f['error'] !== UPLOAD_ERR_OK || $f['size'] > TAILLE_MAX) { retour($page, ['erreur' => 'taille']); }
    $ext = strtolower(pathinfo((string)$f['name'], PATHINFO_EXTENSION));
    if (!isset(EXTENSIONS[$ext])) { retour($page, ['erreur' => 'format']); }
    $contenu = file_get_contents($f['tmp_name']);
    $debut = substr((string)$contenu, 0, 8);                 // vrai PDF / Word, pas seulement le nom
    $valide = ($ext === 'pdf' && str_starts_with($debut, '%PDF'))
        || ($ext === 'docx' && str_starts_with($debut, "PK\x03\x04"))
        || ($ext === 'doc' && str_starts_with($debut, "\xD0\xCF\x11\xE0"));
    if (!$valide) { retour($page, ['erreur' => 'format']); }
    $nomFichier = preg_replace('/[^A-Za-z0-9._-]+/', '_', basename((string)$f['name'])) ?: "piece.$ext";
    $piece = ['nom' => $nomFichier, 'type' => EXTENSIONS[$ext], 'contenu' => $contenu];
}

$titre = 'Site web — ' . SUJETS[$sujet] . ' — ' . $nom;
$corps = "Nouveau message envoyé depuis le site marchemvogmbi.com\n\n"
    . "Nom : $nom\nCourriel : $courriel\nSujet : " . SUJETS[$sujet] . "\nPage : $page\n"
    . 'Date : ' . date('Y-m-d H:i') . "\n\n--- Message ---\n$message\n";

$limite = 'mvogmbi_' . bin2hex(random_bytes(8));
$entetes = [
    'From: Site Marché Mvog-Mbi <' . EXPEDITEUR . '>',
    'Reply-To: ' . $courriel,
    'MIME-Version: 1.0',
    'Content-Type: multipart/mixed; boundary="' . $limite . '"',
];
$contenuMail = "--$limite\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n"
    . chunk_split(base64_encode($corps));
if ($piece) {
    $contenuMail .= "--$limite\r\nContent-Type: {$piece['type']}; name=\"{$piece['nom']}\"\r\n"
        . "Content-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename=\"{$piece['nom']}\"\r\n\r\n"
        . chunk_split(base64_encode($piece['contenu']));
}
$contenuMail .= "--$limite--";

$titreEncode = '=?UTF-8?B?' . base64_encode($titre) . '?=';
$ok = mail(DESTINATAIRE, $titreEncode, $contenuMail, implode("\r\n", $entetes), '-f' . EXPEDITEUR);
retour($page, $ok ? ['envoye' => 1] : ['erreur' => 'envoi']);

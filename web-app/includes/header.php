<?php
// includes/header.php
$page_title = $page_title ?? APP_NAME;
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= htmlspecialchars($page_title) ?> — <?= APP_NAME ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="<?= BASE_URL ?>/css/style.css">
</head>
<body>
<nav class="navbar">
  <a class="navbar-brand" href="<?= BASE_URL ?>">
    <span class="brand-icon">⬡</span>
    <span class="brand-name">ASAG</span>
  </a>
  <div class="nav-links">
    <?php if (!empty($_SESSION['user_id'])): ?>
      <?php if ($_SESSION['role'] === 'admin'): ?>
        <a href="<?= BASE_URL ?>/admin/dashboard.php">Dashboard</a>
        <a href="<?= BASE_URL ?>/admin/tests.php">Tests</a>
        <a href="<?= BASE_URL ?>/admin/results.php">Results</a>
      <?php else: ?>
        <a href="<?= BASE_URL ?>/student/dashboard.php">Dashboard</a>
        <a href="<?= BASE_URL ?>/student/my_results.php">My Results</a>
      <?php endif; ?>
      <a href="<?= BASE_URL ?>/logout.php" class="btn-nav-logout">Logout</a>
    <?php endif; ?>
  </div>
</nav>

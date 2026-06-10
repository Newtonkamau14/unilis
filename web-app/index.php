<?php
require_once __DIR__ . '/includes/config.php';

if (!empty($_SESSION['user_id'])) {
    header('Location: ' . ($_SESSION['role'] === 'admin' ? BASE_URL . '/admin/dashboard.php' : BASE_URL . '/student/dashboard.php'));
    exit;
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? 'login';

    if ($action === 'login') {
        $email    = trim($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';

        $stmt = db()->prepare('SELECT id, name, password_hash, role FROM users WHERE email = ?');
        $stmt->execute([$email]);
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password_hash'])) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['name']    = $user['name'];
            $_SESSION['role']    = $user['role'];
            header('Location: ' . ($user['role'] === 'admin' ? BASE_URL . '/admin/dashboard.php' : BASE_URL . '/student/dashboard.php'));
            exit;
        }
        $error = 'Invalid email or password.';

    } elseif ($action === 'register') {
        $name     = trim($_POST['reg_name']  ?? '');
        $email    = trim($_POST['reg_email'] ?? '');
        $password = $_POST['reg_password']   ?? '';

        if (strlen($password) < 6) {
            $error = 'Password must be at least 6 characters.';
        } else {
            try {
                $stmt = db()->prepare('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, "student")');
                $stmt->execute([$name, $email, password_hash($password, PASSWORD_DEFAULT)]);
                $error = 'Account created! You can now log in.';
            } catch (PDOException $e) {
                $error = 'Email already registered.';
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login — ASAG System</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="<?= BASE_URL ?>/css/style.css">
</head>
<body>
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo">
      <span class="brand-icon">⬡</span>
      <h1>STUDENT ASSESSMENT</h1>
    </div>

    <?php if ($error): ?>
      <div class="alert <?= str_contains($error, 'created') ? 'alert-success' : 'alert-error' ?>">
        <?= htmlspecialchars($error) ?>
      </div>
    <?php endif; ?>

    <!-- TAB SWITCH -->
    <div style="display:flex;gap:0;margin-bottom:1.5rem;border:1.5px solid var(--gray-200);border-radius:var(--radius);overflow:hidden;">
      <button onclick="showTab('login')" id="tab-login"
        style="flex:1;padding:10px;border:none;background:var(--blue);color:var(--white);font-family:var(--font-body);font-weight:600;cursor:pointer;font-size:0.9rem;">
        Login
      </button>
      <button onclick="showTab('register')" id="tab-register"
        style="flex:1;padding:10px;border:none;background:var(--white);color:var(--gray-600);font-family:var(--font-body);font-weight:600;cursor:pointer;font-size:0.9rem;">
        Register
      </button>
    </div>

    <!-- LOGIN FORM -->
    <form id="form-login" method="POST">
      <input type="hidden" name="action" value="login">
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" name="email" required placeholder="you@university.edu">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="password" required placeholder="••••••••">
      </div>
      <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:0.5rem;">
        Sign In
      </button>
    </form>

    <!-- REGISTER FORM -->
    <form id="form-register" method="POST" style="display:none;">
      <input type="hidden" name="action" value="register">
      <div class="form-group">
        <label>Full Name</label>
        <input type="text" name="reg_name" required placeholder="Newton Kamau">
      </div>
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" name="reg_email" required placeholder="you@university.edu">
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="reg_password" required placeholder="Min 6 characters">
      </div>
      <button type="submit" class="btn btn-gold" style="width:100%;justify-content:center;margin-top:0.5rem;">
        Create Account
      </button>
    </form>
  </div>
</div>
<script>
function showTab(tab) {
  document.getElementById('form-login').style.display    = tab === 'login'    ? '' : 'none';
  document.getElementById('form-register').style.display = tab === 'register' ? '' : 'none';
  document.getElementById('tab-login').style.background    = tab === 'login'    ? 'var(--blue)'  : 'var(--white)';
  document.getElementById('tab-login').style.color         = tab === 'login'    ? 'var(--white)' : 'var(--gray-600)';
  document.getElementById('tab-register').style.background = tab === 'register' ? 'var(--blue)'  : 'var(--white)';
  document.getElementById('tab-register').style.color      = tab === 'register' ? 'var(--white)' : 'var(--gray-600)';
}
</script>
</body>
</html>

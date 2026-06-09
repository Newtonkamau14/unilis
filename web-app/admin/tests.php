<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('admin');
$page_title = 'Manage Tests';

$db  = db();
$msg = '';

// Create test
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'create_test') {
    $stmt = $db->prepare("INSERT INTO tests (subject_id, title, description, time_limit, created_by) VALUES (?,?,?,?,?)");
    $stmt->execute([
        $_POST['subject_id'],
        trim($_POST['title']),
        trim($_POST['description']),
        (int)$_POST['time_limit'],
        $_SESSION['user_id'],
    ]);
    $msg = 'Test created successfully.';
}

// Toggle active
if (isset($_GET['toggle'])) {
    $db->prepare("UPDATE tests SET is_active = 1 - is_active WHERE id = ?")->execute([(int)$_GET['toggle']]);
    header('Location: ' . BASE_URL . '/admin/tests.php');
    exit;
}

// Delete test
if (isset($_GET['delete'])) {
    $db->prepare("DELETE FROM tests WHERE id = ?")->execute([(int)$_GET['delete']]);
    header('Location: ' . BASE_URL . '/admin/tests.php');
    exit;
}

$tests    = $db->query("SELECT t.*, s.name AS subject_name,
    (SELECT COUNT(*) FROM questions q WHERE q.test_id = t.id) AS q_count
    FROM tests t JOIN subjects s ON s.id = t.subject_id
    ORDER BY t.created_at DESC")->fetchAll();
$subjects = $db->query("SELECT * FROM subjects ORDER BY name")->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">Manage <span>Tests</span></h1>
  </div>

  <?php if ($msg): ?>
    <div class="alert alert-success"><?= htmlspecialchars($msg) ?></div>
  <?php endif; ?>

  <div class="grid-2" style="align-items:start;">
    <!-- Create Test Form -->
    <div class="card">
      <div class="card-header">Create New Test</div>
      <form method="POST">
        <input type="hidden" name="action" value="create_test">
        <div class="form-group">
          <label>Subject</label>
          <select name="subject_id" required>
            <?php foreach ($subjects as $s): ?>
              <option value="<?= $s['id'] ?>"><?= htmlspecialchars($s['name']) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="form-group">
          <label>Test Title</label>
          <input type="text" name="title" required placeholder="e.g. TCP/IP Fundamentals Quiz">
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea name="description" placeholder="Optional description..."></textarea>
        </div>
        <div class="form-group">
          <label>Time Limit (minutes) — 0 for no limit</label>
          <input type="number" name="time_limit" value="30" min="0" max="180">
        </div>
        <button type="submit" class="btn btn-gold">Create Test</button>
      </form>
    </div>

    <!-- Tests List -->
    <div class="card">
      <div class="card-header">All Tests</div>
      <?php if (empty($tests)): ?>
        <p style="color:var(--gray-400);font-size:0.9rem;">No tests yet.</p>
      <?php else: ?>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Title</th><th>Subject</th><th>Qs</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
          <?php foreach ($tests as $t): ?>
          <tr>
            <td><strong><?= htmlspecialchars($t['title']) ?></strong></td>
            <td style="font-size:0.82rem"><?= htmlspecialchars($t['subject_name']) ?></td>
            <td><?= $t['q_count'] ?></td>
            <td><?= $t['time_limit'] ? $t['time_limit'].'m' : '∞' ?></td>
            <td>
              <span class="badge badge-<?= $t['is_active'] ? 'success' : 'danger' ?>">
                <?= $t['is_active'] ? 'Active' : 'Hidden' ?>
              </span>
            </td>
            <td style="display:flex;gap:6px;flex-wrap:wrap;">
              <a href="<?= BASE_URL ?>/admin/questions.php?test_id=<?= $t['id'] ?>" class="btn btn-primary btn-sm">Questions</a>
              <a href="?toggle=<?= $t['id'] ?>" class="btn btn-outline btn-sm"><?= $t['is_active'] ? 'Hide' : 'Show' ?></a>
              <a href="?delete=<?= $t['id'] ?>" class="btn btn-danger btn-sm" onclick="return confirm('Delete this test?')">Del</a>
            </td>
          </tr>
          <?php endforeach; ?>
          </tbody>
        </table>
      </div>
      <?php endif; ?>
    </div>
  </div>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

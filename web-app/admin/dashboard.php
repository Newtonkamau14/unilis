<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('admin');
$page_title = 'Admin Dashboard';

$db = db();
$total_students = $db->query("SELECT COUNT(*) FROM users WHERE role='student'")->fetchColumn();
$total_tests    = $db->query("SELECT COUNT(*) FROM tests")->fetchColumn();
$total_attempts = $db->query("SELECT COUNT(*) FROM test_attempts WHERE status='submitted'")->fetchColumn();
$avg_score      = $db->query("SELECT AVG(percentage) FROM student_marks")->fetchColumn();

$recent = $db->query("
    SELECT sm.*, u.name AS student_name, t.title AS test_title
    FROM student_marks sm
    JOIN users u ON u.id = sm.student_id
    JOIN tests t ON t.id = sm.test_id
    ORDER BY sm.submitted_at DESC LIMIT 10
")->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">Admin <span>Dashboard</span></h1>
    <a href="<?= BASE_URL ?>/admin/tests.php" class="btn btn-gold">+ New Test</a>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-value"><?= $total_students ?></div>
      <div class="stat-label">Students</div>
    </div>
    <div class="stat-card">
      <div class="stat-value"><?= $total_tests ?></div>
      <div class="stat-label">Tests</div>
    </div>
    <div class="stat-card">
      <div class="stat-value"><?= $total_attempts ?></div>
      <div class="stat-label">Submissions</div>
    </div>
    <div class="stat-card">
      <div class="stat-value"><?= $avg_score ? round($avg_score, 1) . '%' : 'N/A' ?></div>
      <div class="stat-label">Avg Score</div>
    </div>
  </div>

  <div class="card">
    <div class="card-header">Recent Submissions</div>
    <?php if (empty($recent)): ?>
      <p style="color:var(--gray-400);font-size:0.9rem;">No submissions yet.</p>
    <?php else: ?>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Student</th><th>Test</th><th>Score</th><th>Grade</th><th>Submitted</th><th></th>
          </tr>
        </thead>
        <tbody>
          <?php foreach ($recent as $r): ?>
          <tr>
            <td><?= htmlspecialchars($r['student_name']) ?></td>
            <td><?= htmlspecialchars($r['test_title']) ?></td>
            <td><?= $r['total_marks'] ?> / <?= $r['max_marks'] ?></td>
            <td><span class="badge badge-<?= $r['grade'] === 'A' ? 'success' : ($r['grade'] === 'F' ? 'danger' : 'warning') ?>">
              <?= $r['grade'] ?>
            </span></td>
            <td style="font-size:0.82rem;color:var(--gray-400)"><?= date('d M Y H:i', strtotime($r['submitted_at'])) ?></td>
            <td><a href="<?= BASE_URL ?>/admin/view_attempt.php?id=<?= $r['attempt_id'] ?>" class="btn btn-outline btn-sm">View</a></td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
    <?php endif; ?>
  </div>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

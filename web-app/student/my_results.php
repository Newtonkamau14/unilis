<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('student');
$page_title = 'My Results';

$student_id = $_SESSION['user_id'];
$results = db()->prepare("
    SELECT sm.*, t.title AS test_title, s.name AS subject_name
    FROM student_marks sm
    JOIN tests t ON t.id=sm.test_id
    JOIN subjects s ON s.id=t.subject_id
    WHERE sm.student_id=?
    ORDER BY sm.submitted_at DESC
");
$results->execute([$student_id]);
$results = $results->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">My <span>Results</span></h1>
  </div>

  <?php if (empty($results)): ?>
    <div class="card text-center">
      <p style="color:var(--gray-400);margin-bottom:1rem;">You haven't completed any tests yet.</p>
      <a href="<?= BASE_URL ?>/student/dashboard.php" class="btn btn-gold">Take a Test</a>
    </div>
  <?php else: ?>
  <div class="card">
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>Test</th><th>Subject</th><th>Score</th><th>%</th><th>Grade</th><th>Date</th><th></th></tr>
        </thead>
        <tbody>
          <?php foreach ($results as $r): ?>
          <tr>
            <td><strong><?= htmlspecialchars($r['test_title']) ?></strong></td>
            <td style="font-size:0.82rem"><?= htmlspecialchars($r['subject_name']) ?></td>
            <td><?= $r['total_marks'] ?> / <?= $r['max_marks'] ?></td>
            <td>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:60px;background:var(--gray-200);border-radius:4px;height:6px;">
                  <div style="width:<?= min(100,$r['percentage']) ?>%;background:var(--blue);height:6px;border-radius:4px;"></div>
                </div>
                <?= $r['percentage'] ?>%
              </div>
            </td>
            <td>
              <span class="badge badge-<?= $r['grade']==='A' ? 'success' : ($r['grade']==='F' ? 'danger' : 'warning') ?>">
                <?= $r['grade'] ?>
              </span>
            </td>
            <td style="font-size:0.82rem;color:var(--gray-400)"><?= date('d M Y', strtotime($r['submitted_at'])) ?></td>
            <td><a href="<?= BASE_URL ?>/student/results.php?attempt_id=<?= $r['attempt_id'] ?>" class="btn btn-outline btn-sm">View</a></td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  </div>
  <?php endif; ?>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('student');
$page_title = 'Student Dashboard';

$db         = db();
$student_id = $_SESSION['user_id'];

$tests = $db->query("SELECT t.*, s.name AS subject_name,
    (SELECT COUNT(*) FROM questions q WHERE q.test_id=t.id) AS q_count
    FROM tests t JOIN subjects s ON s.id=t.subject_id
    WHERE t.is_active=1 ORDER BY t.created_at DESC")->fetchAll();

$my_results = $db->prepare("SELECT sm.*, t.title AS test_title, s.name AS subject_name
    FROM student_marks sm
    JOIN tests t ON t.id=sm.test_id
    JOIN subjects s ON s.id=t.subject_id
    WHERE sm.student_id=?
    ORDER BY sm.submitted_at DESC LIMIT 5");
$my_results->execute([$student_id]);
$my_results = $my_results->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">Welcome, <span><?= htmlspecialchars($_SESSION['name']) ?></span></h1>
  </div>

  <div class="grid-2" style="align-items:start;">
    <!-- Available Tests -->
    <div>
      <h2 style="font-family:var(--font-display);color:var(--blue);margin-bottom:1rem;font-size:1.2rem;">
        Available Tests
      </h2>
      <?php if (empty($tests)): ?>
        <div class="card"><p style="color:var(--gray-400);">No tests available yet.</p></div>
      <?php else: ?>
        <?php foreach ($tests as $t): ?>
        <div class="card" style="margin-bottom:1rem;">
          <div class="flex-between mb-2">
            <span class="badge badge-blue"><?= htmlspecialchars($t['subject_name']) ?></span>
            <span style="font-size:0.8rem;color:var(--gray-400);">
              ⏱ <?= $t['time_limit'] ? $t['time_limit'].' min' : 'No limit' ?>
            </span>
          </div>
          <h3 style="font-size:1rem;margin-bottom:0.4rem;"><?= htmlspecialchars($t['title']) ?></h3>
          <?php if ($t['description']): ?>
            <p style="font-size:0.85rem;color:var(--gray-400);margin-bottom:0.75rem;">
              <?= htmlspecialchars($t['description']) ?>
            </p>
          <?php endif; ?>
          <div class="flex-between">
            <span style="font-size:0.82rem;color:var(--gray-400);"><?= $t['q_count'] ?> questions</span>
            <a href="<?= BASE_URL ?>/student/take_test.php?test_id=<?= $t['id'] ?>" class="btn btn-gold btn-sm">
              Start Test
            </a>
          </div>
        </div>
        <?php endforeach; ?>
      <?php endif; ?>
    </div>

    <!-- Recent Results -->
    <div>
      <h2 style="font-family:var(--font-display);color:var(--blue);margin-bottom:1rem;font-size:1.2rem;">
        Recent Results
      </h2>
      <?php if (empty($my_results)): ?>
        <div class="card"><p style="color:var(--gray-400);">No results yet. Take a test!</p></div>
      <?php else: ?>
        <?php foreach ($my_results as $r): ?>
        <div class="card" style="margin-bottom:1rem;">
          <div class="flex-between mb-2">
            <span class="badge badge-<?= $r['grade']==='A' ? 'success' : ($r['grade']==='F' ? 'danger' : 'warning') ?>">
              Grade <?= $r['grade'] ?>
            </span>
            <span style="font-size:0.82rem;color:var(--gray-400);">
              <?= date('d M Y', strtotime($r['submitted_at'])) ?>
            </span>
          </div>
          <h3 style="font-size:1rem;margin-bottom:0.4rem;"><?= htmlspecialchars($r['test_title']) ?></h3>
          <div class="flex-between mt-2">
            <span style="font-weight:700;color:var(--blue);">
              <?= $r['total_marks'] ?>/<?= $r['max_marks'] ?>
              <span style="font-size:0.85rem;color:var(--gold);">(<?= $r['percentage'] ?>%)</span>
            </span>
            <a href="<?= BASE_URL ?>/student/results.php?attempt_id=<?= $r['attempt_id'] ?>" class="btn btn-outline btn-sm">
              View Details
            </a>
          </div>
        </div>
        <?php endforeach; ?>
        <a href="<?= BASE_URL ?>/student/my_results.php" class="btn btn-primary btn-sm">View All Results →</a>
      <?php endif; ?>
    </div>
  </div>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('admin');

$attempt_id = (int)($_GET['id'] ?? 0);
$db = db();

$attempt = $db->prepare("
    SELECT ta.*, t.title, s.name AS subject_name, u.name AS student_name, u.email,
           sm.grade, sm.percentage, sm.total_marks, sm.max_marks
    FROM test_attempts ta
    JOIN tests t ON t.id=ta.test_id
    JOIN subjects s ON s.id=t.subject_id
    JOIN users u ON u.id=ta.student_id
    LEFT JOIN student_marks sm ON sm.attempt_id=ta.id
    WHERE ta.id=?
");
$attempt->execute([$attempt_id]);
$attempt = $attempt->fetch();
if (!$attempt) { header('Location: ' . BASE_URL . '/admin/dashboard.php'); exit; }

$answers = $db->prepare("
    SELECT sa.*, q.question_text, q.question_type, q.marks, q.reference_answer
    FROM student_answers sa
    JOIN questions q ON q.id=sa.question_id
    WHERE sa.attempt_id=?
    ORDER BY q.order_index
");
$answers->execute([$attempt_id]);
$answers = $answers->fetchAll();

$page_title = 'Attempt — ' . $attempt['student_name'];
include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">Attempt <span>Detail</span></h1>
    <a href="<?= BASE_URL ?>/admin/results.php" class="btn btn-outline btn-sm">← All Results</a>
  </div>

  <div class="grid-2 mb-2">
    <div class="card">
      <div class="card-header">Student</div>
      <p><strong><?= htmlspecialchars($attempt['student_name']) ?></strong></p>
      <p style="font-size:0.85rem;color:var(--gray-400)"><?= htmlspecialchars($attempt['email']) ?></p>
    </div>
    <div class="card">
      <div class="card-header">Score Summary</div>
      <p style="font-family:var(--font-display);font-size:2rem;color:var(--blue);">
        <?= $attempt['percentage'] ?>%
        <span class="badge badge-<?= $attempt['grade']==='A' ? 'success' : ($attempt['grade']==='F' ? 'danger' : 'warning') ?>" style="font-size:0.9rem;">
          Grade <?= $attempt['grade'] ?>
        </span>
      </p>
      <p style="font-size:0.85rem;color:var(--gray-400)"><?= $attempt['total_marks'] ?> / <?= $attempt['max_marks'] ?> marks</p>
    </div>
  </div>

  <?php foreach ($answers as $i => $a): ?>
  <div class="question-result">
    <div class="question-result-header">
      <strong>Q<?= $i+1 ?>: <?= htmlspecialchars(substr($a['question_text'],0,80)) ?>...</strong>
      <span style="font-weight:700;color:var(--blue)"><?= $a['marks_awarded'] ?>/<?= $a['marks'] ?> marks</span>
    </div>
    <div class="question-result-body">
      <div class="grid-2">
        <div>
          <div style="font-size:0.75rem;font-weight:600;color:var(--gray-400);margin-bottom:4px;text-transform:uppercase;">Student Answer</div>
          <div style="font-size:0.9rem;background:var(--off-white);padding:10px;border-radius:var(--radius);border-left:3px solid var(--blue);">
            <?= htmlspecialchars($a['student_answer_text']) ?>
          </div>
        </div>
        <div>
          <div style="font-size:0.75rem;font-weight:600;color:var(--gray-400);margin-bottom:4px;text-transform:uppercase;">Reference Answer</div>
          <div style="font-size:0.9rem;background:var(--off-white);padding:10px;border-radius:var(--radius);border-left:3px solid var(--gold);">
            <?= htmlspecialchars($a['reference_answer']) ?>
          </div>
        </div>
      </div>
      <?php if ($a['question_type']==='short_answer'): ?>
      <div class="score-bars" style="margin-top:1rem;">
        <div class="score-bar-row">
          <span class="score-bar-label">Semantic</span>
          <div class="score-bar-track"><div class="score-bar-fill fill-blue" style="width:<?= round($a['semantic_score']*100) ?>%"></div></div>
          <span class="score-bar-value"><?= round($a['semantic_score']*100) ?>%</span>
        </div>
        <div class="score-bar-row">
          <span class="score-bar-label">Terminology</span>
          <div class="score-bar-track"><div class="score-bar-fill fill-gold" style="width:<?= round($a['terminology_score']*100) ?>%"></div></div>
          <span class="score-bar-value"><?= round($a['terminology_score']*100) ?>%</span>
        </div>
      </div>
      <?php endif; ?>
      <?php if ($a['feedback']): ?>
        <div class="feedback-box"><?= htmlspecialchars($a['feedback']) ?></div>
      <?php endif; ?>
    </div>
  </div>
  <?php endforeach; ?>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

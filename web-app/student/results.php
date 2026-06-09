<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('student');

$attempt_id = (int)($_GET['attempt_id'] ?? 0);
$student_id = $_SESSION['user_id'];
$db         = db();

$attempt = $db->prepare("
    SELECT ta.*, t.title, t.time_limit, s.name AS subject_name, sm.grade, sm.percentage
    FROM test_attempts ta
    JOIN tests t ON t.id=ta.test_id
    JOIN subjects s ON s.id=t.subject_id
    LEFT JOIN student_marks sm ON sm.attempt_id=ta.id
    WHERE ta.id=? AND ta.student_id=?
");
$attempt->execute([$attempt_id, $student_id]);
$attempt = $attempt->fetch();
if (!$attempt) { header('Location: ' . BASE_URL . '/student/dashboard.php'); exit; }

$answers = $db->prepare("
    SELECT sa.*, q.question_text, q.question_type, q.marks, q.reference_answer
    FROM student_answers sa
    JOIN questions q ON q.id=sa.question_id
    WHERE sa.attempt_id=?
    ORDER BY q.order_index
");
$answers->execute([$attempt_id]);
$answers = $answers->fetchAll();

$page_title = 'Results — ' . $attempt['title'];
include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">Test <span>Results</span></h1>
    <a href="<?= BASE_URL ?>/student/dashboard.php" class="btn btn-outline btn-sm">← Dashboard</a>
  </div>

  <!-- Score Banner -->
  <div class="result-header">
    <p style="font-size:0.85rem;opacity:0.7;margin-bottom:0.5rem;"><?= htmlspecialchars($attempt['subject_name']) ?></p>
    <h2 style="font-family:var(--font-display);font-size:1.5rem;margin-bottom:1.5rem;">
      <?= htmlspecialchars($attempt['title']) ?>
    </h2>
    <div class="result-score"><?= $attempt['percentage'] ?>%</div>
    <div class="result-grade">Grade <?= $attempt['grade'] ?></div>
    <div style="margin-top:1.25rem;display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;font-size:0.85rem;opacity:0.8;">
      <span>📝 <?= count($answers) ?> Questions</span>
      <span>✅ Submitted <?= date('d M Y H:i', strtotime($attempt['submitted_at'])) ?></span>
      <?php if ($attempt['time_taken']): ?>
        <span>⏱ <?= floor($attempt['time_taken']/60) ?>m <?= $attempt['time_taken']%60 ?>s taken</span>
      <?php endif; ?>
      <?php if ($attempt['status'] === 'timed_out'): ?>
        <span style="color:var(--gold);">⚠ Auto-submitted (time expired)</span>
      <?php endif; ?>
    </div>
  </div>

  <!-- Per-question results -->
  <?php foreach ($answers as $i => $a): ?>
  <div class="question-result">
    <div class="question-result-header">
      <div>
        <span class="badge badge-<?= $a['question_type']==='short_answer' ? 'blue' : 'gold' ?>" style="margin-right:8px;">
          <?= $a['question_type']==='short_answer' ? 'Short Answer' : 'MCQ' ?>
        </span>
        <strong style="font-size:0.95rem;">Q<?= $i+1 ?>: <?= htmlspecialchars(substr($a['question_text'], 0, 80)) ?>...</strong>
      </div>
      <div style="text-align:right;">
        <span style="font-weight:700;color:var(--blue);font-size:1.1rem;">
          <?= $a['marks_awarded'] ?> / <?= $a['marks'] ?>
        </span>
        <span style="font-size:0.78rem;color:var(--gray-400);display:block;">marks</span>
      </div>
    </div>

    <div class="question-result-body">
      <div class="grid-2" style="gap:1rem;margin-bottom:1rem;">
        <div>
          <div style="font-size:0.75rem;font-weight:600;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Your Answer</div>
          <div style="font-size:0.92rem;background:var(--off-white);padding:10px 14px;border-radius:var(--radius);border-left:3px solid var(--blue);">
            <?= htmlspecialchars($a['student_answer_text']) ?>
          </div>
        </div>
        <div>
          <div style="font-size:0.75rem;font-weight:600;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Reference Answer</div>
          <div style="font-size:0.92rem;background:var(--off-white);padding:10px 14px;border-radius:var(--radius);border-left:3px solid var(--gold);">
            <?= htmlspecialchars($a['reference_answer']) ?>
          </div>
        </div>
      </div>

      <?php if ($a['question_type'] === 'short_answer'): ?>
      <!-- Score Bars -->
      <div class="score-bars">
        <div class="score-bar-row">
          <span class="score-bar-label">Semantic</span>
          <div class="score-bar-track">
            <div class="score-bar-fill fill-blue" style="width:<?= round($a['semantic_score']*100) ?>%"></div>
          </div>
          <span class="score-bar-value"><?= round($a['semantic_score']*100) ?>%</span>
        </div>
        <div class="score-bar-row">
          <span class="score-bar-label">Terminology</span>
          <div class="score-bar-track">
            <div class="score-bar-fill fill-gold" style="width:<?= round($a['terminology_score']*100) ?>%"></div>
          </div>
          <span class="score-bar-value"><?= round($a['terminology_score']*100) ?>%</span>
        </div>
        <div class="score-bar-row">
          <span class="score-bar-label">Final Score</span>
          <div class="score-bar-track">
            <div class="score-bar-fill fill-green" style="width:<?= round($a['final_score']*100) ?>%"></div>
          </div>
          <span class="score-bar-value"><?= round($a['final_score']*100) ?>%</span>
        </div>
      </div>
      <?php else: ?>
      <div style="margin:0.75rem 0;">
        <span class="badge badge-<?= $a['final_score'] >= 0.9 ? 'success' : 'danger' ?>" style="font-size:0.85rem;padding:5px 14px;">
          <?= $a['final_score'] >= 0.9 ? '✓ Correct' : '✗ Incorrect' ?>
        </span>
      </div>
      <?php endif; ?>

      <?php if ($a['feedback']): ?>
      <div class="feedback-box">
        <?= htmlspecialchars($a['feedback']) ?>
      </div>
      <?php endif; ?>
    </div>
  </div>
  <?php endforeach; ?>

  <div class="text-center mt-3">
    <a href="<?= BASE_URL ?>/student/dashboard.php" class="btn btn-primary">Back to Dashboard</a>
    <a href="<?= BASE_URL ?>/student/my_results.php" class="btn btn-outline" style="margin-left:1rem;">All My Results</a>
  </div>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>

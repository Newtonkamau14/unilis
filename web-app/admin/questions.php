<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('admin');

$test_id = (int)($_GET['test_id'] ?? 0);
$db = db();
$test = $db->prepare("SELECT t.*, s.name AS subject_name FROM tests t JOIN subjects s ON s.id=t.subject_id WHERE t.id=?");
$test->execute([$test_id]);
$test = $test->fetch();
if (!$test) { header('Location: ' . BASE_URL . '/admin/tests.php'); exit; }

$page_title = 'Questions — ' . $test['title'];
$msg = '';

// Add question
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'add_question') {
    $qtype  = $_POST['question_type'];
    $q_text = trim($_POST['question_text']);
    $ref    = trim($_POST['reference_answer']);
    $marks  = (float)$_POST['marks'];

    $stmt = $db->prepare("INSERT INTO questions (test_id, question_text, question_type, reference_answer, marks, order_index)
        VALUES (?,?,?,?,?, (SELECT COALESCE(MAX(order_index),0)+1 FROM questions q2 WHERE q2.test_id=?))");
    $stmt->execute([$test_id, $q_text, $qtype, $ref, $marks, $test_id]);
    $q_id = $db->lastInsertId();

    // Save MCQ options
    if ($qtype === 'multiple_choice') {
        $keys    = ['A','B','C','D'];
        $correct = $_POST['correct_option'] ?? 'A';
        foreach ($keys as $k) {
            $opt_text = trim($_POST['option_' . $k] ?? '');
            if ($opt_text) {
                $db->prepare("INSERT INTO question_options (question_id, option_key, option_text, is_correct) VALUES (?,?,?,?)")
                   ->execute([$q_id, $k, $opt_text, $k === $correct ? 1 : 0]);
            }
        }
    }
    $msg = 'Question added.';
}

// Delete question
if (isset($_GET['delete_q'])) {
    $db->prepare("DELETE FROM questions WHERE id=? AND test_id=?")->execute([(int)$_GET['delete_q'], $test_id]);
    header("Location: " . BASE_URL . "/admin/questions.php?test_id=$test_id");
    exit;
}

$questions = $db->prepare("SELECT q.*, GROUP_CONCAT(CONCAT(qo.option_key,'. ',qo.option_text) ORDER BY qo.option_key SEPARATOR ' | ') AS options
    FROM questions q
    LEFT JOIN question_options qo ON qo.question_id = q.id
    WHERE q.test_id = ?
    GROUP BY q.id ORDER BY q.order_index");
$questions->execute([$test_id]);
$questions = $questions->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">
      Questions — <span><?= htmlspecialchars($test['title']) ?></span>
    </h1>
    <a href="<?= BASE_URL ?>/admin/tests.php" class="btn btn-outline btn-sm">← Back to Tests</a>
  </div>

  <?php if ($msg): ?>
    <div class="alert alert-success"><?= htmlspecialchars($msg) ?></div>
  <?php endif; ?>

  <div class="grid-2" style="align-items:start;">
    <!-- Add Question Form -->
    <div class="card">
      <div class="card-header">Add Question</div>
      <form method="POST" id="q-form">
        <input type="hidden" name="action" value="add_question">

        <div class="form-group">
          <label>Question Type</label>
          <select name="question_type" id="q-type" onchange="toggleMCQ(this.value)" required>
            <option value="short_answer">Short Answer</option>
            <option value="multiple_choice">Multiple Choice (MCQ)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Question Text</label>
          <textarea name="question_text" required placeholder="Enter the question..."></textarea>
        </div>

        <div class="form-group">
          <label>Reference / Model Answer</label>
          <textarea name="reference_answer" required placeholder="The correct/expected answer used for grading..."></textarea>
        </div>

        <!-- MCQ Options (shown only for MCQ) -->
        <div id="mcq-section" style="display:none;">
          <div class="card-header" style="font-size:0.9rem;margin-bottom:1rem;">MCQ Options</div>
          <?php foreach (['A','B','C','D'] as $k): ?>
          <div class="form-group">
            <label>Option <?= $k ?></label>
            <input type="text" name="option_<?= $k ?>" placeholder="Option <?= $k ?> text">
          </div>
          <?php endforeach; ?>
          <div class="form-group">
            <label>Correct Option</label>
            <select name="correct_option">
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Marks</label>
          <input type="number" name="marks" value="1" min="0.5" max="100" step="0.5">
        </div>

        <button type="submit" class="btn btn-gold">Add Question</button>
      </form>
    </div>

    <!-- Questions List -->
    <div class="card">
      <div class="card-header">
        Questions (<?= count($questions) ?>)
        <span style="font-size:0.8rem;color:var(--gray-400);font-weight:400;margin-left:auto;">
          Time limit: <?= $test['time_limit'] ? $test['time_limit'].'m' : 'No limit' ?>
        </span>
      </div>

      <?php if (empty($questions)): ?>
        <p style="color:var(--gray-400);font-size:0.9rem;">No questions yet.</p>
      <?php else: ?>
        <?php foreach ($questions as $i => $q): ?>
        <div style="border:1px solid var(--gray-200);border-radius:var(--radius);padding:1rem;margin-bottom:0.75rem;">
          <div class="flex-between mb-2">
            <span class="badge badge-<?= $q['question_type'] === 'short_answer' ? 'blue' : 'gold' ?>">
              <?= $q['question_type'] === 'short_answer' ? 'Short Answer' : 'MCQ' ?>
            </span>
            <span style="font-size:0.8rem;color:var(--gray-400);"><?= $q['marks'] ?> mark<?= $q['marks'] != 1 ? 's' : '' ?></span>
          </div>
          <p style="font-size:0.9rem;margin-bottom:0.5rem;"><strong>Q<?= $i+1 ?>:</strong> <?= htmlspecialchars($q['question_text']) ?></p>
          <?php if ($q['options']): ?>
            <p style="font-size:0.78rem;color:var(--gray-400);"><?= htmlspecialchars($q['options']) ?></p>
          <?php endif; ?>
          <div class="flex-between mt-2">
            <span style="font-size:0.78rem;color:var(--gray-400);">
              Ref: <?= htmlspecialchars(substr($q['reference_answer'], 0, 60)) ?>...
            </span>
            <a href="?test_id=<?= $test_id ?>&delete_q=<?= $q['id'] ?>" class="btn btn-danger btn-sm"
               onclick="return confirm('Delete this question?')">Delete</a>
          </div>
        </div>
        <?php endforeach; ?>
      <?php endif; ?>
    </div>
  </div>
</div>

<script>
function toggleMCQ(type) {
  document.getElementById('mcq-section').style.display = type === 'multiple_choice' ? '' : 'none';
}
</script>
<?php include __DIR__ . '/../includes/footer.php'; ?>

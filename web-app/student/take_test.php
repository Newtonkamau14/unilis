<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('student');

$test_id    = (int)($_GET['test_id'] ?? 0);
$student_id = $_SESSION['user_id'];
$db         = db();

$test = $db->prepare("SELECT * FROM tests WHERE id=? AND is_active=1");
$test->execute([$test_id]);
$test = $test->fetch();
if (!$test) { header('Location: ' . BASE_URL . '/student/dashboard.php'); exit; }

// Check for existing in-progress attempt
$attempt = $db->prepare("SELECT * FROM test_attempts WHERE test_id=? AND student_id=? AND status='in_progress'");
$attempt->execute([$test_id, $student_id]);
$attempt = $attempt->fetch();

if (!$attempt) {
    $db->prepare("INSERT INTO test_attempts (test_id, student_id) VALUES (?,?)")->execute([$test_id, $student_id]);
    $attempt_id = $db->lastInsertId();
    $attempt    = $db->prepare("SELECT * FROM test_attempts WHERE id=?")->execute([$attempt_id]) ? $db->query("SELECT * FROM test_attempts WHERE id=$attempt_id")->fetch() : null;
}

$attempt_id = $attempt['id'];
$started_at = strtotime($attempt['started_at']);
$time_limit = (int)$test['time_limit'];
$time_remaining = $time_limit > 0 ? max(0, ($time_limit * 60) - (time() - $started_at)) : null;

// Auto-submit if timed out
if ($time_limit > 0 && $time_remaining === 0) {
    header("Location: " . BASE_URL . "/student/submit_test.php?attempt_id=$attempt_id&timeout=1");
    exit;
}

// Load questions with options
$questions = $db->prepare("
    SELECT q.*, GROUP_CONCAT(CONCAT(qo.option_key,'|||',qo.option_text) ORDER BY qo.option_key SEPARATOR '~~~') AS options_raw
    FROM questions q
    LEFT JOIN question_options qo ON qo.question_id=q.id
    WHERE q.test_id=?
    GROUP BY q.id ORDER BY q.order_index
");
$questions->execute([$test_id]);
$questions = $questions->fetchAll();

$page_title = $test['title'];
include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <!-- Quiz Header with Timer -->
  <div class="quiz-header">
    <div>
      <div class="quiz-title"><?= htmlspecialchars($test['title']) ?></div>
      <div style="font-size:0.82rem;opacity:0.7;margin-top:4px;">
        <?= count($questions) ?> questions <?= $time_limit ? '· '.$time_limit.' minutes' : '· No time limit' ?>
      </div>
    </div>
    <?php if ($time_limit): ?>
    <div class="timer-box" id="timer">00:00</div>
    <?php endif; ?>
  </div>

  <form method="POST" action="<?= BASE_URL ?>/student/submit_test.php" id="test-form">
    <input type="hidden" name="attempt_id" value="<?= $attempt_id ?>">

    <!-- Progress -->
    <div class="progress-wrap">
      <span id="progress-label">0 / <?= count($questions) ?> answered</span>
      <div class="progress-track">
        <div class="progress-fill" id="progress-fill" style="width:0%"></div>
      </div>
    </div>

    <?php foreach ($questions as $i => $q): ?>
    <?php
      $opts = [];
      if ($q['options_raw']) {
          foreach (explode('~~~', $q['options_raw']) as $opt) {
              [$k, $v] = explode('|||', $opt, 2);
              $opts[$k] = $v;
          }
      }
    ?>
    <div class="question-card" id="qcard-<?= $i ?>">
      <div class="question-number">Question <?= $i+1 ?> of <?= count($questions) ?></div>
      <div class="question-text"><?= htmlspecialchars($q['question_text']) ?></div>

      <?php if ($q['question_type'] === 'multiple_choice'): ?>
        <div class="mcq-options" id="opts-<?= $q['id'] ?>">
          <?php foreach ($opts as $k => $v): ?>
          <label class="mcq-option" id="opt-<?= $q['id'] ?>-<?= $k ?>" onclick="selectOpt(<?= $q['id'] ?>, '<?= $k ?>')">
            <input type="radio" name="answer[<?= $q['id'] ?>]" value="<?= $k ?>"
                   onchange="updateProgress()" required>
            <span style="font-weight:600;color:var(--gold);min-width:20px;"><?= $k ?>.</span>
            <span><?= htmlspecialchars($v) ?></span>
          </label>
          <?php endforeach; ?>
        </div>
      <?php else: ?>
        <textarea name="answer[<?= $q['id'] ?>]"
                  placeholder="Type your answer here..."
                  rows="4"
                  onkeyup="updateProgress()"
                  required></textarea>
      <?php endif; ?>
    </div>
    <?php endforeach; ?>

    <div style="text-align:right;margin-top:2rem;">
      <button type="submit" class="btn btn-gold" style="font-size:1rem;padding:12px 32px;"
              onclick="return confirm('Submit your test? You cannot change answers after this.')">
        Submit Test ✓
      </button>
    </div>
  </form>
</div>

<script>
// Timer
<?php if ($time_limit): ?>
let seconds = <?= $time_remaining ?>;
const timerEl = document.getElementById('timer');

function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
}

function tick() {
  if (seconds <= 0) {
    timerEl.textContent = '00:00';
    document.getElementById('test-form').submit();
    return;
  }
  timerEl.textContent = formatTime(seconds);
  if (seconds <= 60)       timerEl.className = 'timer-box danger';
  else if (seconds <= 300) timerEl.className = 'timer-box warning';
  seconds--;
  setTimeout(tick, 1000);
}
tick();
<?php endif; ?>

// Progress bar
function updateProgress() {
  const total   = <?= count($questions) ?>;
  let answered  = 0;
  document.querySelectorAll('.question-card').forEach(card => {
    const inputs = card.querySelectorAll('input[type=radio]:checked, textarea');
    inputs.forEach(inp => {
      if ((inp.tagName === 'TEXTAREA' && inp.value.trim()) ||
          (inp.tagName === 'INPUT'    && inp.checked)) answered++;
    });
  });
  document.getElementById('progress-label').textContent = answered + ' / ' + total + ' answered';
  document.getElementById('progress-fill').style.width = (answered / total * 100) + '%';
}

// MCQ highlight
function selectOpt(qid, key) {
  document.querySelectorAll('#opts-' + qid + ' .mcq-option').forEach(el => el.classList.remove('selected'));
  document.getElementById('opt-' + qid + '-' + key).classList.add('selected');
  updateProgress();
}
</script>
<?php include __DIR__ . '/../includes/footer.php'; ?>

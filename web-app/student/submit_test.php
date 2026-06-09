<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('student');

$attempt_id = (int)($_POST['attempt_id'] ?? $_GET['attempt_id'] ?? 0);
$student_id = $_SESSION['user_id'];
$db         = db();

$attempt = $db->prepare("SELECT ta.*, t.time_limit FROM test_attempts ta JOIN tests t ON t.id=ta.test_id WHERE ta.id=? AND ta.student_id=?");
$attempt->execute([$attempt_id, $student_id]);
$attempt = $attempt->fetch();
if (!$attempt || $attempt['status'] !== 'in_progress') {
    header('Location: ' . BASE_URL . '/student/dashboard.php');
    exit;
}

$test_id    = $attempt['test_id'];
$answers    = $_POST['answer'] ?? [];
$time_taken = time() - strtotime($attempt['started_at']);

// Load questions
$questions = $db->prepare("
    SELECT q.*, GROUP_CONCAT(CONCAT(qo.option_key,'|||',qo.option_text,'|||',qo.is_correct) ORDER BY qo.option_key SEPARATOR '~~~') AS opts
    FROM questions q
    LEFT JOIN question_options qo ON qo.question_id=q.id
    WHERE q.test_id=?
    GROUP BY q.id ORDER BY q.order_index
");
$questions->execute([$test_id]);
$questions = $questions->fetchAll();

// Load test info
$test = $db->prepare("SELECT t.*, s.name AS subject_name FROM tests t JOIN subjects s ON s.id=t.subject_id WHERE t.id=?")->execute([$test_id]) ? $db->query("SELECT * FROM tests WHERE id=$test_id")->fetch() : null;

$total_marks = 0;
$max_marks   = 0;
$insert_ans  = $db->prepare("INSERT INTO student_answers
    (attempt_id, question_id, student_answer_text, semantic_score, terminology_score, final_score, marks_awarded, feedback, graded_at)
    VALUES (?,?,?,?,?,?,?,?,NOW())");

foreach ($questions as $q) {
    $q_id   = $q['id'];
    $marks  = (float)$q['marks'];
    $max_marks += $marks;
    $student_answer = trim($answers[$q_id] ?? '');
    if (!$student_answer) $student_answer = '[No answer provided]';

    // Parse MCQ options
    $mcq_opts     = [];
    $correct_key  = '';
    if ($q['opts']) {
        foreach (explode('~~~', $q['opts']) as $o) {
            [$k, $v, $is_correct] = explode('|||', $o, 3);
            $mcq_opts[] = "$k. $v";
            if ($is_correct) $correct_key = $k;
        }
    }

    // Grade via ASAG API
    $ref = $q['question_type'] === 'multiple_choice' ? $correct_key : $q['reference_answer'];
    $result = grade_via_api(
        $q['question_text'],
        $ref,
        $student_answer,
        $q['question_type'],
        $mcq_opts
    );

    $final_score      = (float)($result['final_weighted_score'] ?? 0);
    $semantic_score   = (float)($result['semantic_score']['score'] ?? 0);
    $terminology_score= (float)($result['terminology_score']['score'] ?? 0);
    $feedback         = $result['feedback_report'] ?? '';
    $marks_awarded    = round($final_score * $marks, 2);
    $total_marks     += $marks_awarded;

    $insert_ans->execute([
        $attempt_id, $q_id, $student_answer,
        $semantic_score, $terminology_score, $final_score,
        $marks_awarded, $feedback
    ]);
}

$percentage = $max_marks > 0 ? round(($total_marks / $max_marks) * 100, 2) : 0;
$grade      = grade_label($percentage);
$status     = isset($_GET['timeout']) ? 'timed_out' : 'submitted';

// Update attempt
$db->prepare("UPDATE test_attempts SET status=?, submitted_at=NOW(), time_taken=?, total_score=?, max_score=?, percentage=? WHERE id=?")
   ->execute([$status, $time_taken, $total_marks, $max_marks, $percentage, $attempt_id]);

// Insert summary
$db->prepare("INSERT INTO student_marks (student_id, test_id, attempt_id, total_marks, max_marks, percentage, grade, submitted_at)
    VALUES (?,?,?,?,?,?,?,NOW())")
   ->execute([$student_id, $test_id, $attempt_id, $total_marks, $max_marks, $percentage, $grade]);

header("Location: " . BASE_URL . "/student/results.php?attempt_id=$attempt_id");
exit;

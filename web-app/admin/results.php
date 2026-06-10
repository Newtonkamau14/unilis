<?php
require_once __DIR__ . '/../includes/config.php';
auth_required('admin');
$page_title = 'All Results';

$db      = db();
$results = $db->query("
    SELECT sm.*, u.name AS student_name, t.title AS test_title, s.name AS subject_name
    FROM student_marks sm
    JOIN users u ON u.id = sm.student_id
    JOIN tests t ON t.id = sm.test_id
    JOIN subjects s ON s.id = t.subject_id
    ORDER BY sm.submitted_at DESC
")->fetchAll();

include __DIR__ . '/../includes/header.php';
?>
<div class="container">
  <div class="page-header">
    <h1 class="page-title">All <span>Results</span></h1>
  </div>
  <div class="card">
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Student</th><th>Test</th><th>Subject</th>
            <th>Score</th><th>%</th><th>Grade</th><th>Date</th><th></th>
          </tr>
        </thead>
        <tbody>
          <?php foreach ($results as $r): ?>
          <tr>
            <td><?= htmlspecialchars($r['student_name']) ?></td>
            <td><?= htmlspecialchars($r['test_title']) ?></td>
            <td style="font-size:0.82rem"><?= htmlspecialchars($r['subject_name']) ?></td>
            <td><?= $r['total_marks'] ?> / <?= $r['max_marks'] ?></td>
            <td>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:50px;background:var(--gray-200);border-radius:4px;height:6px;">
                  <div style="width:<?= min(100,$r['percentage']) ?>%;background:var(--blue);height:6px;border-radius:4px;"></div>
                </div>
                <?= $r['percentage'] ?>%
              </div>
            </td>
            <td>
              <span class="badge badge-<?= $r['grade']==='A'?'success':($r['grade']==='F'?'danger':'warning') ?>">
                <?= $r['grade'] ?>
              </span>
            </td>
            <td style="font-size:0.82rem;color:var(--gray-400)">
              <?= date('d M Y H:i', strtotime($r['submitted_at'])) ?>
            </td>
            <td>
              <a href="<?= BASE_URL ?>/admin/view_attempt.php?id=<?= $r['attempt_id'] ?>"
                 class="btn btn-outline btn-sm">View</a>
            </td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  </div>
</div>
<?php include __DIR__ . '/../includes/footer.php'; ?>
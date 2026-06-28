<?php

declare(strict_types=1);

$root = __DIR__;
$python = $root . DIRECTORY_SEPARATOR . '.venv' . DIRECTORY_SEPARATOR . 'Scripts' . DIRECTORY_SEPARATOR . 'python.exe';
$serverScript = $root . DIRECTORY_SEPARATOR . 'scripts' . DIRECTORY_SEPARATOR . 'predict_server.py';
$model = 'models/literary_parsbert_light.joblib';
$host = '127.0.0.1';
$port = 8765;
$serverUrl = "http://{$host}:{$port}";

function service_is_ready(string $url): bool
{
    $context = stream_context_create(['http' => ['timeout' => 0.3]]);
    $response = @file_get_contents($url . '/health', false, $context);
    return is_string($response) && strpos($response, '"ready": true') !== false;
}

if (!service_is_ready($serverUrl) && file_exists($serverScript)) {
    $pythonCommand = file_exists($python) ? $python : 'python';
    $command = 'start /B "" '
        . escapeshellarg($pythonCommand) . ' '
        . escapeshellarg($serverScript)
        . ' --host ' . escapeshellarg($host)
        . ' --port ' . escapeshellarg((string)$port)
        . ' --model ' . escapeshellarg($model)
        . ' > NUL 2>&1';
    @pclose(@popen($command, 'r'));
}
?>
<!doctype html>
<html lang="fa" dir="rtl">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>سامانه سنجش سبک ادبی جمله فارسی</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
        :root {
            --bg: #f6f7f9;
            --surface: #ffffff;
            --surface-soft: #f9fafb;
            --text: #172026;
            --muted: #66707a;
            --line: #dde3ea;
            --primary: #27695f;
            --primary-hover: #1f5a51;
            --primary-soft: #e5f2ef;
            --danger: #b3261e;
            --shadow: 0 14px 34px rgba(22, 32, 38, 0.08);
            --radius: 8px;
            --font: Vazirmatn, Tahoma, Arial, sans-serif;
        }

        * {
            box-sizing: border-box;
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            line-height: 1.9;
            margin: 0;
        }

        button,
        input {
            font-family: var(--font);
        }

        .app-shell {
            direction: ltr;
            display: grid;
            grid-template-columns: 300px minmax(0, 1fr);
            min-height: 100vh;
        }

        .history-panel {
            background: var(--surface);
            border-right: 1px solid var(--line);
            direction: rtl;
            padding: 22px 16px;
        }

        .content {
            direction: rtl;
            margin: 0 auto;
            max-width: 920px;
            padding: 34px 20px 60px;
            width: 100%;
        }

        .brand {
            align-items: center;
            display: flex;
            gap: 10px;
            margin-bottom: 22px;
        }

        .brand-icon {
            align-items: center;
            background: var(--primary-soft);
            border-radius: var(--radius);
            color: var(--primary);
            display: inline-flex;
            height: 42px;
            justify-content: center;
            width: 42px;
        }

        h1,
        h2,
        p {
            margin-top: 0;
        }

        h1 {
            font-size: 28px;
            font-weight: 800;
            line-height: 1.45;
            margin-bottom: 6px;
        }

        h2 {
            font-size: 17px;
            font-weight: 800;
            margin-bottom: 0;
        }

        .muted {
            color: var(--muted);
            font-size: 14px;
            margin-bottom: 0;
        }

        .page-head {
            align-items: flex-start;
            display: flex;
            gap: 18px;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .status-pill {
            align-items: center;
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 999px;
            color: var(--muted);
            display: inline-flex;
            flex: 0 0 auto;
            font-size: 13px;
            gap: 6px;
            min-height: 36px;
            padding: 0 12px;
        }

        .panel,
        .result-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }

        .panel {
            padding: 18px;
        }

        label {
            color: var(--text);
            display: block;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .input-head {
            align-items: center;
            display: flex;
            gap: 12px;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .input-head label {
            margin-bottom: 0;
        }

        .sentence-list {
            display: grid;
            gap: 10px;
        }

        .sentence-row {
            align-items: center;
            display: grid;
            gap: 8px;
            grid-template-columns: minmax(0, 1fr) 42px;
        }

        .sentence-input {
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            color: var(--text);
            direction: rtl;
            font-size: 15px;
            min-height: 46px;
            padding: 0 14px;
            width: 100%;
        }

        .sentence-input:focus {
            background: #ffffff;
            border-color: var(--primary);
            outline: 3px solid rgba(39, 105, 95, 0.16);
        }

        .icon-btn {
            align-items: center;
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            color: var(--muted);
            cursor: pointer;
            display: inline-flex;
            height: 42px;
            justify-content: center;
            width: 42px;
        }

        .icon-btn:hover {
            background: var(--surface-soft);
            color: var(--text);
        }

        .icon-btn:disabled {
            cursor: not-allowed;
            opacity: 0.35;
        }

        .icon-btn.add {
            background: var(--primary-soft);
            border-color: transparent;
            color: var(--primary);
        }

        .icon-btn.add:hover {
            background: #d8ece7;
        }

        .actions {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: space-between;
            margin-top: 14px;
        }

        .btn {
            align-items: center;
            border: 1px solid transparent;
            border-radius: var(--radius);
            cursor: pointer;
            display: inline-flex;
            font-size: 14px;
            font-weight: 700;
            gap: 8px;
            justify-content: center;
            min-height: 44px;
            padding: 0 16px;
            transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
        }

        .btn:disabled {
            cursor: wait;
            opacity: 0.7;
        }

        .btn-primary {
            background: var(--primary);
            color: #ffffff;
        }

        .btn-primary:hover:not(:disabled) {
            background: var(--primary-hover);
            transform: translateY(-1px);
        }

        .btn-ghost {
            background: #ffffff;
            border-color: var(--line);
            color: var(--muted);
            min-height: 36px;
            padding: 0 10px;
        }

        .btn-ghost:hover {
            background: var(--surface-soft);
            color: var(--text);
        }

        .material-symbols-outlined {
            font-size: 20px;
            line-height: 1;
        }

        .progress-wrap {
            background: var(--surface-soft);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            display: none;
            margin-top: 14px;
            padding: 12px;
        }

        .progress-wrap.active {
            display: block;
        }

        .progress-row {
            align-items: center;
            color: var(--muted);
            display: flex;
            font-size: 13px;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .progress-track {
            background: #e8edf1;
            border-radius: 999px;
            height: 8px;
            overflow: hidden;
        }

        .progress-fill {
            background: var(--primary);
            border-radius: inherit;
            height: 100%;
            transition: width 0.25s ease;
            width: 0%;
        }

        .error {
            background: #fff7f6;
            border: 1px solid #f0c7c3;
            border-radius: var(--radius);
            color: var(--danger);
            display: none;
            margin-top: 12px;
            padding: 12px;
            white-space: pre-wrap;
        }

        .error.active {
            display: block;
        }

        .results {
            margin-top: 18px;
        }

        .result-card {
            box-shadow: none;
            margin-top: 12px;
            padding: 16px;
        }

        .meta {
            align-items: center;
            color: var(--muted);
            display: flex;
            flex-wrap: wrap;
            font-size: 13px;
            gap: 8px 12px;
        }

        .score {
            background: var(--primary-soft);
            border-radius: 999px;
            color: var(--primary);
            display: inline-block;
            font-weight: 800;
            min-width: 68px;
            padding: 1px 10px;
            text-align: center;
        }

        .sentence {
            color: var(--text);
            font-size: 18px;
            font-weight: 600;
            margin: 12px 0 8px;
        }

        .explanation {
            color: var(--muted);
            font-size: 14px;
            margin: 0;
        }

        .history-title {
            align-items: center;
            display: flex;
            gap: 8px;
            justify-content: space-between;
            margin-bottom: 14px;
        }

        .history-list {
            display: grid;
            gap: 8px;
        }

        .history-item {
            background: var(--surface-soft);
            border: 1px solid transparent;
            border-radius: var(--radius);
            color: var(--text);
            cursor: pointer;
            padding: 11px 12px;
            text-align: right;
            width: 100%;
        }

        .history-item:hover {
            background: #ffffff;
            border-color: var(--line);
        }

        .history-item strong {
            display: block;
            font-size: 13px;
            font-weight: 700;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .history-item span {
            color: var(--muted);
            display: block;
            font-size: 12px;
            margin-top: 4px;
        }

        .empty-history {
            background: var(--surface-soft);
            border: 1px dashed var(--line);
            border-radius: var(--radius);
            color: var(--muted);
            font-size: 13px;
            margin: 0;
            padding: 12px;
        }

        @media (max-width: 820px) {
            .app-shell {
                display: block;
            }

            .history-panel {
                border-bottom: 1px solid var(--line);
                border-right: 0;
            }

            .content {
                padding-top: 24px;
            }

            .page-head {
                display: block;
            }

            .status-pill {
                margin-top: 12px;
            }
        }
    </style>
</head>

<body>
    <div class="app-shell">
        <aside class="history-panel">
            <div class="brand">
                <span class="brand-icon material-symbols-outlined">history</span>
                <div>
                    <h2>تاریخچه</h2>
                    <p class="muted">سوابق تحلیل‌های پیشین</p>
                </div>
            </div>
            <div class="history-title">
                <span class="muted">نمونه‌های ذخیره‌شده</span>
                <button class="btn btn-ghost" id="clearHistory" type="button">
                    <span class="material-symbols-outlined">delete</span>
                    پاک کردن
                </button>
            </div>
            <div class="history-list" id="historyList"></div>
        </aside>

        <main class="content">
            <header class="page-head">
                <div>
                    <h1>سامانه سنجش سبک ادبی جمله فارسی</h1>
                    <p class="muted">این سامانه با استفاده از بازنمایی‌های زبانی ParsBERT، میزان ادبی بودن هر جمله را در بازه ۱ تا ۱۰ برآورد می‌کند.</p>
                </div>
                <div class="status-pill">
                    <span class="material-symbols-outlined">bolt</span>
                    <span id="statusText">آماده پردازش</span>
                </div>
            </header>

            <section class="panel">
                <div class="input-head">
                    <label>جمله‌های مورد ارزیابی</label>
                    <button class="icon-btn add" id="addSentence" type="button" title="افزودن جمله">
                        <span class="material-symbols-outlined">add</span>
                    </button>
                </div>
                <div class="sentence-list" id="sentenceList"></div>
                <div class="actions">
                    <button class="btn btn-primary" id="predictButton" type="button">
                        <span class="material-symbols-outlined">psychology</span>
                        اجرای تحلیل
                    </button>
                    <span class="muted">هر ورودی معادل یک جمله مستقل برای تحلیل است.</span>
                </div>
                <div class="progress-wrap" id="progressWrap">
                    <div class="progress-row">
                        <span id="progressLabel">در حال آماده‌سازی مؤلفه‌های مدل...</span>
                        <b id="progressPercent">0%</b>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
                <div class="error" id="errorBox"></div>
            </section>

            <section class="results" id="results"></section>
        </main>
    </div>

    <script>
        const API_BASE = <?= json_encode($serverUrl, JSON_UNESCAPED_SLASHES) ?>;
        const STORAGE_KEY = 'persian_literary_history_v3';

        const sentenceList = document.getElementById('sentenceList');
        const addSentence = document.getElementById('addSentence');
        const predictButton = document.getElementById('predictButton');
        const resultsEl = document.getElementById('results');
        const historyList = document.getElementById('historyList');
        const clearHistory = document.getElementById('clearHistory');
        const errorBox = document.getElementById('errorBox');
        const statusText = document.getElementById('statusText');
        const progressWrap = document.getElementById('progressWrap');
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressLabel = document.getElementById('progressLabel');

        let progressTimer = null;
        let currentProgress = 0;

        function escapeHtml(value) {
            return String(value ?? '').replace(/[&<>"']/g, char => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            } [char]));
        }

        function setProgress(value, label) {
            const target = Math.max(0, Math.min(100, Math.round(value)));
            const percent = Math.max(currentProgress, target);
            currentProgress = percent;
            progressFill.style.width = `${percent}%`;
            progressPercent.textContent = `${percent}%`;
            progressLabel.textContent = label;
        }

        function startProgress() {
            clearInterval(progressTimer);
            currentProgress = 0;
            progressFill.style.transition = 'none';
            progressFill.style.width = '0%';
            progressPercent.textContent = '0%';
            progressFill.offsetHeight;
            progressFill.style.transition = 'width 0.25s ease';
            progressWrap.classList.add('active');
            setProgress(4, 'در حال آماده‌سازی مؤلفه‌های مدل...');
            let value = 4;
            progressTimer = setInterval(() => {
                value = Math.max(value, currentProgress);
                value += value < 55 ? 4 : value < 85 ? 2 : 0.5;
                setProgress(Math.min(value, 92), value < 65 ? 'در حال آماده‌سازی مؤلفه‌های مدل...' : 'در حال محاسبه بازنمایی زبانی...');
            }, 650);
        }

        function finishProgress() {
            clearInterval(progressTimer);
            setProgress(100, 'کامل شد');
            setTimeout(() => progressWrap.classList.remove('active'), 750);
        }

        function showError(message) {
            errorBox.textContent = message;
            errorBox.classList.add('active');
        }

        function clearError() {
            errorBox.textContent = '';
            errorBox.classList.remove('active');
        }

        function addSentenceInput(value = '') {
            const row = document.createElement('div');
            row.className = 'sentence-row';
            row.innerHTML = `
        <input class="sentence-input" type="text" value="${escapeHtml(value)}" placeholder="جمله فارسی مورد ارزیابی را وارد کنید">
        <button class="icon-btn remove-sentence" type="button" title="حذف جمله">
            <span class="material-symbols-outlined">close</span>
        </button>
    `;
            sentenceList.appendChild(row);
            updateRemoveButtons();
            row.querySelector('input').focus();
        }

        function updateRemoveButtons() {
            const buttons = sentenceList.querySelectorAll('.remove-sentence');
            buttons.forEach(button => {
                button.disabled = buttons.length <= 1;
            });
        }

        function getSentenceValues() {
            return [...sentenceList.querySelectorAll('.sentence-input')]
                .map(input => input.value.trim())
                .filter(Boolean);
        }

        function setSentenceInputs(text) {
            const values = String(text || '')
                .split('\n')
                .map(item => item.trim())
                .filter(Boolean);
            sentenceList.innerHTML = '';
            (values.length ? values : ['']).forEach(value => addSentenceInput(value));
            updateRemoveButtons();
        }

        function getHistory() {
            try {
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            } catch {
                return [];
            }
        }

        function saveHistory(text, results) {
            const history = getHistory();
            history.unshift({
                id: Date.now(),
                text,
                results,
                createdAt: new Date().toLocaleString('fa-IR')
            });
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, 20)));
            renderHistory();
        }

        function renderHistory() {
            const history = getHistory();
            if (!history.length) {
                historyList.innerHTML = '<p class="empty-history">هنوز سابقه تحلیلی ثبت نشده است.</p>';
                return;
            }

            historyList.innerHTML = history.map(item => `
        <button class="history-item" type="button" data-id="${item.id}">
            <strong>${escapeHtml(item.text.split('\n')[0])}</strong>
            <span>${escapeHtml(item.createdAt)} | ${item.results.length} جمله</span>
        </button>
    `).join('');
        }

        function renderResults(results) {
            resultsEl.innerHTML = results.map(row => `
        <article class="result-card">
            <div class="meta">
                <span>#${escapeHtml(row.id)}</span>
                <strong class="score">${escapeHtml(row.predicted_score)} / 10</strong>
                <span>${escapeHtml(row.label)}</span>
            </div>
            <p class="sentence">${escapeHtml(row.sentence)}</p>
            <p class="explanation">${escapeHtml(row.explanation)}</p>
        </article>
    `).join('');
        }

        async function waitForServer() {
            for (let attempt = 0; attempt < 45; attempt++) {
                try {
                    const response = await fetch(`${API_BASE}/health`, {
                        cache: 'no-store'
                    });
                    if (response.ok) return true;
                } catch {}
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            return false;
        }

        async function predict() {
            const sentences = getSentenceValues();
            if (!sentences.length) {
                showError('برای شروع تحلیل، حداقل یک جمله فارسی وارد کنید.');
                return;
            }
            const text = sentences.join('\n');

            clearError();
            resultsEl.innerHTML = '';
            predictButton.disabled = true;
            statusText.textContent = 'در حال پردازش';
            startProgress();

            try {
                const ready = await waitForServer();
                if (!ready) throw new Error('سرویس مدل آماده نشد. صفحه را refresh کنید یا مطمئن شوید PHP مجوز اجرای Python را دارد.');

                setProgress(Math.max(currentProgress, 72), 'در حال محاسبه بازنمایی زبانی...');
                const response = await fetch(`${API_BASE}/predict`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text
                    })
                });
                const data = await response.json();
                if (!response.ok || !data.ok) throw new Error(data.error || 'خطا در فرایند تحلیل زبانی');

                renderResults(data.results);
                saveHistory(text, data.results);
                statusText.textContent = 'آماده پردازش';
                finishProgress();
            } catch (error) {
                clearInterval(progressTimer);
                progressWrap.classList.remove('active');
                statusText.textContent = 'خطا';
                showError(error.message);
            } finally {
                predictButton.disabled = false;
            }
        }

        predictButton.addEventListener('click', predict);
        clearHistory.addEventListener('click', () => {
            localStorage.removeItem(STORAGE_KEY);
            renderHistory();
        });
        historyList.addEventListener('click', event => {
            const button = event.target.closest('.history-item');
            if (!button) return;
            const item = getHistory().find(entry => String(entry.id) === button.dataset.id);
            if (!item) return;
            setSentenceInputs(item.text);
            renderResults(item.results);
        });

        addSentence.addEventListener('click', () => addSentenceInput(''));
        sentenceList.addEventListener('click', event => {
            const button = event.target.closest('.remove-sentence');
            if (!button) return;
            button.closest('.sentence-row').remove();
            updateRemoveButtons();
        });

        setSentenceInputs('');
        renderHistory();
    </script>
</body>

</html>
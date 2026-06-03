<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Lab | Telemetry Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-blue: #1E6FBA;
            --gold: #D4AF37;
            --deep-green: #2E8B57;
            --dark-gray: #2C3E50;
            --light-bg: #F8F9FA;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background-color: var(--light-bg); color: var(--dark-gray); padding: 40px 20px; }
        .container { max-width: 950px; margin: 0 auto; }
        
        header { margin-bottom: 32px; text-align: center; }
        header h1 { font-size: 2rem; font-weight: 700; color: var(--dark-gray); letter-spacing: -0.5px; }
        header p { color: #7F8C8D; margin-top: 4px; font-size: 0.95rem; }

        .hero-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 32px;
            box-shadow: var(--card-shadow);
            margin-bottom: 32px;
            text-align: center;
            border: 1px solid #E2E8F0;
        }
        .hero-card .label { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #94A3B8; }
        .hero-card .value { font-size: 4rem; font-weight: 700; margin: 12px 0; color: #1E293B; display: inline-block; }
        .hero-card .unit { font-size: 1.5rem; font-weight: 500; color: #64748B; margin-left: 4px; }
        
        .badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 8px;
        }

        .table-card {
            background: #FFFFFF;
            border-radius: 16px;
            box-shadow: var(--card-shadow);
            border: 1px solid #E2E8F0;
            overflow: hidden;
        }
        .table-card h2 { padding: 20px 24px; font-size: 1.1rem; font-weight: 600; border-bottom: 1px solid #F1F5F9; }
        
        .table-wrapper { max-height: 500px; overflow-y: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { background: #F8FAFC; padding: 14px 24px; font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; position: sticky; top: 0; z-index: 10; }
        td { padding: 14px 24px; font-size: 0.95rem; border-bottom: 1px solid #F1F5F9; color: #334155; }
        tr:hover td { background-color: #F8FAFC; }
        
        .no-data { padding: 40px; text-align: center; color: #94A3B8; font-style: italic; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Smart Lab Management Dashboard</h1>
        <p>Integrated Environment Tracking & Academic Forensic Access Log</p>
    </header>

    <div class="hero-card" id="live-card">
        <div class="no-data">Initialising hardware tracking stream hook...</div>
    </div>

    <div class="table-card">
        <h2>Live System Telemetry Array</h2>
        <div class="table-wrapper">
            <table id="data-table" style="display: none;">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>CO₂ Concentration</th>
                        <th>Logged User Badge</th>
                        <th>Safety Index</th>
                    </tr>
                </thead>
                <tbody id="table-body"></tbody>
            </table>
            <div id="table-placeholder" class="no-data">Awaiting sensor matrices...</div>
        </div>
    </div>
</div>

<script>
    async function syncDashboardEngine() {
        try {
            const response = await fetch('data-api.php');
            if (!response.ok) throw new Error("Data channel disconnected");
            
            const data = await response.json();
            if (data.length === 0) return;

            // Render Hero Summary
            const latest = data[0];
            const liveCard = document.getElementById('live-card');
            
            let userDisplayString = latest.rfid_tag !== "None" 
                ? `<span style="color:var(--primary-blue); font-weight:600;">[Card Scanned: ${latest.rfid_tag}]</span>`
                : "Monitoring Room Activity...";

            liveCard.innerHTML = `
                <span class="label">Current Atmospheric Density</span><br>
                <div class="value">${latest.co2_ppm}<span class="unit">PPM</span></div>
                <br>
                <span class="badge" style="background-color: ${latest.bg}; color: ${latest.color};">
                    Air Quality: ${latest.status}
                </span>
                <p style="font-size: 0.85rem; color: #64748B; margin-top: 16px; font-weight:500;">
                    ${userDisplayString}
                </p>
            `;

            // Render Tabular Metrics Grid
            const tableBody = document.getElementById('table-body');
            let rowsHTML = '';
            
            data.forEach(entry => {
                const rfidStyle = entry.rfid_tag !== "None" 
                    ? `background: #E8F1F8; color: #1E6FBA; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-weight:600; font-size:0.85rem; border:1px solid #D6E4F0;` 
                    : `color: #94A3B8; font-style: italic; font-size:0.9rem;`;

                rowsHTML += `
                    <tr>
                        <td>${entry.date}</td>
                        <td>${entry.timestamp}</td>
                        <td style="font-weight: 700; color:#1E293B;">${entry.co2_ppm} PPM</td>
                        <td><span style="${rfidStyle}">${entry.rfid_tag}</span></td>
                        <td>
                            <span style="color: ${entry.color}; font-weight: 600; font-size: 0.9rem;">
                                ● ${entry.status}
                            </span>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = rowsHTML;
            document.getElementById('data-table').style.display = 'table';
            document.getElementById('table-placeholder').style.display = 'none';

        } catch (err) {
            console.error("UI Synchronization core fault:", err);
        }
    }

    syncDashboardEngine();
    setInterval(syncDashboardEngine, 2000); // Poll local pipeline array cache every 2 seconds
</script>

</body>
</html>
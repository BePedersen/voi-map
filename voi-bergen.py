# --- Left box: Zone counts ---
table_html = f"""
<div style="
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1000;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    padding: 16px 20px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    max-height: 600px;
    overflow-y: auto;
    width: 280px;
    border: 1px solid #eee;
">
    <h3 style="margin-top: 0; font-size: 16px; color: #333;">🛴 Scooter Zones</h3>
    <p style="margin: 4px 0;"><strong>Total scooters:</strong> {total_scooters}</p>
    <p style="margin: 4px 0;"><strong>Out-of-zone:</strong> {out_of_zones}</p>
    <table style="width: 100%; margin-top: 10px; border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 2px solid #ddd;">
                <th style="text-align: left; padding: 6px 0; color: #555;">Zone</th>
                <th style="text-align: right; padding: 6px 0; color: #555;">Count</th>
            </tr>
        </thead>
        <tbody>
"""

for i, zone in enumerate(zones_sorted):
    bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
    table_html += f"""
        <tr style="background: {bg};">
            <td style="padding: 6px 0;">{zone['name']}</td>
            <td style="padding: 6px 0; text-align: right; font-family: monospace;">{zone['count']}</td>
        </tr>
    """

table_html += """
        </tbody>
    </table>
</div>
"""

fmap.get_root().html.add_child(Element(table_html))

# --- Right box: Battery stats ---
category_html = f"""
<div style="
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    padding: 16px 20px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    width: 260px;
    border: 1px solid #eee;
">
    <h3 style="margin-top: 0; font-size: 16px; color: #333;">⚡ Battery Stats</h3>
    <p style="margin: 4px 0; color: green;"><strong>Availability:</strong> {availability_percent:.1f}%</p>
    <table style="width: 100%; margin-top: 10px; border-collapse: collapse;">
        <tbody>
            <tr><td style="padding: 6px 0;">🖤 <span style='color:#333;'>Critical low &lt; 4%</span></td><td style="text-align: right; font-family: monospace;">{black_count}</td></tr>
            <tr><td style="padding: 6px 0;">🤎 <span style='color:#6e4b3a;'>Superlow 4–10%</span></td><td style="text-align: right; font-family: monospace;">{brown_count}</td></tr>
            <tr><td style="padding: 6px 0;">🧡 <span style='color:#e67e22;'>One-Trip low10–25%</span></td><td style="text-align: right; font-family: monospace;">{orange_count}</td></tr>
            <tr><td style="padding: 6px 0;">💛 <span style='color:#f1c40f;'>Low25–55%</span></td><td style="text-align: right; font-family: monospace;">{yellow_count}</td></tr>
            <tr><td style="padding: 6px 0;">💚 <span style='color:#27ae60;'>Good &gt; 55%</span></td><td style="text-align: right; font-family: monospace;">{green_count}</td></tr>
            <tr><td style="padding: 6px 0;">🔴 <span style='color:#e74c3c;'>Broken (&gt;10% + disabled)</span></td><td style="text-align: right; font-family: monospace;">{red_count}</td></tr>
        </tbody>
    </table>
</div>
"""

fmap.get_root().html.add_child(Element(category_html))

from jinja2 import Template
from playwright.async_api import async_playwright
from graph.state import RoastForgeState,ResumeSchema
import os
import base64
import tempfile

async def download_pdf_node(state: RoastForgeState):
    """
    Generate final PDF from structured ResumeSchema output.

    This is a rendering/output node.
    It should not contain business logic.

    Input:
        state["new_resume"]

    Output:
        {
            "generated_pdf_path": str
        }
    """

    new_resume = state.get("new_resume")

    if not new_resume:
        raise ValueError("new_resume not found for PDF generation")

    if isinstance(new_resume, ResumeSchema):
        resume_data = new_resume.model_dump()
    else:
        resume_data = dict(new_resume)

    filename = "roastforge_resume.pdf"

    # Use writable temp directory instead of current directory
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8"/>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        color: #1a1a2e;
        background: white;
        padding: 36px 44px;
        line-height: 1.5;
    }

    /* ── Header ── */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 2.5px solid #1a1a2e;
        padding-bottom: 12px;
        margin-bottom: 18px;
    }
    .header-left h1 {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #1a1a2e;
    }
    .header-left h2 {
        font-size: 12px;
        font-weight: 400;
        color: #e94560;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 3px;
    }
    .header-right {
        text-align: right;
        font-family: 'DM Mono', monospace;
        font-size: 9.5px;
        color: #555;
        line-height: 1.8;
    }
    .header-right a { color: #555; text-decoration: none; }

    /* ── Section ── */
    .section { margin-bottom: 16px; }
    .section-title {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #e94560;
        margin-bottom: 8px;
        padding-bottom: 3px;
        border-bottom: 1px solid #e8e8e8;
    }

    /* ── Summary ── */
    .summary { color: #333; font-size: 10.5px; }

    /* ── Experience / Projects ── */
    .item { margin-bottom: 10px; }
    .item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .item-title {
        font-weight: 600;
        font-size: 11px;
        color: #1a1a2e;
    }
    .item-sub {
        font-size: 9.5px;
        color: #777;
        font-family: 'DM Mono', monospace;
    }
    .item-stack {
        font-family: 'DM Mono', monospace;
        font-size: 8.5px;
        color: #e94560;
        margin: 2px 0 4px;
    }
    ul { padding-left: 14px; }
    ul li {
        font-size: 10px;
        color: #333;
        margin-bottom: 2px;
    }

    /* ── Skills ── */
    .skills-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }
    .skill-group-title {
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #1a1a2e;
        margin-bottom: 4px;
    }
    .skill-tags { display: flex; flex-wrap: wrap; gap: 4px; }
    .tag {
        background: #f0f0f5;
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 2px 7px;
        font-size: 9px;
        font-family: 'DM Mono', monospace;
        color: #333;
    }

    /* ── Education ── */
    .edu-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .edu-degree { font-weight: 600; font-size: 11px; }
    .edu-college { font-size: 10px; color: #555; margin-top: 2px; }
    .edu-meta {
        font-family: 'DM Mono', monospace;
        font-size: 9.5px;
        color: #e94560;
        text-align: right;
    }

    /* ── Footer line ── */
    .footer {
        margin-top: 20px;
        border-top: 1px solid #e8e8e8;
        padding-top: 6px;
        font-size: 8px;
        color: #bbb;
        font-family: 'DM Mono', monospace;
        text-align: center;
    }
    </style>
    </head>
    <body>

    <!-- HEADER -->
    <div class="header">
    <div class="header-left">
        <h1>{{ name }}</h1>
        <h2>{{ title }}</h2>
    </div>
    <div class="header-right">
        <div>{{ email }}</div>
        <div>{{ phone }}</div>
        <div>{{ linkedin }}</div>
        <div>{{ github }}</div>
    </div>
    </div>

    <!-- SUMMARY -->
    <div class="section">
    <div class="section-title">Profile</div>
    <p class="summary">{{ summary }}</p>
    </div>

    <!-- EXPERIENCE -->
    <div class="section">
    <div class="section-title">Experience</div>
    {% for exp in experience %}
    <div class="item">
        <div class="item-header">
        <span class="item-title">{{ exp.role }} — {{ exp.company }}</span>
        <span class="item-sub">{{ exp.duration }}</span>
        </div>
        <ul>
        {% for point in exp.points %}<li>{{ point }}</li>{% endfor %}
        </ul>
    </div>
    {% endfor %}
    </div>

    <!-- PROJECTS -->
    <div class="section">
    <div class="section-title">Projects</div>
    {% for proj in projects %}
    <div class="item">
        <div class="item-title">{{ proj.name }}</div>
        <div class="item-stack">{{ proj.stack }}</div>
        <ul>
        {% for point in proj.points %}<li>{{ point }}</li>{% endfor %}
        </ul>
    </div>
    {% endfor %}
    </div>

    <!-- SKILLS -->
    <div class="section">
    <div class="section-title">Skills</div>
    <div class="skills-grid">
        {% for group, items in skills.items() %}
        <div>
        <div class="skill-group-title">{{ group }}</div>
        <div class="skill-tags">
            {% for s in items %}<span class="tag">{{ s }}</span>{% endfor %}
        </div>
        </div>
        {% endfor %}
    </div>
    </div>

    <!-- EDUCATION -->
    <div class="section">
    <div class="section-title">Education</div>
    <div class="edu-row">
        <div>
        <div class="edu-degree">{{ education.degree }}</div>
        <div class="edu-college">{{ education.college }}</div>
        </div>
        <div class="edu-meta">
        <div>{{ education.year }}</div>
        <div>CGPA {{ education.cgpa }}</div>
        </div>
    </div>
    </div>

    <div class="footer">Generated by RoastForge · AI Resume Rebuilder</div>

    </body>
    </html>
    """

    template = Template(HTML_TEMPLATE)
    html = template.render(**resume_data)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content(
            html,
            wait_until="networkidle"
        )

        await page.pdf(
            path=file_path,
            format="A4",
            print_background=True,
            margin={
                "top": "20px",
                "bottom": "20px",
                "left": "20px",
                "right": "20px"
            }
        )

        await browser.close()

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return {
        "generated_pdf_filename": filename,
        "generated_pdf_base64": pdf_base64
    }
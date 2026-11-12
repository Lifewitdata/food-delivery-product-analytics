from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]


def main():
    ab = pd.read_csv(ROOT / 'reports' / 'ab_results.csv')
    sim = ab[ab.data.str.startswith('SIMULATED')].set_index('metric')
    conv = sim.loc['conversion (session)']
    rev = sim.loc['revenue per user, SAR']
    time = sim.loc['avg delivery time, min']
    late = sim.loc['late rate (delivered)']
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    slides = [
        ('1 | The experiment', ['Free-delivery threshold: SAR 75 vs SAR 50', 'Portfolio exercise: synthetic source, Saudi adaptation, SIMULATED treatment effect.', 'Business hypothesis: lower threshold improves conversion without harmful delivery effects.', 'Observed baskets all >= SAR 375: observed comparison is an A/A test.']),
        ('2 | Success measures', ['Customer-level assignment, 50/50; SRM p = 0.2107 (3,601 / 3,708 customers).', 'Primary: delivered / checkout sessions; customer-level mean conversion robustness check.', 'Secondary: delivered GMV per customer, Welch t-test.', 'Guardrails: delivery time and source late rate. Cancellation = 1 minus conversion.', '3 pp MDE, alpha 0.05, power 80%; 1,779 sessions/arm at observed baseline; clustering caveat.']),
        ('3 | Headline result - SIMULATED', [f'Conversion: {conv.control:.2%} control vs {conv.treatment:.2%} treatment.', f'Net lift {conv["diff"] * 100:+.2f} pp; 95% CI {conv.ci_low * 100:+.2f} to {conv.ci_high * 100:+.2f} pp; p < 0.001.', 'Customer-level check: +2.30 pp, p < 0.001.', '228 treatment cancellations flipped to delivery (+3 pp over its own baseline), seed 42.']),
        ('4 | Funnel', ['15,000 browse -> 15,000 cart -> 15,000 checkout -> 12,997 delivered in observed data.', 'No pre-checkout drop-off: events were generated only for placed orders.', 'Observed checkout conversion 86.65%; cancellation 13.35%.', 'Next: log sessions without an order before claiming full-funnel conversion.']),
        ('5 | Revenue - no proven lift', [f'SIMULATED revenue per user: SAR {rev.control:.2f} vs {rev.treatment:.2f}.', f'Difference SAR {rev["diff"]:+.2f}; 95% CI {rev.ci_low:+.2f} to {rev.ci_high:+.2f}; p = {rev.p_value:.3f}.', 'Not statistically significant. Conversion is the demo launch case, not revenue.', 'Revenue moves only from newly delivered orders. No unrelated revenue offset added.']),
        ('6 | Guardrails and segments', [f'SIMULATED delivery time {time["diff"]:+.2f} min (p = {time.p_value:.3f}); late rate {late["diff"] * 100:+.2f} pp (p = {late.p_value:.3f}).', 'No significant harm found; this does NOT prove non-inferiority.', 'City cuts positive; premium alone +1.50 pp, p = .125 (exploratory, no multiplicity adjustment).', 'Real launch needs acceptable harm margins and clustered inference.']),
        ('7 | Recommendation', ['Observed: REVISE AND RETEST; the threshold never binds in this dataset.', 'Simulation: demonstration LAUNCH by the stated rule (positive conversion CI, no significant guardrail harm).', 'Not a production recommendation and not evidence about real customers.', 'Real test: baskets SAR 50-75, actual fee policy, margin / subsidy costs and independent guardrails.']),
        ('8 | Post-launch monitoring plan', ['Before exposure: validate assignment, eligibility, event sequence, subsidy accounting and SRM.', 'Daily operational monitoring: cancellation, ETA breach, p95 delivery time and support contacts.', 'Fixed-window decision readout: cluster-aware conversion and contribution-margin CIs, no peeking.', 'Rollback only against predeclared harm thresholds; audit premium/city heterogeneity afterward.']),
    ]
    for title, bullets in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title
        frame = slide.placeholders[1].text_frame
        frame.clear()
        for i, text in enumerate(bullets):
            p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            p.text = text
            p.font.size = Pt(23)
            p.space_after = Pt(20)
    out = ROOT / 'reports' / 'launch_deck.pptx'
    prs.save(out)
    print(f'{len(prs.slides)} slides saved: {out.name}')


if __name__ == '__main__':
    main()

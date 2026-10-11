import io
from datetime import date
from decimal import Decimal, InvalidOperation

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .models import CostRate, EstimateLog

COVERAGE = Decimal('0.70')   # share of the plot built on per floor
MARGIN = Decimal('0.10')     # ± range around the estimate


def calculate(data):
    """Returns (result_dict, error_message). Shared by the JSON and PDF views."""
    try:
        plot = Decimal(str(data.get('plot_size')))
        floors = int(data.get('floors'))
    except (InvalidOperation, TypeError, ValueError):
        return None, 'Plot size and floors must be numbers.'

    finish = data.get('finish_level')
    if plot <= 0 or plot > 100000 or not (1 <= floors <= 10):
        return None, 'Plot size must be between 1 and 100000 sq ft, and floors between 1 and 10.'
    if finish not in ('basic', 'standard', 'premium'):
        return None, 'Invalid finish level.'

    rates = CostRate.objects.filter(finish_level=finish)
    if not rates.exists():
        return None, 'No rates configured yet. Add them in the admin panel.'

    built_up = plot * COVERAGE * floors
    items, total = [], Decimal('0')
    for r in rates:
        cost = built_up * r.rate_per_sqft
        total += cost
        items.append({'item': r.item, 'rate': float(r.rate_per_sqft), 'cost': round(float(cost))})

    return {
        'plot_size': float(plot),
        'floors': floors,
        'finish_level': finish,
        'built_up_area': round(float(built_up), 1),
        'items': items,
        'total': round(float(total)),
        'low': round(float(total * (1 - MARGIN))),
        'high': round(float(total * (1 + MARGIN))),
    }, None


@api_view(['POST'])
def estimate(request):
    result, error = calculate(request.data)
    if error:
        return Response({'error': error}, status=400)
    # one row per estimate, used by the admin analytics dashboard
    EstimateLog.objects.create(
        plot_size=result['plot_size'],
        floors=result['floors'],
        finish_level=result['finish_level'],
        total=result['total'],
    )
    return Response(result)


def inr(n):
    """Indian digit grouping: 2540160 -> 25,40,160"""
    s = str(int(n))
    if len(s) <= 3:
        return s
    last3, rest, groups = s[-3:], s[:-3], []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return ','.join(groups + [last3])


@api_view(['POST'])
def estimate_pdf(request):
    result, error = calculate(request.data)
    if error:
        return Response({'error': error}, status=400)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=18*mm, bottomMargin=18*mm,
                            title='Construction Cost Estimate')
    styles = getSampleStyleSheet()
    story = [
        Paragraph('Construction Cost Estimate', styles['Title']),
        Paragraph(f'Generated on {date.today().strftime("%d %b %Y")}', styles['Normal']),
        Spacer(1, 8*mm),
    ]

    summary = [
        ['Plot size', f'{result["plot_size"]:g} sq ft'],
        ['Number of floors', str(result['floors'])],
        ['Finish level', result['finish_level'].title()],
        ['Estimated built-up area', f'{result["built_up_area"]:g} sq ft'],
    ]
    t1 = Table(summary, colWidths=[70*mm, 100*mm])
    t1.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story += [t1, Spacer(1, 8*mm)]

    story.append(Paragraph('Itemised breakdown', styles['Heading2']))
    rows = [['Item', 'Rate (Rs/sq ft)', 'Cost (Rs)']]
    for it in result['items']:
        rows.append([it['item'], inr(it['rate']), inr(it['cost'])])
    rows.append(['Total', '', inr(result['total'])])

    t2 = Table(rows, colWidths=[90*mm, 40*mm, 40*mm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2a33')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fdeee6')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story += [t2, Spacer(1, 8*mm)]

    story.append(Paragraph(
        f'<b>Estimated cost range: Rs {inr(result["low"])} to Rs {inr(result["high"])}</b>',
        styles['Heading3']))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        'This is an indicative estimate based on average local material and labour rates and '
        'assumes about 70% of the plot is built on each floor. Final cost depends on design, '
        'site conditions and market prices. Request quotes from verified companies for an '
        'accurate figure.', styles['Italic']))

    doc.build(story)

    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="construction-estimate.pdf"'
    return response
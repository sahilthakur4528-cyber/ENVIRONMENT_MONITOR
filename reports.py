from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from io import BytesIO


def generate_water_report(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    story.append(
        Paragraph(
            "ENVIRONMENTAL MONITORING SYSTEM",
            title_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Water Quality Report",
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 20))

    table_data = [
        ["Parameter", "Value"],

        ["pH Level", str(data.get("ph", "N/A"))],

        [
            "Water Temperature",
            str(
                data.get(
                    "water_temperature",
                    data.get("temperature", "N/A")
                )
            ) + " °C"
        ],

        [
            "Turbidity",
            str(data.get("turbidity", "N/A")) + " NTU"
        ],

        [
            "Dissolved Oxygen",
            str(
                data.get("dissolved_oxygen", "N/A")
            ) + " mg/L"
        ],

        [
            "TDS",
            str(data.get("tds", "N/A")) + " mg/L"
        ],

        [
            "Water Quality Index",
            str(data.get("wqi", "N/A"))
        ],

        [
            "Updated At",
            str(data.get("created_at", "N/A"))
        ]
    ]

    table = Table(
        table_data,
        colWidths=[230, 230]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#16a34a")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.whitesmoke
            )
        ])
    )

    story.append(table)

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "This report is generated using the latest "
            "water quality data available in the system.",
            styles["BodyText"]
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer





from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from io import BytesIO


def generate_water_report(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    story.append(
        Paragraph(
            "ENVIRONMENTAL MONITORING SYSTEM",
            title_style
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Water Quality Report",
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 20))

    table_data = [
        ["Parameter", "Value"],

        ["pH Level", str(data.get("ph", "N/A"))],

        [
            "Water Temperature",
            str(
                data.get(
                    "water_temperature",
                    data.get("temperature", "N/A")
                )
            ) + " °C"
        ],

        [
            "Turbidity",
            str(data.get("turbidity", "N/A")) + " NTU"
        ],

        [
            "Dissolved Oxygen",
            str(
                data.get("dissolved_oxygen", "N/A")
            ) + " mg/L"
        ],

        [
            "TDS",
            str(data.get("tds", "N/A")) + " mg/L"
        ],

        [
            "Water Quality Index",
            str(data.get("wqi", "N/A"))
        ],

        [
            "Updated At",
            str(data.get("created_at", "N/A"))
        ]
    ]

    table = Table(
        table_data,
        colWidths=[230, 230]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#16a34a")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                10
            )
        ])
    )

    story.append(table)

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "This report is generated using the latest "
            "water quality data available in the system.",
            styles["BodyText"]
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer



from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(data,name):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Environmental Monitoring Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Air Quality Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    if data:

        story.append(
            Paragraph(
                f"city: {data.get('city', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"AQI: {data.get('aqi', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"PM2.5: {data.get('pm25', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"PM10: {data.get('pm10', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"CO: {data.get('co', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"NO2: {data.get('no2', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"SO2: {data.get('so2', 'N/A')}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"O3: {data.get('o3', 'N/A')}",
                styles["Normal"]
            )
        )

    else:

        story.append(
            Paragraph(
                "No air quality data available.",
                styles["Normal"]
            )
        )

    doc.build(story)

    buffer.seek(0)

    return buffer
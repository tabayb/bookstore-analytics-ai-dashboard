from dateutil import parser

def clean_timestamp(timestamp):
    normalized = timestamp.replace(",", " ")
    normalized = normalized.replace(";", " ")
    normalized = normalized.replace("A.M.", "AM")
    normalized = normalized.replace("P.M.", "PM")

    parsed = parser.parse(normalized)

    return parsed

print(clean_timestamp("09:28,10-Dec-2025"))
print(clean_timestamp("2025-06-25;05:00:01 A.M."))
print(clean_timestamp("10:31:43 P.M. 2026-01-14"))
import csv
import io


def build_session_csv(messages: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["role", "content", "timestamp"])
    for m in messages:
        writer.writerow([m.role, m.content, m.timestamp])
    return output.getvalue()

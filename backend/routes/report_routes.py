from flask_restful import Resource
from backend.models.report_model import Report


class ReportResource(Resource):
    """Endpoint to retrieve report metadata by ID."""

    def get(self, report_id: int):
        report = Report.query.get(report_id)
        if report is None:
            return {"message": "Report not found."}, 404

        return {"report": report.to_dict()}, 200

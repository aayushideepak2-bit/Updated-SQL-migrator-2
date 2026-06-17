from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.user_model import User
from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory


def is_admin_user() -> bool:
    identity = get_jwt_identity()
    return isinstance(identity, dict) and identity.get("role") == "Admin"


class AdminUserListResource(Resource):
    """Admin-only endpoint to list all registered users."""

    @jwt_required()
    def get(self):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        users = [user.to_dict() for user in User.query.all()]
        return {"users": users, "count": len(users)}, 200


class AdminUserDeleteResource(Resource):
    """Admin-only endpoint to delete a specific user."""

    @jwt_required()
    def delete(self, user_id: int):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        user = User.query.get(user_id)
        if user is None:
            return {"message": "User not found."}, 404

        User.query.filter_by(id=user.id).delete()
        from backend.extensions import db
        db.session.commit()
        return {"message": f"User {user.username} deleted."}, 200


class AdminStatsResource(Resource):
    """Admin-only endpoint for migration statistics and failed jobs."""

    @jwt_required()
    def get(self):
        if not is_admin_user():
            return {"message": "Admin access required."}, 403

        total_migrations = Migration.query.count()
        history_count = MigrationHistory.query.count()
        failed_migrations = Migration.query.filter_by(status="failed").count()
        failed_history = MigrationHistory.query.filter(MigrationHistory.status.ilike("%failed%"))

        return {
            "total_migrations": total_migrations,
            "migration_history_count": history_count,
            "failed_migrations": failed_migrations,
            "failed_history_count": failed_history.count(),
        }, 200

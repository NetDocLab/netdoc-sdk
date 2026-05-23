import pytest


@pytest.mark.django_db
class TestAuditLog:
    @pytest.mark.django_db(transaction=True)
    async def test_audit_log(self, admin_client):
        # Generate a log
        await admin_client.user_add(username='test-user', password='test-password', role='admin')

        res = await admin_client.auditlog_list()
        assert res.count == 1
        for audit_log in res.results:
            await admin_client.auditlog_get(id=audit_log.id)

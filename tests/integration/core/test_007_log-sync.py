import pytest


@pytest.mark.django_db
class TestLogSyncClient:
    @pytest.mark.django_db(transaction=True)
    def test_log(self, collector_sync_client, superuser_sync_client):
        log = collector_sync_client.log_add(
            level='INFO',
            message='Test Log',
            correlation_id='a774c74b-71f8-4e51-9625-c611e907f729',
            module='remote-log',
            func_name='__main__',
            line_no='34',
            hostname='localhost',
            process=37,
            thread_name='MainThread',
        )

        res = superuser_sync_client.auditlog_list()
        assert res.count == 1
        superuser_sync_client.log_get(id=log.id)

import pytest


@pytest.mark.django_db
class TestLog:
    @pytest.mark.django_db(transaction=True)
    async def test_log(self, collector_client, superuser_client):
        log = await collector_client.log_add(
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

        res = await superuser_client.auditlog_list()
        assert res.count == 1
        await superuser_client.log_get(id=log.id)

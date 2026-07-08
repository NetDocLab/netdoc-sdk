# GENERATED FILE — do not edit manually.
# Run: python scripts/generate.py

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any

from pydantic import BaseModel

from netdoc_sdk.models._generated_models import (
    VLAN,
    VRF,
    ARPEntry,
    AuditLogDetail,
    AuthToken,
    CanonicalDeviceDetail,
    CanonicalEndpoint,
    CollectorDetail,
    CredentialDetail,
    DeviceConnectionDetail,
    DeviceDetail,
    DiscoveryJobClaim,
    DiscoveryJobStatus,
    DiscoveryRunDetail,
    DiscoverySchedule,
    EndpointConnectionDetail,
    EndpointDetail,
    InterfaceDetail,
    IPAddress,
    LogRecordDetail,
    MACEntry,
    PaginatedARPEntryList,
    PaginatedAuditLogDetailList,
    PaginatedCanonicalDeviceListList,
    PaginatedCanonicalEndpointList,
    PaginatedCollectorListList,
    PaginatedCredentialListList,
    PaginatedDeviceConnectionListList,
    PaginatedDeviceListList,
    PaginatedDiscoveryJobDetailList,
    PaginatedDiscoveryRunDetailList,
    PaginatedDiscoveryScheduleList,
    PaginatedEndpointConnectionListList,
    PaginatedEndpointListList,
    PaginatedInterfaceListList,
    PaginatedIPAddressList,
    PaginatedLogRecordDetailList,
    PaginatedMACEntryList,
    PaginatedRawOutputListList,
    PaginatedRouteEntryList,
    PaginatedSiteListList,
    PaginatedSnapshotListList,
    PaginatedTenantListList,
    PaginatedTunnelConnectionListList,
    PaginatedUserListList,
    PaginatedVLANList,
    PaginatedVRFList,
    RouteEntry,
    SiteDetail,
    SnapshotDetail,
    TenantDetail,
    TopologyGraph,
    TunnelConnectionDetail,
    UserDetail,
)

JsonMapping = Mapping[str, Any] | BaseModel


class _GeneratedEndpoints:
    """Auto-generated endpoint methods — do not edit manually.

    Inherited by _NetDocClientBase. Override individual methods
    in _client_base.py when custom logic is required (e.g. special
    headers, dual expected_status, or non-standard request shapes).
    """

    @abstractmethod
    def _request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | str | None = None,
        expected_status: int | Iterable[int] | None = None,
        headers: Mapping[str, str] | None = None,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        response_model: Any = None,
    ) -> Any: ...

    @abstractmethod
    def _serialize_body(
        self, body: JsonMapping | None = None, **fields: Any
    ) -> dict[str, Any] | None: ...

    def arp_entries_list(self, **params: Any) -> PaginatedARPEntryList:
        """List ARP entries"""
        return self._request(
            'GET',
            'arp-entries/',
            params=params,
            expected_status=200,
            response_model=PaginatedARPEntryList,
        )

    def arp_entries_get(self, id: str) -> ARPEntry:
        """Get ARP entry details"""
        return self._request(
            'GET',
            f'arp-entries/{id}/',
            expected_status=200,
            response_model=ARPEntry,
        )

    def audit_logs_list(self, **params: Any) -> PaginatedAuditLogDetailList:
        """List audit logs"""
        return self._request(
            'GET',
            'audit-logs/',
            params=params,
            expected_status=200,
            response_model=PaginatedAuditLogDetailList,
        )

    def audit_logs_get(self, id: str) -> AuditLogDetail:
        """Get audit log details"""
        return self._request(
            'GET',
            f'audit-logs/{id}/',
            expected_status=200,
            response_model=AuditLogDetail,
        )

    def canonical_devices_list(self, **params: Any) -> PaginatedCanonicalDeviceListList:
        """List canonical devices"""
        return self._request(
            'GET',
            'canonical-devices/',
            params=params,
            expected_status=200,
            response_model=PaginatedCanonicalDeviceListList,
        )

    def canonical_devices_add(
        self, data: JsonMapping | None = None, **fields: Any
    ) -> CanonicalDeviceDetail:
        """Create canonical device"""
        return self._request(
            'POST',
            'canonical-devices/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=CanonicalDeviceDetail,
        )

    def canonical_devices_get(self, id: str) -> CanonicalDeviceDetail:
        """Get canonical device details"""
        return self._request(
            'GET',
            f'canonical-devices/{id}/',
            expected_status=200,
            response_model=CanonicalDeviceDetail,
        )

    def canonical_devices_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> CanonicalDeviceDetail:
        """Update canonical device"""
        return self._request(
            'PATCH',
            f'canonical-devices/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=CanonicalDeviceDetail,
        )

    def canonical_devices_delete(self, id: str) -> None:
        """Delete canonical device"""
        return self._request(
            'DELETE',
            f'canonical-devices/{id}/',
            expected_status=204,
        )

    def canonical_devices_history(self, id: str, **params: Any) -> PaginatedDeviceListList:
        """Get device history"""
        return self._request(
            'GET',
            f'canonical-devices/{id}/history/',
            params=params,
            expected_status=200,
            response_model=PaginatedDeviceListList,
        )

    def canonical_endpoints_list(self, **params: Any) -> PaginatedCanonicalEndpointList:
        """List canonical endpoints"""
        return self._request(
            'GET',
            'canonical-endpoints/',
            params=params,
            expected_status=200,
            response_model=PaginatedCanonicalEndpointList,
        )

    def canonical_endpoints_get(self, id: str) -> CanonicalEndpoint:
        """Get canonical endpoint details"""
        return self._request(
            'GET',
            f'canonical-endpoints/{id}/',
            expected_status=200,
            response_model=CanonicalEndpoint,
        )

    def canonical_endpoints_history(self, id: str, **params: Any) -> PaginatedEndpointListList:
        """Get endpoint history"""
        return self._request(
            'GET',
            f'canonical-endpoints/{id}/history/',
            params=params,
            expected_status=200,
            response_model=PaginatedEndpointListList,
        )

    def collectors_list(self, **params: Any) -> PaginatedCollectorListList:
        """List collectors"""
        return self._request(
            'GET',
            'collectors/',
            params=params,
            expected_status=200,
            response_model=PaginatedCollectorListList,
        )

    def collectors_get(self, id: str) -> CollectorDetail:
        """Get collector details"""
        return self._request(
            'GET',
            f'collectors/{id}/',
            expected_status=200,
            response_model=CollectorDetail,
        )

    def collectors_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> CollectorDetail:
        """Update collector"""
        return self._request(
            'PATCH',
            f'collectors/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=CollectorDetail,
        )

    def collectors_delete(self, id: str) -> None:
        """Delete collector"""
        return self._request(
            'DELETE',
            f'collectors/{id}/',
            expected_status=204,
        )

    def collectors_heartbeat(
        self, data: JsonMapping | None = None, **fields: Any
    ) -> CollectorDetail:
        """collectors_heartbeat"""
        return self._request(
            'POST',
            'collectors/heartbeat/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=CollectorDetail,
        )

    def credentials_list(self, **params: Any) -> PaginatedCredentialListList:
        """List credentials"""
        return self._request(
            'GET',
            'credentials/',
            params=params,
            expected_status=200,
            response_model=PaginatedCredentialListList,
        )

    def credentials_add(self, data: JsonMapping | None = None, **fields: Any) -> CredentialDetail:
        """Create credential"""
        return self._request(
            'POST',
            'credentials/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=CredentialDetail,
        )

    def credentials_get(self, id: str) -> CredentialDetail:
        """Get credential details"""
        return self._request(
            'GET',
            f'credentials/{id}/',
            expected_status=200,
            response_model=CredentialDetail,
        )

    def credentials_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> CredentialDetail:
        """Update credential"""
        return self._request(
            'PATCH',
            f'credentials/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=CredentialDetail,
        )

    def credentials_delete(self, id: str) -> None:
        """Delete credential"""
        return self._request(
            'DELETE',
            f'credentials/{id}/',
            expected_status=204,
        )

    def device_connections_list(self, **params: Any) -> PaginatedDeviceConnectionListList:
        """List device connections"""
        return self._request(
            'GET',
            'device-connections/',
            params=params,
            expected_status=200,
            response_model=PaginatedDeviceConnectionListList,
        )

    def device_connections_get(self, id: str) -> DeviceConnectionDetail:
        """Get device connection details"""
        return self._request(
            'GET',
            f'device-connections/{id}/',
            expected_status=200,
            response_model=DeviceConnectionDetail,
        )

    def devices_list(self, **params: Any) -> PaginatedDeviceListList:
        """List devices"""
        return self._request(
            'GET',
            'devices/',
            params=params,
            expected_status=200,
            response_model=PaginatedDeviceListList,
        )

    def devices_get(self, id: str, **params: Any) -> DeviceDetail:
        """Get device details"""
        return self._request(
            'GET',
            f'devices/{id}/',
            params=params,
            expected_status=200,
            response_model=DeviceDetail,
        )

    def devices_interfaces_list(self, id: str, **params: Any) -> PaginatedInterfaceListList:
        """List device interfaces"""
        return self._request(
            'GET',
            f'devices/{id}/interfaces/',
            params=params,
            expected_status=200,
            response_model=PaginatedInterfaceListList,
        )

    def devices_routes_list(self, id: str, **params: Any) -> PaginatedRouteEntryList:
        """List device routes"""
        return self._request(
            'GET',
            f'devices/{id}/routes/',
            params=params,
            expected_status=200,
            response_model=PaginatedRouteEntryList,
        )

    def discoveries_list(self, **params: Any) -> PaginatedDiscoveryRunDetailList:
        """List discovery runs"""
        return self._request(
            'GET',
            'discoveries/',
            params=params,
            expected_status=200,
            response_model=PaginatedDiscoveryRunDetailList,
        )

    def discoveries_add(self, data: JsonMapping | None = None, **fields: Any) -> DiscoveryRunDetail:
        """Create discovery run"""
        return self._request(
            'POST',
            'discoveries/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=DiscoveryRunDetail,
        )

    def discoveries_get(self, id: str) -> DiscoveryRunDetail:
        """Get discovery run details"""
        return self._request(
            'GET',
            f'discoveries/{id}/',
            expected_status=200,
            response_model=DiscoveryRunDetail,
        )

    def discoveries_cancel(self, id: str, data: JsonMapping | None = None, **fields: Any) -> None:
        """Cancel a discovery"""
        return self._request(
            'POST',
            f'discoveries/{id}/cancel/',
            json=self._serialize_body(data, **fields),
            expected_status=204,
        )

    def discoveries_jobs_list(self, id: str, **params: Any) -> PaginatedDiscoveryJobDetailList:
        """Get jobs"""
        return self._request(
            'GET',
            f'discoveries/{id}/jobs/',
            params=params,
            expected_status=200,
            response_model=PaginatedDiscoveryJobDetailList,
        )

    def discovery_jobs_complete(
        self, id: str, claim_token: str, data: JsonMapping | None = None, **fields: Any
    ) -> None:
        """Close a job"""
        headers = {'X-Claim-Token': claim_token}
        return self._request(
            'POST',
            f'discovery-jobs/{id}/complete/',
            headers=headers,
            json=self._serialize_body(data, **fields),
            expected_status=204,
        )

    def discovery_jobs_logs(self, id: str, **params: Any) -> PaginatedRawOutputListList:
        """Get logs"""
        return self._request(
            'GET',
            f'discovery-jobs/{id}/logs/',
            params=params,
            expected_status=200,
            response_model=PaginatedRawOutputListList,
        )

    def discovery_jobs_push_discovered_device(
        self, id: str, claim_token: str, data: JsonMapping | None = None, **fields: Any
    ) -> DiscoveryJobStatus:
        """Push a discovered device"""
        headers = {'X-Claim-Token': claim_token}
        return self._request(
            'POST',
            f'discovery-jobs/{id}/push-discovered-device/',
            headers=headers,
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=DiscoveryJobStatus,
        )

    def discovery_jobs_claim(
        self, data: JsonMapping | None = None, **fields: Any
    ) -> DiscoveryJobClaim | None:
        """Claim a job"""
        return self._request(
            'POST',
            'discovery-jobs/claim/',
            json=self._serialize_body(data, **fields),
            expected_status=[200, 204],
            response_model=DiscoveryJobClaim | None,
        )

    def discovery_schedules_list(self, **params: Any) -> PaginatedDiscoveryScheduleList:
        """discovery_schedules_list"""
        return self._request(
            'GET',
            'discovery-schedules/',
            params=params,
            expected_status=200,
            response_model=PaginatedDiscoveryScheduleList,
        )

    def discovery_schedules_add(
        self, data: JsonMapping | None = None, **fields: Any
    ) -> DiscoverySchedule:
        """discovery_schedules_add"""
        return self._request(
            'POST',
            'discovery-schedules/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=DiscoverySchedule,
        )

    def discovery_schedules_get(self, id: str) -> DiscoverySchedule:
        """discovery_schedules_get"""
        return self._request(
            'GET',
            f'discovery-schedules/{id}/',
            expected_status=200,
            response_model=DiscoverySchedule,
        )

    def discovery_schedules_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> DiscoverySchedule:
        """discovery_schedules_update"""
        return self._request(
            'PATCH',
            f'discovery-schedules/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=DiscoverySchedule,
        )

    def discovery_schedules_delete(self, id: str) -> None:
        """discovery_schedules_delete"""
        return self._request(
            'DELETE',
            f'discovery-schedules/{id}/',
            expected_status=204,
        )

    def endpoint_connections_list(self, **params: Any) -> PaginatedEndpointConnectionListList:
        """List endpoint connections"""
        return self._request(
            'GET',
            'endpoint-connections/',
            params=params,
            expected_status=200,
            response_model=PaginatedEndpointConnectionListList,
        )

    def endpoint_connections_get(self, id: str) -> EndpointConnectionDetail:
        """Get endpoint connection details"""
        return self._request(
            'GET',
            f'endpoint-connections/{id}/',
            expected_status=200,
            response_model=EndpointConnectionDetail,
        )

    def endpoints_list(self, **params: Any) -> PaginatedEndpointListList:
        """List endpoints"""
        return self._request(
            'GET',
            'endpoints/',
            params=params,
            expected_status=200,
            response_model=PaginatedEndpointListList,
        )

    def endpoints_get(self, id: str) -> EndpointDetail:
        """Get endpoint details"""
        return self._request(
            'GET',
            f'endpoints/{id}/',
            expected_status=200,
            response_model=EndpointDetail,
        )

    def endpoints_by_device_list(self, device_id: str, **params: Any) -> PaginatedEndpointListList:
        """Get endpoints by device"""
        return self._request(
            'GET',
            f'endpoints/by-device/{device_id}/',
            params=params,
            expected_status=200,
            response_model=PaginatedEndpointListList,
        )

    def endpoints_search_list(self, **params: Any) -> PaginatedEndpointListList:
        """Search endpoints"""
        return self._request(
            'GET',
            'endpoints/search/',
            params=params,
            expected_status=200,
            response_model=PaginatedEndpointListList,
        )

    def interfaces_list(self, **params: Any) -> PaginatedInterfaceListList:
        """List interfaces"""
        return self._request(
            'GET',
            'interfaces/',
            params=params,
            expected_status=200,
            response_model=PaginatedInterfaceListList,
        )

    def interfaces_get(self, id: str) -> InterfaceDetail:
        """Get interface details"""
        return self._request(
            'GET',
            f'interfaces/{id}/',
            expected_status=200,
            response_model=InterfaceDetail,
        )

    def ip_addresses_list(self, **params: Any) -> PaginatedIPAddressList:
        """List IP addresses"""
        return self._request(
            'GET',
            'ip-addresses/',
            params=params,
            expected_status=200,
            response_model=PaginatedIPAddressList,
        )

    def ip_addresses_get(self, id: str) -> IPAddress:
        """Get IP address details"""
        return self._request(
            'GET',
            f'ip-addresses/{id}/',
            expected_status=200,
            response_model=IPAddress,
        )

    def logs_list(self, **params: Any) -> PaginatedLogRecordDetailList:
        """List logs"""
        return self._request(
            'GET',
            'logs/',
            params=params,
            expected_status=200,
            response_model=PaginatedLogRecordDetailList,
        )

    def logs_get(self, id: str) -> LogRecordDetail:
        """Get audit log details"""
        return self._request(
            'GET',
            f'logs/{id}/',
            expected_status=200,
            response_model=LogRecordDetail,
        )

    def mac_entries_list(self, **params: Any) -> PaginatedMACEntryList:
        """List MAC addresses"""
        return self._request(
            'GET',
            'mac-entries/',
            params=params,
            expected_status=200,
            response_model=PaginatedMACEntryList,
        )

    def mac_entries_get(self, id: str) -> MACEntry:
        """Get MAC address details"""
        return self._request(
            'GET',
            f'mac-entries/{id}/',
            expected_status=200,
            response_model=MACEntry,
        )

    def routes_list(self, **params: Any) -> PaginatedRouteEntryList:
        """List route entries"""
        return self._request(
            'GET',
            'routes/',
            params=params,
            expected_status=200,
            response_model=PaginatedRouteEntryList,
        )

    def routes_get(self, id: str) -> RouteEntry:
        """Get route entry details"""
        return self._request(
            'GET',
            f'routes/{id}/',
            expected_status=200,
            response_model=RouteEntry,
        )

    def sites_list(self, **params: Any) -> PaginatedSiteListList:
        """List sites"""
        return self._request(
            'GET',
            'sites/',
            params=params,
            expected_status=200,
            response_model=PaginatedSiteListList,
        )

    def sites_add(self, data: JsonMapping | None = None, **fields: Any) -> SiteDetail:
        """Create site"""
        return self._request(
            'POST',
            'sites/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=SiteDetail,
        )

    def sites_get(self, id: str) -> SiteDetail:
        """Get site details"""
        return self._request(
            'GET',
            f'sites/{id}/',
            expected_status=200,
            response_model=SiteDetail,
        )

    def sites_update(self, id: str, data: JsonMapping | None = None, **fields: Any) -> SiteDetail:
        """Update site"""
        return self._request(
            'PATCH',
            f'sites/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=SiteDetail,
        )

    def sites_delete(self, id: str) -> None:
        """Delete site"""
        return self._request(
            'DELETE',
            f'sites/{id}/',
            expected_status=204,
        )

    def snapshots_list(self, **params: Any) -> PaginatedSnapshotListList:
        """List snapshots"""
        return self._request(
            'GET',
            'snapshots/',
            params=params,
            expected_status=200,
            response_model=PaginatedSnapshotListList,
        )

    def snapshots_get(self, id: str) -> SnapshotDetail:
        """Get snapshot details"""
        return self._request(
            'GET',
            f'snapshots/{id}/',
            expected_status=200,
            response_model=SnapshotDetail,
        )

    def snapshots_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> SnapshotDetail:
        """Update snapshot"""
        return self._request(
            'PATCH',
            f'snapshots/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=SnapshotDetail,
        )

    def snapshots_delete(self, id: str) -> None:
        """Delete snapshot"""
        return self._request(
            'DELETE',
            f'snapshots/{id}/',
            expected_status=204,
        )

    def snapshots_pin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> TenantDetail:
        """Pin snapshot"""
        return self._request(
            'POST',
            f'snapshots/{id}/pin/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=TenantDetail,
        )

    def snapshots_stats(self, id: str) -> SnapshotDetail:
        """Get snapshot statistics"""
        return self._request(
            'GET',
            f'snapshots/{id}/stats/',
            expected_status=200,
            response_model=SnapshotDetail,
        )

    def snapshots_unpin(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> TenantDetail:
        """Unpin snapshot"""
        return self._request(
            'POST',
            f'snapshots/{id}/unpin/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=TenantDetail,
        )

    def snapshots_latest(self) -> SnapshotDetail | None:
        """Latest snapshot"""
        return self._request(
            'GET',
            'snapshots/latest/',
            expected_status=[200, 204],
            response_model=SnapshotDetail | None,
        )

    def tenants_list(self, **params: Any) -> PaginatedTenantListList:
        """List tenants"""
        return self._request(
            'GET',
            'tenants/',
            params=params,
            expected_status=200,
            response_model=PaginatedTenantListList,
        )

    def tenants_add(self, data: JsonMapping | None = None, **fields: Any) -> TenantDetail:
        """Create tenant"""
        return self._request(
            'POST',
            'tenants/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=TenantDetail,
        )

    def tenants_get(self, id: str) -> TenantDetail:
        """Get tenant details"""
        return self._request(
            'GET',
            f'tenants/{id}/',
            expected_status=200,
            response_model=TenantDetail,
        )

    def tenants_update(
        self, id: str, data: JsonMapping | None = None, **fields: Any
    ) -> TenantDetail:
        """Update tenant"""
        return self._request(
            'PATCH',
            f'tenants/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=TenantDetail,
        )

    def tenants_delete(self, id: str) -> None:
        """Delete tenant"""
        return self._request(
            'DELETE',
            f'tenants/{id}/',
            expected_status=204,
        )

    def tenants_current(self) -> TenantDetail:
        """Get current user's tenant details"""
        return self._request(
            'GET',
            'tenants/current/',
            expected_status=200,
            response_model=TenantDetail,
        )

    def tokens_add(self, data: JsonMapping | None = None, **fields: Any) -> AuthToken:
        """tokens_add"""
        return self._request(
            'POST',
            'tokens/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=AuthToken,
        )

    def topology_list(self, **params: Any) -> list[TopologyGraph]:
        """Get topology graph"""
        return self._request(
            'GET',
            'topology/',
            params=params,
            expected_status=200,
            response_model=list[TopologyGraph],
        )

    def topology_l2_domain_get(self, **params: Any) -> None:
        """Get L2 domain"""
        return self._request(
            'GET',
            'topology/l2_domain/',
            params=params,
            expected_status=200,
        )

    def tunnel_connections_list(self, **params: Any) -> PaginatedTunnelConnectionListList:
        """List tunnel connections"""
        return self._request(
            'GET',
            'tunnel-connections/',
            params=params,
            expected_status=200,
            response_model=PaginatedTunnelConnectionListList,
        )

    def tunnel_connections_get(self, id: str) -> TunnelConnectionDetail:
        """Get tunnel connection details"""
        return self._request(
            'GET',
            f'tunnel-connections/{id}/',
            expected_status=200,
            response_model=TunnelConnectionDetail,
        )

    def users_list(self, **params: Any) -> PaginatedUserListList:
        """List users"""
        return self._request(
            'GET',
            'users/',
            params=params,
            expected_status=200,
            response_model=PaginatedUserListList,
        )

    def users_add(self, data: JsonMapping | None = None, **fields: Any) -> UserDetail:
        """Create user"""
        return self._request(
            'POST',
            'users/',
            json=self._serialize_body(data, **fields),
            expected_status=201,
            response_model=UserDetail,
        )

    def users_get(self, id: str) -> UserDetail:
        """Get user details"""
        return self._request(
            'GET',
            f'users/{id}/',
            expected_status=200,
            response_model=UserDetail,
        )

    def users_update(self, id: str, data: JsonMapping | None = None, **fields: Any) -> UserDetail:
        """Update user"""
        return self._request(
            'PATCH',
            f'users/{id}/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=UserDetail,
        )

    def users_delete(self, id: str) -> None:
        """Delete tenant"""
        return self._request(
            'DELETE',
            f'users/{id}/',
            expected_status=204,
        )

    def users_current_get(self) -> UserDetail:
        """Get current user's details"""
        return self._request(
            'GET',
            'users/current/',
            expected_status=200,
            response_model=UserDetail,
        )

    def users_current_update(self, data: JsonMapping | None = None, **fields: Any) -> UserDetail:
        """Update current user's details"""
        return self._request(
            'PATCH',
            'users/current/',
            json=self._serialize_body(data, **fields),
            expected_status=200,
            response_model=UserDetail,
        )

    def vlans_list(self, **params: Any) -> PaginatedVLANList:
        """List VLANs"""
        return self._request(
            'GET',
            'vlans/',
            params=params,
            expected_status=200,
            response_model=PaginatedVLANList,
        )

    def vlans_get(self, id: str) -> VLAN:
        """Get VLAN details"""
        return self._request(
            'GET',
            f'vlans/{id}/',
            expected_status=200,
            response_model=VLAN,
        )

    def vrfs_list(self, **params: Any) -> PaginatedVRFList:
        """List VRFs"""
        return self._request(
            'GET',
            'vrfs/',
            params=params,
            expected_status=200,
            response_model=PaginatedVRFList,
        )

    def vrfs_get(self, id: str) -> VRF:
        """Get VRF details"""
        return self._request(
            'GET',
            f'vrfs/{id}/',
            expected_status=200,
            response_model=VRF,
        )

"""
Shield — Scope Validator
Validates targets against blacklisted networks and scope constraints.
Prevents accidental scanning of private/unauthorized networks.
"""

import ipaddress
import re
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse


class ScopeValidator:
    """Validates scan targets against scope rules and blacklists"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        scope_config = config.get("scope", {})

        # Parse blacklisted networks
        self.blacklist: List[ipaddress.IPv4Network] = []
        for cidr in scope_config.get("blacklist", []):
            try:
                self.blacklist.append(ipaddress.ip_network(cidr, strict=False))
            except ValueError:
                pass

        self.require_scope_file = scope_config.get("require_scope_file", False)
        self.max_targets = scope_config.get("max_targets", 100)

    def validate_target(self, target: str) -> Tuple[bool, str]:
        """
        Validate a target string.

        Returns:
            (is_valid, reason) tuple
        """
        if not target or not target.strip():
            return False, "Target cannot be empty"

        # Extract hostname/IP from URL
        clean_target = self._extract_host(target)

        # Check if it's an IP address or CIDR
        try:
            # Single IP
            ip = ipaddress.ip_address(clean_target)
            return self._check_ip(ip)
        except ValueError:
            pass

        try:
            # CIDR range
            network = ipaddress.ip_network(clean_target, strict=False)
            # Check network size
            if network.num_addresses > self.max_targets:
                return False, (
                    f"Network {clean_target} has {network.num_addresses} addresses, "
                    f"exceeds max_targets ({self.max_targets})"
                )
            # Check if any part overlaps blacklist
            for blacklisted in self.blacklist:
                if network.overlaps(blacklisted):
                    return False, f"Network {clean_target} overlaps blacklisted range {blacklisted}"
            return True, "Valid target"
        except ValueError:
            pass

        # It's a hostname/domain — allowed (DNS will resolve later)
        if self._is_valid_hostname(clean_target):
            return True, "Valid hostname"

        return False, f"Invalid target format: {target}"

    def _extract_host(self, target: str) -> str:
        """Extract hostname or IP from a target string (may be URL)"""
        # If it looks like a URL, parse it
        if "://" in target:
            parsed = urlparse(target)
            return parsed.hostname or target

        # Remove port if present
        if ":" in target and not target.startswith("["):
            host_part = target.rsplit(":", 1)[0]
            return host_part

        return target.strip()

    def _check_ip(self, ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> Tuple[bool, str]:
        """Check if an IP address is in the blacklist"""
        for network in self.blacklist:
            if ip in network:
                return False, f"IP {ip} is in blacklisted range {network}"
        return True, "Valid target"

    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if a string is a valid hostname"""
        if len(hostname) > 253:
            return False
        pattern = re.compile(
            r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*\.?$"
        )
        return bool(pattern.match(hostname))

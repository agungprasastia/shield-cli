"""
Shield — Input Validation & Sanitization
Prevents command injection and validates target formats.
"""

import re
from urllib.parse import urlparse
from typing import Tuple


# Characters that could enable shell injection
DANGEROUS_CHARS = re.compile(r'[;&|`$(){}!\[\]<>\'\"\\]')

# Valid hostname pattern (RFC 1123)
HOSTNAME_RE = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,}$'
)

# Valid IPv4
IPV4_RE = re.compile(
    r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(/\d{1,2})?$'
)

# Valid IPv6 (simplified)
IPV6_RE = re.compile(r'^[0-9a-fA-F:]+(/\d{1,3})?$')


def validate_target(target: str) -> Tuple[bool, str]:
    """
    Validate and sanitize a target string.
    Returns (is_valid, error_message).
    """
    if not target or not target.strip():
        return False, "Target cannot be empty"

    target = target.strip()

    # Check for command injection characters
    if DANGEROUS_CHARS.search(target):
        return False, f"Target contains dangerous characters: {target}"

    # Check max length
    if len(target) > 253:
        return False, "Target too long (max 253 characters)"

    # Try parsing as URL
    if target.startswith(("http://", "https://")):
        try:
            parsed = urlparse(target)
            hostname = parsed.hostname
            if not hostname:
                return False, f"Invalid URL: {target}"
            if DANGEROUS_CHARS.search(hostname):
                return False, f"URL hostname contains dangerous characters"
            return True, ""
        except Exception:
            return False, f"Invalid URL format: {target}"

    # Try as IP address
    ipv4_match = IPV4_RE.match(target)
    if ipv4_match:
        # Validate each octet
        octets = [int(ipv4_match.group(i)) for i in range(1, 5)]
        if all(0 <= o <= 255 for o in octets):
            return True, ""
        return False, f"Invalid IPv4 address: {target}"

    # Try as IPv6
    if IPV6_RE.match(target):
        return True, ""

    # Try as hostname
    # Remove trailing dot if present
    clean = target.rstrip(".")
    if HOSTNAME_RE.match(clean):
        return True, ""

    # CIDR notation (e.g., 192.168.1.0/24)
    if "/" in target:
        base = target.split("/")[0]
        valid, msg = validate_target(base)
        if valid:
            return True, ""
        return False, f"Invalid CIDR: {target}"

    return False, f"Invalid target format: {target}. Use a hostname, IP, URL, or CIDR."


def sanitize_for_command(value: str) -> str:
    """
    Sanitize a string value before passing to subprocess.
    Strips dangerous characters.
    """
    return DANGEROUS_CHARS.sub('', value).strip()

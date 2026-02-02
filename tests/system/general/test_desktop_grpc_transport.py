# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
from datetime import timedelta
from datetime import timezone
import os
from pathlib import Path
import signal
import socket
from unittest.mock import patch

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID
from cryptography.x509.oid import NameOID
import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.core import settings
from ansys.aedt.core.desktop import _find_free_port
from ansys.aedt.core.generic.settings import DEFAULT_GRPC_LISTEN_ALL
from ansys.aedt.core.generic.settings import DEFAULT_GRPC_LOCAL
from ansys.aedt.core.generic.settings import DEFAULT_GRPC_SECURE_MODE
from tests.conftest import DESKTOP_VERSION

pytestmark = pytest.mark.skipif(DESKTOP_VERSION < "2026.2", reason="To be moved in another test suite.")

# pytestmark = pytest.mark.desktop_grpc_stransport


# NOTE: Activating this environment variable forces PyAEDT to use the
# old grpc connection arguments. This is useful for testing backward
# compatibility with previous SP of AEDT.
# os.environ["PYAEDT_USE_PRE_GRPC_ARGS"] = "True"

AEDT_VERSION = DESKTOP_VERSION
HOST_NAME = socket.gethostbyname(socket.gethostname())
IS_WINDOWS = os.name == "nt"
GRPC_CONNECTION_TIMEOUT = 30  # seconds


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


LOCAL_IP = get_local_ip()
REMOTE_HOSTS = (LOCAL_IP, socket.gethostname()) if os.getenv("ON_CI", "False") == "True" else (LOCAL_IP,)
LOCAL_HOSTS = ("127.0.0.1", "localhost")


def generate_private_key(key_size: int = 4096) -> rsa.RSAPrivateKey:
    """
    Generate an RSA private key.

    Parameters
    ----------
    key_size : int, optional
        Size of the RSA key in bits, by default 4096

    Returns
    -------
    rsa.RSAPrivateKey
        Generated RSA private key
    """
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )


def save_private_key(key: rsa.RSAPrivateKey, filename: str) -> None:
    """
    Save a private key to a PEM file.

    Parameters
    ----------
    key : rsa.RSAPrivateKey
        The private key to save
    filename : str
        Path to the output file
    """
    with open(filename, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def save_certificate(cert: x509.Certificate, filename: str) -> None:
    """
    Save a certificate to a PEM file.

    Parameters
    ----------
    cert : x509.Certificate
        The certificate to save
    filename : str
        Path to the output file
    """
    with open(filename, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def create_ca_certificate(ca_key: rsa.RSAPrivateKey, validity_days: int) -> x509.Certificate:
    """
    Create a self-signed CA certificate.

    Parameters
    ----------
    ca_key : rsa.RSAPrivateKey
        The private key for the CA certificate
    validity_days : int
        Number of days the certificate should be valid

    Returns
    -------
    x509.Certificate
        Self-signed CA certificate with appropriate extensions for certificate signing
    """
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "Test CA"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def create_server_certificate(
    server_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    server_common_name: str,
    validity_days: int,
    san_names: list = None,
) -> x509.Certificate:
    """
    Create a server certificate signed by the CA with optional Subject Alternative Names.

    Parameters
    ----------
    server_key : rsa.RSAPrivateKey
        The private key for the server certificate
    ca_cert : x509.Certificate
        The CA certificate to use as issuer
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign the certificate
    server_common_name : str
        The common name for the server certificate (will be used as CN and primary SAN)
    validity_days : int
        Number of days the certificate should be valid
    san_names : list, optional
        Additional Subject Alternative Names to include, by default None

    Returns
    -------
    x509.Certificate
        Server certificate signed by the CA with SERVER_AUTH extended key usage
    """
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, server_common_name),
        ]
    )

    # Build SAN list - always include the CN, plus any additional names
    san_list = [x509.DNSName(server_common_name)]
    if san_names:
        for name in san_names:
            # Skip if it's the same as CN to avoid duplicates
            if name != server_common_name:
                san_list.append(x509.DNSName(name))

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage(
                [
                    ExtendedKeyUsageOID.SERVER_AUTH,
                ]
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def create_client_certificate(
    client_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    client_common_name: str,
    validity_days: int,
) -> x509.Certificate:
    """
    Create a client certificate signed by the CA.

    Parameters
    ----------
    client_key : rsa.RSAPrivateKey
        The private key for the client certificate
    ca_cert : x509.Certificate
        The CA certificate to use as issuer
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign the certificate
    client_common_name : str
        The common name for the client certificate
    validity_days : int
        Number of days the certificate should be valid

    Returns
    -------
    x509.Certificate
        Client certificate signed by the CA with CLIENT_AUTH extended key usage
    """
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, client_common_name),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(client_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName(client_common_name),
                ]
            ),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage(
                [
                    ExtendedKeyUsageOID.CLIENT_AUTH,
                ]
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def parse_server_spec(server_spec: str) -> tuple[str, list]:
    """
    Parse a server specification string into primary hostname and SAN list.

    Parameters
    ----------
    server_spec : str
        A comma-separated string like "node01,192.0.2.1" or just "node01"

    Returns
    -------
    tuple[str, list]
        Tuple containing (primary_hostname, [additional_san_names])

    Raises
    ------
    ValueError
        If the server specification is empty or invalid
    """
    names = [name.strip() for name in server_spec.split(",") if name.strip()]
    if not names:
        raise ValueError("Server specification cannot be empty")

    primary_hostname = names[0]
    additional_sans = names[1:] if len(names) > 1 else []

    return primary_hostname, additional_sans


def generate_server_certificates(
    ca_cert: x509.Certificate, ca_key: rsa.RSAPrivateKey, server_specs: list, validity_days: int
) -> list:
    """
    Generate server certificates.

    Parameters
    ----------
    ca_cert : x509.Certificate
        The CA certificate to sign with
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign with
    server_specs : list
        List of server specification strings in format "hostname[,san1,san2,...]"
    validity_days : int
        Number of days the certificates should be valid

    Returns
    -------
    list
        List of generated certificate filenames
    """
    generated_files = []

    for spec in server_specs:
        primary_hostname, additional_sans = parse_server_spec(spec)

        # If only one server is specified, use 'server' as generic name
        if len(server_specs) == 1:
            filename = "server"
        else:
            filename = primary_hostname

        print(f"Generating server certificate for {primary_hostname}")
        if additional_sans:
            print(f"  Additional SAN names: {', '.join(additional_sans)}")

        # Generate server key and certificate
        server_key = generate_private_key()
        server_cert = create_server_certificate(
            server_key, ca_cert, ca_key, primary_hostname, validity_days, additional_sans
        )

        # Save with primary hostname as filename
        key_filename = f"{filename}.key"
        cert_filename = f"{filename}.crt"

        save_private_key(server_key, key_filename)
        save_certificate(server_cert, cert_filename)

        generated_files.extend([key_filename, cert_filename])

    return generated_files


settings.enable_error_handler = False
settings.enable_debug_logger = True


def generate_certs(server_specs: list[str], output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    os.chdir(output_dir)

    generated_files = []

    print("Generating CA key and certificate for self-signing...")
    # Generate CA key and certificate for self-signing
    ca_key = generate_private_key()
    ca_cert = create_ca_certificate(ca_key, 1)

    save_private_key(ca_key, "ca.key")
    save_certificate(ca_cert, "ca.crt")
    generated_files.extend(["ca.key", "ca.crt"])

    # Generate server certificates
    print("Generating server certificate(s)...")
    server_files = generate_server_certificates(ca_cert, ca_key, server_specs, 1)
    generated_files.extend(server_files)

    print("Generating client certificate (CN: Test Client)...")
    # Generate client key and certificate
    client_key = generate_private_key()
    client_cert = create_client_certificate(client_key, ca_cert, ca_key, "Test Client", 1)

    save_private_key(client_key, "client.key")
    save_certificate(client_cert, "client.crt")
    generated_files.extend(["client.key", "client.crt"])


# ##############################################################################


@pytest.mark.skipif(not IS_WINDOWS, reason="WNUA is only available on Windows.")
def test_desktop_default_to_wnua_on_windows(monkeypatch) -> None:
    """Test that Desktop defaults to WNUA mode on Windows."""
    monkeypatch.setattr(settings, "grpc_local", DEFAULT_GRPC_LOCAL)
    monkeypatch.setattr(settings, "grpc_secure_mode", DEFAULT_GRPC_SECURE_MODE)
    monkeypatch.setattr(settings, "grpc_listen_all", DEFAULT_GRPC_LISTEN_ALL)

    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True)
    assert desktop.grpc_mode == "wnua"
    desktop.release_desktop()


@pytest.mark.skipif(IS_WINDOWS, reason="UDS is only available on Linux.")
def test_desktop_default_to_uds_on_linux(monkeypatch) -> None:
    """Test that Desktop defaults to UDS mode on Linux."""
    monkeypatch.setattr(settings, "grpc_local", DEFAULT_GRPC_LOCAL)
    monkeypatch.setattr(settings, "grpc_secure_mode", DEFAULT_GRPC_SECURE_MODE)
    monkeypatch.setattr(settings, "grpc_listen_all", DEFAULT_GRPC_LISTEN_ALL)

    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True)
    assert desktop.grpc_mode == "uds"
    desktop.release_desktop()


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
@pytest.mark.parametrize("missing_file", ("ca.crt", "client.crt", "client.key"))
def test_desktop_default_mtls_failure_due_to_missing_certificate(missing_file, monkeypatch) -> None:
    """Test that Desktop raises FileNotFoundError when a required certificate file is missing."""
    monkeypatch.setattr(settings, "grpc_local", DEFAULT_GRPC_LOCAL)
    monkeypatch.setattr(settings, "grpc_secure_mode", DEFAULT_GRPC_SECURE_MODE)
    monkeypatch.setattr(settings, "grpc_listen_all", DEFAULT_GRPC_LISTEN_ALL)

    if IS_WINDOWS:
        certs_dir = Path(os.environ["USERPROFILE"], "certs")
    else:
        certs_dir = Path(os.environ["HOME"], "certs")

    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(certs_dir))
    with patch.object(Path, "is_file", side_effect=lambda self: self.name != missing_file, autospec=True):
        with pytest.raises(FileNotFoundError) as exc:
            Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True)

    assert f"Certificate file '{missing_file}' not found in folder" in str(exc.value)


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
def test_desktop_default_mtls_failure_due_to_bad_certificate(monkeypatch, tmp_path) -> None:
    """Test that Desktop raises an exception when certificate files are present but invalid."""
    monkeypatch.setattr(settings, "grpc_local", DEFAULT_GRPC_LOCAL)
    monkeypatch.setattr(settings, "grpc_secure_mode", DEFAULT_GRPC_SECURE_MODE)
    monkeypatch.setattr(settings, "grpc_listen_all", DEFAULT_GRPC_LISTEN_ALL)
    port = _find_free_port()

    for file in ("ca.crt", "client.crt", "client.key", "server.crt", "server.key"):
        file_path = tmp_path / file
        file_path.write_text("Dummy content")
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")

    with pytest.raises(Exception):
        Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, port=port)
    from ansys.aedt.core.generic.general_methods import active_sessions

    sessions = active_sessions()
    for j, k in sessions.items():
        if k == port:
            os.kill(j, signal.SIGTERM)


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
@pytest.mark.parametrize("machine", LOCAL_HOSTS)
def test_desktop_local_insecure_success(machine, monkeypatch) -> None:
    """Test that Desktop can connect in local insecure mode."""
    monkeypatch.setattr(settings, "grpc_local", True)
    monkeypatch.setattr(settings, "grpc_secure_mode", False)
    monkeypatch.setattr(settings, "grpc_listen_all", False)
    port = None if machine != "localhost" else _find_free_port()

    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, port=port)
    assert desktop.grpc_mode == "insecure"
    desktop.release_desktop()


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
@pytest.mark.parametrize("machine", LOCAL_HOSTS)
def test_desktop_local_mtls_success(machine, monkeypatch, tmp_path) -> None:
    """Test that Desktop can connect in local mTLS mode."""
    monkeypatch.setattr(settings, "grpc_local", True)
    monkeypatch.setattr(settings, "grpc_secure_mode", True)
    monkeypatch.setattr(settings, "grpc_listen_all", False)
    port = None if machine != "localhost" else _find_free_port()
    generate_certs([machine], tmp_path)
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")

    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, machine=machine, port=port)
    assert desktop.grpc_mode == "mtls"
    desktop.release_desktop()


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
@pytest.mark.parametrize("machine", REMOTE_HOSTS)
def test_desktop_remote_insecure_success(machine, monkeypatch) -> None:
    """Test that Desktop can connect in remote insecure mode."""
    monkeypatch.setattr(settings, "grpc_local", False)
    monkeypatch.setattr(settings, "grpc_secure_mode", False)
    monkeypatch.setattr(settings, "grpc_listen_all", False)
    port = _find_free_port()
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")
    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, machine=machine, port=port)

    assert desktop.grpc_mode == "insecure"
    desktop.release_desktop()


# NOTE: This test is disabled to avoid exposing unnecessary network interfaces during CI runs.
# Uncomment and use with caution.
# @pytest.mark.parametrize("machine", REMOTE_HOSTS)
# def test_desktop_remote_insecure_all_interface_success(machine, monkeypatch):
#     """Test that Desktop can connect in remote insecure mode listening on all interfaces."""
#    monkeypatch.setattr(settings, 'grpc_local', False)
#    monkeypatch.setattr(settings, 'grpc_secure_mode', False)
#    monkeypatch.setattr(settings, 'grpc_listen_all', False)
#     port = _find_free_port()
#     monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", "10")
#     desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, machine=machine, port=port)

#     assert desktop.grpc_mode == "insecure"
#     desktop.release_desktop()


@pytest.mark.skipif(
    DESKTOP_VERSION < "2026.1",
    reason="Not working in versions without grpc patch",
)
@pytest.mark.parametrize("machine", REMOTE_HOSTS)
def test_desktop_remote_mtls_success(machine, monkeypatch, tmp_path) -> None:
    """Test that Desktop can connect in remote mTLS mode."""
    monkeypatch.setattr(settings, "grpc_local", False)
    monkeypatch.setattr(settings, "grpc_secure_mode", True)
    monkeypatch.setattr(settings, "grpc_listen_all", False)

    port = _find_free_port()
    generate_certs([machine], tmp_path)
    monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
    monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", f"{GRPC_CONNECTION_TIMEOUT}")
    desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, machine=machine, port=port)

    assert desktop.grpc_mode == "mtls"
    desktop.release_desktop()


# NOTE: This test is disabled to avoid exposing unnecessary network interfaces during CI runs.
# Uncomment and use with caution.
# @pytest.mark.parametrize("machine", REMOTE_HOSTS)
# def test_desktop_remote_mtls_all_interface_success(machine, monkeypatch, tmp_path):
#     """Test that Desktop can connect in remote mTLS mode listening on all interfaces."""
#    monkeypatch.setattr(settings, 'grpc_local', False)
#    monkeypatch.setattr(settings, 'grpc_secure_mode', True)
#    monkeypatch.setattr(settings, 'grpc_listen_all', True)
#     port = _find_free_port()
#     generate_certs([machine], tmp_path)
#     monkeypatch.setenv("ANSYS_GRPC_CERTIFICATES", str(tmp_path))
#     monkeypatch.setenv("AnsysEM_GRPC_Connection_Timeout", "10")
#     desktop = Desktop(version=AEDT_VERSION, non_graphical=True, new_desktop=True, machine=machine, port=port)

#     assert desktop.grpc_mode == "mtls"
#     desktop.release_desktop()

import logging
import socket
from pathlib import Path
from typing import Union

from asyncua import Client, ua
from asyncua.crypto.cert_gen import setup_self_signed_certificate
from asyncua.crypto.security_policies import (
    SecurityPolicyAes128Sha256RsaOaep,
    SecurityPolicyAes256Sha256RsaPss,
    SecurityPolicyBasic256Sha256,
)
from cryptography.x509.oid import ExtendedKeyUsageOID

_logger = logging.getLogger(__name__)


async def _generate_certificate(private_key: Path, certificate: Path, client_app_uri: str, hostname: str) -> None:
    """
    Generate a basic self-signed certificate if needed.
    """
    await setup_self_signed_certificate(
        private_key,
        certificate,
        client_app_uri,
        hostname,
        [ExtendedKeyUsageOID.CLIENT_AUTH],
        {
            "countryName": "AT",
            "stateOrProvinceName": "Vorarlberg",
            "localityName": "RW",
            "organizationName": "HMA",
        },
    )


def _get_security_policy(security_policy: str) -> Union[dict, None]:
    """
    Get the security policy object for a given policy name.
    Args:
        security_policy (str): The name of the security policy.
    Returns:
        Union[dict, None]: The security policy object if the policy name is valid, otherwise `None`.
    """
    sec_policy_dict = {
        "basic256sha256": SecurityPolicyBasic256Sha256,
        "aes128sha256rsaoaep": SecurityPolicyAes128Sha256RsaOaep,
        "aes256sha256rsapss": SecurityPolicyAes256Sha256RsaPss,
    }
    if security_policy.lower() in sec_policy_dict.keys():
        return sec_policy_dict.get(security_policy.lower())
    else:
        return None


def _get_security_mode(mode: str) -> Union[dict, None]:
    """
    Get the security mode object for a given mode name.
    Args:
        mode (str): The security mode name.
    Returns:
        Union[dict, None]: The security mode object if the mode is valid, otherwise `None`.
    """
    sec_mode_dict = {
        "none": ua.MessageSecurityMode.None_,
        "sign": ua.MessageSecurityMode.Sign,
        "signandencrypt": ua.MessageSecurityMode.SignAndEncrypt,
    }
    # set message security mode
    if mode.lower() in sec_mode_dict.keys():
        _logger.debug(f"setting security mode to {mode.lower()}")
        return sec_mode_dict.get(mode.lower())
    else:
        return None


async def _get_authentification(auth_method: str, credentials: dict, client_app_uri: str) -> dict:
    """
    Generates the authentication object based on the provided authentication method and credentials.
    Args:
        auth_method (str): The authentication method to use.
        credentials (dict): The user credentials, including username and password.
        client_app_uri (str): The URI of the client application.
    Returns:
        dict: The authentication object, containing the user, password, private key, and certificate.
    """
    auth_object = {}
    auth_object["user"] = ""
    auth_object["password"] = ""
    # get hostname
    hostname = socket.gethostname()
    auth_object["private_key"] = (Path(__file__).parent / "certs" / f"{hostname}_private_key.pem").resolve()
    auth_object["cert"] = (Path(__file__).parent / "certs" / f"{hostname}_certificate").resolve()
    # check what auth method needs to be used
    if auth_method.lower() == "none":
        _logger.debug("setting security mode to none")
        return auth_object
    if auth_method.lower() == "username":
        # set user credentials
        auth_object["user"] = credentials["user"]
        auth_object["password"] = credentials["password"]

        # delete old certificate if it exists
        if auth_object["cert"].is_file():
            auth_object["cert"].unlink()
            _logger.debug(f"Deleted old certificate at {auth_object['cert']}")

        # generate new certificate
        await _generate_certificate(
            private_key=auth_object["private_key"],
            certificate=auth_object["cert"],
            hostname=hostname,
            client_app_uri=client_app_uri,
        )

    return auth_object


@staticmethod
async def configure_opc_client(opc_client: Client, opc_config: dict) -> None:
    """
    Configures an OPC UA client with the provided configuration.
    Args:
        opc_client (OpcUaClient): The OPC UA client to configure.
        opc_config (dict): The configuration for the OPC UA client, including authentication method, security policy, and security mode.
    Returns:
        None
    """

    # OPC client configuration
    opc_client.name = "uaview_client"
    opc_client.description = "uaView OPC-UA terminal client"
    opc_client.product_uri = "urn:uaview:opcclient"
    opc_client.application_uri = "urn:uaview:client:1"
    credentials = {
        "user": opc_config.get("username", ""),  # empty string if missing
        "password": opc_config.get("password", ""),
    }

    # Set authentication method
    if credentials["user"]:  # if username is non-empty
        opc_config["auth_method"] = "username"
    else:
        opc_config["auth_method"] = "anonymous"
    # get security policy
    security_policy = _get_security_policy(opc_config.get("security_policy", None))
    # get security mode
    security_mode = _get_security_mode(opc_config.get("security_mode", None))
    # get authentication
    authentication = await _get_authentification(
        auth_method=opc_config["auth_method"],
        credentials=credentials,
        client_app_uri=opc_client.application_uri,
    )
    # set security
    if security_mode and security_policy:
        await opc_client.set_security(
            policy=security_policy,
            certificate=str(authentication["cert"]),
            private_key=str(authentication["private_key"]),
            mode=security_mode,
        )
    # set user and password
    if credentials:
        opc_client.set_user(authentication["user"])
        opc_client.set_password(authentication["password"])

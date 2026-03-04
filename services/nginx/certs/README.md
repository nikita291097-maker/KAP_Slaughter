# TLS certificate notes

This stage uses a self-signed certificate with SAN entries for:

- `IP:10.46.68.216`
- `IP:127.0.0.1`
- `DNS:localhost`

To remove the `Not Secure` warning in browsers, import `kap-selfsigned.crt` into the trusted root certificate store on each workstation.

For production/corporate rollout, replace this pair with a certificate issued by AD CS / internal PKI and keep the same file names in nginx.

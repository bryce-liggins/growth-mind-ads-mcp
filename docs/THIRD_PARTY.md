# Third-party components

The management code was adapted from Growth Mind's local Python bridge, with the account owner authorizing public release. It uses external libraries rather than copying their implementations into this source tree.

Direct runtime dependencies: FastMCP, google-auth and requests. Their transitive dependencies are resolved in uv.lock and retain their respective licenses. Hatchling builds the package. Installed distribution metadata provides the exact version/license notices for the resolved environment; preserve applicable notices when redistributing dependency binaries or combined distributions.

Google's separate Google Ads MCP project is linked as a possible reporting connector and is not bundled or relicensed here. Provider names identify compatibility and documentation, not endorsement.

The MIT license applies to this repository's original source and documentation. It does not grant rights to third-party trademarks, credentials, private client material or provider services.


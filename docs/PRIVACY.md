# Privacy and application-document worksheet

Use this to draft truthful documentation for your own deployment. This is not a universal privacy policy, Google approval or legal compliance certification.

## Map the real data flow

For the local design: owner authorizes Google access → agent host calls a local MCP tool → server sends an authenticated request to Google → Google response returns through the host → a local audit record is saved for successful validation/application.

The server does not directly send data to an AI provider. The host may send tool inputs/results to its provider. Identify the actual provider, settings and terms. Hosted or multi-user deployments need a separate architecture review.

## Gather facts before drafting

Use existing verified deployment records first. Guide the owner through missing facts one question at a time, wait for the answer and save it before continuing. Explain an unfamiliar choice briefly when needed. The list below is the agent's coverage checklist, not a form to send all at once. Do not request secret values or infer policy commitments from missing answers.

- Operator/legal identity, application name, contact and controlled domain.
- Internal tool or external users; who grants access and can revoke it.
- Actual Google scopes and account permissions.
- Data read/written, purpose of each use, and data sent to the host/provider.
- Storage locations, access controls, backups and audit contents.
- Actual retention and deletion procedures, including provider limitations.
- Other processors and integrations.
- Owner/user rights and a working request channel.
- Credential revocation and incident response.

Never invent encryption certifications, deletion periods, model-training promises or approval status.

## Application description template

Replace every bracketed field before use:

“[APP NAME] is operated by [OPERATOR] for [AUDIENCE]. It connects [AGENT CLIENT] to authorized Google Ads accounts to [ACTUAL PURPOSES]. Reporting uses [REPORTING COMPONENT]. Management uses a local server supporting [ENABLED OPERATION SCOPE]. Changes are validated, presented for account-owner approval, applied and checked afterward. Credentials are stored in [PRIVATE LOCATION]. [ACTUAL HOST/PROCESSORS] receive [DATA CATEGORIES] for [PURPOSE]. Contact [CONTACT] for access or deletion requests.”

Don't say “read-only” if the configured system can write. Don't say the approval ticket independently proves human consent.

## Privacy-page outline

1. Identity and scope of this notice.
2. Data accessed/collected and why.
3. Google access and account-change controls.
4. AI hosts, other processors and data sharing.
5. Storage, access controls and actual retention.
6. Revocation, deletion and request process.
7. Changes and contact.

Include applicable provider commitments only after confirming they apply and your implementation follows them. [Google brand verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification) and [sensitive-scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification) describe relevant requirements.

## Acceptance

Owner approves the factual description; domains/contacts work; revocation/deletion procedures can be followed; document links match the configured app; verification state is recorded honestly. Never publish the template with placeholders or another operator's identity.


# Enoch drafting with an existing Azure identity

The Azure backend supports explicit `AZURE_OPENAI_AUTH_MODE=azure-cli`.
Set the existing account HTTPS endpoint and deployment with
`AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT_ID`.
For a deployment that does not accept temperature, explicitly set
`AZURE_OPENAI_OMIT_TEMPERATURE=1`; the YAML then omits that metadata rather
than claiming a parameter was used.

No key is created or printed. Token acquisition uses the existing Azure CLI
session and the Cognitive Services audience. Only Azure OpenAI account hosts
are accepted in CLI mode. Failed token acquisition never prints CLI output.
The identity still needs model inference permission on the selected account.
This backend neither grants roles nor creates deployments.

On 2026-10-06 the user approved Cognitive Services OpenAI User on the single
existing cartha-aoai-truth-1c9177c8 resource. A direct serial Enoch7:6 draft
succeeded with gpt-5.6-sol-2026-07-09. The result remains an external draft,
not canonical source, specialist review, artwork approval or public delivery.
Existing API-key mode remains the default for compatibility.

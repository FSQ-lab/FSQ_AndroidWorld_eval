# Private evaluator diagnostics

New attempts capture existing evaluator-thread root/absl logging records and bounded native exception arguments/frames during the original, single is_successful call. Reward, action/time budgets and native scoring are not redefined. This does not rescore historical attempts or change the retained 83.1897% result.

The sidecar is raw-private/evaluator-diagnostics.json (0700 private directory, 0600 file). It associates task name/frozen parameter digest, evaluator phase/timestamps and original reward with existing log templates/bounded arguments and exception metadata. No extra DB/device query or inferred component score is added. A scalar-only interface reports componentResults.status=not_provided.

The public evaluator.diagnostics reference contains path/SHA256/bytes/status; write_failed contains only status/errorType. Evaluator public errors retain bounded type metadata, not private arguments or traceback. Do not copy private sidecars into Agent prompts, tools, Skills or normalized events. Existing native log sinks are unchanged and may already emit private values; this is not an OS confidentiality guarantee.

Successful receipts are limited to 64 KiB, logs to 48 KiB / 256 records. Literal/type metadata share a 2,048-character / 64-node projection budget, containers have 8-item / depth-3 limits, type names are clipped to 128 characters, and exception frames to 16 without locals. Omission/truncation/capture/write failures are explicit. Written does not imply complete logs, component scores or final DB/device snapshots. Disk latency is not bounded.

Managed filter registration/detach uses serialized copy-on-write snapshots preserving foreign filters/handlers and in-flight dispatch. Type checks use identity; builtin type-name descriptors/string operations avoid user metaclass equality/name hooks. Arbitrary concurrent third-party logger reconfiguration is outside this guarantee.

These reviewed source fixes do not establish installed identity or launch qualification. The new AndroidWorld gitlink identifies corrected 001 / 014 / 076 definitions described in its task guide. Full runtime/installed import identity, new manifest/readiness and fresh qualification remain separate gates; historical manifests and raw evidence are unchanged.

Reviewed task-contract source: AndroidWorld commit `09a579126c2a4d33902b33bbcf5cb80b3eb521a7`.

# The negative controls, as runnable code

These are the deliberately broken builds used to test Consullo's checks on 2026-08-10. They are
here because **a negative control described in prose is a plan, not evidence** (NCP N2), and
because the next person to apply this profile should not have to re-derive them.

| file | breaks | for |
|---|---|---|
| `broken_socket_only.py` | binds 127.0.0.1:8080, accepts connections, serves nothing | `connectivity_check` — reproduces AS-01's state: process alive, capability dead |
| `broken_unhealthy.py` | returns HTTP 503 with `{"status":"unhealthy"}` | `responsiveness_check` — the endpoint answering that it is *not* healthy |
| `NcpProbe.java` | drives the real `SystemUtilities.getHealthStatus()` | `getHealthStatus` under `-Dhealth.check.database.enabled=false` and `-Ddev.mode=true` |

Running them:

```bash
python3 broken_socket_only.py &                 # then run connectivity_check
python3 broken_unhealthy.py &                   # then run responsiveness_check
env -u _JAVA_OPTIONS java -cp "<utilities-jar>:$(mvn -q dependency:build-classpath \
    -Dmdep.outputFile=/dev/stdout -DincludeScope=runtime | tail -1)" \
    -Dhealth.check.database.enabled=false NcpProbe.java
```

**Each perturbs the declared capability, not the transport** (N5). None of them cuts the network,
kills a process, or blocks a port — those would make every check fail and demonstrate nothing
about any of them.

**What they do not establish.** They reproduce the *shape* of AS-01's failure on a workstation.
They are not the production failure, and a check that fails here may still be blind to the variant
that actually occurs.

`_JAVA_OPTIONS` must be unset for the Java probe: the workstation's global options include
`--add-exports` flags that are rejected under `--release`, and the probe fails to compile with
them set. That cost twenty minutes and is recorded so it costs the next person none.

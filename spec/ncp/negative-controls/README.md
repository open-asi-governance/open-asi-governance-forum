# The negative controls, as runnable code

These are the deliberately broken builds used to test a real implementer's checks on 2026-08-10.
They are here because **a negative control described in prose is a plan, not evidence** (NCP N2),
and because the next person to apply this profile should not have to re-derive them.

**Abstracted.** These reproduce the *shape* of each perturbation without naming the assessed
system's files, classes or configuration keys. See `record/designs/implementer-disclosure.md` for
why: the detail belongs to the implementer, not to this repository.

| file | breaks | for |
|---|---|---|
| `broken_socket_only.py` | binds 127.0.0.1:8080, accepts connections, serves nothing | any port-liveness probe — reproduces "process alive, capability dead" |
| `broken_unhealthy.py` | returns HTTP 503 with `{"status":"unhealthy"}` | any responsiveness probe — the endpoint answering that it is *not* healthy |
| `NcpProbe.java` | drives a static health-aggregator method reflectively, under chosen `-D` flags | any component-health aggregator whose verdict depends on configuration |

Running them:

```bash
python3 broken_socket_only.py &          # then run the port-liveness probe
python3 broken_unhealthy.py &            # then run the responsiveness probe

java -cp "<app-jar>:$(mvn -q dependency:build-classpath \
    -Dmdep.outputFile=/dev/stdout -DincludeScope=runtime | tail -1)" \
    -D<flag-under-test>=<value> NcpProbe.java com.example.Health getHealthStatus
```

**Drive the aggregator directly, not through the HTTP surface.** Where the aggregator ships as a
separate artifact from the service that serves it, a change is invisible until that artifact is
rebuilt and installed — so verifying through the endpoint can "confirm" a fix against a stale
build. That is a green signal not causally downstream of the change, which is the exact class this
profile exists to catch, reappearing inside the verification of a fix for it.

**Each perturbs the declared capability, not the transport** (N5). None cuts the network, kills a
process, or blocks a port — those make every check fail and demonstrate nothing about any of them.

**What they do not establish.** They reproduce the shape of a recorded production failure on a
workstation. They are not that failure, and a check that fails here may still be blind to the
variant that actually occurs.

**Gotcha, recorded so it costs the next person nothing:** if a global `_JAVA_OPTIONS` sets
`--add-exports` flags, the probe fails to compile under `--release`. Run it with
`env -u _JAVA_OPTIONS`. That cost twenty minutes.

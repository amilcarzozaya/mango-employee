# Architecture

`Employee + Skill + Task → Context Resolver → Runtime Package → Safety Contract → Runtime Adapter → Model`

The Employee contract defines identity, mission, MANGO design, sources, memory, Skills, tools, autonomy, gates, routines, evaluation, learning and governance.

The Runtime Package is the portability boundary. Adapters should be thin: they should not redefine the Employee. They only translate the same bounded package into the invocation expected by each supported runtime.
